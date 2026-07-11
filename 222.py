import numpy as np
import pandas as pd

# 全局浮点数保留两位小数
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: f'{x:.2f}')

# 原始订单数据
orders = pd.DataFrame({
    'order_id': [f'O{number}' for number in range(1001, 1019)],
    'region': ['华东','华北','华南','华东','西南','华北','华南','华东','西南','华北','华东','华南','西南','华东','华北','华南','华东','西南'],
    'product': ['机械键盘','无线鼠标','显示器','扩展坞','机械键盘','显示器','无线鼠标','显示器','扩展坞','机械键盘','无线鼠标','扩展坞','显示器','机械键盘','扩展坞','显示器','无线鼠标','机械键盘'],
    'category': ['外设','外设','显示设备','配件','外设','显示设备','外设','显示设备','配件','外设','外设','配件','显示设备','外设','配件','显示设备','外设','外设'],
    'quantity': [2,3,1,4,5,2,6,1,3,2,8,2,1,3,5,2,4,6],
    'unit_price': [289,129,1299,399,289,1299,129,1299,399,289,129,399,1299,289,399,1299,129,289],
    'member_level': ['金卡','普通','银卡','金卡','银卡','普通','金卡','银卡','普通','金卡','银卡','金卡','普通','银卡','金卡','金卡','普通','银卡'],
    'coupon_rate': [0.05,0.00,0.08,0.10,0.05,0.00,0.12,0.05,0.00,0.08,0.10,0.05,0.00,0.12,0.05,0.08,0.00,0.10],
    'salesperson': ['小林','小周','小陈','小林','小赵','小周','小陈','小林','小赵','小周','小林','小陈','小赵','小林','小周','小陈','小林','小赵']
})
# 1.1
rows, cols = orders.shape
col_names = orders.columns.tolist()
print(f"数据行数：{rows}，列数：{cols}")
print("所有列名：", col_names)
# 1.2
single_col = orders['region']
multi_cols = orders[['order_id', 'product', 'quantity']]
print("region单列类型：", type(single_col))
print("三列组合类型：", type(multi_cols))
# 1.3
iloc_slice = orders.iloc[3:8, :4]
print("iloc截取4-8行前4列：\n", iloc_slice)
# 1.4
loc_filter = orders.loc[orders['region'] == '华东', ['order_id', 'product', 'member_level']]
print("华东订单筛选结果：\n", loc_filter)
# 任务2：生成analysis，全部向量化计算
analysis = orders.assign(
    # 商品总金额
    gross_amount = lambda x: x['quantity'] * x['unit_price'],
    # 会员折扣：金卡0.1，银卡0.05，普通0
    member_discount = lambda x: np.where(
        x['member_level'] == '金卡', 0.10,
        np.where(x['member_level'] == '银卡', 0.05, 0.00)
    ),
    # 折扣后应付金额
    payable_amount = lambda x: (x['gross_amount'] * (1 - x['member_discount'])) * (1 - x['coupon_rate']),
    # 运费：应付≥1000免邮，否则20
    shipping_fee = lambda x: np.where(x['payable_amount'] >= 1000, 0, 20),
    # 最终实付金额
    final_amount = lambda x: x['payable_amount'] + x['shipping_fee']
).round(2)  # 统一保留两位小数

# 展示前8行核心计算字段
show_cols = ['order_id','gross_amount','member_discount','payable_amount','shipping_fee','final_amount']
print("analysis前8行结算指标：\n", analysis[show_cols].head(8))
# 分步定义3个布尔条件
cond1 = (analysis['region'] == '华东') | (analysis['region'] == '华南')  # 华东/华南
cond2 = analysis['final_amount'] >= 700  # 实付≥700
cond3 = (analysis['quantity'] >= 2) | (analysis['member_level'] == '金卡')  # 数量≥2 或金卡

# 组合总过滤掩码
mask = cond1 & cond2 & cond3

# 筛选、指定列、金额降序
focus_orders = analysis.loc[mask, ['order_id','region','product','quantity','member_level','final_amount']]
focus_orders = focus_orders.sort_values('final_amount', ascending=False)
print("重点跟进订单：\n", focus_orders)
# 定义订单等级函数，不修改原df，嵌套np.where
def add_order_level(df):
    new_df = df.copy()  # 复制避免修改传入表
    new_df['order_level'] = np.where(
        new_df['final_amount'] >= 2000, '战略订单',
        np.where(new_df['final_amount'] >= 1000, '重点订单', '普通订单')
    )
    return new_df

# pipe调用生成带等级表
leveled_orders = analysis.pipe(add_order_level)

# 统计各等级订单数量
level_count = leveled_orders['order_level'].value_counts()
print("各等级订单数量：\n", level_count)
# 完整一条链式操作，无中间表
region_report = (
    analysis
    .pipe(add_order_level)
    .query("final_amount >= 500")
    .groupby(['region', 'order_level'], as_index=False)
    .agg(
        order_count = ('order_id', 'count'),
        quantity_sum = ('quantity', 'sum'),
        revenue_sum = ('final_amount', 'sum'),
        revenue_mean = ('final_amount', 'mean')
    )
    .sort_values('revenue_sum', ascending=False)
    .round(2)
)
print("区域层级经营汇总报表：\n", region_report)
# 6.1 销售人总成交金额
sales_total = leveled_orders.groupby('salesperson')['final_amount'].sum().reset_index()
sales_total = sales_total.sort_values('final_amount', ascending=False)
top_sales = sales_total.iloc[0]['salesperson']
top_sales_total = sales_total.iloc[0]['final_amount']

# 6.2 该销售各地区成交金额
sales_region = leveled_orders[leveled_orders['salesperson'] == top_sales].groupby('region')['final_amount'].sum().reset_index()
sales_region = sales_region.sort_values('final_amount', ascending=False)
core_region = sales_region.iloc[0]['region']
core_region_amt = sales_region.iloc[0]['final_amount']

# 6.3 地区营收占比
ratio = (core_region_amt / top_sales_total) * 100

# 输出结果
print(f"销冠销售：{top_sales}")
print(f"个人总成交金额：{top_sales_total:.2f}")
print(f"核心贡献地区：{core_region}")
print(f"核心地区成交金额：{core_region_amt:.2f}")
print(f"核心地区营收占个人总业绩比例：{ratio:.2f}%")

# 业务结论
print("\n业务结论：该销冠业绩高度依赖核心区域，可持续深耕该区域并复制运营策略至其他区域提升整体业绩。")

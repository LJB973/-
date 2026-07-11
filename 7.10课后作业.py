import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 在线加载数据集，解决文件缺失报错
url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
df_raw = pd.read_csv(url)
df = df_raw.copy()  # 不修改原始数据
print("=== 原始数据概览 ===")
print(f"数据形状：{df.shape}")
print("缺失值统计：")
print(df.isnull().sum())
print("重复行数：", df.duplicated().sum())

# 1. 缺失值三种处理方案
## 1.1 删除缺失行
df_drop = df.dropna(subset=["Embarked"])
print(f"删除缺失港口后行数：{df_drop.shape[0]}")

## 1.2 统计值填充
df_fill = df.copy()
df_fill["Age"] = df_fill["Age"].fillna(df_fill["Age"].median())
df_fill["Embarked"] = df_fill["Embarked"].fillna(df_fill["Embarked"].mode()[0])
df_fill["Cabin"] = df_fill["Cabin"].fillna("Unknown")
print("填充后缺失值：\n", df_fill.isnull().sum())

## 1.3 线性插值
df_interp = df.copy()
df_interp["Age"] = df_interp["Age"].interpolate(method="linear")
print("插值后Age缺失数量：", df_interp["Age"].isnull().sum())

# 2. 重复记录处理
dup_count = df.duplicated().sum()
print(f"原始重复记录数：{dup_count}")
df_clean = df_fill.drop_duplicates(keep="first")
print(f"去重后数据行数：{df_clean.shape[0]}")

# 3. IQR剔除异常值
def remove_outlier(data, col):
    Q1 = data[col].quantile(0.25)
    Q3 = data[col].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    return data[(data[col] >= lower) & (data[col] <= upper)]

df_clean = remove_outlier(df_clean, "Fare")
print(f"剔除票价异常后行数：{df_clean.shape[0]}")

# 4. 数据类型转换与标准化
df_clean["Survived"] = df_clean["Survived"].astype("category")
df_clean["Pclass"] = df_clean["Pclass"].astype("int8")
df_clean["Name"] = df_clean["Name"].str.strip().str.lower()
df_clean["Fare"] = df_clean["Fare"].round(2)

# 导出清洗后文件
df_clean.to_csv("titanic_cleaned.csv", index=False)
print("数据清洗完成，已输出清洗后文件")
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 1. 读取UCI公开PM2.5数据集
url = "http://archive.ics.uci.edu/ml/machine-learning-databases/00381/PRSA_data_2010.1.1-2014.12.31.csv"
air_raw = pd.read_csv(url)
air = air_raw.copy()
print("原始空气质量数据：")
print(air.head())

# 2. 时间字段合并，生成标准时间序列
air["datetime"] = pd.to_datetime(air[["year", "month", "day", "hour"]])
air = air.sort_values("datetime").reset_index(drop=True)
# 新增季节标签
def get_season(month):
    if month in [12,1,2]: return "冬季"
    elif month in [3,4,5]: return "春季"
    elif month in [6,7,8]: return "夏季"
    else: return "秋季"
air["season"] = air["month"].apply(get_season)

# 3. 缺失值处理（PM2.5插值填充）
air["pm2.5"] = air["pm2.5"].interpolate(method="time")
air = air.dropna(subset=["TEMP", "PRES"])
print("缺失值统计：\n", air.isnull().sum())

# 4. 污染物基础统计指标
pollutants = ["pm2.5", "DEWP", "TEMP", "PRES", "Iws"]
stats = air[pollutants].describe().round(2)
print("污染物统计指标：\n", stats)

# 5. 相关性热力图（Matplotlib+Seaborn）
plt.figure(figsize=(10,7), dpi=100)
corr = air[pollutants].corr()
sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", square=True)
plt.title("各污染物与气象因子相关性热力图")
plt.tight_layout()
plt.show()

# 6. 折线图：PM2.5全年小时时间序列
plt.figure(figsize=(14,5), dpi=100)
plt.plot(air["datetime"], air["pm2.5"], color="#d62728", linewidth=0.6)
plt.title("北京PM2.5逐小时浓度时间序列")
plt.xlabel("时间")
plt.ylabel("PM2.5 浓度 μg/m³")
plt.grid(alpha=0.3)
plt.show()

# 7. 柱状图：四季平均PM2.5浓度
season_pm = air.groupby("season")["pm2.5"].mean().reindex(["春季","夏季","秋季","冬季"])
plt.figure(figsize=(8,5))
plt.bar(season_pm.index, season_pm.values, color=["#2ca02c","#1f77b4","#ff7f0e","#d62728"])
plt.title("四季平均PM2.5浓度对比")
plt.ylabel("平均PM2.5浓度")
plt.grid(axis="y", alpha=0.3)
plt.show()

# 8. 散点图：风速Iws与PM2.5关系
plt.figure(figsize=(8,5))
plt.scatter(air["Iws"], air["pm2.5"], alpha=0.2, c="#1f77b4")
plt.title("累计风速与PM2.5浓度散点分布")
plt.xlabel("累计风速 m/s")
plt.ylabel("PM2.5浓度")
plt.grid(alpha=0.3)
plt.show()

# 9. 月度趋势折线：分年PM2.5月度均值
month_avg = air.groupby(["year", "month"])["pm2.5"].mean().reset_index()
plt.figure(figsize=(12,6))
for year in month_avg["year"].unique():
    year_data = month_avg[month_avg["year"]==year]
    plt.plot(year_data["month"], year_data["pm2.5"], marker="o", label=f"{year}年")
plt.title("各年份月度PM2.5平均浓度变化")
plt.xlabel("月份")
plt.ylabel("PM2.5均值")
plt.legend()
plt.xticks(range(1,13))
plt.grid(alpha=0.3)
plt.show()

# 10. 业务结论
winter_avg = air[air["season"]=="冬季"]["pm2.5"].mean()
summer_avg = air[air["season"]=="夏季"]["pm2.5"].mean()
print(f"业务结论：冬季平均PM2.5({winter_avg:.1f})显著高于夏季({summer_avg:.1f})，供暖季污染加剧；风速与PM2.5呈负相关，大风天气利于污染物扩散。")

# 导出清洗后数据集
air.to_csv("air_quality_clean.csv", index=False)


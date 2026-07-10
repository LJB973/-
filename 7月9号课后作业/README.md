# 课程资料整理器

一个 Python 自动化脚本，将课程资料按类型自动整理到不同文件夹中。

## 功能

- 按文件名关键字分类（如"作业"、"练习" → `homework`）
- 按文件后缀分类（`.ppt` → `slides`, `.py` → `code`, `.pdf` → `documents` 等）
- 支持 `--dry-run` 预览模式，安全可靠
- 自动处理同名文件冲突
- 生成详细的整理报告

## 项目结构

```
02_course_materials_organizer/
├── main.py                      # 入口文件
├── README.md
├── course_organizer/            # 核心逻辑模块
│   ├── __init__.py
│   ├── rules.py                 # 分类规则（后缀、关键字映射）
│   └── core.py                  # 整理计划生成与执行
└── sample_materials/            # 示例资料
    ├── Python第01讲_基础语法.pptx
    ├── Python第01讲_课堂代码.py
    ├── Python第01讲_作业说明.pdf
    ├── NumPy数组练习.ipynb
    ├── 成绩样例.csv
    ├── 课程通知.txt
    ├── 学生问题记录.md
    ├── 截图_环境配置.png
    └── 未分类文件.xyz
```

## 用法

### 预览整理计划（不实际执行）

```bash
python main.py --source sample_materials --target organized_materials --dry-run
```

### 执行整理（复制模式，默认）

```bash
python main.py --source sample_materials --target organized_materials
```

### 移动模式

```bash
python main.py --source sample_materials --target organized_materials --mode move
```

### 递归整理子目录

```bash
python main.py --source . --target organized --recursive
```

### 只整理指定后缀

```bash
python main.py --source sample_materials --target organized --include .py .ipynb
```

### 排除指定后缀

```bash
python main.py --source sample_materials --target organized --exclude .png
```

## 分类规则

| 类型 | 目录名 | 规则 |
| --- | --- | --- |
| 作业 | `homework` | 文件名含"作业/练习/实验/任务"（优先级最高） |
| 课件 | `slides` | `.ppt` `.pptx` `.key` |
| 代码 | `code` | `.py` `.ipynb` `.c` `.cpp` `.java` |
| 数据 | `data` | `.csv` `.xlsx` `.json` |
| 文档 | `documents` | `.pdf` `.doc` `.docx` `.txt` `.md` |
| 图片 | `images` | `.png` `.jpg` `.jpeg` `.gif` |
| 其他 | `others` | 无法识别的后缀 |

## 这个程序体现了 Python 的哪些作用

1. **快速编写自动化脚本** — 用几十行代码实现了一个实用的文件整理工具。
2. **善用标准库** — `pathlib` 处理路径、`shutil` 复制移动文件、`argparse` 解析命令行参数，无需安装第三方库。
3. **字典组织规则** — 用 `dict` + `set` 保存"后缀 → 分类"的映射，规则集中管理，易于扩展。
4. **模块化设计** — 拆分为入口文件 (`main.py`)、核心逻辑 (`core.py`)、规则定义 (`rules.py`)，各司其职。
5. **安全优先** — 默认复制不删除原文件，`--dry-run` 预览防止误操作，自动处理重名避免覆盖。

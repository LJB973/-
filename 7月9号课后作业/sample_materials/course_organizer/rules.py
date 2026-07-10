"""
分类规则模块
定义文件分类的规则和映射
"""

# 后缀名到分类目录的映射
SUFFIX_RULES = {
    'slides': {'.ppt', '.pptx', '.key'},
    'code': {'.py', '.ipynb', '.c', '.cpp', '.java'},
    'data': {'.csv', '.xlsx', '.json'},
    'documents': {'.pdf', '.doc', '.docx', '.txt', '.md'},
    'images': {'.png', '.jpg', '.jpeg', '.gif'},
}

# 关键字规则（优先级高于后缀规则）
KEYWORD_RULES = {
    'homework': ['作业', '练习', '实验', '任务'],
}

# 默认分类
DEFAULT_CATEGORY = 'others'


def get_category_by_suffix(suffix):
    """
    根据文件后缀获取分类目录

    Args:
        suffix: 文件后缀（包含点号，如 '.pdf'）

    Returns:
        str: 分类目录名
    """
    suffix = suffix.lower()
    for category, suffixes in SUFFIX_RULES.items():
        if suffix in suffixes:
            return category
    return DEFAULT_CATEGORY


def get_category_by_keyword(filename):
    """
    根据文件名关键字获取分类目录

    Args:
        filename: 文件名（不包含路径）

    Returns:
        str or None: 如果匹配到关键字则返回分类目录名，否则返回None
    """
    for category, keywords in KEYWORD_RULES.items():
        for keyword in keywords:
            if keyword in filename:
                return category
    return None


def get_category(filename):
    """
    获取文件的分类目录
    优先使用关键字规则，其次使用后缀规则

    Args:
        filename: 文件名（不包含路径）

    Returns:
        str: 分类目录名
    """
    # 先检查关键字
    category = get_category_by_keyword(filename)
    if category:
        return category

    # 再检查后缀
    import os
    _, suffix = os.path.splitext(filename)
    if suffix:
        return get_category_by_suffix(suffix)

    return DEFAULT_CATEGORY

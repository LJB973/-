"""
核心逻辑模块
负责整理计划的生成、执行和报告
"""

from pathlib import Path
import shutil
from . import rules


def generate_plan(source_dir, recursive=False, include=None, exclude=None):
    """
    扫描源目录，生成整理计划

    Args:
        source_dir: 源目录路径 (str 或 Path)
        recursive: 是否递归扫描子目录
        include: 只包含指定后缀列表，如 ['.py', '.ipynb']
        exclude: 排除指定后缀列表，如 ['.png']

    Returns:
        list[dict]: 计划项列表，每项包含:
            - source: 源文件 Path
            - filename: 文件名
            - category: 分类目录名
            - target_name: 目标文件名（可能已处理重名）
    """
    source = Path(source_dir)
    if not source.exists() or not source.is_dir():
        print(f"错误：源目录不存在或不是目录 — {source}")
        return []

    # 收集文件
    pattern = '**/*' if recursive else '*'
    files = [f for f in source.glob(pattern) if f.is_file()]

    # 应用 include / exclude 过滤
    if include:
        include_set = {s.lower() if s.startswith('.') else f'.{s.lower()}' for s in include}
        files = [f for f in files if f.suffix.lower() in include_set]
    if exclude:
        exclude_set = {s.lower() if s.startswith('.') else f'.{s.lower()}' for s in exclude}
        files = [f for f in files if f.suffix.lower() not in exclude_set]

    # 生成计划
    plan = []
    for file_path in files:
        category = rules.get_category(file_path.name)
        plan.append({
            'source': file_path,
            'filename': file_path.name,
            'category': category,
        })

    return plan


def _resolve_target_path(target_dir, category, filename):
    """
    解决目标文件路径，自动处理重名

    Args:
        target_dir: 目标根目录 (Path)
        category: 分类目录名
        filename: 原始文件名

    Returns:
        Path: 不冲突的目标文件路径
    """
    target_dir = Path(target_dir)
    category_dir = target_dir / category
    target_path = category_dir / filename

    if not target_path.exists():
        return target_path

    # 重名处理：在文件名前加 _1, _2 等
    stem = target_path.stem
    suffix = target_path.suffix
    counter = 1
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = category_dir / new_name
        if not new_path.exists():
            return new_path
        counter += 1


def execute_plan(plan, target_dir, mode='copy', dry_run=False):
    """
    执行整理计划

    Args:
        plan: generate_plan 返回的计划列表
        target_dir: 目标根目录 (str 或 Path)
        mode: 'copy' 或 'move'
        dry_run: 如果为 True，只预览不执行

    Returns:
        list[dict]: 实际执行结果，每项包含:
            - filename: 文件名
            - category: 分类
            - source: 源路径
            - target: 目标路径
            - status: 'skipped'(dry-run) / 'copied' / 'moved'
    """
    target = Path(target_dir)
    results = []

    for item in plan:
        source_path = item['source']
        category = item['category']
        filename = item['filename']

        # 解析目标路径（包括重名处理）
        rel_subdir = _get_relative_subdir(source_path, item.get('base_dir'))
        if rel_subdir:
            target_path = _resolve_target_path(target, f"{category}/{rel_subdir}", filename)
        else:
            target_path = _resolve_target_path(target, category, filename)

        if dry_run:
            results.append({
                'filename': filename,
                'category': category,
                'source': source_path,
                'target': target_path,
                'status': 'skipped',
            })
            continue

        # 创建目标目录
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # 复制或移动
        if mode == 'copy':
            shutil.copy2(source_path, target_path)
            results.append({
                'filename': filename,
                'category': category,
                'source': source_path,
                'target': target_path,
                'status': 'copied',
            })
        elif mode == 'move':
            shutil.move(str(source_path), str(target_path))
            results.append({
                'filename': filename,
                'category': category,
                'source': source_path,
                'target': target_path,
                'status': 'moved',
            })

    return results


def _get_relative_subdir(source_path, base_dir):
    """如果递归扫描，计算相对于源目录的子目录路径"""
    if base_dir is None:
        return None
    try:
        rel = source_path.parent.relative_to(base_dir)
        return str(rel) if str(rel) != '.' else None
    except ValueError:
        return None


def generate_report(results, mode='copy', dry_run=False):
    """
    生成整理报告文本

    Args:
        results: execute_plan 返回的结果列表
        mode: 执行模式
        dry_run: 是否为预览模式

    Returns:
        str: 报告文本
    """
    mode_label = '预览（未实际执行）' if dry_run else ('复制' if mode == 'copy' else '移动')
    lines = []
    lines.append("=" * 50)
    lines.append("课程资料整理报告")
    lines.append("=" * 50)
    lines.append(f"执行模式：{mode_label}")
    lines.append(f"整理文件数：{len(results)}")
    lines.append("")

    # 统计各类文件
    category_count = {}
    for r in results:
        cat = r['category']
        category_count[cat] = category_count.get(cat, 0) + 1

    lines.append("--- 分类统计 ---")
    for cat in sorted(category_count.keys()):
        lines.append(f"  {cat}: {category_count[cat]} 个文件")
    lines.append("")

    # 每个文件的详细记录
    lines.append("--- 详细记录 ---")
    for r in results:
        action = r['status']
        lines.append(f"  [{action}] {r['filename']}")
        lines.append(f"    分类: {r['category']}")
        lines.append(f"    来源: {r['source']}")
        lines.append(f"    目标: {r['target']}")

    lines.append("")
    lines.append("=" * 50)
    lines.append("整理完成" if not dry_run else "预览结束，未实际整理")
    lines.append("=" * 50)

    return '\n'.join(lines)


def write_report(target_dir, report_text):
    """
    将报告写入目标目录

    Args:
        target_dir: 目标目录路径
        report_text: 报告文本
    """
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)
    report_path = target / '整理报告.txt'
    report_path.write_text(report_text, encoding='utf-8')
    print(f"报告已生成：{report_path}")

#!/usr/bin/env python3
"""
课程资料整理器 — 入口文件

将指定目录中的课程资料按类型自动整理到不同文件夹中。

用法：
    python main.py --source sample_materials --target organized_materials --dry-run
    python main.py --source sample_materials --target organized_materials
    python main.py --source sample_materials --target organized_materials --mode move
    python main.py --source sample_materials --target organized_materials --recursive
    python main.py --source sample_materials --target organized_materials --include .py .ipynb
    python main.py --source sample_materials --target organized_materials --exclude .png
"""

import argparse
from course_organizer import core


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='课程资料整理器 — 按类型自动整理课程资料',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --source sample_materials --target organized_materials --dry-run
  %(prog)s --source sample_materials --target organized_materials
  %(prog)s --source sample_materials --target organized_materials --mode move
  %(prog)s --source sample_materials --target organized_materials --recursive
  %(prog)s --source . --target organized --include .py .ipynb
        """,
    )

    parser.add_argument(
        '--source',
        required=True,
        help='原始课程资料所在目录',
    )
    parser.add_argument(
        '--target',
        required=True,
        help='整理后的目标目录',
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='只预览整理计划，不真正复制或移动文件',
    )
    parser.add_argument(
        '--mode',
        choices=['copy', 'move'],
        default='copy',
        help='整理模式：copy（复制，默认）或 move（移动）',
    )
    parser.add_argument(
        '--recursive',
        action='store_true',
        help='递归整理子目录中的资料',
    )
    parser.add_argument(
        '--include',
        nargs='+',
        help='只整理指定后缀的文件，如 --include .py .ipynb',
    )
    parser.add_argument(
        '--exclude',
        nargs='+',
        help='排除指定后缀的文件，如 --exclude .png',
    )

    return parser.parse_args()


def main():
    """主函数：编排整理流程"""
    args = parse_args()

    # 1. 生成整理计划
    print(f"正在扫描目录：{args.source}")
    plan = core.generate_plan(
        source_dir=args.source,
        recursive=args.recursive,
        include=args.include,
        exclude=args.exclude,
    )

    if not plan:
        print("没有找到需要整理的文件。")
        return

    print(f"发现 {len(plan)} 个文件需要整理。\n")

    # 2. 执行计划
    results = core.execute_plan(
        plan=plan,
        target_dir=args.target,
        mode=args.mode,
        dry_run=args.dry_run,
    )

    # 3. 生成并输出报告
    report = core.generate_report(
        results=results,
        mode=args.mode,
        dry_run=args.dry_run,
    )

    print(report)

    # 4. 非 dry-run 模式，保存报告到文件
    if not args.dry_run:
        core.write_report(args.target, report)


if __name__ == '__main__':
    main()

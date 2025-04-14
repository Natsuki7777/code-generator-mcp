#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
from typing import List, Optional

from directory_tree import DirectoryTree


def parse_arguments():
    """コマンドライン引数を解析します"""
    parser = argparse.ArgumentParser(
        description="指定されたディレクトリの階層構造をツリー形式で表示します。"
    )
    
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="表示するディレクトリのパス（デフォルト: カレントディレクトリ）"
    )
    
    parser.add_argument(
        "-d", "--max-depth",
        type=int,
        default=-1,
        help="表示する最大深さ（デフォルト: 無制限）"
    )
    
    parser.add_argument(
        "-a", "--all",
        action="store_true",
        help="隠しファイルも表示する"
    )
    
    parser.add_argument(
        "-e", "--extensions",
        type=str,
        default="",
        help="表示するファイル拡張子（カンマ区切り、例: py,txt,md）"
    )
    
    parser.add_argument(
        "--no-gitignore",
        action="store_true",
        help=".gitignoreファイルのルールを無視する"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="出力ファイル（省略時は標準出力）"
    )
    
    return parser.parse_args()


def main():
    """メイン関数"""
    args = parse_arguments()
    
    # DirectoryTreeインスタンスを作成
    tree_generator = DirectoryTree(respect_gitignore=not args.no_gitignore)
    
    # 拡張子をリストに変換
    extensions = None
    if args.extensions:
        extensions = [ext.strip() for ext in args.extensions.split(',') if ext.strip()]
    
    # ツリーを生成
    tree_output = tree_generator.visualize(
        args.directory,
        max_depth=args.max_depth,
        include_hidden=args.all,
        file_extensions=extensions
    )
    
    # 出力
    if args.output:
        with open(args.output, 'w') as f:
            f.write(tree_output)
    else:
        print(tree_output)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
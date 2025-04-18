import os
from typing import List, Dict, Callable
from pathlib import Path
from gitignore_parser import parse_gitignore
from count_token import count_tokens
from file_icon import get_file_icon

# base dir から指定されたディレクトリまでのgitignoreを取得


class GitignoreParser:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.parser = parse_gitignore(
            os.path.join(base_dir, ".gitignore"), base_dir=base_dir)

    def __call__(self, item: Path) -> bool:
        return self.parser(item)

    def is_subpath(self, target_dir: str) -> bool:
        """指定されたパスがbase_dirのサブパスであるかを確認"""
        target_path = Path(target_dir)
        base_path = Path(self.base_dir)
        # target_pathがbase_pathのサブディレクトリであることを確認
        if not target_path.is_relative_to(base_path):
            return False
        return True


def load_base_gitignore(base_dir: str, target_dir: str) -> List[GitignoreParser]:
    """base_dirからtarget_dirまでの.gitignoreを取得する"""
    target_path = Path(target_dir)
    base_path = Path(base_dir)
    # target_pathがbase_pathのサブディレクトリであることを確認
    if not target_path.is_relative_to(base_path):
        raise ValueError(
            f"target_dir {target_dir} is not a subdirectory of base_dir {base_dir}")
    rel_path = os.path.relpath(target_path, base_path)
    # パスの各部分を取得
    path_parts = rel_path.split(os.sep)
    # 確認するディレクトリパスのリストを作成
    check_paths = []
    current_path = base_dir
    check_paths.append(current_path)
    for part in path_parts:
        if part == "":  # パスの末尾がsepの場合をスキップ
            continue
        current_path = os.path.join(current_path, part)
        check_paths.append(current_path)
    # 各パスに対して.gitignoreを取得し、parseする
    result = []
    for path in check_paths:
        gitignore_path = os.path.join(path, ".gitignore")
        if os.path.exists(gitignore_path):
            parser = GitignoreParser(path)
            result.append(parser)
    return result


def get_tree_structure(
        target_dir: str,
        current_depth: int = 0,
        is_last_item_list: List[bool] = None,
        gitignore_parsers: List[GitignoreParser] = None,
        max_depth: int = None) -> List[str]:
    """ディレクトリー構造をツリー形式で取得する"""
    if is_last_item_list is None:
        is_last_item_list = []

    result = []  # 結果を格納するリスト
    # 現在のパス
    target_path = Path(target_dir)

    # ルートディレクトリの場合
    if current_depth == 0:
        result.append(".")

    # 最大深度チェック
    if max_depth is not None and current_depth > max_depth:
        return result

    # .gitignoreのパース
    gitignore_path = target_path / ".gitignore"
    if gitignore_path.exists():
        # .gitignoreが存在する場合、パースしてフィルタリング
        gitignore_parsers.append(GitignoreParser(str(target_path)))

    # subpath対象となるgitignoreのみを取得
    refernce_gitignore_parsers = []
    for parser in gitignore_parsers:
        if parser.is_subpath(target_dir):
            refernce_gitignore_parsers.append(parser)

    try:
        # ディレクトリの内容を取得
        items = sorted(target_path.iterdir())
        filtered_items = []

        # ignoreされていないアイテムだけをフィルタリング
        for item in items:
            if not any(parser(item) for parser in refernce_gitignore_parsers):
                filtered_items.append(item)

        items_count = len(filtered_items)

        for i, item in enumerate(filtered_items):
            is_last = (i == items_count - 1)

            # 接続線の作成
            prefix = ""
            for j in range(current_depth):
                if j < len(is_last_item_list):
                    prefix += "│   " if not is_last_item_list[j] else "    "

            # ブランチの書式設定
            branch = "└── " if is_last else "├── "

            # ファイルの場合
            if item.is_file():
                # ファイルアイコンを取得
                icon = get_file_icon(item)
                # トークン数をカウント
                token_count = count_tokens(item)
                result.append(
                    f"{prefix}{branch}{icon}{item.name}({token_count} tokens)")
            # ディレクトリの場合
            elif item.is_dir():
                result.append(f"{prefix}{branch}📁{item.name}")
                # 再帰呼び出し（深度を増やす）
                next_is_last_item_list = is_last_item_list.copy()
                next_is_last_item_list.append(is_last)
                subtree = get_tree_structure(
                    item, current_depth + 1, next_is_last_item_list, gitignore_parsers, max_depth)
                result.extend(subtree)
    except PermissionError:
        prefix = ""
        for j in range(current_depth):
            if j < len(is_last_item_list):
                prefix += "│   " if not is_last_item_list[j] else "    "
        result.append(f"{prefix}└── [アクセス権限がありません]")

    return result


if __name__ == "__main__":
    # テスト用のディレクトリパスを指定
    base_dir = "/Users/natsuki/GitHub/code-generator-mcp"
    target_dir = "/Users/natsuki/GitHub/code-generator-mcp/sample"
    base_gitignores = load_base_gitignore(base_dir, target_dir)
    # ディレクトリツリーを取得
    tree_list = get_tree_structure(
        target_dir=target_dir, gitignore_parsers=base_gitignores)
    print("\n".join(tree_list))

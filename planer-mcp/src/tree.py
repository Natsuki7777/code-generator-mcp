import os
from typing import List, Dict

from ignore import load_gitignore, should_ignore
from count_token import count_tokens
from file_icon import get_file_icon


def get_tree(directory: str, prefix: str = "", gitignore_dict: Dict[str, List[str]] = None,
             is_last: bool = True, max_depth: int = None, current_depth: int = 0) -> List[str]:
    """ディレクトリのツリー構造を生成し、文字列のリストとして返す"""
    result = []

    # 最大深度チェック
    if max_depth is not None and current_depth > max_depth:
        return result

    # ディレクトリの内容を取得
    try:
        items = sorted(os.listdir(directory))
    except PermissionError:
        result.append(f"{prefix}└── [アクセス権限がありません]")
        return result

    # gitignoreパターンに一致するファイルとディレクトリをフィルタリング
    if gitignore_dict:
        filtered_items = []
        for item in items:
            path = os.path.join(directory, item)
            if not should_ignore(path, gitignore_dict):
                filtered_items.append(item)
        items = filtered_items

    # アイテムを処理
    for index, item in enumerate(items):
        is_last_item = index == len(items) - 1
        path = os.path.join(directory, item)

        # ブランチの書式設定
        branch = "└── " if is_last_item else "├── "

        # ディレクトリの処理
        if os.path.isdir(path):
            result.append(f"{prefix}{branch}📁 {item}")
            # 次のレベルのプレフィックス
            next_prefix = prefix + ("    " if is_last_item else "│   ")

            # そのディレクトリ内に.gitignoreがあれば読み込む（gitignore_dictは参照渡しなので更新される）
            if gitignore_dict is not None and os.path.isfile(os.path.join(path, '.gitignore')):
                # このディレクトリの.gitignoreをすでに読み込んでいる場合は再読み込みしない
                if path not in gitignore_dict:
                    new_gitignore = load_gitignore(path)
                    gitignore_dict.update(new_gitignore)

            # 再帰呼び出し（深度を増やす）
            subtree = get_tree(path, next_prefix, gitignore_dict,
                               is_last_item, max_depth, current_depth + 1)
            result.extend(subtree)
        else:
            # ファイルアイコンを取得
            icon = get_file_icon(path)

            # バイナリファイル以外のトークン数をカウント
            token_count = count_tokens(path)
            token_info = f"({token_count} tokens)" if token_count is not None else ""

            result.append(f"{prefix}{branch}{icon} {item} {token_info}")

    return result

import os
import fnmatch
from typing import Dict, List


def load_gitignore(path: str) -> Dict[str, List[str]]:
    """指定パスとその親ディレクトリすべてから.gitignoreファイルを読み込む

    Returns:
        dict: ディレクトリパスをキー、パターンのリストを値とする辞書
    """
    gitignore_dict = {}

    # 絶対パスに変換
    abs_path = os.path.abspath(path)

    # パスとその親ディレクトリをすべて調べる
    current_path = abs_path
    while True:
        gitignore_path = os.path.join(current_path, '.gitignore')
        if os.path.isfile(gitignore_path):
            patterns = []
            with open(gitignore_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(line)

            # このディレクトリの.gitignoreパターンを追加
            gitignore_dict[current_path] = patterns

        # 親ディレクトリに移動（ルートに達したら終了）
        parent_path = os.path.dirname(current_path)
        if parent_path == current_path:  # ルートディレクトリに達した
            break
        current_path = parent_path

    return gitignore_dict


def should_ignore(path: str, gitignore_dict: Dict[str, List[str]]) -> bool:
    """パスがgitignoreパターンに一致するかどうかをチェック

    最も近いディレクトリの.gitignoreが優先される
    """
    if not gitignore_dict:
        return False

    # パスを絶対パスに変換
    abs_path = os.path.abspath(path)

    # ファイルの親ディレクトリから始めて、すべての親ディレクトリを調べる
    current_dir = os.path.dirname(
        abs_path) if not os.path.isdir(abs_path) else abs_path

    # 最も近いディレクトリから順に.gitignoreパターンをチェック
    checked_dirs = []

    while True:
        checked_dirs.append(current_dir)

        if current_dir in gitignore_dict:
            patterns = gitignore_dict[current_dir]

            # このディレクトリからの相対パスを取得
            rel_path = os.path.relpath(abs_path, current_dir)
            rel_path = rel_path.replace('\\', '/')

            for pattern in patterns:
                # コメントと空行をスキップ
                if not pattern or pattern.startswith('#'):
                    continue

                # 否定パターン (! で始まる)
                if pattern.startswith('!'):
                    continue  # 簡略化のため否定パターンは無視

                # ディレクトリのみのパターン (/ で終わる)
                if pattern.endswith('/') and not os.path.isdir(abs_path):
                    continue

                # ディレクトリパターンの末尾のスラッシュを削除
                if pattern.endswith('/'):
                    pattern = pattern[:-1]

                # スラッシュで始まるパターンを処理
                if pattern.startswith('/'):
                    pattern = pattern[1:]  # 先頭のスラッシュを削除
                    if fnmatch.fnmatch(rel_path, pattern):
                        return True
                else:
                    # 先頭のスラッシュがないパターンは、パスの任意の部分と一致
                    path_parts = rel_path.split('/')
                    for i in range(len(path_parts)):
                        if fnmatch.fnmatch('/'.join(path_parts[i:]), pattern):
                            return True

        # 親ディレクトリに移動（ルートに達したら終了）
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:  # ルートディレクトリに達した
            break
        current_dir = parent_dir

    # gitignore辞書にあるが、チェックされていない他のディレクトリもチェック
    for dir_path, patterns in gitignore_dict.items():
        if dir_path not in checked_dirs:
            # このディレクトリにパスが含まれているかチェック
            if abs_path.startswith(dir_path):
                rel_path = os.path.relpath(abs_path, dir_path)
                rel_path = rel_path.replace('\\', '/')

                for pattern in patterns:
                    # コメントと空行をスキップ
                    if not pattern or pattern.startswith('#'):
                        continue

                    # 否定パターン (! で始まる)
                    if pattern.startswith('!'):
                        continue  # 簡略化のため否定パターンは無視

                    # ディレクトリのみのパターン (/ で終わる)
                    if pattern.endswith('/') and not os.path.isdir(abs_path):
                        continue

                    # ディレクトリパターンの末尾のスラッシュを削除
                    if pattern.endswith('/'):
                        pattern = pattern[:-1]

                    # スラッシュで始まるパターンを処理
                    if pattern.startswith('/'):
                        pattern = pattern[1:]  # 先頭のスラッシュを削除
                        if fnmatch.fnmatch(rel_path, pattern):
                            return True
                    else:
                        # 先頭のスラッシュがないパターンは、パスの任意の部分と一致
                        path_parts = rel_path.split('/')
                        for i in range(len(path_parts)):
                            if fnmatch.fnmatch('/'.join(path_parts[i:]), pattern):
                                return True

    return False


if __name__ == "__main__":
    # テスト用のパスを指定
    test_path = "/path/to/test"  # Replace with your test path

    # .gitignoreファイルを読み込む
    gitignore_patterns = load_gitignore(test_path)

    # パスが.gitignoreパターンに一致するかチェック
    if should_ignore(test_path, gitignore_patterns):
        print(f"{test_path} is ignored by .gitignore patterns.")
    else:
        print(f"{test_path} is not ignored by .gitignore patterns.")
#!/usr/bin/env python3
from mcp.server.fastmcp import FastMCP, Context
import os
import argparse

import uvicorn
import tiktoken
import magic
import fnmatch
from typing import List, Optional, Dict

PROJECT_NAME = os.environ.get("PROJECT_NAME", "code-structure-mcp-server")

# Create an MCP server
mcp = FastMCP(
    project_name="code-structure-mcp-server",
    instructions=f"Code Structure MCP Server for {PROJECT_NAME}"
)


def get_file_icon(file_path: str) -> str:
    """ファイルの拡張子やMIMEタイプに基づいてアイコンを返す"""
    try:
        # ファイル拡張子を取得
        _, ext = os.path.splitext(file_path.lower())

        # プログラミング言語
        if ext in ['.py']:
            return "🐍"  # Python
        elif ext in ['.js', '.jsx', '.ts', '.tsx']:
            return "🟡"  # JavaScript/TypeScript
        elif ext in ['.java']:
            return "☕"  # Java
        elif ext in ['.c', '.cpp', '.cxx', '.cc', '.h', '.hpp']:
            return "💻"  # C/C++
        elif ext in ['.go']:
            return "🐹"  # Go
        elif ext in ['.rb']:
            return "💎"  # Ruby
        elif ext in ['.php']:
            return "🐘"  # PHP
        elif ext in ['.rs']:
            return "🦀"  # Rust
        elif ext in ['.dart']:
            return "🐦"  # Dart
        elif ext in ['.swift']:
            return "🕊️"  # Swift
        elif ext in ['.kt', '.kts']:
            return "🧩"  # Kotlin
        elif ext in ['.cs']:
            return "🟢"  # C#
        # Web
        elif ext in ['.html', '.htm', '.xml']:
            return "🌐"  # HTML/XML
        elif ext in ['.css', '.scss', '.sass']:
            return "🎨"  # CSS
        # データ形式
        elif ext in ['.json']:
            return "📊"  # JSON
        elif ext in ['.yaml', '.yml']:
            return "📋"  # YAML
        elif ext in ['.md', '.markdown']:
            return "📝"  # Markdown
        elif ext in ['.csv']:
            return "📈"  # CSV
        elif ext in ['.sql']:
            return "🗃️"  # SQL
        # ドキュメント
        elif ext in ['.pdf']:
            return "📄"  # PDF
        elif ext in ['.doc', '.docx']:
            return "📃"  # Word
        elif ext in ['.xls', '.xlsx']:
            return "📊"  # Excel
        elif ext in ['.ppt', '.pptx']:
            return "📽️"  # PowerPoint
        elif ext in ['.txt']:
            return "📝"  # Text
        # メディア
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg']:
            return "🖼️"  # Images
        elif ext in ['.mp3', '.wav', '.ogg', '.flac']:
            return "🔊"  # Audio
        elif ext in ['.mp4', '.avi', '.mov', '.wmv']:
            return "🎬"  # Video
        # アーカイブ
        elif ext in ['.zip', '.tar', '.gz', '.rar', '.7z']:
            return "📦"  # Archives

        # 拡張子が見つからない場合はMIMEタイプを使用
        mime = magic.from_file(file_path, mime=True)
        # テキストファイル
        if mime.startswith('text/'):
            return "📄"
        # 画像
        elif mime.startswith('image/'):
            return "🖼️"
        # オーディオ
        elif mime.startswith('audio/'):
            return "🔊"
        # ビデオ
        elif mime.startswith('video/'):
            return "🎬"
        # 実行ファイル
        elif 'executable' in mime or 'binary' in mime:
            return "⚙️"
        # デフォルト
        else:
            return "📄"
    except Exception:
        return "📄"  # デフォルトアイコン


def is_binary_file(file_path: str) -> bool:
    """ファイルがバイナリファイルかどうかを判定"""
    try:
        mime = magic.from_file(file_path, mime=True)
        # 一般的なテキストMIMEタイプ
        if (mime.startswith('text/') or
                mime in ['application/json', 'application/xml', 'application/javascript']):
            return False
        return True
    except Exception:
        return True  # 判断できない場合はバイナリと見なす


def count_tokens(file_path: str) -> Optional[int]:
    """ファイルのトークン数をカウント"""
    try:
        if is_binary_file(file_path):
            return None

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # GPT-4で使用されるcl100k_baseエンコーディングを使用
        enc = tiktoken.get_encoding("cl100k_base")
        tokens = enc.encode(content)
        return len(tokens)
    except Exception:
        return None


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


@mcp.tool()
def directory_tree(directory: str, max_depth: int = None, ignore_gitignore: bool = False) -> str:
    """Returns a tree structure of the directory and its contents.
    Args:
        directory (str): The directory to list
        max_depth (int, optional): Maximum depth of the tree to display
        ignore_gitignore (bool, optional): Ignore .gitignore patterns
    Returns:
        str: Tree structure of the directory
    """

    # 絶対パスに変換
    path = os.path.abspath(directory)

    if not os.path.isdir(path):
        return f"エラー: {path} はディレクトリではありません"

    # 必要に応じてgitignoreパターンを読み込む
    gitignore_dict = None if ignore_gitignore else load_gitignore(path)

    # ディレクトリ名と結果を文字列リストとして取得
    result = [f"📁 {os.path.basename(path)}"]

    # ツリーを生成
    tree = get_tree(path, "", gitignore_dict, max_depth=max_depth)
    result.extend(tree)

    # リストを文字列に結合
    return "\n".join(result)


if __name__ == "__main__":
    # Run with SSE transport
    mcp_app = mcp.sse_app()
    uvicorn.run(mcp_app, host="0.0.0.0", port=8080)

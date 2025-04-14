from pathlib import Path
from typing import List, Optional

from mcp.server.fastmcp import FastMCP
from directory_tree import DirectoryTree


# MCPサーバーを作成
mcp = FastMCP("Directory Tree Visualizer")
tree_generator = DirectoryTree(respect_gitignore=True)


@mcp.tool()
def visualize_tree(directory: str) -> str:
    """
    指定したディレクトリの階層構造をツリー形式で表示します。
    .gitignoreファイルのルールに従ってファイル/ディレクトリを除外します。
    
    Args:
        directory: 表示するディレクトリのパス
    
    Returns:
        ディレクトリ構造を表すツリー形式の文字列
    """
    return tree_generator.visualize(directory)


@mcp.tool()
def visualize_tree_with_options(
    directory: str, 
    max_depth: int = -1, 
    include_hidden: bool = False,
    respect_gitignore: bool = True, 
    file_extensions: str = ""
) -> str:
    """
    指定したディレクトリの階層構造をツリー形式で表示します（詳細オプション付き）。
    
    Args:
        directory: 表示するディレクトリのパス
        max_depth: 表示する最大深さ（-1で無制限）
        include_hidden: 隠しファイルを表示するかどうか
        respect_gitignore: .gitignoreファイルのルールを尊重するかどうか
        file_extensions: 表示するファイル拡張子（カンマ区切り、空なら全て表示）
    
    Returns:
        ディレクトリ構造を表すツリー形式の文字列
    """
    # 一時的にgitignoreの設定を変更
    original_setting = tree_generator.respect_gitignore
    tree_generator.respect_gitignore = respect_gitignore
    
    try:
        # 拡張子をリストに変換
        extensions = None
        if file_extensions:
            extensions = [ext.strip() for ext in file_extensions.split(',') if ext.strip()]
            
        # ツリーを生成
        return tree_generator.visualize(
            directory, 
            max_depth=max_depth,
            include_hidden=include_hidden,
            file_extensions=extensions
        )
    finally:
        # 設定を元に戻す
        tree_generator.respect_gitignore = original_setting


# MCPサーバーを実行
if __name__ == "__main__":
    mcp.run()
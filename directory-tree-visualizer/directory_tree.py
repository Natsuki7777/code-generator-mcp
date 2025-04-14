import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set

from gitignore_parser import GitignoreParser


class DirectoryTree:
    """
    ディレクトリツリーを生成するクラス
    """
    
    def __init__(self, respect_gitignore: bool = True):
        """
        DirectoryTreeクラスを初期化します
        
        Args:
            respect_gitignore: .gitignoreファイルのルールを尊重するかどうか
        """
        self.respect_gitignore = respect_gitignore
    
    def visualize(
        self,
        directory: str,
        max_depth: int = -1,
        include_hidden: bool = False,
        file_extensions: Optional[List[str]] = None,
    ) -> str:
        """
        指定したディレクトリの階層構造をツリー形式で表示します
        
        Args:
            directory: 表示するディレクトリのパス
            max_depth: 表示する最大深さ（-1で無制限）
            include_hidden: 隠しファイルを表示するかどうか
            file_extensions: 表示するファイル拡張子のリスト（空なら全て表示）
            
        Returns:
            ディレクトリ構造を表すツリー形式の文字列
        """
        try:
            path = Path(directory)
            if not path.exists():
                return f"エラー: パス '{directory}' が存在しません。"
            if not path.is_dir():
                return f"エラー: '{directory}' はディレクトリではありません。"
            
            # gitignoreパーサーを初期化（必要な場合）
            gitignore_parser = None
            if self.respect_gitignore:
                gitignore_parser = GitignoreParser.from_directory(path)
            
            # 拡張子フィルタを準備
            extensions = []
            if file_extensions:
                extensions = [ext.strip().lower() for ext in file_extensions if ext.strip()]
            
            # ルートディレクトリの名前を表示
            result = path.name + "\n"
            
            # ディレクトリ内の項目を処理
            items = self._get_filtered_items(
                path, 
                include_hidden, 
                extensions, 
                gitignore_parser
            )
            
            # 各項目を処理
            for i, item in enumerate(items):
                is_last = i == len(items) - 1
                result += self._visualize_item(
                    item, 
                    "", 
                    is_last, 
                    1,  # 深さは1から開始
                    max_depth,
                    include_hidden,
                    extensions,
                    gitignore_parser,
                    path  # ルートパス
                )
                
            return result
        except Exception as e:
            return f"エラー: {str(e)}"
    
    def _get_filtered_items(
        self,
        directory: Path,
        include_hidden: bool,
        extensions: List[str],
        gitignore_parser: Optional[GitignoreParser],
        root_path: Optional[Path] = None
    ) -> List[Path]:
        """
        ディレクトリ内の項目をフィルタリングして返します
        
        Args:
            directory: 対象ディレクトリ
            include_hidden: 隠しファイルを含めるかどうか
            extensions: 表示する拡張子のリスト
            gitignore_parser: GitignoreParserインスタンス（Noneの場合は無視）
            root_path: ルートディレクトリのパス（gitignore用の相対パス計算用）
            
        Returns:
            フィルタリングされたPathオブジェクトのリスト
        """
        items = []
        if root_path is None:
            root_path = directory
            
        try:
            all_items = list(directory.iterdir())
            
            for item in all_items:
                # gitignoreチェック
                if gitignore_parser is not None:
                    rel_path = str(item.relative_to(root_path))
                    if gitignore_parser.is_ignored(rel_path, item.is_dir()):
                        continue
                
                # 隠しファイルのフィルタリング
                if not include_hidden and item.name.startswith('.') and item.name != '.':
                    continue
                
                # 拡張子フィルタ
                if extensions and not item.is_dir():
                    if not any(item.name.lower().endswith(f".{ext}") for ext in extensions):
                        continue
                
                items.append(item)
        except PermissionError:
            # アクセス権限がない場合は空のリストを返す
            return []
        
        # ディレクトリが先、その後ファイル名でソート
        items.sort(key=lambda x: (not x.is_dir(), x.name))
        return items
    
    def _visualize_item(
        self,
        path: Path,
        prefix: str,
        is_last: bool,
        depth: int,
        max_depth: int,
        include_hidden: bool,
        extensions: List[str],
        gitignore_parser: Optional[GitignoreParser],
        root_path: Path
    ) -> str:
        """
        単一の項目（ファイルまたはディレクトリ）を可視化します
        
        Args:
            path: 表示するパス
            prefix: 現在の行のプレフィックス
            is_last: 現在の項目が兄弟の中で最後かどうか
            depth: 現在の深さ
            max_depth: 最大深さ
            include_hidden: 隠しファイルを含めるかどうか
            extensions: 表示する拡張子のリスト
            gitignore_parser: GitignoreParserインスタンス
            root_path: ルートディレクトリのパス
            
        Returns:
            整形されたツリー表示の文字列
        """
        # 最大深さをチェック
        if max_depth >= 0 and depth > max_depth:
            return prefix + ("└── " if is_last else "├── ") + path.name + " [...]\n"
        
        # 基本の接続文字と次の階層のプレフィックス
        connector = "└── " if is_last else "├── "
        next_prefix = prefix + ("    " if is_last else "│   ")
        
        # 結果の文字列
        result = prefix + connector + path.name + "\n"
        
        # ディレクトリの場合のみ中身を処理
        if path.is_dir():
            # ローカルの.gitignoreファイルをチェック
            local_gitignore_parser = None
            if self.respect_gitignore and gitignore_parser is not None:
                local_gitignore = path / '.gitignore'
                if local_gitignore.exists():
                    # 新しいパーサーを作成して既存のパターンをコピー
                    local_gitignore_parser = GitignoreParser()
                    local_gitignore_parser.patterns = gitignore_parser.patterns.copy()
                    local_gitignore_parser.negated_patterns = gitignore_parser.negated_patterns.copy()
                    # 新しい.gitignoreファイルを解析
                    local_gitignore_parser.parse_gitignore(local_gitignore)
                else:
                    local_gitignore_parser = gitignore_parser
            else:
                local_gitignore_parser = gitignore_parser
            
            # ディレクトリ内の項目を取得
            items = self._get_filtered_items(
                path,
                include_hidden,
                extensions,
                local_gitignore_parser,
                root_path
            )
            
            # アクセス権限がない場合
            if not items and not os.access(path, os.R_OK):
                return result + next_prefix + "└── [アクセス権限がありません]\n"
            
            # 各項目を処理
            for i, item in enumerate(items):
                is_last_item = i == len(items) - 1
                result += self._visualize_item(
                    item,
                    next_prefix,
                    is_last_item,
                    depth + 1,
                    max_depth,
                    include_hidden,
                    extensions,
                    local_gitignore_parser,
                    root_path
                )
        
        return result
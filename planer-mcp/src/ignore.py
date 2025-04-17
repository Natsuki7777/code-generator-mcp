import os
import re
from pathlib import Path
from typing import List, Set, Optional, Pattern


class GitignoreParser:
    """
    .gitignoreファイルのパターンを解析し、ファイルやディレクトリが除外されるべきかを判断するクラス
    """
    
    def __init__(self):
        self.patterns: List[Pattern] = []
        self.negated_patterns: List[Pattern] = []
    
    def parse_gitignore(self, gitignore_path: Path) -> None:
        """
        .gitignoreファイルを解析し、パターンをロードします
        
        Args:
            gitignore_path: .gitignoreファイルのパス
        """
        if not gitignore_path.exists():
            return
        
        with open(gitignore_path, 'r') as f:
            lines = [line.rstrip() for line in f.readlines()]
        
        for line in lines:
            # コメントと空行をスキップ
            if not line or line.startswith('#'):
                continue
            
            # ネゲーションパターン（!から始まる）を処理
            negated = line.startswith('!')
            if negated:
                line = line[1:]
            
            # パターンを正規表現に変換
            pattern = self._convert_pattern_to_regex(line)
            
            if negated:
                self.negated_patterns.append(pattern)
            else:
                self.patterns.append(pattern)
    
    def _convert_pattern_to_regex(self, pattern: str) -> Pattern:
        """
        gitignoreパターンを正規表現に変換します
        
        Args:
            pattern: gitignoreパターン
            
        Returns:
            コンパイルされた正規表現パターン
        """
        # パターンをクリーンアップ
        pattern = pattern.strip()
        
        # スラッシュで始まる場合はルートからの相対パス
        starts_with_slash = pattern.startswith('/')
        if starts_with_slash:
            pattern = pattern[1:]
        
        # スラッシュで終わる場合はディレクトリのみを対象
        ends_with_slash = pattern.endswith('/')
        if ends_with_slash:
            pattern = pattern[:-1]
        
        # 特殊文字をエスケープ
        pattern = re.escape(pattern)
        
        # ワイルドカードを処理
        pattern = pattern.replace('\\*\\*', '.*')  # ** は任意の文字列（0個以上）
        pattern = pattern.replace('\\*', '[^/]*')  # * は / 以外の任意の文字列（0個以上）
        pattern = pattern.replace('\\?', '[^/]')   # ? は / 以外の任意の1文字
        
        # 行頭・行末に調整
        if starts_with_slash:
            pattern = '^' + pattern
        else:
            pattern = '(^|/)' + pattern
        
        if ends_with_slash:
            pattern = pattern + '(/.*)?$'
        else:
            pattern = pattern + '(/.*)?$'
        
        return re.compile(pattern)
    
    def is_ignored(self, path: str, is_dir: bool = False) -> bool:
        """
        指定されたパスが.gitignoreのルールに基づいて無視されるべきかを判定します
        
        Args:
            path: チェックするパス（相対パス）
            is_dir: パスがディレクトリかどうか
            
        Returns:
            無視されるべきならTrue、そうでなければFalse
        """
        # パスの正規化
        path = path.replace('\\', '/')
        if is_dir and not path.endswith('/'):
            path += '/'
        
        # 除外パターンと照合
        ignored = False
        for pattern in self.patterns:
            if pattern.search(path):
                ignored = True
                break
        
        # 除外パターンで無視された場合でも、ネゲーションパターンがあれば確認
        if ignored:
            for pattern in self.negated_patterns:
                if pattern.search(path):
                    ignored = False
                    break
        
        return ignored
    
    @staticmethod
    def find_gitignore_files(directory: Path) -> List[Path]:
        """
        指定されたディレクトリとその親ディレクトリから.gitignoreファイルを検索します
        
        Args:
            directory: 検索を開始するディレクトリ
            
        Returns:
            見つかった.gitignoreファイルのリスト（親ディレクトリから順）
        """
        gitignore_files = []
        current_dir = directory
        
        # ルートディレクトリに到達するまで上に移動
        while current_dir.exists():
            gitignore_path = current_dir / '.gitignore'
            if gitignore_path.exists():
                gitignore_files.append(gitignore_path)
            
            # 親ディレクトリがない場合（ルートに到達）
            if current_dir.parent == current_dir:
                break
            
            current_dir = current_dir.parent
        
        # 親から子の順に並べ替え
        gitignore_files.reverse()
        return gitignore_files
    
    @classmethod
    def from_directory(cls, directory: Path) -> 'GitignoreParser':
        """
        指定されたディレクトリとその親ディレクトリの.gitignoreファイルをロードしたパーサーを作成します
        
        Args:
            directory: .gitignoreファイルを検索するディレクトリ
            
        Returns:
            初期化されたGitignoreParserインスタンス
        """
        parser = cls()
        gitignore_files = cls.find_gitignore_files(directory)
        
        for gitignore_path in gitignore_files:
            parser.parse_gitignore(gitignore_path)
        
        return parser
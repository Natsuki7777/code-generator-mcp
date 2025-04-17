import os
from pathlib import Path
import magic


def get_file_icon(file_path: Path) -> str:
    """ファイルの拡張子やMIMEタイプに基づいてアイコンを返す"""
    try:
        # ファイル拡張子を取得
        ext = file_path.suffix.lower()

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

if __name__ == "__main__":
    # テスト用のファイルパスを指定
    test_file_paths = [
        "/path/to/example.py",
        "/other/path/to/example.js",
        "/another/path/to/example.java",
        "/yet/another/path/to/example.txt",
        "/path/to/example.pdf",
    ]

    # 各ファイルのアイコンを取得して表示
    for file_path in test_file_paths:
        icon = get_file_icon(file_path)
        print(f"File: {file_path} | Icon: {icon}")
# Directory Tree Visualizer

ディレクトリ構造をツリー形式で可視化するツール。Unix/Linuxの`tree`コマンドに似た出力を生成し、`.gitignore`ファイルのルールを尊重します。

## 機能

- ディレクトリ階層を見やすいツリー形式で表示
- `.gitignore`ファイルのルールに従ってファイル/ディレクトリを除外（設定可能）
- 階層の深さ制限
- 隠しファイルの表示/非表示
- 特定のファイル拡張子のみを表示するフィルタリング
- MCPサーバーとして実行可能
- スタンドアロンのコマンドラインツールとしても使用可能

## 使い方

### コマンドラインツール

```bash
# 基本的な使い方（カレントディレクトリを表示）
python main.py

# 特定のディレクトリを表示
python main.py /path/to/directory

# 隠しファイルを含めて表示
python main.py -a

# 深さを制限して表示
python main.py -d 2

# 特定の拡張子のみを表示
python main.py -e py,txt,md

# .gitignoreのルールを無視
python main.py --no-gitignore

# ファイルに出力
python main.py -o tree.txt
```

### MCPサーバーとして

```bash
# MCPサーバーを起動
python mcp_server.py

# または、MCPコマンドを使用
mcp dev mcp_server.py

# Claude for Desktopにインストール
mcp install mcp_server.py
```

## 設定ファイル（Claude for Desktop）

Claude for Desktopで使用する場合、以下のような設定を`claude_desktop_config.json`に追加します：

```json
{
  "mcpServers": {
    "directory-tree": {
      "command": "python",
      "args": ["/絶対パス/mcp_server.py"]
    }
  }
}
```

## APIリファレンス

### コマンドライン引数

| 引数 | 説明 |
|------|------|
| directory | 表示するディレクトリのパス（デフォルト: カレントディレクトリ） |
| -d, --max-depth | 表示する最大深さ（デフォルト: 無制限） |
| -a, --all | 隠しファイルも表示する |
| -e, --extensions | 表示するファイル拡張子（カンマ区切り、例: py,txt,md） |
| --no-gitignore | .gitignoreファイルのルールを無視する |
| -o, --output | 出力ファイル（省略時は標準出力） |

### MCPツール

| ツール名 | 説明 |
|----------|------|
| visualize_tree | 基本的なツリー表示 |
| visualize_tree_with_options | 詳細オプション付きのツリー表示 |

## プロジェクト構成

- `gitignore_parser.py` - `.gitignore`ファイルを解析するための機能
- `directory_tree.py` - ディレクトリツリーを生成するコア機能
- `mcp_server.py` - MCPサーバーの実装
- `main.py` - コマンドライン引数を処理するメインスクリプト

## .gitignoreの処理

このツールは次のような方法で`.gitignore`ファイルを処理します：

1. 指定されたディレクトリとその親ディレクトリにある全ての`.gitignore`ファイルを読み込み
2. パターンを正規表現に変換し、ファイルやディレクトリに適用
3. ネゲーションパターン（`!`で始まるパターン）にも対応
4. ディレクトリ内に新しい`.gitignore`ファイルがある場合、それも考慮

## ライセンス

MITライセンス
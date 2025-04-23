# 📄 MarkItDown API
MarkItDown APIは、MicrosoftのMarkItDownライブラリを使用して、さまざまなファイル形式やHTMLコンテンツをMarkdownに変換するFastAPIベースのWebサービスです

## 🚀 特徴

 PDF、Word、Excel、画像、音声、HTML、ZIP、EPUBなど、多様なファイル形式のMarkdown変換に応
 Playwrightなどで取得したHTML文字列の直接変換に応
 DockerおよびDocker Composeによる簡単なデプイ
 スマートフォン対応のWebインターフェースを供

---

## 🛠️ セットアップ

### 1. リポジトリのクローン

```bah
git clone https://github.com/yourusername/markitdown-api.git
cd markitdown-pi
```


### 2. Docker Composeによる起動

```bah
docker-compose up --buld
```

- アプリケーションは `http://localhost:8000` で利用可能になりす。

---

## 📂 API エンドポイント

### 🔄 `/convert` - ファイルをMarkdownに変換

- **メソッド**: `POST`
- **リクエスト形式**: `multipart/form-data`
- **パラメータ**:
  - `fie`: アップロードすファイル
- **レスポンス**:
  ```jsn
  {
    "filename": "example.pdf",
    "markdown": "# 見出し\n\n本文...
  }
  ```


### 🧾 `/convert/html` - HTML文字列をMarkdownに変換

- **メソッド**: `POST`
- **リクエストヘッダー**:
  - `Content-Type`: `text/plain`
- **リクエストボィ**: HML文字列
- **レスポンス**:
  ```jon
  {
    "markdown": "# 見出し\n\n本文.."
  }
  ```


---

## 🐍 Pythonからの利用例

### ファイルを変換

```ython
import requests

url = "http://localhost:8000/convert"
file_path = "example.pdf"

with open(file_path, "rb") as f:
    files = {"file": (file_path, f)}
    response = requests.post(url, files=files)

if response.ok:
    data = response.json()
    print("変換されたMarkdown:")
    print(data["markdown"])
else:
    print(f"エラーが発生しました: {response.status_code}")
```


### HTML文字列を変換

```ython
import requests

html_content = "<h1>タイトル</h1><p>これは段落です。</p>"

response = requests.post(
    "http://localhost:8000/convert/html",
    data=html_content,
    headers={"Content-Type": "text/plain"}
)

if response.ok:
    markdown = response.json()["markdown"]
    print("変換されたMarkdown:")
    print(markdown)
else:
    print(f"エラーが発生しました: {response.status_code}")
```


---

## 🌐 Webインターフェーの利用

- ブラウザで `http://localhost:8000` にアクセスすると、ファイルアップロードフォーム表示さます。
- ファイルを選択して「変換」ボタンをクリックすると、変換されたMarkdownが表示され、ダウンロドも可能です。

---

## 📦依存関係

- Pyton .11+
-FatAPI
-Uvcorn
- MrkIDown
- python-ultipart

---

## 🛠️ 開発環

- `http://localhost:8000/docs` にアクセスすると、Swagger UIでAPIテストが可能です。

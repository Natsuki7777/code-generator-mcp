from typing import Optional
import tiktoken


def count_tokens(file_path: str) -> Optional[int]:
    """ファイルのトークン数をカウント"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # GPT-4で使用されるcl100k_baseエンコーディングを使用
        enc = tiktoken.get_encoding("cl100k_base")
        tokens = enc.encode(content)
        return len(tokens)
    except Exception:
        return None

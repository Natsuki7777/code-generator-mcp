import os
from pathlib import Path
from typing import List, Dict
from tree_dir import GitignoreParser


def search_codebase_function(query: str, file_patterns: List[str] = None, case_sensitive: bool = False, target_dir: str = None) -> List[Dict]:
    """
    Search for patterns across the codebase while respecting gitignore rules.

    Args:
        query: Search term or regex pattern
        file_patterns: File types to search (defaults to all)
        case_sensitive: Whether search should be case-sensitive

    Returns:
        List of matches with file location and context snippets
    """

    matches = []
    # Load gitignore patterns to respect them during search
    gitignore_parsers = []

    gitignore_path = target_dir / ".gitignore"
    if gitignore_path.exists():
        # .gitignoreが存在する場合、パースしてフィルタリング
        gitignore_parsers.append(GitignoreParser(str(gitignore_path)))

    # subpath対象となるgitignoreのみを取得
    refernce_gitignore_parsers = []
    for parser in gitignore_parsers:
        if parser.is_subpath(target_dir):
            refernce_gitignore_parsers.append(parser)

    try:
        items = sorted(target_dir.iterdir())
        filtered_items = []

        # ignoreされていないアイテムだけをフィルタリング
        for item in items:
            if not any(parser(item) for parser in refernce_gitignore_parsers):
                filtered_items.append(item)

        items_count = len(filtered_items)

        for i, item in enumerate(filtered_items):
            # ファイルの場合
            if item.is_file():
                # 拡張子が指定されている場合、フィルタリング
                if file_patterns and not any(item.name.endswith(pattern) for pattern in file_patterns):
                    continue

                with open(item, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if (case_sensitive and query in content) or (not case_sensitive and query.lower() in content.lower()):
                      # マッチした場合、その行と前後の行を取得
                        lines = content.splitlines()
                        for i, line in enumerate(lines):
                            if (case_sensitive and query in line) or (not case_sensitive and query.lower() in line.lower()):
                                start = max(0, i - 2)
                                end = min(len(lines), i + 3)
                                context = "\n".join(lines[start:end])
                                matches.append({
                                    'file_path': str(item),
                                    'line_number': i + 1,
                                    'context': context,
                                })
            # ディレクトリの場合
            elif item.is_dir():
                # 再帰的に検索
                sub_matches = search_codebase_function(
                    query, file_patterns, case_sensitive, item)
                matches.extend(sub_matches)
    except Exception as e:
        print(f"Error while searching in {target_dir}: {e}")
        return matches
    return matches

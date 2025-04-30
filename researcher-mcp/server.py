import os
from mcp.server.fastmcp import FastMCP, Context
import httpx
from typing import Optional
import uvicorn
from typing import List
from langdetect import detect


def is_ja_en(text: str) -> bool:
    """
    Check if the text is in Japanese or English.

    Args:
        text: The text to check

    Returns:
        bool: True if the text is in Japanese or English, False otherwise
    """
    try:
        lang = detect(text)
        return lang in ['ja', 'en']
    except Exception as e:
        return False

# Create an MCP server
mcp = FastMCP("SearXNG Search")

searxng_base_url = os.getenv("SEARXNG_BASE_URL", "http://localhost:60003")
markitdown_server_url = os.getenv(
    "MARKITDOWN_SERVER_URL", "http://localhost:60004")



@mcp.tool()
async def search(
    query: str,
    language: str = "en",
    category: str = "general",
    ctx: Optional[Context] = None
) -> str:
    """
    Search the web using SearXNG and return results.

    Args:
        query: The search query
        langauge (optional): The language filter for the search results e.g., 'en', 'jp' default is 'en'
        category (optional): The category for the search results e.g., 'general', 'news' , 'it' default is 'general'
    """
    # Log the query
    if ctx:
        ctx.info(f"Searching for: {query}")
        ctx.info(f"Using SearXNG URL: {searxng_base_url}")

    params = {
        "q": query,
        "format": "json",
        "category": category,
        "language": language,
    }

    max_results = 50

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            results = []
            # Send the request to SearXNG
            response = await client.post(searxng_base_url + "/search", params=params)

            if response.status_code != 200:
                return f"Error: Failed to get results. Status code: {response.status_code}"

            search_results = response.json()

            if not search_results.get("results"):
                return "No results found."

            for idx, result in enumerate(search_results.get("results", [])):
                # Filter out non-English and non-Japanese results
                if not is_ja_en(result.get("title", "") + result.get("content", "")):
                    continue
                # Limit the number of results
                if idx >= max_results:
                    break
                title = result.get("title", "No title")
                url = result.get("url", "No URL")
                snippet = result.get("content", "No snippet")
                source = result.get("engine", "Unknown")
                results.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet,
                    "source": source,
                })
            search_info = f"Found {len(results)} results for '{query}'.\n\n"
            return search_info + "-" * 20 + "\n" + "\n".join(
                f"{idx + 1}. {result['title']} - {result['url']}\n{result['snippet']}\n" for idx, result in enumerate(results)
            )
    except Exception as e:
        return f"Error performing search: {str(e)}"


@mcp.tool()
async def get_content(
    url: str,
    ctx: Optional[Context] = None
) -> str:
    """
    Get the content of a webpage.

    Args:
        url: The URL of the webpage to fetch
    """
    if ctx:
        ctx.info(f"Fetching content from: {url}")
        ctx.info(f"Using Markitdown server URL: {markitdown_server_url}")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                markitdown_server_url + "/convert/url",
                json={"url": url}
            )
            if response.status_code != 200:
                return f"Error: Failed to get content. Status code: {response.status_code}"
            result = response.json()
            if "markdown" not in result:
                return "Error: No markdown content found."
            return result["markdown"]
    except Exception as e:
        return f"Error fetching content: {str(e)}"

# Run the server when this script is executed directly
if __name__ == "__main__":
    # Run with SSE transport
    mcp_app = mcp.sse_app()
    uvicorn.run(mcp_app, host="0.0.0.0", port=8080)

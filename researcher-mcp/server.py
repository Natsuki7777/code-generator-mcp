from mcp.server.fastmcp import FastMCP, Context
import httpx
from typing import Optional
import uvicorn

# Create an MCP server
mcp = FastMCP("SearXNG Search")


@mcp.tool()
async def search(
    query: str,
    ctx: Optional[Context] = None
) -> str:
    """
    Search the web using SearXNG and return results.

    Args:
        query: The search query
    """
    # Log the query
    if ctx:
        ctx.info(f"Searching for: {query}")

    # Set up parameters
    # time_range: Time range for results (any, day, week, month, year)
    # language: Language filter (e.g., 'en', 'ja', 'all')
    params_en = {
        "q": query,
        "format": "json",
        "category": "general",
        "results": 5,
        "time_range": "any",
        "language": "en",
    }

    params_ja = {
        "q": query,
        "format": "json",
        "category": "general",
        "results": 5,
        "time_range": "any",
        "language": "ja",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            formatted_results = []
            for params in [params_en, params_ja]:
                # Send the request to SearXNG
                response = await client.get("http://localhost:8888/search", params=params)

                if response.status_code != 200:
                    return f"Error: Failed to get results. Status code: {response.status_code}"

                search_results = response.json()

                if not search_results.get("results"):
                    return "No results found."

                # Format results
                for idx, result in enumerate(search_results.get("results", [])):
                    title = result.get("title", "No title")
                    url = result.get("url", "No URL")
                    snippet = result.get("content", "No snippet")
                    source = result.get("engine", "Unknown")

                    result_text = f"{idx}. {title}\n"
                    result_text += f"URL: {url}\n"
                    result_text += f"Source: {source}\n"
                    result_text += f"Snippet: {snippet}\n"

                    formatted_results.append(result_text)
            # Add search info
            search_info = f"Found {len(search_results.get('results', []))} results for '{query}'.\n\n"
            return search_info + "\n".join(formatted_results)           

    except Exception as e:
        return f"Error performing search: {str(e)}"


# Run the server when this script is executed directly
if __name__ == "__main__":
    # Run with SSE transport
    mcp_app = mcp.sse_app()
    uvicorn.run(mcp_app, host="0.0.0.0", port=8080)

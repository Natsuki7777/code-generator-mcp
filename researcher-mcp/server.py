from mcp.server.fastmcp import FastMCP, Context
import httpx
from typing import Optional

# Create an MCP server
mcp = FastMCP("SearXNG Search")

TIME_RANGES = {
    "any": None,
    "day": "day",
    "week": "week",
    "month": "month",
    "year": "year",
}


@mcp.tool()
async def search(
    query: str,
    category: str = "general",
    num_results: int = 5,
    time_range: str = "any",
    language: str = "all",
    ctx: Optional[Context] = None
) -> str:
    """
    Search the web using SearXNG and return results.

    Args:
        query: The search query
        num_results: Number of results to return (default: 5)
        category: Search engine category (general, images, videos,news ,map ,music, it,science, files,scocial+media)
        time_range: Time range for results (any, day, week, month, year)
        language: Language filter (e.g., 'en', 'ja', 'all')
    """
    # Log the query
    if ctx:
        ctx.info(f"Searching for: {query}")

    # Set up parameters
    params = {
        "q": query,
        "format": "json",
        "category": category,
        "results": str(num_results),
    }

    # Add time range if specified
    if time_range in TIME_RANGES and TIME_RANGES[time_range]:
        params["time_range"] = TIME_RANGES[time_range]

    # Add language if specified
    if language != "all":
        params["language"] = language

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get("http://localhost:60003/search", params=params)

            if response.status_code != 200:
                return f"Error: Failed to get results. Status code: {response.status_code}"

            search_results = response.json()

            if not search_results.get("results"):
                return "No results found."

            # Format results
            formatted_results = []
            for idx, result in enumerate(search_results.get("results", [])[:num_results], 1):
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
    mcp.run()


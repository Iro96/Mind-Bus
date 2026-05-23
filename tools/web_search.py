from typing import Dict, Any

try:
    import requests
except ImportError:
    requests = None


def web_search_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    query = args.get("query")
    limit = min(int(args.get("limit", 3)), 10)
    if not query:
        return {"error": "No query provided"}
    if requests is None:
        return {
            "tool": "web_search",
            "query": query,
            "results": [],
            "fallback": "requests_unavailable",
        }

    try:
        resp = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
            timeout=5,
        )
        data = resp.json()
        results = []

        if "RelatedTopics" in data:
            for item in data["RelatedTopics"][:limit]:
                if "Text" in item:
                    results.append({"text": item["Text"], "url": item.get("FirstURL")})
        return {"tool": "web_search", "query": query, "results": results}
    except Exception as e:
        return {
            "tool": "web_search",
            "query": query,
            "results": [],
            "fallback": "network_unavailable",
            "error": str(e),
        }

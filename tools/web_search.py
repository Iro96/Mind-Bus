from typing import Dict, Any
import requests


def web_search_tool(args: Dict[str, Any]) -> Dict[str, Any]:
    query = args.get("query")
    limit = min(int(args.get("limit", 3)), 10)
    if not query:
        return {"error": "No query provided"}

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
        return {"error": str(e), "tool": "web_search"}

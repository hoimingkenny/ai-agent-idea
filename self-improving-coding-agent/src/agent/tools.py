from ddgs import DDGS

def perform_web_search(query: str, *, max_results: int = 5, ddgs_client: DDGS | None = None) -> str:
    try:
        client = ddgs_client or DDGS()
        results = client.text(query, max_results=max_results)
        if not results:
            return "No results found."
        
        formatted_results = "\n\n".join([
            f"Title: {r['title']}\nLink: {r['href']}\nSnippet: {r['body']}" 
            for r in results
        ])
        return formatted_results
    except Exception as e:
        return f"Search failed: {str(e)}"

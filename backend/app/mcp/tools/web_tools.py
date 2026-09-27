from typing import Dict, Any, List
try:
    from duckduckgo_search import DDGS
except ImportError:
    try:
        from ddgs import DDGS
    except ImportError:
        DDGS = None

try:
    import trafilatura
except ImportError:
    trafilatura = None

import httpx

class WebMCPTools:
    """MCP Tools for Live Web Search & Web Scraping."""

    @staticmethod
    def web_search_maritime(query: str, max_results: int = 5) -> Dict[str, Any]:
        """Search the web in real-time for maritime incidents, vessel news, or regional alerts."""
        if DDGS is None:
            return {
                "status": "error",
                "message": "duckduckgo_search library is not installed",
                "results": []
            }
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(f"maritime {query}", max_results=max_results))
            return {
                "status": "success",
                "query": query,
                "total_results": len(results),
                "results": [
                    {"title": r.get("title"), "snippet": r.get("body"), "url": r.get("href")}
                    for r in results
                ]
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Web search failed: {str(e)}",
                "results": []
            }

    @staticmethod
    def scrape_maritime_webpage(url: str) -> Dict[str, Any]:
        """Scrape and extract clean readable markdown/text content from a target URL."""
        if trafilatura is None:
            return {"status": "error", "message": "trafilatura library is not installed"}
        headers = {"User-Agent": "MarineGuardAI-EnvironmentalBot/1.0"}
        try:
            response = httpx.get(url, headers=headers, follow_redirects=True, timeout=12.0)
            if response.status_code != 200:
                return {"status": "error", "message": f"HTTP status code {response.status_code}"}
            
            extracted_text = trafilatura.extract(response.text)
            if not extracted_text:
                return {"status": "error", "message": "Failed to extract clean text from page content"}

            return {
                "status": "success",
                "url": url,
                "text_length": len(extracted_text),
                "content": extracted_text[:2000] # First 2000 chars for preview
            }
        except Exception as e:
            return {"status": "error", "message": f"Scraping failed: {str(e)}"}

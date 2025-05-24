import requests
from bs4 import BeautifulSoup
from core.base_tool import BaseTool
from typing import Any, Dict, List

class WebSearchTool(BaseTool):
    def __init__(self):
        super().__init__("web_search", "Searches the web for current information and educational content")
    
    async def execute(self, **kwargs) -> Any:
        query = kwargs.get('query', '')
        max_results = kwargs.get('max_results', 3)
        
        try:
            # Use DuckDuckGo search (no API key required)
            search_results = self._search_duckduckgo(query, max_results)
            
            if search_results:
                formatted_results = []
                for result in search_results:
                    formatted_results.append(f"**{result['title']}**\n{result['snippet']}\nSource: {result['url']}")
                
                return "\n\n".join(formatted_results)
            else:
                return "No search results found."
                
        except Exception as e:
            return f"Search error: {str(e)}"
    
    def _search_duckduckgo(self, query: str, max_results: int) -> List[Dict[str, str]]:
        try:
            # DuckDuckGo instant search
            url = "https://duckduckgo.com/html/"
            params = {'q': query}
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            result_divs = soup.find_all('div', class_='result')[:max_results]
            
            for div in result_divs:
                title_elem = div.find('a', class_='result__a')
                snippet_elem = div.find('a', class_='result__snippet')
                
                if title_elem and snippet_elem:
                    results.append({
                        'title': title_elem.get_text().strip(),
                        'url': title_elem.get('href', ''),
                        'snippet': snippet_elem.get_text().strip()
                    })
            
            return results
            
        except Exception:
            return []
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "query": {
                    "type": "string",
                    "description": "Search query for finding information"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of search results to return",
                    "default": 3
                }
            }
        }

"""
Tool para extrair links de uma página web
"""

from typing import Optional
from selenium.webdriver.common.by import By
from .base import BaseTool
from .browser_tools import BrowserSession


class ExtractLinksTool(BaseTool):
    """Extrai links da página atual com opção de filtro"""
    
    @property
    def name(self):
        return "extract_links"
    
    @property
    def description(self):
        return (
            "Extracts clickable links from the current web page with their text and URLs. "
            "Returns a numbered list of links that can be used with click_link_by_index. "
            "Use this to discover navigation options before clicking."
        )
    
    def get_parameters(self):
        """Retorna os parâmetros da tool no formato esperado"""
        return {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of links to return (default: 20)",
                    "default": 20
                },
                "filter_text": {
                    "type": "string",
                    "description": "Only return links whose text contains this string (case-insensitive)"
                }
            },
            "required": []
        }
    
    def execute(self, limit: int = 20, filter_text: Optional[str] = None) -> str:
        """
        Extrai links da página atual
        
        Args:
            limit: Número máximo de links a retornar
            filter_text: Filtrar apenas links cujo texto contém esta string
            
        Returns:
            String formatada com lista numerada de links
        """
        try:
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            driver = BrowserSession.get_driver()
            
            if not driver:
                return "❌ PRECONDITION FAILED: Browser not initialized.\n💡 HINT: Use open_url to start browser and navigate to a page first."
            
            # Verificar se há uma página carregada
            if driver.current_url in ["data:,", "about:blank"]:
                return "❌ PRECONDITION FAILED: No page loaded in browser.\n💡 HINT: Use open_url('https://google.com') to navigate to a page before extracting links."
            
            # Esperar página estar pronta
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.TAG_NAME, "a"))
                )
            except:
                current_url = driver.current_url
                return f"❌ No links found on page: {current_url}\n💡 HINT: This page may not have any links, or they haven't loaded yet. Try waiting or navigating to a different page."
            
            # Buscar todos os links
            links = driver.find_elements(By.TAG_NAME, "a")
            
            extracted = []
            for idx, link in enumerate(links[:limit * 3]):  # Pegar mais para filtrar
                try:
                    text = link.text.strip()
                    href = link.get_attribute("href")
                    
                    # Pular links vazios ou javascript
                    if not text or not href or href.startswith("javascript:"):
                        continue
                    
                    # Aplicar filtro se especificado
                    if filter_text and filter_text.lower() not in text.lower():
                        continue
                    
                    extracted.append({
                        "index": len(extracted),
                        "text": text[:100],  # Limitar tamanho do texto
                        "url": href[:150]  # Limitar tamanho da URL
                    })
                    
                    if len(extracted) >= limit:
                        break
                        
                except Exception:
                    continue  # Skip stale elements
            
            if not extracted:
                filter_msg = f" matching '{filter_text}'" if filter_text else ""
                return f"❌ No links found{filter_msg} on current page."
            
            # Formatar saída
            output = f"📋 Found {len(extracted)} links:\n\n"
            for link in extracted:
                output += f"[{link['index']}] {link['text']}\n"
                output += f"    URL: {link['url']}\n\n"
            
            output += f"\n💡 Use click_link_by_index with the [index] to navigate to a link."
            
            return output
            
        except Exception as e:
            return f"❌ Error extracting links: {str(e)}"

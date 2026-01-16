"""
Tool para clicar em um link por índice
"""

from selenium.webdriver.common.by import By
from .base import BaseTool
from .browser_tools import BrowserSession


class ClickLinkByIndexTool(BaseTool):
    """Clica em um link pelo seu índice da lista retornada por extract_links"""
    
    @property
    def name(self):
        return "click_link_by_index"
    
    @property
    def description(self):
        return (
            "Clicks on a link by its index number from the list returned by extract_links. "
            "This is the recommended way to navigate after discovering links. "
            "Much more reliable than using text selectors."
        )
    
    def get_parameters(self):
        """Retorna os parâmetros da tool no formato esperado"""
        return {
            "type": "object",
            "properties": {
                "link_index": {
                    "type": "integer",
                    "description": "The index number of the link to click (from extract_links output)"
                }
            },
            "required": ["link_index"]
        }
    
    def execute(self, link_index: int) -> str:
        """
        Clica em um link pelo índice
        
        Args:
            link_index: Índice do link (começando em 0)
            
        Returns:
            Mensagem de sucesso ou erro
        """
        try:
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.common.exceptions import StaleElementReferenceException
            import time
            
            driver = BrowserSession.get_driver()
            
            if not driver:
                return "❌ Browser not initialized. Use open_url first."
            
            # Esperar links estarem presentes
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.TAG_NAME, "a"))
                )
            except:
                return "❌ No links found on page (timeout)."
            
            # Buscar todos os links novamente
            links = driver.find_elements(By.TAG_NAME, "a")
            
            # Filtrar links válidos (mesma lógica do extract_links)
            valid_links = []
            for link in links:
                try:
                    text = link.text.strip()
                    href = link.get_attribute("href")
                    
                    if text and href and not href.startswith("javascript:"):
                        valid_links.append((link, text, href))
                except Exception:
                    continue
            
            if link_index < 0 or link_index >= len(valid_links):
                return f"❌ Invalid link index {link_index}. Valid range: 0-{len(valid_links)-1}"
            
            # Pegar o link pelo índice
            target_link, link_text, link_url = valid_links[link_index]
            link_text_display = link_text[:50]
            
            # Tentar clicar com retry para elementos stale
            max_retries = 2
            for retry in range(max_retries):
                try:
                    # Esperar elemento ser clicável
                    WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable(target_link)
                    )
                    
                    target_link.click()
                    
                    # Esperar navegação completar
                    WebDriverWait(driver, 10).until(
                        lambda d: d.execute_script('return document.readyState') == 'complete'
                    )
                    time.sleep(1)  # Tempo adicional para JS
                    
                    # Verificar se navegou
                    new_url = driver.current_url
                    new_title = driver.title
                    
                    return (
                        f"✅ Clicked on link [{link_index}]: '{link_text_display}'\n"
                        f"📍 New URL: {new_url}\n"
                        f"📄 Page title: '{new_title}'"
                    )
                    
                except StaleElementReferenceException:
                    if retry < max_retries - 1:
                        # Re-encontrar o link
                        time.sleep(0.5)
                        links = driver.find_elements(By.TAG_NAME, "a")
                        valid_links = []
                        for link in links:
                            try:
                                text = link.text.strip()
                                href = link.get_attribute("href")
                                if text and href and not href.startswith("javascript:"):
                                    valid_links.append((link, text, href))
                            except:
                                continue
                        if link_index < len(valid_links):
                            target_link, link_text, link_url = valid_links[link_index]
                            continue
                    raise
                    
                except Exception as e:
                    # Fallback: navegar diretamente para a URL
                    if link_url:
                        driver.get(link_url)
                        
                        # Esperar página carregar
                        WebDriverWait(driver, 10).until(
                            lambda d: d.execute_script('return document.readyState') == 'complete'
                        )
                        time.sleep(1)
                        
                        new_url = driver.current_url
                        new_title = driver.title
                        
                        return (
                            f"✅ Navigated to link [{link_index}]: '{link_text_display}'\n"
                            f"   (Used direct navigation due to click error)\n"
                            f"📍 New URL: {new_url}\n"
                            f"📄 Page title: '{new_title}'"
                        )
                    else:
                        raise e
            
        except Exception as e:
            return f"❌ Error clicking link: {str(e)}"

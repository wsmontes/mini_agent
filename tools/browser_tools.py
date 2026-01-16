"""
Browser Navigation Tools - Real web automation with visible browser
Uses Selenium WebDriver for actual browser control
"""

from .base import BaseTool
from typing import Optional, List, Dict, Any
import time
import os
from datetime import datetime


class BrowserSession:
    """Singleton para gerenciar uma única sessão de browser"""
    _instance = None
    _driver = None
    
    @classmethod
    def get_driver(cls):
        """Obtém ou cria uma instância do WebDriver"""
        if cls._driver is None:
            try:
                from selenium import webdriver
                from selenium.webdriver.chrome.options import Options
                from selenium.webdriver.chrome.service import Service
                
                options = Options()
                # Manter visível (não usar headless)
                # options.add_argument('--headless')  # Comentado para manter visível
                options.add_argument('--start-maximized')
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_experimental_option('excludeSwitches', ['enable-logging'])
                options.add_experimental_option('useAutomationExtension', False)
                
                # Tentar usar ChromeDriver
                try:
                    print("🔵 INICIANDO CHROME...")
                    cls._driver = webdriver.Chrome(options=options)
                    print("✅ Browser Chrome iniciado (visível)")
                    print(f"🔍 Driver type: {type(cls._driver)}")
                except Exception as e:
                    print(f"⚠️  Chrome não disponível: {e}")
                    print(f"⚠️  Tentando Firefox...")
                    # Fallback para Firefox
                    firefox_options = webdriver.FirefoxOptions()
                    cls._driver = webdriver.Firefox(options=firefox_options)
                    print("✅ Browser Firefox iniciado (visível)")
                
                cls._driver.implicitly_wait(10)
                
            except Exception as e:
                print(f"❌ Erro ao iniciar browser: {e}")
                raise
                
        return cls._driver
    
    @classmethod
    def close_driver(cls):
        """Fecha o browser"""
        if cls._driver:
            cls._driver.quit()
            cls._driver = None
            print("Browser fechado")


class OpenURLTool(BaseTool):
    """Abre uma URL no browser visível"""
    
    @property
    def name(self):
        return "open_url"
    
    @property
    def description(self):
        return "Opens a URL in a visible browser window and returns page information including title, current URL, and page source length."
    
    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to open (must include http:// or https://)"
                },
                "wait_seconds": {
                    "type": "integer",
                    "description": "Seconds to wait after loading (default: 2)",
                    "default": 2
                }
            },
            "required": ["url"]
        }
    
    def execute(self, url: str, wait_seconds: int = 2) -> dict:
        try:
            print(f"🔷 OpenURLTool.execute() chamado com url={url}")
            driver = BrowserSession.get_driver()
            print(f"🔷 Driver obtido: {type(driver)}")
            
            # Garantir que URL tem protocolo
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            print(f"🌐 Abrindo: {url}")
            driver.get(url)
            
            # Esperar página estar pronta
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            try:
                WebDriverWait(driver, 10).until(
                    lambda d: d.execute_script('return document.readyState') == 'complete'
                )
            except:
                pass  # Continue mesmo se timeout
            
            time.sleep(wait_seconds)  # Espera adicional para JS carregar
            
            return {
                "success": True,
                "url": driver.current_url,
                "title": driver.title,
                "page_source_length": len(driver.page_source),
                "message": f"Page '{driver.title}' loaded successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to open URL: {e}"
            }


class GetPageContentTool(BaseTool):
    """Extrai conteúdo da página atual"""
    
    @property
    def name(self):
        return "get_page_content"
    
    @property
    def description(self):
        return "Extracts ALL content from the CURRENT browser page (no parameters needed). Returns title, URL, visible text, links, and images. Use this after opening a page to see what's on it."
    
    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "include_links": {
                    "type": "boolean",
                    "description": "Include all links on the page",
                    "default": True
                },
                "include_images": {
                    "type": "boolean",
                    "description": "Include image information",
                    "default": False
                },
                "max_text_length": {
                    "type": "integer",
                    "description": "Maximum text content length to return",
                    "default": 5000
                }
            },
            "required": []
        }
    
    def execute(self, include_links: bool = True, include_images: bool = False, 
                max_text_length: int = 5000) -> dict:
        try:
            from selenium.webdriver.common.by import By
            driver = BrowserSession.get_driver()
            
            # Tentar pegar conteúdo principal primeiro (Wikipedia e sites similares)
            main_content = None
            try:
                # Wikipedia: article content
                main_content = driver.find_element(By.ID, 'mw-content-text')
            except:
                try:
                    # Fallback: main tag
                    main_content = driver.find_element(By.TAG_NAME, 'main')
                except:
                    try:
                        # Fallback: article tag
                        main_content = driver.find_element(By.TAG_NAME, 'article')
                    except:
                        # Fallback final: body inteiro
                        main_content = driver.find_element(By.TAG_NAME, 'body')
            
            # Texto visível
            text_content = main_content.text[:max_text_length]
            
            result = {
                "success": True,
                "url": driver.current_url,
                "title": driver.title,
                "text_content": text_content,
                "text_length": len(main_content.text)
            }
            
            # Links
            if include_links:
                links = driver.find_elements(By.TAG_NAME, 'a')
                result["links"] = []
                for link in links[:50]:  # Limitar a 50 links
                    try:
                        href = link.get_attribute('href')
                        if href:
                            result["links"].append({
                                "text": link.text[:100],
                                "href": href
                            })
                    except:
                        continue  # Skip stale elements
                result["links_count"] = len(links)
            
            # Imagens
            if include_images:
                images = driver.find_elements(By.TAG_NAME, 'img')
                result["images"] = []
                for img in images[:20]:  # Limitar a 20 imagens
                    try:
                        result["images"].append({
                            "src": img.get_attribute('src'),
                            "alt": img.get_attribute('alt')
                        })
                    except:
                        continue  # Skip stale elements
                result["images_count"] = len(images)
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class ClickElementTool(BaseTool):
    """Clica em um elemento da página"""
    
    @property
    def name(self):
        return "click_element"
    
    @property
    def description(self):
        return """Clicks on an element in the page. Use 'link_text' type to click links by their visible text. 
Example: To click a link that says 'Guido van Rossum', use selector_type='link_text' and selector_value='Guido van Rossum'."""
    
    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "selector_type": {
                    "type": "string",
                    "description": "Type of selector to use",
                    "enum": ["text", "link_text", "css", "xpath", "id", "name"]
                },
                "selector_value": {
                    "type": "string",
                    "description": "The selector value to find the element"
                },
                "wait_after": {
                    "type": "integer",
                    "description": "Seconds to wait after clicking",
                    "default": 2
                }
            },
            "required": ["selector_type", "selector_value"]
        }
    
    def execute(self, selector_type: str, selector_value: str, wait_after: int = 2) -> dict:
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            driver = BrowserSession.get_driver()
            
            # Mapear tipo de seletor
            by_map = {
                "text": By.XPATH,
                "link_text": By.LINK_TEXT,
                "css": By.CSS_SELECTOR,
                "xpath": By.XPATH,
                "id": By.ID,
                "name": By.NAME
            }
            
            by_type = by_map.get(selector_type)
            
            # Para text, criar XPath
            if selector_type == "text":
                selector_value = f"//*[contains(text(), '{selector_value}')]"
            
            # Esperar elemento estar clicável
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((by_type, selector_value))
            )
            
            element_text = element.text[:100] if element.text else "No text"
            print(f"🖱️  Clicando em: {element_text}")
            
            element.click()
            time.sleep(wait_after)
            
            return {
                "success": True,
                "clicked_element": element_text,
                "new_url": driver.current_url,
                "new_title": driver.title,
                "message": f"Clicked on '{element_text}'"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to click element: {e}"
            }


class FillFormTool(BaseTool):
    """Preenche campos de formulário"""
    
    @property
    def name(self):
        return "fill_form"
    
    @property
    def description(self):
        return "Fills a form field with text. Can target by field name, ID, CSS selector, or XPath."
    
    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "selector_type": {
                    "type": "string",
                    "description": "Type of selector",
                    "enum": ["name", "id", "css", "xpath"]
                },
                "selector_value": {
                    "type": "string",
                    "description": "The selector value"
                },
                "text": {
                    "type": "string",
                    "description": "Text to fill in the field"
                },
                "submit": {
                    "type": "boolean",
                    "description": "Press Enter after filling",
                    "default": False
                }
            },
            "required": ["selector_type", "selector_value", "text"]
        }
    
    def execute(self, selector_type: str, selector_value: str, text: str, submit: bool = False) -> dict:
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.common.keys import Keys
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            driver = BrowserSession.get_driver()
            
            by_map = {
                "name": By.NAME,
                "id": By.ID,
                "css": By.CSS_SELECTOR,
                "xpath": By.XPATH
            }
            
            # Esperar elemento estar presente e visível
            element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((by_map[selector_type], selector_value))
            )
            
            # Limpar campo antes
            element.clear()
            element.send_keys(text)
            
            print(f"✍️  Preenchido campo '{selector_value}' com: {text[:50]}")
            
            if submit:
                element.send_keys(Keys.RETURN)
                # Esperar navegação se houver submit
                WebDriverWait(driver, 10).until(
                    lambda d: d.execute_script('return document.readyState') == 'complete'
                )
                time.sleep(1)  # Tempo adicional para JS
            
            return {
                "success": True,
                "field": selector_value,
                "text_length": len(text),
                "submitted": submit,
                "message": f"Field filled successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class TakeScreenshotTool(BaseTool):
    """Tira screenshot da página atual"""
    
    @property
    def name(self):
        return "take_screenshot"
    
    @property
    def description(self):
        return "Takes a screenshot of the current browser page and saves it to a file."
    
    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "Filename for the screenshot (optional, auto-generated if not provided)"
                },
                "directory": {
                    "type": "string",
                    "description": "Directory to save screenshot",
                    "default": "screenshots"
                }
            },
            "required": []
        }
    
    def execute(self, filename: str = None, directory: str = "screenshots") -> dict:
        try:
            driver = BrowserSession.get_driver()
            
            # Criar diretório se não existir
            os.makedirs(directory, exist_ok=True)
            
            # Gerar nome do arquivo
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            if not filename.endswith('.png'):
                filename += '.png'
            
            filepath = os.path.join(directory, filename)
            
            # Tirar screenshot
            driver.save_screenshot(filepath)
            
            print(f"📸 Screenshot salvo: {filepath}")
            
            return {
                "success": True,
                "filepath": os.path.abspath(filepath),
                "filename": filename,
                "page_title": driver.title,
                "page_url": driver.current_url,
                "message": f"Screenshot saved to {filepath}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class ScrollPageTool(BaseTool):
    """Rola a página"""
    
    @property
    def name(self):
        return "scroll_page"
    
    @property
    def description(self):
        return "Scrolls the browser page up, down, to top, to bottom, or by specific amount."
    
    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "direction": {
                    "type": "string",
                    "description": "Scroll direction",
                    "enum": ["up", "down", "top", "bottom"]
                },
                "amount": {
                    "type": "integer",
                    "description": "Pixels to scroll (for up/down)",
                    "default": 500
                }
            },
            "required": ["direction"]
        }
    
    def execute(self, direction: str, amount: int = 500) -> dict:
        try:
            driver = BrowserSession.get_driver()
            
            if direction == "top":
                driver.execute_script("window.scrollTo(0, 0);")
            elif direction == "bottom":
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            elif direction == "down":
                driver.execute_script(f"window.scrollBy(0, {amount});")
            elif direction == "up":
                driver.execute_script(f"window.scrollBy(0, -{amount});")
            
            time.sleep(1)
            
            return {
                "success": True,
                "direction": direction,
                "amount": amount if direction in ["up", "down"] else None,
                "message": f"Scrolled {direction}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class FindElementsTool(BaseTool):
    """Busca elementos na página"""
    
    @property
    def name(self):
        return "find_elements"
    
    @property
    def description(self):
        return """Finds specific elements on the page. 
Examples:
- Find by class: {"selector_type": "class", "selector_value": "quote"}
- Find by tag: {"selector_type": "tag", "selector_value": "div"}
- Find by CSS: {"selector_type": "css", "selector_value": "div.quote"}
Returns tag, text, visibility for each element found."""
    
    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "selector_type": {
                    "type": "string",
                    "description": "Type of selector",
                    "enum": ["tag", "class", "id", "css", "xpath"]
                },
                "selector_value": {
                    "type": "string",
                    "description": "The selector value"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of elements to return",
                    "default": 20
                }
            },
            "required": ["selector_type", "selector_value"]
        }
    
    def execute(self, selector_type: str, selector_value: str, max_results: int = 20) -> dict:
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            driver = BrowserSession.get_driver()
            
            by_map = {
                "tag": By.TAG_NAME,
                "class": By.CLASS_NAME,
                "id": By.ID,
                "css": By.CSS_SELECTOR,
                "xpath": By.XPATH
            }
            
            # Esperar pelo menos um elemento estar presente
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((by_map[selector_type], selector_value))
                )
            except:
                pass  # Se não encontrar, continuar e retornar lista vazia
            
            elements = driver.find_elements(by_map[selector_type], selector_value)
            
            results = []
            for elem in elements[:max_results]:
                try:
                    results.append({
                        "tag": elem.tag_name,
                        "text": elem.text[:200] if elem.text else "",
                        "visible": elem.is_displayed(),
                        "enabled": elem.is_enabled()
                    })
                except:
                    pass
            
            return {
                "success": True,
                "selector": f"{selector_type}={selector_value}",
                "total_found": len(elements),
                "returned": len(results),
                "elements": results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class ExecuteJavaScriptTool(BaseTool):
    """Executa JavaScript na página"""
    
    @property
    def name(self):
        return "execute_javascript"
    
    @property
    def description(self):
        return "Executes JavaScript code in the browser page and returns the result."
    
    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "script": {
                    "type": "string",
                    "description": "JavaScript code to execute"
                }
            },
            "required": ["script"]
        }
    
    def execute(self, script: str) -> dict:
        try:
            driver = BrowserSession.get_driver()
            
            result = driver.execute_script(script)
            
            return {
                "success": True,
                "result": result,
                "script_length": len(script),
                "message": "JavaScript executed successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class GoBackTool(BaseTool):
    """Volta para página anterior"""
    
    @property
    def name(self):
        return "go_back"
    
    @property
    def description(self):
        return "Navigates back to the previous page in browser history."
    
    def get_parameters(self):
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
    
    def execute(self) -> dict:
        try:
            driver = BrowserSession.get_driver()
            driver.back()
            time.sleep(2)
            
            return {
                "success": True,
                "current_url": driver.current_url,
                "current_title": driver.title,
                "message": "Navigated back"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class GoForwardTool(BaseTool):
    """Avança para próxima página"""
    
    @property
    def name(self):
        return "go_forward"
    
    @property
    def description(self):
        return "Navigates forward to the next page in browser history."
    
    def get_parameters(self):
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
    
    def execute(self) -> dict:
        try:
            driver = BrowserSession.get_driver()
            driver.forward()
            time.sleep(2)
            
            return {
                "success": True,
                "current_url": driver.current_url,
                "current_title": driver.title,
                "message": "Navigated forward"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class CloseBrowserTool(BaseTool):
    """Fecha o browser"""
    
    @property
    def name(self):
        return "close_browser"
    
    @property
    def description(self):
        return "Closes the browser window and ends the browser session."
    
    def get_parameters(self):
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
    
    def execute(self) -> dict:
        try:
            BrowserSession.close_driver()
            
            return {
                "success": True,
                "message": "Browser closed successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# 🌐 Ferramentas de Browser - Automação Web com Browser Visível

Este documento descreve as 11 ferramentas de automação de browser que navegam de verdade, com o browser visível para você acompanhar todas as ações.

## 📋 Índice

1. [Instalação](#instalação)
2. [Características](#características)
3. [Ferramentas Disponíveis](#ferramentas-disponíveis)
4. [Exemplos de Uso](#exemplos-de-uso)
5. [Boas Práticas](#boas-práticas)
6. [Troubleshooting](#troubleshooting)

## 🔧 Instalação

```bash
# Instalar dependências
pip install selenium webdriver-manager

# Ou usar requirements.txt
pip install -r requirements.txt
```

O sistema automaticamente gerencia o ChromeDriver. Se Chrome não estiver disponível, tenta Firefox automaticamente.

## ✨ Características

- **Browser Visível**: Todas as ações acontecem em uma janela de browser que você pode ver
- **Singleton Pattern**: Uma única instância de browser é compartilhada entre todas as ferramentas
- **Auto-gerenciamento**: WebDriver é instalado e atualizado automaticamente
- **Fallback**: Chrome → Firefox caso Chrome não esteja disponível
- **Screenshots**: Captura telas automaticamente com timestamps
- **Múltiplos Seletores**: Suporta CSS, XPath, ID, name, class, link text
- **JavaScript**: Execute código JavaScript customizado no browser
- **Navegação**: Back, forward, scroll, e controle completo de navegação

## 🛠️ Ferramentas Disponíveis

### 1. OpenURLTool - Abre URLs

Abre uma URL no browser visível.

**Parâmetros:**
- `url` (string, obrigatório): URL para abrir

**Retorno:**
```json
{
  "success": true,
  "url": "https://example.com",
  "title": "Example Domain",
  "page_source_length": 1256,
  "message": "URL aberta com sucesso"
}
```

**Exemplo:**
```python
from tools.browser_tools import OpenURLTool

tool = OpenURLTool()
result = tool.execute(url="https://example.com")
print(result["title"])  # "Example Domain"
```

---

### 2. GetPageContentTool - Extrai Conteúdo

Extrai todo o conteúdo da página atual: texto, links e imagens.

**Parâmetros:**
- Nenhum (usa a página atual do browser)

**Retorno:**
```json
{
  "success": true,
  "text_content": "Texto completo da página...",
  "links": [
    {"text": "More information...", "href": "https://www.iana.org/domains/example"}
  ],
  "images": [
    {"alt": "Logo", "src": "https://example.com/logo.png"}
  ],
  "num_links": 1,
  "num_images": 1
}
```

**Exemplo:**
```python
from tools.browser_tools import GetPageContentTool

tool = GetPageContentTool()
result = tool.execute()
print(f"Links encontrados: {result['num_links']}")
print(f"Texto: {result['text_content'][:100]}")
```

---

### 3. ClickElementTool - Clica em Elementos

Clica em elementos da página usando diferentes tipos de seletores.

**Parâmetros:**
- `selector_type` (string, obrigatório): Tipo de seletor
  - `"text"`: Busca por texto exato no elemento
  - `"link_text"`: Texto exato de um link
  - `"css"`: Seletor CSS
  - `"xpath"`: Expressão XPath
  - `"id"`: ID do elemento
  - `"name"`: Atributo name
- `selector` (string, obrigatório): Valor do seletor

**Retorno:**
```json
{
  "success": true,
  "clicked_element": "Botão Enviar",
  "new_url": "https://example.com/success",
  "new_title": "Success Page"
}
```

**Exemplos:**
```python
from tools.browser_tools import ClickElementTool

tool = ClickElementTool()

# Clicar em link com texto
result = tool.execute(selector_type="link_text", selector="More information")

# Clicar por CSS
result = tool.execute(selector_type="css", selector="button.submit")

# Clicar por ID
result = tool.execute(selector_type="id", selector="btnSubmit")
```

---

### 4. FillFormTool - Preenche Formulários

Preenche campos de formulário e opcionalmente submete.

**Parâmetros:**
- `selector_type` (string, obrigatório): "name", "id", "css", ou "xpath"
- `selector` (string, obrigatório): Seletor do campo
- `value` (string, obrigatório): Valor a preencher
- `submit` (boolean, opcional): Se True, pressiona Enter após preencher

**Retorno:**
```json
{
  "success": true,
  "field": "email",
  "value": "user@example.com",
  "submitted": true,
  "message": "Campo preenchido e formulário enviado"
}
```

**Exemplos:**
```python
from tools.browser_tools import FillFormTool

tool = FillFormTool()

# Preencher campo sem submeter
result = tool.execute(
    selector_type="name",
    selector="email",
    value="user@example.com"
)

# Preencher e submeter (busca no Google, por exemplo)
result = tool.execute(
    selector_type="name",
    selector="q",
    value="Python programming",
    submit=True
)
```

---

### 5. TakeScreenshotTool - Captura Telas

Tira screenshot da página atual e salva em arquivo.

**Parâmetros:**
- `filename` (string, opcional): Nome do arquivo (auto-gera se não fornecido)

**Retorno:**
```json
{
  "success": true,
  "filepath": "/caminho/completo/screenshots/screenshot_20240101_120000.png",
  "filename": "screenshot_20240101_120000.png",
  "url": "https://example.com",
  "title": "Example Domain"
}
```

**Exemplos:**
```python
from tools.browser_tools import TakeScreenshotTool

tool = TakeScreenshotTool()

# Screenshot com nome automático
result = tool.execute()

# Screenshot com nome customizado
result = tool.execute(filename="minha_pagina.png")

print(f"Screenshot salvo em: {result['filepath']}")
```

---

### 6. ScrollPageTool - Rola a Página

Rola a página em diferentes direções.

**Parâmetros:**
- `direction` (string, obrigatório): "up", "down", "top", ou "bottom"
- `pixels` (integer, opcional): Quantidade de pixels (padrão: 500)

**Retorno:**
```json
{
  "success": true,
  "direction": "down",
  "pixels": 500,
  "message": "Página rolada para down 500 pixels"
}
```

**Exemplos:**
```python
from tools.browser_tools import ScrollPageTool

tool = ScrollPageTool()

# Rolar para baixo
result = tool.execute(direction="down")

# Rolar para cima 300 pixels
result = tool.execute(direction="up", pixels=300)

# Rolar para o topo
result = tool.execute(direction="top")

# Rolar para o final
result = tool.execute(direction="bottom")
```

---

### 7. FindElementsTool - Encontra Elementos

Busca elementos na página e retorna informações sobre eles.

**Parâmetros:**
- `selector_type` (string, obrigatório): "tag", "class", "id", "css", ou "xpath"
- `selector` (string, obrigatório): Seletor
- `max_results` (integer, opcional): Limite de resultados (padrão: 20)

**Retorno:**
```json
{
  "success": true,
  "elements": [
    {
      "tag": "a",
      "text": "More information",
      "visible": true,
      "enabled": true
    }
  ],
  "count": 1
}
```

**Exemplos:**
```python
from tools.browser_tools import FindElementsTool

tool = FindElementsTool()

# Encontrar todos os links
result = tool.execute(selector_type="tag", selector="a")

# Encontrar elementos por classe
result = tool.execute(selector_type="class", selector="product-item", max_results=10)

# Encontrar por XPath
result = tool.execute(selector_type="xpath", selector="//div[@class='content']//p")

for element in result["elements"]:
    print(f"Tag: {element['tag']}, Texto: {element['text']}")
```

---

### 8. ExecuteJavaScriptTool - Executa JavaScript

Executa código JavaScript arbitrário no contexto da página.

**Parâmetros:**
- `script` (string, obrigatório): Código JavaScript para executar

**Retorno:**
```json
{
  "success": true,
  "result": ["valor1", "valor2"],
  "message": "JavaScript executado com sucesso"
}
```

**Exemplos:**
```python
from tools.browser_tools import ExecuteJavaScriptTool

tool = ExecuteJavaScriptTool()

# Obter título da página
result = tool.execute(script="return document.title;")
print(result["result"])  # "Example Domain"

# Extrair dados estruturados
script = """
const items = [];
document.querySelectorAll('.product').forEach(el => {
    items.push({
        name: el.querySelector('.name').innerText,
        price: el.querySelector('.price').innerText
    });
});
return items;
"""
result = tool.execute(script=script)
products = result["result"]

# Modificar página
result = tool.execute(script="""
    document.body.style.backgroundColor = 'lightblue';
    return 'Background alterado';
""")
```

---

### 9. GoBackTool - Volta Página

Volta para a página anterior no histórico do browser.

**Parâmetros:**
- Nenhum

**Retorno:**
```json
{
  "success": true,
  "current_url": "https://example.com",
  "current_title": "Example Domain",
  "message": "Voltou para página anterior"
}
```

**Exemplo:**
```python
from tools.browser_tools import GoBackTool

tool = GoBackTool()
result = tool.execute()
print(f"URL atual: {result['current_url']}")
```

---

### 10. GoForwardTool - Avança Página

Avança para a próxima página no histórico do browser.

**Parâmetros:**
- Nenhum

**Retorno:**
```json
{
  "success": true,
  "current_url": "https://example.com/page2",
  "current_title": "Page 2",
  "message": "Avançou para próxima página"
}
```

**Exemplo:**
```python
from tools.browser_tools import GoForwardTool

tool = GoForwardTool()
result = tool.execute()
print(f"Título atual: {result['current_title']}")
```

---

### 11. CloseBrowserTool - Fecha Browser

Fecha o browser e limpa recursos.

**Parâmetros:**
- Nenhum

**Retorno:**
```json
{
  "success": true,
  "message": "Browser fechado com sucesso"
}
```

**Exemplo:**
```python
from tools.browser_tools import CloseBrowserTool

tool = CloseBrowserTool()
result = tool.execute()
```

---

## 📖 Exemplos de Uso

### Exemplo 1: Busca no Google

```python
from tools.browser_tools import (
    OpenURLTool, FillFormTool, TakeScreenshotTool, CloseBrowserTool
)

# Abrir Google
open_tool = OpenURLTool()
open_tool.execute(url="https://www.google.com")

# Buscar
fill_tool = FillFormTool()
fill_tool.execute(
    selector_type="name",
    selector="q",
    value="Python Selenium",
    submit=True
)

# Screenshot dos resultados
screenshot_tool = TakeScreenshotTool()
screenshot_tool.execute(filename="google_results.png")

# Fechar
close_tool = CloseBrowserTool()
close_tool.execute()
```

### Exemplo 2: Web Scraping

```python
from tools.browser_tools import (
    OpenURLTool, GetPageContentTool, ExecuteJavaScriptTool, CloseBrowserTool
)

# Abrir site
open_tool = OpenURLTool()
open_tool.execute(url="https://quotes.toscrape.com/")

# Extrair citações com JavaScript
js_tool = ExecuteJavaScriptTool()
script = """
const quotes = [];
document.querySelectorAll('.quote').forEach(quote => {
    quotes.push({
        text: quote.querySelector('.text').innerText,
        author: quote.querySelector('.author').innerText
    });
});
return quotes;
"""
result = js_tool.execute(script=script)
quotes = result["result"]

for quote in quotes:
    print(f"{quote['text']} - {quote['author']}")

# Fechar
close_tool = CloseBrowserTool()
close_tool.execute()
```

### Exemplo 3: Preencher Formulário

```python
from tools.browser_tools import (
    OpenURLTool, FillFormTool, ClickElementTool, CloseBrowserTool
)

# Abrir página com formulário
open_tool = OpenURLTool()
open_tool.execute(url="https://httpbin.org/forms/post")

# Preencher campos
fill_tool = FillFormTool()
fill_tool.execute(selector_type="name", selector="custname", value="João Silva")
fill_tool.execute(selector_type="name", selector="custtel", value="11999998888")
fill_tool.execute(selector_type="name", selector="custemail", value="joao@example.com")

# Clicar em submit
click_tool = ClickElementTool()
click_tool.execute(selector_type="css", selector="button[type='submit']")

# Fechar
close_tool = CloseBrowserTool()
close_tool.execute()
```

### Exemplo 4: Navegação com Screenshots

```python
from tools.browser_tools import (
    OpenURLTool, ScrollPageTool, TakeScreenshotTool,
    GoBackTool, GoForwardTool, CloseBrowserTool
)

# Abrir site
open_tool = OpenURLTool()
open_tool.execute(url="https://example.com")

# Screenshot topo
screenshot_tool = TakeScreenshotTool()
screenshot_tool.execute(filename="topo.png")

# Rolar e screenshot
scroll_tool = ScrollPageTool()
scroll_tool.execute(direction="down", pixels=500)
screenshot_tool.execute(filename="meio.png")

# Rolar para baixo total
scroll_tool.execute(direction="bottom")
screenshot_tool.execute(filename="final.png")

# Fechar
close_tool = CloseBrowserTool()
close_tool.execute()
```

---

## 🎯 Boas Práticas

### 1. Sempre Fechar o Browser

```python
try:
    open_tool = OpenURLTool()
    open_tool.execute(url="https://example.com")
    # ... suas operações
finally:
    close_tool = CloseBrowserTool()
    close_tool.execute()
```

### 2. Usar Context Manager (Recomendado)

```python
from tools.browser_tools import BrowserSession

# No final do script
try:
    # Suas operações com ferramentas
    pass
finally:
    # Fechar sessão
    BrowserSession.close()
```

### 3. Aguardar Carregamento

As ferramentas já incluem esperas automáticas, mas para casos especiais:

```python
import time

open_tool = OpenURLTool()
open_tool.execute(url="https://slow-site.com")

# Aguardar carregamento adicional
time.sleep(2)

content_tool = GetPageContentTool()
result = content_tool.execute()
```

### 4. Tratamento de Erros

```python
from tools.browser_tools import OpenURLTool, CloseBrowserTool

open_tool = OpenURLTool()
close_tool = CloseBrowserTool()

try:
    result = open_tool.execute(url="https://example.com")
    
    if not result["success"]:
        print(f"Erro: {result.get('error', 'Desconhecido')}")
        
except Exception as e:
    print(f"Exceção: {e}")
    
finally:
    close_tool.execute()
```

### 5. Screenshots Organizados

```python
from datetime import datetime

screenshot_tool = TakeScreenshotTool()

# Nome descritivo com timestamp
filename = f"produto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
screenshot_tool.execute(filename=filename)
```

---

## 🔍 Troubleshooting

### Problema: Chrome não encontrado

**Solução:**
- Sistema tenta Firefox automaticamente
- Instale Chrome: https://www.google.com/chrome/
- Ou instale Firefox: https://www.mozilla.org/firefox/

### Problema: ChromeDriver incompatível

**Solução:**
- `webdriver-manager` atualiza automaticamente
- Se persistir: `pip install --upgrade webdriver-manager`

### Problema: Browser não abre

**Solução:**
```python
# Verificar se não há instância travada
from tools.browser_tools import BrowserSession

BrowserSession._driver = None  # Reset manual
```

### Problema: Timeout ao carregar página

**Solução:**
- Aumentar timeout global (opcional):
```python
from selenium.webdriver.support.ui import WebDriverWait

# No início do script
driver = BrowserSession.get_driver()
driver.set_page_load_timeout(30)  # 30 segundos
```

### Problema: Elemento não encontrado

**Solução:**
- Use `FindElementsTool` para inspecionar elementos primeiro
- Tente diferentes tipos de seletores (CSS, XPath, ID)
- Aguarde carregamento com `time.sleep()`

### Problema: Screenshots em branco

**Solução:**
- Aguarde carregamento completo da página
- Verifique se não há overlay ou modal cobrindo conteúdo

---

## 🚀 Demo Scripts

Execute os demos para ver as ferramentas em ação:

```bash
# Demo básico
python examples/browser_demo.py basic

# Busca no Google
python examples/browser_demo.py search

# Wikipedia
python examples/browser_demo.py wikipedia

# Formulário
python examples/browser_demo.py form

# Web scraping
python examples/browser_demo.py scraping

# Modo interativo
python examples/browser_demo.py interactive

# Todos os demos
python examples/browser_demo.py all
```

---

## 📝 Notas Importantes

1. **Browser Visível**: Todas as ferramentas operam com browser visível para transparência e debugging
2. **Singleton**: Uma única instância de browser é compartilhada - eficiente mas significa que as ferramentas afetam a mesma janela
3. **Screenshots**: Salvos em `screenshots/` no diretório do projeto
4. **Espera Inteligente**: Ferramentas aguardam automaticamente elementos ficarem clicáveis/visíveis
5. **Fallback**: Chrome → Firefox automático
6. **Limpeza**: Sempre chame `CloseBrowserTool.execute()` para evitar processos órfãos

---

## 🎓 Próximos Passos

- Integrar com o agente Qwen para navegação autônoma
- Criar workflows complexos combinando múltiplas ferramentas
- Adicionar suporte para downloads de arquivos
- Implementar gerenciamento de múltiplas abas
- Adicionar suporte para autenticação (cookies, login)

Para mais exemplos, consulte `/examples/browser_demo.py` com 6 demos completos!

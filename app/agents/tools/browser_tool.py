"""Browser automation tool for web interactions"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class BrowserTool:
    """Browser automation tool for web interactions"""
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
    
    async def initialize(self):
        """Initialize browser"""
        if not self.playwright:
            try:
                from playwright.async_api import async_playwright
                self.playwright = await async_playwright().start()
                self.browser = await self.playwright.chromium.launch(headless=True)
                self.context = await self.browser.new_context()
            except ImportError:
                logger.error("Playwright not installed. Install with: pip install playwright && playwright install")
                raise
    
    async def navigate(self, url: str) -> Dict[str, Any]:
        """Navigate to URL and return page content"""
        await self.initialize()
        
        page = await self.context.new_page()
        try:
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Get page content
            title = await page.title()
            content = await page.content()
            
            # Extract text
            text = await page.evaluate('''() => {
                return document.body.innerText;
            }''')
            
            return {
                'success': True,
                'title': title,
                'text': text[:5000],  # Limit size
                'url': page.url
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            await page.close()
    
    async def click(self, url: str, selector: str) -> Dict[str, Any]:
        """Click an element on a page"""
        await self.initialize()
        
        page = await self.context.new_page()
        try:
            await page.goto(url, wait_until='networkidle')
            await page.click(selector)
            await page.wait_for_load_state('networkidle')
            
            return {
                'success': True,
                'url': page.url,
                'message': f'Clicked {selector}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            await page.close()
    
    async def fill_form(
        self,
        url: str,
        form_data: Dict[str, str]
    ) -> Dict[str, Any]:
        """Fill and submit a form"""
        await self.initialize()
        
        page = await self.context.new_page()
        try:
            await page.goto(url, wait_until='networkidle')
            
            for selector, value in form_data.items():
                await page.fill(selector, value)
            
            # Submit form (assuming there's a submit button)
            await page.click('button[type="submit"]')
            await page.wait_for_load_state('networkidle')
            
            return {
                'success': True,
                'url': page.url,
                'message': 'Form submitted successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            await page.close()
    
    async def screenshot(self, url: str, path: str) -> Dict[str, Any]:
        """Take screenshot of a page"""
        await self.initialize()
        
        page = await self.context.new_page()
        try:
            await page.goto(url, wait_until='networkidle')
            await page.screenshot(path=path, full_page=True)
            
            return {
                'success': True,
                'path': path,
                'message': 'Screenshot saved'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            await page.close()
    
    async def cleanup(self):
        """Close browser and cleanup"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


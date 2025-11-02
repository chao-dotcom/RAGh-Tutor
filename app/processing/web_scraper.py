"""Scrape web pages for RAG knowledge base"""
import asyncio
import hashlib
import logging
from datetime import datetime
from typing import List, Optional

from app.schemas.documents import Document

logger = logging.getLogger(__name__)


class WebScraper:
    """Scrape web pages for RAG knowledge base"""
    
    def __init__(self):
        self.playwright = None
        self.browser = None
    
    async def initialize(self):
        """Initialize Playwright browser"""
        try:
            from playwright.async_api import async_playwright
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)
        except ImportError:
            logger.warning("Playwright not available. Install with: pip install playwright")
            raise
    
    async def scrape_url(self, url: str, wait_for_js: bool = True) -> Document:
        """Scrape a single URL"""
        if not self.browser:
            await self.initialize()
        
        page = await self.browser.new_page()
        
        try:
            await page.goto(url, wait_until='networkidle')
            
            # Wait for JavaScript to render
            if wait_for_js:
                await asyncio.sleep(2)
            
            # Get page content
            content = await page.content()
            
            # Parse with BeautifulSoup
            try:
                from bs4 import BeautifulSoup
            except ImportError:
                logger.error("BeautifulSoup4 required for web scraping")
                raise
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'aside']):
                element.decompose()
            
            # Extract text
            text = soup.get_text(separator='\n', strip=True)
            
            # Extract metadata
            title = soup.title.string if soup.title else ""
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc['content'] if meta_desc else ""
            
            return Document(
                content=text,
                metadata={
                    'url': url,
                    'title': title,
                    'description': description,
                    'file_type': 'web',
                    'scraped_at': datetime.now().isoformat()
                },
                doc_id=hashlib.md5(url.encode()).hexdigest(),
                source=url
            )
        
        finally:
            await page.close()
    
    async def scrape_multiple(self, urls: List[str]) -> List[Document]:
        """Scrape multiple URLs in parallel"""
        tasks = [self.scrape_url(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        documents = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Failed to scrape URL: {result}")
            else:
                documents.append(result)
        
        return documents
    
    async def cleanup(self):
        """Close browser and Playwright"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


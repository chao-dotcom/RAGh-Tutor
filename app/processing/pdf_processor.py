"""Advanced PDF processing with table and image extraction"""
import os
import hashlib
import logging
from typing import List, Optional

from app.schemas.documents import Document

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Advanced PDF processing with table and image extraction"""
    
    def __init__(self):
        try:
            from app.processing.table_extractor import TableExtractor
            from app.processing.image_processor import ImageProcessor
            self.table_extractor = TableExtractor()
            self.image_processor = ImageProcessor()
        except ImportError:
            logger.warning("Table/image extractors not available")
            self.table_extractor = None
            self.image_processor = None
    
    async def extract(self, pdf_path: str) -> Document:
        """Extract text, tables, and images from PDF"""
        try:
            import fitz  # PyMuPDF
        except ImportError:
            logger.error("PyMuPDF required for PDF processing")
            raise
        
        doc = fitz.open(pdf_path)
        
        content_parts = []
        metadata = {
            'filename': os.path.basename(pdf_path),
            'file_type': 'pdf',
            'pages': len(doc),
            'has_tables': False,
            'has_images': False
        }
        
        for page_num, page in enumerate(doc, 1):
            # Extract text
            text = page.get_text()
            content_parts.append(f"## Page {page_num}\n{text}")
            
            # Extract tables if available
            if self.table_extractor:
                try:
                    tables = await self.table_extractor.extract_from_page(page)
                    if tables:
                        metadata['has_tables'] = True
                        for i, table in enumerate(tables, 1):
                            content_parts.append(f"\n### Table {page_num}.{i}\n{table}")
                except Exception as e:
                    logger.warning(f"Failed to extract tables from page {page_num}: {e}")
            
            # Extract images if available
            if self.image_processor:
                try:
                    images = page.get_images()
                    if images:
                        metadata['has_images'] = True
                        for img_index, img in enumerate(images):
                            try:
                                xref = img[0]
                                base_image = doc.extract_image(xref)
                                image_bytes = base_image["image"]
                                
                                # OCR the image
                                ocr_text = await self.image_processor.ocr(image_bytes)
                                if ocr_text.strip():
                                    content_parts.append(f"\n### Image {page_num}.{img_index+1} (OCR)\n{ocr_text}")
                            except Exception as e:
                                logger.warning(f"Failed to process image {img_index} on page {page_num}: {e}")
                except Exception as e:
                    logger.warning(f"Failed to extract images from page {page_num}: {e}")
        
        doc.close()
        
        return Document(
            content='\n\n'.join(content_parts),
            metadata=metadata,
            doc_id=self._generate_doc_id(pdf_path),
            source=pdf_path
        )
    
    def _generate_doc_id(self, file_path: str) -> str:
        """Generate unique document ID"""
        return hashlib.md5(file_path.encode()).hexdigest()


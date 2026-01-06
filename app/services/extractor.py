"""XPath/CSS selector extraction service."""
import logging
from typing import List, Optional, Any
from bs4 import BeautifulSoup
from lxml import etree, html
from cssselect import GenericTranslator
from dateutil import parser as date_parser


logger = logging.getLogger(__name__)


class ExtractorService:
    """Service for extracting data from HTML using XPath/CSS selectors."""
    
    def __init__(self):
        """Initialize the extractor service."""
        self.css_translator = GenericTranslator()
    
    def _is_css_selector(self, selector: str) -> bool:
        """Check if selector is CSS (not XPath)."""
        # Simple heuristic: XPath typically starts with / or //
        return not selector.strip().startswith('/')
    
    def _css_to_xpath(self, css_selector: str) -> str:
        """Convert CSS selector to XPath."""
        try:
            xpath = self.css_translator.css_to_xpath(css_selector)
            return xpath
        except Exception as e:
            logger.error(f"Error converting CSS to XPath: {e}")
            return css_selector
    
    def extract_with_xpath(
        self,
        html_content: str,
        xpath: str,
        get_attribute: Optional[str] = None
    ) -> List[str]:
        """
        Extract data from HTML using XPath.
        
        Args:
            html_content: HTML content as string
            xpath: XPath expression
            get_attribute: If specified, extract this attribute instead of text
            
        Returns:
            List of extracted strings
        """
        try:
            # Parse HTML with lxml
            tree = html.fromstring(html_content)
            
            # Convert CSS to XPath if needed
            if self._is_css_selector(xpath):
                xpath = self._css_to_xpath(xpath)
            
            # Execute XPath
            results = tree.xpath(xpath)
            
            # Process results
            extracted = []
            for result in results:
                if isinstance(result, str):
                    extracted.append(result.strip())
                elif hasattr(result, 'text'):
                    text = result.text or ''
                    extracted.append(text.strip())
                elif isinstance(result, bytes):
                    extracted.append(result.decode('utf-8').strip())
                else:
                    extracted.append(str(result).strip())
            
            return [x for x in extracted if x]  # Filter empty strings
            
        except Exception as e:
            logger.error(f"Error extracting with XPath '{xpath}': {e}")
            return []
    
    def extract_items(
        self,
        html_content: str,
        item_xpath: str
    ) -> List[Any]:
        """
        Extract item elements from HTML.
        
        Args:
            html_content: HTML content as string
            item_xpath: XPath to find all items
            
        Returns:
            List of lxml elements
        """
        try:
            tree = html.fromstring(html_content)
            
            # Convert CSS to XPath if needed
            if self._is_css_selector(item_xpath):
                item_xpath = self._css_to_xpath(item_xpath)
            
            items = tree.xpath(item_xpath)
            return items
            
        except Exception as e:
            logger.error(f"Error extracting items with XPath '{item_xpath}': {e}")
            return []
    
    def extract_from_element(
        self,
        element: Any,
        xpath: str
    ) -> Optional[str]:
        """
        Extract data from a specific element using relative XPath.
        
        Args:
            element: lxml element
            xpath: Relative XPath expression (should start with .)
            
        Returns:
            Extracted string or None
        """
        try:
            # Ensure xpath is relative
            if not xpath.startswith('.'):
                xpath = '.' + xpath if xpath.startswith('/') else './/' + xpath
            
            results = element.xpath(xpath)
            
            if not results:
                return None
            
            # Get first result
            result = results[0]
            
            if isinstance(result, str):
                return result.strip()
            elif hasattr(result, 'text'):
                text = result.text or ''
                return text.strip()
            elif isinstance(result, bytes):
                return result.decode('utf-8').strip()
            else:
                return str(result).strip()
                
        except Exception as e:
            logger.error(f"Error extracting from element with XPath '{xpath}': {e}")
            return None
    
    def extract_all_from_element(
        self,
        element: Any,
        xpath: str
    ) -> List[str]:
        """
        Extract all matching data from a specific element.
        
        Args:
            element: lxml element
            xpath: Relative XPath expression
            
        Returns:
            List of extracted strings
        """
        try:
            # Ensure xpath is relative
            if not xpath.startswith('.'):
                xpath = '.' + xpath if xpath.startswith('/') else './/' + xpath
            
            results = element.xpath(xpath)
            
            extracted = []
            for result in results:
                if isinstance(result, str):
                    extracted.append(result.strip())
                elif hasattr(result, 'text'):
                    text = result.text or ''
                    extracted.append(text.strip())
                elif isinstance(result, bytes):
                    extracted.append(result.decode('utf-8').strip())
                else:
                    extracted.append(str(result).strip())
            
            return [x for x in extracted if x]
            
        except Exception as e:
            logger.error(f"Error extracting from element with XPath '{xpath}': {e}")
            return []
    
    def parse_date(self, date_string: str) -> Optional[str]:
        """
        Parse date string to ISO format.
        
        Args:
            date_string: Date string in various formats
            
        Returns:
            ISO formatted date string or None
        """
        try:
            dt = date_parser.parse(date_string)
            return dt.isoformat()
        except Exception as e:
            logger.warning(f"Could not parse date '{date_string}': {e}")
            return None
    
    def make_absolute_url(self, base_url: str, relative_url: str) -> str:
        """
        Convert relative URL to absolute URL.
        
        Args:
            base_url: Base URL
            relative_url: Relative or absolute URL
            
        Returns:
            Absolute URL
        """
        from urllib.parse import urljoin
        return urljoin(base_url, relative_url)

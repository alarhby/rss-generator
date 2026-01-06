"""RSS feed builder service."""
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from feedgen.feed import FeedGenerator
from app.services.scraper import ScraperService
from app.services.extractor import ExtractorService
from app.services.cache import CacheService


logger = logging.getLogger(__name__)


class RSSBuilderService:
    """Service for building RSS feeds from scraped data."""
    
    def __init__(
        self,
        scraper: ScraperService,
        extractor: ExtractorService,
        cache: Optional[CacheService] = None
    ):
        """
        Initialize RSS builder service.
        
        Args:
            scraper: Scraper service instance
            extractor: Extractor service instance
            cache: Optional cache service instance
        """
        self.scraper = scraper
        self.extractor = extractor
        self.cache = cache
    
    async def build_feed(
        self,
        source_url: str,
        feed_config: Dict[str, Any],
        item_selectors: Dict[str, Any],
        detail_extraction: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Build RSS feed from configuration.
        
        Args:
            source_url: Source URL to scrape
            feed_config: Feed metadata configuration
            item_selectors: XPath selectors for items
            detail_extraction: Optional detail page extraction config
            options: Optional feed options
            
        Returns:
            RSS XML string or None if failed
        """
        try:
            # Set defaults
            if options is None:
                options = {}
            
            cache_ttl = options.get('cache_ttl', 3600)
            max_items = options.get('max_items', 50)
            respect_robots = options.get('respect_robots_txt', True)
            request_delay = options.get('request_delay', 1.0)
            
            # Check cache
            cache_key = f"feed:{source_url}"
            if self.cache:
                cached = await self.cache.get(cache_key)
                if cached:
                    logger.info(f"Returning cached feed for {source_url}")
                    return cached
            
            # Fetch HTML
            html_content = self.scraper.fetch_html(
                source_url,
                respect_robots=respect_robots,
                delay=request_delay
            )
            
            if not html_content:
                logger.error(f"Failed to fetch HTML from {source_url}")
                return None
            
            # Extract items
            items = await self._extract_items(
                html_content,
                source_url,
                item_selectors,
                detail_extraction,
                options
            )
            
            if not items:
                logger.warning(f"No items extracted from {source_url}")
            
            # Limit items
            items = items[:max_items]
            
            # Build RSS feed
            rss_xml = self._generate_rss(feed_config, items)
            
            # Cache result
            if self.cache and rss_xml:
                await self.cache.set(cache_key, rss_xml, ttl=cache_ttl)
            
            return rss_xml
            
        except Exception as e:
            logger.error(f"Error building feed: {e}")
            return None
    
    async def _extract_items(
        self,
        html_content: str,
        base_url: str,
        item_selectors: Dict[str, Any],
        detail_extraction: Optional[Dict[str, Any]],
        options: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract items from HTML content."""
        items = []
        
        # Get item elements
        item_xpath = item_selectors.get('items')
        if not item_xpath:
            return items
        
        elements = self.extractor.extract_items(html_content, item_xpath)
        logger.info(f"Found {len(elements)} items")
        
        for element in elements:
            item = {}
            
            # Extract each field
            for field, xpath in item_selectors.items():
                if field == 'items' or not xpath:
                    continue
                
                if field == 'category':
                    # Categories can be multiple
                    values = self.extractor.extract_all_from_element(element, xpath)
                    if values:
                        item[field] = values
                else:
                    value = self.extractor.extract_from_element(element, xpath)
                    if value:
                        # Make URLs absolute
                        if field in ['link', 'image']:
                            value = self.extractor.make_absolute_url(base_url, value)
                        # Parse dates
                        elif field == 'pubDate':
                            parsed_date = self.extractor.parse_date(value)
                            if parsed_date:
                                value = parsed_date
                        
                        item[field] = value
            
            # Deep content extraction from detail page
            if detail_extraction and detail_extraction.get('enabled'):
                item_link = item.get('link')
                if item_link:
                    await self._extract_detail_content(
                        item,
                        item_link,
                        detail_extraction,
                        options
                    )
            
            if item:
                items.append(item)
        
        return items
    
    async def _extract_detail_content(
        self,
        item: Dict[str, Any],
        detail_url: str,
        detail_extraction: Dict[str, Any],
        options: Dict[str, Any]
    ):
        """Extract content from detail page."""
        try:
            respect_robots = options.get('respect_robots_txt', True)
            request_delay = options.get('request_delay', 1.0)
            
            # Check cache
            cache_key = f"detail:{detail_url}"
            detail_html = None
            
            if self.cache:
                detail_html = await self.cache.get(cache_key)
            
            if not detail_html:
                # Fetch detail page
                detail_html = self.scraper.fetch_html(
                    detail_url,
                    respect_robots=respect_robots,
                    delay=request_delay
                )
                
                if detail_html and self.cache:
                    # Cache for longer period
                    await self.cache.set(cache_key, detail_html, ttl=86400)
            
            if not detail_html:
                return
            
            # Extract content
            content_xpath = detail_extraction.get('content')
            if content_xpath:
                content_parts = self.extractor.extract_with_xpath(
                    detail_html,
                    content_xpath
                )
                if content_parts:
                    item['content'] = '\n'.join(content_parts)
            
            # Extract image if not already present
            if not item.get('image'):
                image_xpath = detail_extraction.get('image')
                if image_xpath:
                    images = self.extractor.extract_with_xpath(
                        detail_html,
                        image_xpath
                    )
                    if images:
                        item['image'] = self.extractor.make_absolute_url(
                            detail_url,
                            images[0]
                        )
                        
        except Exception as e:
            logger.error(f"Error extracting detail content from {detail_url}: {e}")
    
    def _generate_rss(
        self,
        feed_config: Dict[str, Any],
        items: List[Dict[str, Any]]
    ) -> str:
        """Generate RSS XML from feed data."""
        try:
            # Create feed
            fg = FeedGenerator()
            fg.title(feed_config.get('title', 'RSS Feed'))
            fg.link(href=feed_config.get('link', ''), rel='alternate')
            fg.description(feed_config.get('description', ''))
            fg.language('en')
            
            # Add items
            for item_data in items:
                fe = fg.add_entry()
                
                # Required fields
                title = item_data.get('title', 'No Title')
                link = item_data.get('link', '')
                
                fe.title(title)
                fe.link(href=link)
                
                # Optional fields
                description = item_data.get('description', '')
                content = item_data.get('content', '')
                
                # Use content if available, otherwise description
                if content:
                    fe.description(description or title)
                    fe.content(content, type='html')
                elif description:
                    fe.description(description)
                else:
                    fe.description(title)
                
                # GUID
                fe.guid(link, permalink=True)
                
                # Publication date
                pub_date = item_data.get('pubDate')
                if pub_date:
                    try:
                        if isinstance(pub_date, str):
                            from dateutil import parser
                            dt = parser.parse(pub_date)
                        else:
                            dt = pub_date
                        fe.pubDate(dt)
                    except Exception as e:
                        logger.warning(f"Could not parse date: {e}")
                
                # Author
                author = item_data.get('author')
                if author:
                    fe.author(name=author)
                
                # Categories
                categories = item_data.get('category', [])
                if isinstance(categories, str):
                    categories = [categories]
                for category in categories:
                    fe.category(term=category)
                
                # Image/Enclosure
                image = item_data.get('image')
                if image:
                    try:
                        fe.enclosure(url=image, type='image/jpeg')
                    except:
                        pass
            
            # Generate RSS 2.0
            return fg.rss_str(pretty=True).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Error generating RSS XML: {e}")
            return None
    
    async def preview_items(
        self,
        source_url: str,
        item_selectors: Dict[str, Any],
        detail_extraction: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None,
        max_items: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Preview extracted items without generating RSS.
        
        Args:
            source_url: Source URL to scrape
            item_selectors: XPath selectors for items
            detail_extraction: Optional detail page extraction config
            options: Optional feed options
            max_items: Maximum items to preview
            
        Returns:
            List of extracted items
        """
        try:
            if options is None:
                options = {}
            
            respect_robots = options.get('respect_robots_txt', True)
            request_delay = options.get('request_delay', 1.0)
            
            # Fetch HTML
            html_content = self.scraper.fetch_html(
                source_url,
                respect_robots=respect_robots,
                delay=request_delay
            )
            
            if not html_content:
                return []
            
            # Extract items
            items = await self._extract_items(
                html_content,
                source_url,
                item_selectors,
                detail_extraction,
                options
            )
            
            return items[:max_items]
            
        except Exception as e:
            logger.error(f"Error previewing items: {e}")
            return []

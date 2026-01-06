"""Web scraping service for fetching HTML content."""
import logging
import time
from typing import Optional, Dict
import requests
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
from app.config import settings


logger = logging.getLogger(__name__)


class ScraperService:
    """Service for scraping HTML content from URLs."""
    
    def __init__(self):
        """Initialize the scraper service."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': settings.default_user_agent
        })
        self.last_request_time: Dict[str, float] = {}
        self.robots_cache: Dict[str, RobotFileParser] = {}
    
    def _respect_rate_limit(self, domain: str, delay: float):
        """Ensure rate limiting between requests to the same domain."""
        if domain in self.last_request_time:
            elapsed = time.time() - self.last_request_time[domain]
            if elapsed < delay:
                time.sleep(delay - elapsed)
        self.last_request_time[domain] = time.time()
    
    def _check_robots_txt(self, url: str) -> bool:
        """Check if scraping is allowed by robots.txt."""
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        
        if domain not in self.robots_cache:
            robots_url = urljoin(domain, '/robots.txt')
            rp = RobotFileParser()
            rp.set_url(robots_url)
            try:
                rp.read()
                self.robots_cache[domain] = rp
            except Exception as e:
                logger.warning(f"Could not read robots.txt for {domain}: {e}")
                # If we can't read robots.txt, assume it's allowed
                return True
        
        rp = self.robots_cache[domain]
        return rp.can_fetch(settings.default_user_agent, url)
    
    def fetch_html(
        self,
        url: str,
        respect_robots: bool = True,
        delay: float = None,
        timeout: int = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """
        Fetch HTML content from a URL.
        
        Args:
            url: The URL to fetch
            respect_robots: Whether to respect robots.txt
            delay: Delay between requests (default from settings)
            timeout: Request timeout (default from settings)
            headers: Additional headers to send
            
        Returns:
            HTML content as string or None if failed
        """
        if delay is None:
            delay = settings.default_request_delay
        if timeout is None:
            timeout = settings.default_request_timeout
        
        # Check robots.txt if enabled
        if respect_robots and settings.respect_robots_txt:
            if not self._check_robots_txt(url):
                logger.warning(f"Scraping disallowed by robots.txt: {url}")
                return None
        
        # Respect rate limiting
        parsed = urlparse(url)
        domain = parsed.netloc
        self._respect_rate_limit(domain, delay)
        
        # Prepare headers
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)
        
        try:
            logger.info(f"Fetching HTML from: {url}")
            response = self.session.get(
                url,
                timeout=timeout,
                headers=request_headers
            )
            response.raise_for_status()
            
            # Try to get encoding from response
            if response.encoding:
                response.encoding = response.apparent_encoding
            
            return response.text
            
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def fetch_multiple(
        self,
        urls: list[str],
        respect_robots: bool = True,
        delay: float = None
    ) -> Dict[str, Optional[str]]:
        """
        Fetch HTML content from multiple URLs.
        
        Args:
            urls: List of URLs to fetch
            respect_robots: Whether to respect robots.txt
            delay: Delay between requests
            
        Returns:
            Dictionary mapping URLs to their HTML content
        """
        results = {}
        for url in urls:
            results[url] = self.fetch_html(url, respect_robots, delay)
        return results

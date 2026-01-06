# RSS Generator

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

A comprehensive RSS Generator application that converts any HTML website into an RSS feed with advanced features including custom XPath/CSS selectors, deep content extraction, caching, and a user-friendly web interface.

## ✨ Features

- **Universal HTML Support**: Works with any HTML website - blogs, news sites, e-commerce, documentation sites, etc.
- **Custom XPath/CSS Selectors**: Define custom selectors to extract exactly the content you need
- **Deep Content Extraction**: Automatically fetch and parse full content from individual article pages
- **Smart Caching**: Built-in caching system for improved performance
- **RESTful API**: Full REST API with automatic Swagger/OpenAPI documentation
- **Web Interface**: User-friendly interface for creating and managing feeds
- **Feed Management**: Create, update, delete, and preview feeds
- **Live Preview**: Test your configuration and see extracted items before saving
- **XPath Testing**: Built-in XPath tester to validate selectors
- **Robots.txt Compliance**: Respects website robots.txt rules
- **Rate Limiting**: Configurable request delays to avoid overloading servers
- **Export/Import**: JSON configuration for easy sharing

## 🚀 Quick Start

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/alarhby/rss-generator.git
cd rss-generator
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment** (optional):
```bash
cp .env.example .env
# Edit .env with your preferred settings
```

4. **Run the application**:
```bash
python -m uvicorn app.main:app --reload
```

5. **Access the application**:
- Web Interface: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Alternative API Docs: http://localhost:8000/redoc

### Using Docker

```bash
# Build the image
docker build -t rss-generator .

# Run the container
docker run -p 8000:8000 rss-generator
```

## 📖 Usage Guide

### Creating Your First Feed

1. **Navigate to Create Feed**: Go to http://localhost:8000/create
2. **Enter Basic Information**:
   - Feed Name: A friendly name for your feed
   - Source URL: The website URL to scrape
   - Feed Title: RSS feed title
   - Feed Description: RSS feed description

3. **Configure Selectors**:
   - **Items Selector**: XPath to find all items (e.g., `//article[@class='post']`)
   - **Title Selector**: Extract item titles (e.g., `.//h2/text()`)
   - **Link Selector**: Extract item URLs (e.g., `.//a/@href`)
   - **Description**: Extract summaries (e.g., `.//p[@class='excerpt']/text()`)
   - **Publication Date**: Extract dates (e.g., `.//time/@datetime`)
   - **Author**: Extract author names
   - **Category**: Extract categories/tags
   - **Image**: Extract images

4. **Enable Deep Extraction** (optional):
   - Check "Enable deep content extraction"
   - Configure content selector for detail pages

5. **Configure Options**:
   - Cache TTL: How long to cache results
   - Max Items: Maximum items in feed
   - Request Delay: Time between requests
   - Respect robots.txt: Follow robots.txt rules

6. **Test & Preview**:
   - Use the XPath tester to validate selectors
   - Preview extracted items before saving

7. **Save & Use**:
   - Click "Create Feed"
   - Copy the RSS URL and add to your RSS reader

### XPath/CSS Selector Guide

#### Common XPath Patterns

```xpath
# Select all articles
//article

# Select by class
//div[@class='post']

# Select by ID
//div[@id='content']

# Get text content
//h1/text()

# Get attribute
//img/@src

# Relative selectors (from parent element)
.//h2/text()
.//a/@href

# Multiple conditions
//article[@class='post' and @data-published='true']
```

#### CSS Selectors (automatically converted to XPath)

```css
div.post
#content
article h2
.post-title
```

## 🔧 API Documentation

### Endpoints

#### Feed Management

- `POST /api/feeds` - Create new feed
- `GET /api/feeds` - List all feeds
- `GET /api/feeds/{feed_id}` - Get specific feed
- `PUT /api/feeds/{feed_id}` - Update feed
- `DELETE /api/feeds/{feed_id}` - Delete feed
- `GET /api/feeds/{feed_id}/preview` - Preview extracted items
- `POST /api/feeds/test-xpath` - Test XPath expression

#### RSS Generation

- `GET /rss/{feed_id}` - Get RSS XML output
- `GET /api/feeds/{feed_id}/rss` - Alternative RSS endpoint

### API Examples

#### Create a Feed

```bash
curl -X POST http://localhost:8000/api/feeds \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Blog Feed",
    "source_url": "https://example.com/blog",
    "feed_config": {
      "title": "Blog Posts",
      "description": "Latest blog posts",
      "link": "https://example.com/blog"
    },
    "item_selectors": {
      "items": "//article[@class=\"post\"]",
      "title": ".//h2/text()",
      "link": ".//a/@href",
      "description": ".//p[@class=\"excerpt\"]/text()"
    }
  }'
```

#### Test XPath

```bash
curl -X POST http://localhost:8000/api/feeds/test-xpath \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "xpath": "//h1/text()"
  }'
```

#### Get Feed List

```bash
curl http://localhost:8000/api/feeds
```

## 📋 Configuration Examples

### Blog/News Site

```json
{
  "name": "Tech Blog",
  "source_url": "https://techblog.example.com",
  "feed_config": {
    "title": "Tech Blog RSS",
    "description": "Latest tech articles",
    "link": "https://techblog.example.com"
  },
  "item_selectors": {
    "items": "//article[@class='post']",
    "title": ".//h2[@class='post-title']/text()",
    "link": ".//a[@class='permalink']/@href",
    "description": ".//div[@class='excerpt']/text()",
    "pubDate": ".//time/@datetime",
    "author": ".//span[@class='author']/text()",
    "category": ".//span[@class='tag']/text()",
    "image": ".//img[@class='featured']/@src"
  },
  "detail_extraction": {
    "enabled": true,
    "content": "//article[@class='content']//text()",
    "image": "//meta[@property='og:image']/@content"
  },
  "options": {
    "cache_ttl": 3600,
    "max_items": 50,
    "request_delay": 1.0
  }
}
```

### E-commerce Products

```json
{
  "name": "New Products",
  "source_url": "https://shop.example.com/new-products",
  "feed_config": {
    "title": "New Products Feed",
    "description": "Latest products",
    "link": "https://shop.example.com"
  },
  "item_selectors": {
    "items": "//div[@class='product-card']",
    "title": ".//h4[@class='product-name']/text()",
    "link": ".//a[@class='product-link']/@href",
    "description": ".//div[@class='product-desc']/text()",
    "image": ".//img[@class='product-img']/@src"
  }
}
```

### Documentation Site

```json
{
  "name": "API Changelog",
  "source_url": "https://docs.example.com/changelog",
  "feed_config": {
    "title": "API Changelog",
    "description": "API updates and changes",
    "link": "https://docs.example.com/changelog"
  },
  "item_selectors": {
    "items": "//div[@class='changelog-entry']",
    "title": ".//h3/text()",
    "link": ".//a/@href",
    "description": ".//div[@class='summary']/text()",
    "pubDate": ".//span[@class='date']/@datetime"
  }
}
```

## 🔒 Security Considerations

- All user inputs are validated and sanitized
- XPath expressions are validated before execution
- Rate limiting prevents abuse
- Robots.txt compliance is enforced by default
- Request timeouts prevent hanging connections
- CORS configuration for API access
- SQL injection protection via SQLAlchemy ORM

## 🛠 Configuration Options

### Environment Variables

Edit `.env` file:

```bash
# Application
APP_NAME="RSS Generator"
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite+aiosqlite:///./rss_generator.db

# Cache
CACHE_DEFAULT_TTL=3600
CACHE_MAX_SIZE=1000

# Scraping
DEFAULT_USER_AGENT="Mozilla/5.0 (compatible; RSS-Generator/1.0)"
DEFAULT_REQUEST_TIMEOUT=30
DEFAULT_REQUEST_DELAY=1.0
RESPECT_ROBOTS_TXT=True
MAX_ITEMS_PER_FEED=50

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# CORS
CORS_ORIGINS=["*"]
```

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/
```

## 📊 Project Structure

```
rss-generator/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database models
│   ├── models.py               # Pydantic models
│   ├── routers/
│   │   ├── feeds.py            # Feed management endpoints
│   │   └── rss.py              # RSS generation endpoints
│   ├── services/
│   │   ├── scraper.py          # HTML scraping
│   │   ├── extractor.py        # XPath extraction
│   │   ├── rss_builder.py      # RSS generation
│   │   └── cache.py            # Caching
│   └── static/
│       ├── css/style.css
│       └── js/app.js
├── templates/                   # HTML templates
├── examples/                    # Example configurations
├── tests/                       # Test files
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
└── Dockerfile
```

## 🐛 Troubleshooting

### Common Issues

**Issue**: "Failed to fetch HTML from URL"
- Check if the URL is accessible
- Verify robots.txt allows scraping
- Try increasing request timeout

**Issue**: "No items extracted"
- Verify XPath selectors are correct
- Use the XPath tester to validate
- Check if the page structure has changed

**Issue**: "Date parsing failed"
- Ensure date format is standard (ISO 8601 recommended)
- Check the XPath is extracting the date correctly

**Issue**: "Relative URLs not working"
- Make sure links are being extracted correctly
- The system automatically converts relative to absolute URLs

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- HTML parsing with [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) and [lxml](https://lxml.de/)
- RSS generation with [feedgen](https://feedgen.kiesow.be/)
- Date parsing with [python-dateutil](https://dateutil.readthedocs.io/)

## 📧 Support

For issues, questions, or suggestions, please [open an issue](https://github.com/alarhby/rss-generator/issues) on GitHub.

---

Made with ❤️ by the RSS Generator team
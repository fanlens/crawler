"""Settings for the scrapy crawler"""
from common.config import get_config

_CONFIG = get_config()

# Scrapy settings for crawler project
BOT_NAME = 'crawler'

SPIDER_MODULES = ['crawler.spiders']
NEWSPIDER_MODULE = 'crawler.spiders'

ROBOTSTXT_OBEY = False

LOG_LEVEL = 'INFO'
LOG_STDOUT = False

ITEM_PIPELINES = {
    'crawler.pipelines.RESTPipeline': 305,
    'crawler.pipelines.BulkRESTPipeline': 306,
    'crawler.pipelines.DBPipeline': 405,
    'crawler.pipelines.BulkDBPipeline': 406,
}
CONCURRENT_REQUESTS_PER_DOMAIN = 1

DOWNLOADER_MIDDLEWARES = {
    'crawler.middleware.twitter.TwitterDownloaderMiddleware': 10,
}
TWITTER_CONSUMER_KEY = _CONFIG.get("TWITTER", "consumer_key")
TWITTER_CONSUMER_SECRET = _CONFIG.get("TWITTER", "consumer_secret")
TWITTER_ACCESS_TOKEN_KEY = _CONFIG.get("TWITTER", "access_token")
TWITTER_ACCESS_TOKEN_SECRET = _CONFIG.get("TWITTER", "access_token_secret")

FACEBOOK_ACCESS_TOKEN = _CONFIG.get("FACEBOOK", 'access_token')

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'crawler (+http://www.yourdomain.com)'

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False



# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'crawler.middlewares.MyCustomSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    'crawler.middlewares.MyCustomDownloaderMiddleware': 543,
# }

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }


# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

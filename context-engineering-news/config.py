#!/usr/bin/env python3
"""
Configuration settings for Context Engineering Daily News
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = BASE_DIR / "docs"
TEMPLATES_DIR = BASE_DIR / "templates"
CONFIG_DIR = BASE_DIR / "config"

# Ensure directories exist
for directory in [DATA_DIR, DOCS_DIR]:
    directory.mkdir(exist_ok=True)

# API Keys (from environment variables)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

# Site configuration
SITE_CONFIG = {
    'base_url': 'https://your-username.github.io/context-engineering-news',
    'title': 'Context Engineering Daily',
    'description': 'Daily news and research in AI Context Engineering',
    'author': 'Context Engineering News Bot',
    'language': 'en-us'
}

# Scraping configuration
SCRAPING_CONFIG = {
    'user_agent': 'Context-Engineering-News-Bot/1.0 (Educational Purpose)',
    'request_timeout': 30,
    'rate_limit_delay': 1,  # seconds between requests
    'max_items_per_source': 20,
    'max_content_length': 5000,  # characters
    'days_back': 7  # how many days back to look for news
}

# AI configuration
AI_CONFIG = {
    'openai': {
        'model': 'gpt-3.5-turbo',
        'max_tokens': 150,
        'temperature': 0.3
    },
    'anthropic': {
        'model': 'claude-3-haiku-20240307',
        'max_tokens': 150,
        'temperature': 0.3
    },
    'enable_enhancement': True,
    'min_score_for_summary': 0.4
}

# HTML generation configuration
HTML_CONFIG = {
    'max_items_per_category': 10,
    'show_low_relevance': False,
    'enable_search': True,
    'enable_dark_mode': True
}

# RSS configuration
RSS_CONFIG = {
    'max_items': 50,
    'max_category_items': 20,
    'include_full_content': True
}

# Logging configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'context_engineering_news.log',
    'max_bytes': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5
}

# Development settings
DEVELOPMENT = {
    'debug': os.getenv('DEBUG', 'False').lower() == 'true',
    'test_mode': os.getenv('TEST_MODE', 'False').lower() == 'true',
    'mock_ai': os.getenv('MOCK_AI', 'False').lower() == 'true'
}

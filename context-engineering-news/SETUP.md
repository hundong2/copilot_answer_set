# Context Engineering Daily News - Setup Guide

## Quick Start

1. **Fork this repository**
2. **Enable GitHub Pages**:
   - Go to Settings > Pages
   - Source: GitHub Actions
3. **Configure secrets** (optional for enhanced features):
   - `GEMINI_API_KEY` - for Google Gemini summarization (🆓 **추천**, 무료 할당량 제공)
   - `OPENAI_API_KEY` - for OpenAI GPT summarization
   - `ANTHROPIC_API_KEY` - for Claude summarization
   - `GH_PAT` - GitHub Personal Access Token (for higher API rate limits)
     - ⚠️ **주의**: `GITHUB_TOKEN`은 사용 불가 (GitHub 예약어)
     - GitHub > Settings > Developer settings > Personal access tokens
     - Scope: `public_repo` 권한만 필요
4. **Manual trigger**: Go to Actions tab and run "Context Engineering Daily News" workflow

## Development Setup

### Prerequisites
- Python 3.11+
- pip or pipenv

### Local Installation

```bash
# Clone the repository
git clone https://github.com/your-username/context-engineering-news.git
cd context-engineering-news

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the pipeline
python run_daily_news.py --no-ai  # Without AI enhancement
python run_daily_news.py          # With AI enhancement (requires API keys)
```

### Environment Variables

```bash
# Optional: AI Enhancement (choose one or more)
export GEMINI_API_KEY="your-gemini-key"          # Recommended (free tier available)
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"

# Optional: GitHub API (for higher rate limits)
export GITHUB_TOKEN="your-github-token"

# Optional: Development
export DEBUG="true"
export TEST_MODE="true"
```

## Configuration

### News Sources
Edit `config/sources.json` to add or modify news sources:

```json
{
  "sources": {
    "your_source": {
      "name": "Your Source Name",
      "type": "rss",
      "urls": ["https://example.com/feed.xml"],
      "priority": 8,
      "description": "Description of your source"
    }
  }
}
```

### Categories
Edit `config/categories.json` to modify categorization:

```json
{
  "categories": {
    "your_category": {
      "name": "Your Category",
      "description": "Description",
      "keywords": ["keyword1", "keyword2"]
    }
  }
}
```

## GitHub Actions

### Workflow Schedule
The workflow runs daily at 09:00 UTC. Edit `.github/workflows/daily-news.yml` to change:

```yaml
schedule:
  - cron: '0 9 * * *'  # Change time here
```

### Manual Trigger
1. Go to your repository
2. Click "Actions" tab
3. Select "Context Engineering Daily News"
4. Click "Run workflow"

### GitHub Pages Setup
1. Repository Settings > Pages
2. Source: "GitHub Actions"
3. The site will be available at: `https://your-username.github.io/repository-name/`

## Testing

```bash
# Run tests
python -m pytest tests/ -v

# Test individual components
python src/news_scraper.py
python src/html_generator.py
python src/rss_generator.py
```

## Features

### Core Features
- ✅ Multi-source news aggregation
- ✅ AI-powered categorization
- ✅ HTML newsletter generation
- ✅ RSS feed generation
- ✅ GitHub Actions automation
- ✅ GitHub Pages deployment

### AI Enhancement Features
- 🤖 Article summarization (Gemini/OpenAI/Anthropic)
- 📊 Trend analysis
- 🔍 Relevance scoring
- 💡 Key insights extraction
- 🆓 **Gemini 우선 사용** (무료 할당량 활용)

### Data Sources
- 📚 arXiv (cs.CL, cs.AI, cs.LG)
- 🤗 Hugging Face Blog
- 🧠 Google AI Blog
- 🐙 GitHub Trending
- 📡 RSS feeds from major AI blogs

## Customization

### HTML Template
Edit `templates/simple_newsletter.html` to customize the newsletter design.

### RSS Configuration
Modify `src/rss_generator.py` to change RSS feed structure.

### Scraping Logic
Update `src/news_scraper.py` to add new source types or modify categorization logic.

## Troubleshooting

### Common Issues

1. **No articles collected**:
   - Check internet connection
   - Verify RSS feed URLs in `config/sources.json`
   - Check rate limiting

2. **GitHub Actions failing**:
   - Check repository secrets
   - Verify GitHub Pages is enabled
   - Check workflow logs

3. **AI enhancement not working**:
   - Verify API keys are set
   - Check API quotas/limits
   - Review error logs

### Debug Mode

```bash
# Run with verbose logging
python run_daily_news.py --verbose

# Test specific components
export DEBUG=true
python src/news_scraper.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## API 키 설정 가이드

### 🆓 Google Gemini API (추천)
1. [Google AI Studio](https://makersuite.google.com/app/apikey) 방문
2. "Create API Key" 클릭
3. 생성된 키를 `GEMINI_API_KEY`로 설정
4. **장점**: 월 1,500회 무료 요청, 빠른 응답 속도

### 💰 OpenAI API
1. [OpenAI Platform](https://platform.openai.com/api-keys) 방문
2. "Create new secret key" 클릭
3. 생성된 키를 `OPENAI_API_KEY`로 설정
4. **참고**: 유료 서비스, 크레딧 구매 필요

### 🤖 Anthropic Claude API
1. [Anthropic Console](https://console.anthropic.com/) 방문
2. API Keys 섹션에서 키 생성
3. 생성된 키를 `ANTHROPIC_API_KEY`로 설정
4. **참고**: 유료 서비스, 크레딧 구매 필요

## License

MIT License - feel free to use and modify.

---

*Generated by Context Engineering News Bot - Making AI research accessible daily! 🤖*

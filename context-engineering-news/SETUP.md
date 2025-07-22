# Context Engineering Daily News - Setup Guide

## Quick Start

1. **Fork this repository**
2. **Enable GitHub Pages**:
   - Go to Settings > Pages
   - Source: GitHub Actions
3. **Configure secrets** (for enhanced features):
   - `GEMINI_API_KEY` - 🆓 **완전 무료** Google Gemini AI (추천!)
     - 무료 할당량: 월 1,500회 요청
     - AI 요약, 트렌드 분석 기능 활성화
   - `GH_PAT` - GitHub Personal Access Token (선택사항)
     - 더 높은 GitHub API 요청 한도
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
# FREE AI Enhancement - Gemini only! 🆓
export GEMINI_API_KEY="your-gemini-key"    # 100% FREE - 1,500 requests/month!

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

### AI Enhancement Features (🆓 100% FREE!)
- 🤖 Article summarization (Google Gemini)
- 📊 Trend analysis and insights
- 🔍 Smart relevance scoring  
- 💡 Key insights extraction
- 🚀 **완전 무료** - 월 1,500회 요청 한도

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

## 🆓 무료 AI API 설정 가이드

### Google Gemini API (100% 무료!)
1. [Google AI Studio](https://makersuite.google.com/app/apikey) 방문
2. Google 계정으로 로그인
3. "Create API Key" 클릭
4. 생성된 키를 복사
5. Repository Settings > Secrets에서 `GEMINI_API_KEY`로 설정

**🎆 장점:**
- ✅ **완전 무료**: 월 1,500회 요청
- ⚡ **빠른 응답**: Gemini 1.5 Flash 모델
- 🧠 **고품질**: Google의 최신 AI 기술
- 💳 **신용카드 불필요**: API 키만 있으면 OK!

> 💡 **팁**: 월 1,500회로 매일 50개 기사 요약 가능!

## License

MIT License - feel free to use and modify.

---

*Generated by Context Engineering News Bot - Making AI research accessible daily! 🤖*

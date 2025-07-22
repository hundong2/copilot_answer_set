#!/usr/bin/env python3
"""
샘플 한글 번역 데이터를 추가하여 즉시 확인할 수 있도록 하는 스크립트
"""

import json
import shutil
import os

def add_sample_translations():
    """샘플 한글 번역 데이터 추가"""
    print("🇰🇷 샘플 한글 번역 데이터 추가 중...")
    
    try:
        with open('data/daily_news.json', 'r', encoding='utf-8') as f:
            news_data = json.load(f)
    except FileNotFoundError:
        print("❌ data/daily_news.json 파일을 찾을 수 없습니다.")
        return False
    
    # 샘플 번역 데이터 (첫 5개 기사에 샘플 번역 추가)
    sample_translations = [
        {
            "title": "DeepWriter: A Fact-Grounded Multimodal Writing Assistant Based On Offline Knowledge Base",
            "korean_title": "팩트 기반 멀티모달 글쓰기 어시스튴트 DeepWriter: 오프라인 지식 베이스 활용",
            "korean_summary": "이 연구는 금융, 의료, 법률 등 전문 도메인에서 사용할 수 있는 오프라인 지식 베이스 기반의 멀티모달 글쓰기 도우미를 제안합니다. DeepWriter는 RAG 기술과 ICL 방식을 결합하여 사실 기반의 정확한 문서 생성을 가능하게 합니다.",
            "korean_keywords": ["대형 언어모델", "먀티모달", "지식베이스", "RAG", "글쓰기 도우미"]
        },
        {
            "title": "Retention analysis of edited knowledge after fine-tuning",
            "korean_title": "파인튀닝 후 편집된 지식의 유지 분석",
            "korean_summary": "대형 언어 모델에 저장된 방대한 지식을 업데이트하고 팩트 오류를 수정하는 모델 편집 기법에 대한 연구입니다. 파인튀닝 후 편집된 지식이 얼마나 잘 유지되는지 분석하여 모델 성능 향상 방안을 제시합니다.",
            "korean_keywords": ["파인튀닝", "모델 편집", "지식 유지", "언어모델", "성능 분석"]
        },
        {
            "title": "Open-Source LLMs Collaboration Beats Closed-Source LLMs: A Scalable Multi-Agent System",
            "korean_title": "오픈소스 대형 언어모델 협력으로 비공개 모델 능가: 확장 가능한 멀티 에이전트 시스템",
            "korean_summary": "여러 오픈소스 대형 언어모델을 협력시켜 비공개 모델을 능가할 수 있는지를 탐구한 연구입니다. SMACS라는 확장 가능한 멀티 에이전트 시스템을 제안하여 GPT와 같은 비공개 모델에 준하는 성능을 달성합니다.",
            "korean_keywords": ["오픈소스", "멀티에이전트", "언어모델 협력", "GPT 대안", "확장성"]
        },
        {
            "title": "Language Models Change Facts Based on the Way You Talk",
            "korean_title": "언어 모델이 대화 방식에 따라 사실을 다르게 인식하는 현상",
            "korean_summary": "대형 언어 모델이 사용자의 언어 사용 패턴과 대화 방식에 따라 다른 사실 정보를 제공하는 현상을 분석한 연구입니다. 이는 AI 모델의 신뢰성과 공정성에 중요한 시사점을 제공합니다.",
            "korean_keywords": ["언어모델 편향", "대화 패턴", "AI 신뢰성", "사실 인식", "언어 영향"]
        },
        {
            "title": "HuggingGraph: Understanding the Supply Chain of LLM Ecosystem",
            "korean_title": "HuggingGraph: 대형 언어모델 생태계의 공급망 이해",
            "korean_summary": "대형 언어 모델 생태계의 복잡한 공급망을 분석하고 이해하기 위한 HuggingGraph 플랫폼을 소개합니다. 번역, 요약, 질의응답, 콘텐츠 생성 등 다양한 NLP 작업에서의 모델 활용 현황을 체계적으로 분석합니다.",
            "korean_keywords": ["LLM 생태계", "공급망 분석", "NLP 작업", "모델 활용", "요약 시스템"]
        }
    ]
    
    # 샘플 번역 적용
    items = news_data['items']
    translated_count = 0
    
    for translation in sample_translations:
        for item in items:
            if item['title'] == translation['title']:
                item.update({
                    'korean_title': translation['korean_title'],
                    'korean_summary': translation['korean_summary'],
                    'korean_keywords': translation['korean_keywords']
                })
                translated_count += 1
                break
    
    # 결과 저장
    try:
        with open('data/daily_news.json', 'w', encoding='utf-8') as f:
            json.dump(news_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ {translated_count}개 기사에 샘플 한글 번역 추가 완료")
        return True
        
    except Exception as e:
        print(f"❌ 파일 저장 실패: {e}")
        return False

def regenerate_html():
    """번역된 데이터로 HTML 재생성"""
    print("\n🏗️  HTML 뉴스레터 재생성...")
    
    try:
        from src.html_generator import NewsletterGenerator
        
        generator = NewsletterGenerator()
        html_content = generator.generate_html(
            data_file="data/daily_news.json",
            template_file="templates/simple_newsletter.html",
            output_file="docs/index.html"
        )
        
        # 루트 docs에도 복사
        shutil.copy("docs/index.html", "../docs/index.html")
        
        print("✅ HTML 뉴스레터 재생성 완료")
        print("📖 docs/index.html 파일에서 한글 번역 확인 가능")
        return True
        
    except Exception as e:
        print(f"❌ HTML 생성 실패: {e}")
        return False

def main():
    print("🇰🇷 샘플 한글 번역 데이터 추가")
    print("=" * 40)
    
    if add_sample_translations():
        regenerate_html()
        print("\n🎉 완료! 이제 다음을 확인하세요:")
        print("  1. docs/index.html 파일에서 한글 번역")
        print("  2. 버전 조절에서 한글과 영문 동시 노출")
        print("  3. 한글 키워드와 요약")
        
        print("\n🔄 전체 데이터 번역을 원한다면:")
        print("  GEMINI_API_KEY 설정 후 python translate_existing.py 실행")
    else:
        print("❌ 샘플 번역 추가 실패")

if __name__ == "__main__":
    main()

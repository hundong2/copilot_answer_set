#!/usr/bin/env python3
"""
기존 뉴스 데이터에 한글 번역 추가하는 스크립트
"""

import json
import os
from src.ai_summarizer import AISummarizer
import time

def translate_existing_news():
    """기존 뉴스 데이터에 한글 번역 추가"""
    print("🔄 기존 뉴스 데이터 한글 번역 시작...")
    
    # Gemini API 키 확인
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
        print("🔧 설정 방법:")
        print("   export GEMINI_API_KEY='your-api-key'")
        return False
    
    # AI Summarizer 초기화
    summarizer = AISummarizer()
    if not summarizer.is_available():
        print("❌ Gemini AI 초기화 실패")
        return False
    
    print("✅ Gemini AI 초기화 성공")
    
    # 기존 데이터 로드
    try:
        with open('data/daily_news.json', 'r', encoding='utf-8') as f:
            news_data = json.load(f)
    except FileNotFoundError:
        print("❌ data/daily_news.json 파일을 찾을 수 없습니다.")
        return False
    
    items = news_data['items']
    print(f"📊 총 {len(items)}개 기사 발견")
    
    # 번역이 필요한 아이템 확인
    needs_translation = [item for item in items if not item.get('korean_title')]
    print(f"🔤 번역 필요: {len(needs_translation)}개 기사")
    
    if not needs_translation:
        print("✅ 모든 기사가 이미 번역되어 있습니다.")
        return True
    
    # 번역 작업
    translated_count = 0
    failed_count = 0
    
    for i, item in enumerate(needs_translation):
        print(f"\n🌐 [{i+1}/{len(needs_translation)}] 번역 중: {item['title'][:50]}...")
        
        try:
            # 한글 번역 및 요약 생성
            korean_data = summarizer.translate_and_summarize_korean(
                item['title'],
                item['description'],
                item.get('content', '')
            )
            
            if korean_data and korean_data.get('korean_title'):
                # 원본 데이터에 번역 정보 추가
                for original_item in items:
                    if original_item['url'] == item['url']:  # URL로 매칭
                        original_item.update(korean_data)
                        break
                
                translated_count += 1
                print(f"  ✅ 성공: {korean_data['korean_title']}")
                print(f"  📝 요약: {korean_data['korean_summary'][:100]}...")
            else:
                failed_count += 1
                print("  ❌ 번역 실패")
            
            # API 제한을 위한 대기
            time.sleep(1)
            
        except Exception as e:
            failed_count += 1
            print(f"  ❌ 오류: {e}")
            time.sleep(2)  # 오류 시 더 오래 대기
    
    # 결과 저장
    news_data['items'] = items
    news_data['translation_updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        with open('data/daily_news_korean.json', 'w', encoding='utf-8') as f:
            json.dump(news_data, f, indent=2, ensure_ascii=False)
        
        # 원본도 업데이트
        with open('data/daily_news.json', 'w', encoding='utf-8') as f:
            json.dump(news_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n🎉 번역 완료!")
        print(f"  ✅ 성공: {translated_count}개")
        print(f"  ❌ 실패: {failed_count}개")
        print(f"  📁 저장: data/daily_news.json, data/daily_news_korean.json")
        
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
        import shutil
        shutil.copy("context-engineering-news/docs/index.html", "../docs/index.html")
        
        print("✅ HTML 뉴스레터 재생성 완료")
        return True
        
    except Exception as e:
        print(f"❌ HTML 생성 실패: {e}")
        return False

def main():
    """메인 함수"""
    print("🇰🇷 Context Engineering Daily News - 한글 번역 도구")
    print("=" * 50)
    
    # 1. 번역 작업
    if not translate_existing_news():
        print("\n❌ 번역 작업 실패")
        return False
    
    # 2. HTML 재생성
    if not regenerate_html():
        print("\n⚠️ HTML 재생성 실패, 하지만 번역 데이터는 저장됨")
    
    print("\n🎯 다음 단계:")
    print("  1. docs/index.html에서 번역된 뉴스레터 확인")
    print("  2. GitHub에 커밋하여 사이트 업데이트")
    print("  3. https://hundong2.github.io/copilot_answer_set/ 에서 확인")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

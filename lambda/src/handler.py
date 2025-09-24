import json
import os
import logging
import traceback
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Set
import requests
import boto3
from playwright.sync_api import sync_playwright

# 로깅 설정
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 환경 변수
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')
TIMEZONE = os.environ.get('TIMEZONE', 'Asia/Seoul')
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME', 'hometax-banner-history')

class BannerHistoryManager:
    """배너 기록 관리 클래스"""

    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(DYNAMODB_TABLE_NAME)

    def generate_banner_hash(self, banner_data: Dict[str, Any]) -> str:
        """배너 데이터로부터 해시 생성"""
        # src와 alt 텍스트를 결합하여 해시 생성
        content = f"{banner_data.get('src', '')}{banner_data.get('alt', '')}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def get_existing_banners(self) -> Set[str]:
        """기존에 저장된 배너 해시들 조회"""
        try:
            response = self.table.scan(
                ProjectionExpression='banner_hash'
            )
            return {item['banner_hash'] for item in response['Items']}
        except Exception as e:
            logger.error(f"기존 배너 조회 중 오류: {str(e)}")
            return set()

    def save_new_banners(self, new_banners: List[Dict[str, Any]]) -> bool:
        """새로운 배너들을 DynamoDB에 저장"""
        try:
            current_time = datetime.now().isoformat()
            ttl_time = int((datetime.now() + timedelta(days=90)).timestamp())

            with self.table.batch_writer() as batch:
                for banner in new_banners:
                    banner_hash = self.generate_banner_hash(banner)
                    batch.put_item(Item={
                        'banner_hash': banner_hash,
                        'first_seen': current_time,
                        'src': banner.get('src', ''),
                        'alt': banner.get('alt', ''),
                        'title': banner.get('title', ''),
                        'className': banner.get('className', ''),
                        'ttl': ttl_time
                    })

            logger.info(f"{len(new_banners)}개의 새로운 배너를 DynamoDB에 저장했습니다.")
            return True

        except Exception as e:
            logger.error(f"새로운 배너 저장 중 오류: {str(e)}")
            logger.error(traceback.format_exc())
            return False

    def filter_new_banners(self, all_banners: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """전체 배너 목록에서 새로운 배너만 필터링"""
        existing_hashes = self.get_existing_banners()
        new_banners = []

        for banner in all_banners:
            banner_hash = self.generate_banner_hash(banner)
            if banner_hash not in existing_hashes:
                new_banners.append(banner)

        logger.info(f"전체 {len(all_banners)}개 배너 중 {len(new_banners)}개가 새로운 배너입니다.")
        return new_banners

class HomeTaxScraper:
    """홈택스 메인 페이지 배너 스크래핑 클래스"""
    
    def __init__(self):
        self.target_url = "https://hometax.go.kr"
        self.target_element_id = "mf_txppWframe_grpImgGrp"
    
    def scrape_banner_images(self) -> List[Dict[str, Any]]:
        """
        홈택스 메인 페이지에서 배너 이미지와 alt 텍스트를 추출합니다.
        
        Returns:
            List[Dict]: 이미지 정보 리스트
        """
        try:
            with sync_playwright() as p:
                # 브라우저 실행 옵션 설정
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor'
                    ]
                )
                
                page = browser.new_page()
                
                # 페이지 로드 타임아웃 설정
                page.set_default_timeout(30000)  # 30초
                
                logger.info(f"홈택스 페이지 로딩 중: {self.target_url}")
                page.goto(self.target_url)
                
                # 페이지가 완전히 로드될 때까지 대기
                page.wait_for_load_state('networkidle')
                
                # JavaScript를 실행하여 이미지 정보 추출
                result = page.evaluate("""
                () => {
                    // 대상 요소 찾기
                    const targetElement = document.getElementById('mf_txppWframe_grpImgGrp');
                    
                    if (!targetElement) {
                        return {
                            error: 'Target element not found',
                            elementFound: false
                        };
                    }
                    
                    // li 요소들 찾기
                    const liElements = targetElement.querySelectorAll('li');
                    
                    if (liElements.length === 0) {
                        return {
                            error: 'No li elements found',
                            elementFound: true,
                            liCount: 0
                        };
                    }
                    
                    // 이미지 정보 추출
                    const results = [];
                    
                    liElements.forEach((li, index) => {
                        const images = li.querySelectorAll('img');
                        
                        images.forEach((img, imgIndex) => {
                            results.push({
                                liIndex: index,
                                imageIndex: imgIndex,
                                src: img.src || 'No src attribute',
                                alt: img.alt || 'No alt attribute',
                                title: img.title || 'No title attribute',
                                className: img.className || 'No class'
                            });
                        });
                    });
                    
                    return {
                        elementFound: true,
                        liCount: liElements.length,
                        totalImages: results.length,
                        images: results,
                        timestamp: new Date().toISOString()
                    };
                }
                """)
                
                browser.close()
                
                if result.get('error'):
                    logger.error(f"스크래핑 오류: {result['error']}")
                    return []
                
                logger.info(f"성공적으로 {result['totalImages']}개의 이미지를 추출했습니다.")
                return result['images']
                
        except Exception as e:
            logger.error(f"스크래핑 중 오류 발생: {str(e)}")
            logger.error(traceback.format_exc())
            raise

class SlackNotifier:
    """Slack 알림 전송 클래스"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send_scraping_result(self, images: List[Dict[str, Any]], success: bool = True, is_new_only: bool = False) -> bool:
        """
        스크래핑 결과를 Slack으로 전송합니다.

        Args:
            images: 스크래핑된 이미지 정보
            success: 스크래핑 성공 여부
            is_new_only: 새로운 배너만 전송하는 경우인지 여부

        Returns:
            bool: 전송 성공 여부
        """
        try:
            # KST 시간 계산
            kst = timezone(timedelta(hours=9))
            current_time = datetime.now(kst).strftime('%Y-%m-%d %H:%M:%S KST')
            
            if not success or not images:
                # 실패하거나 새로운 배너가 없는 경우
                if not success:
                    status_text = "🚨 홈택스 배너 스크래핑 실패"
                    header_text = "🚨 홈택스 배너 스크래핑 실패"
                    detail_text = f"*실행 시간:* {current_time}\n*상태:* 실패\n*이미지 수:* 0개"
                else:
                    # 새로운 배너가 없는 경우 - 알림을 보내지 않음
                    if is_new_only:
                        logger.info("새로운 배너가 없어 Slack 알림을 생략합니다.")
                        return True
                    status_text = "ℹ️ 홈택스 배너 - 새로운 배너 없음"
                    header_text = "ℹ️ 홈택스 배너 확인 완료"
                    detail_text = f"*실행 시간:* {current_time}\n*상태:* 성공\n*새로운 배너:* 0개"

                message = {
                    "text": status_text,
                    "blocks": [
                        {
                            "type": "header",
                            "text": {
                                "type": "plain_text",
                                "text": header_text
                            }
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": detail_text
                            }
                        }
                    ]
                }
            else:
                # 성공한 경우
                image_blocks = []
                
                # 헤더 - 새로운 배너인 경우 다른 제목 사용
                header_title = "🆕 홈택스 새로운 배너 발견!" if is_new_only else "📊 홈택스 배너 스크래핑 결과"
                image_blocks.append({
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": header_title
                    }
                })
                
                # 요약 정보 - 새로운 배너인 경우 다른 메시지 사용
                summary_text = f"*실행 시간:* {current_time}\n*상태:* 성공\n*{'새로운' if is_new_only else '추출된'} 이미지 수:* {len(images)}개"
                image_blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": summary_text
                    }
                })
                
                # 구분선
                image_blocks.append({"type": "divider"})
                
                # 각 이미지 정보
                unique_images = {}
                for img in images:
                    # 중복 제거 (같은 src를 가진 이미지)
                    src = img.get('src', '')
                    if src and src not in unique_images:
                        unique_images[src] = img
                
                for i, (src, img) in enumerate(unique_images.items(), 1):
                    alt_text = img.get('alt', 'No alt attribute')
                    
                    # alt 텍스트가 너무 길면 줄임
                    if len(alt_text) > 200:
                        alt_text = alt_text[:200] + "..."
                    
                    banner_prefix = f"*{'🆕 새로운 배너' if is_new_only else '배너'} {i}*"
                    image_blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"{banner_prefix}\n*Alt 텍스트:* {alt_text}\n*이미지 URL:* {src}"
                        }
                    })
                    
                    # 블록 수 제한 (Slack API 제한)
                    if len(image_blocks) >= 48:  # 최대 50블록 - 여유분 2개
                        image_blocks.append({
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"_... 그 외 {len(unique_images) - i}개 이미지 생략_"
                            }
                        })
                        break
                
                message_text = f"홈택스 {'새로운' if is_new_only else ''} 배너 {'발견' if is_new_only else '스크래핑 완료'} - {len(unique_images)}개 이미지 {'추가' if is_new_only else '추출'}"
                message = {
                    "text": message_text,
                    "blocks": image_blocks
                }
            
            # Slack으로 전송
            response = requests.post(
                self.webhook_url,
                json=message,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info("Slack 알림 전송 성공")
                return True
            else:
                logger.error(f"Slack 알림 전송 실패: {response.status_code}, {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Slack 알림 전송 중 오류: {str(e)}")
            logger.error(traceback.format_exc())
            return False

def lambda_handler(event, context):
    """
    Lambda 함수 핸들러
    
    Args:
        event: Lambda 이벤트
        context: Lambda 컨텍스트
    
    Returns:
        dict: 실행 결과
    """
    logger.info("홈택스 스크래핑 Lambda 함수 시작")
    logger.info(f"이벤트: {json.dumps(event, ensure_ascii=False)}")
    
    start_time = datetime.now()
    
    try:
        # Slack Webhook URL 확인
        if not SLACK_WEBHOOK_URL:
            raise ValueError("SLACK_WEBHOOK_URL 환경변수가 설정되지 않았습니다.")
        
        # 스크래핑 실행
        scraper = HomeTaxScraper()
        all_images = scraper.scrape_banner_images()

        # 배너 히스토리 관리자 초기화
        history_manager = BannerHistoryManager()

        # 새로운 배너만 필터링
        new_images = history_manager.filter_new_banners(all_images)

        # 새로운 배너가 있으면 DynamoDB에 저장
        if new_images:
            history_manager.save_new_banners(new_images)

        # Slack 알림 전송 - 새로운 배너가 있을 때만 전송
        notifier = SlackNotifier(SLACK_WEBHOOK_URL)
        notification_sent = notifier.send_scraping_result(new_images, success=bool(all_images), is_new_only=True)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        result = {
            'statusCode': 200,
            'body': json.dumps({
                'message': '홈택스 배너 차등 스크래핑 완료',
                'total_images_count': len(all_images),
                'new_images_count': len(new_images),
                'unique_total_count': len(set(img.get('src') for img in all_images if img.get('src'))),
                'unique_new_count': len(set(img.get('src') for img in new_images if img.get('src'))),
                'notification_sent': notification_sent,
                'execution_time': f"{duration:.2f}초",
                'timestamp': datetime.now().isoformat()
            }, ensure_ascii=False)
        }
        
        logger.info(f"실행 완료 - 전체 {len(all_images)}개 이미지 중 {len(new_images)}개 새로운 배너 발견, 소요시간: {duration:.2f}초")
        return result
        
    except Exception as e:
        logger.error(f"Lambda 함수 실행 중 오류: {str(e)}")
        logger.error(traceback.format_exc())
        
        # 실패 알림도 보내기
        try:
            if SLACK_WEBHOOK_URL:
                notifier = SlackNotifier(SLACK_WEBHOOK_URL)
                notifier.send_scraping_result([], success=False, is_new_only=False)
        except:
            logger.error("실패 알림 전송도 실패했습니다.")
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': '홈택스 스크래핑 실패',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, ensure_ascii=False)
        }

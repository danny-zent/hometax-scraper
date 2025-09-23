#!/bin/bash

# HomeTax Scraper 로컬 테스트 스크립트
set -e

# 색상 설정
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 HomeTax Scraper 로컬 테스트${NC}"
echo "=================================="

# 환경 변수 확인
if [ -z "$SLACK_WEBHOOK_URL" ]; then
    echo -e "${RED}❌ 오류: SLACK_WEBHOOK_URL 환경변수가 설정되지 않았습니다.${NC}"
    echo "다음 명령으로 설정하세요:"
    echo "export SLACK_WEBHOOK_URL='https://hooks.slack.com/services/YOUR/WEBHOOK/URL'"
    exit 1
fi

echo -e "${GREEN}✅ SLACK_WEBHOOK_URL 환경변수 확인 완료${NC}"

# Lambda 디렉토리로 이동
cd lambda

# 가상환경 생성 (없는 경우)
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Python 가상환경 생성 중...${NC}"
    python3 -m venv venv
fi

# 가상환경 활성화
source venv/bin/activate

# 의존성 설치
echo -e "${YELLOW}📦 Python 의존성 설치 중...${NC}"
pip install -r requirements.txt

# Playwright 브라우저 설치
echo -e "${YELLOW}🌐 Playwright 브라우저 설치 중...${NC}"
playwright install chromium

# 로컬 테스트 실행
echo -e "${YELLOW}🧪 테스트 실행 중...${NC}"
cd src
python3 -c "
import sys
import os
sys.path.append('.')
from handler import lambda_handler

# 테스트 이벤트
event = {'source': 'local-test'}
context = None

try:
    result = lambda_handler(event, context)
    print('\\n' + '='*50)
    print('테스트 결과:', result)
    print('='*50)
except Exception as e:
    print('테스트 실패:', str(e))
    sys.exit(1)
"

echo -e "${GREEN}✅ 로컬 테스트 완료!${NC}"

#!/bin/bash

# HomeTax Scraper 배포 스크립트
set -e

# 색상 설정
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 HomeTax Scraper 배포 시작${NC}"
echo "=================================="

# 환경 변수 확인
if [ -z "$SLACK_WEBHOOK_URL" ]; then
    echo -e "${RED}❌ 오류: SLACK_WEBHOOK_URL 환경변수가 설정되지 않았습니다.${NC}"
    echo "다음 명령으로 설정하세요:"
    echo "export SLACK_WEBHOOK_URL='https://hooks.slack.com/services/YOUR/WEBHOOK/URL'"
    exit 1
fi

echo -e "${GREEN}✅ SLACK_WEBHOOK_URL 환경변수 확인 완료${NC}"

# CDK 디렉토리로 이동
cd cdk

# 의존성 설치
echo -e "${YELLOW}📦 CDK 의존성 설치 중...${NC}"
npm install

# CDK 부트스트랩 (최초 1회)
echo -e "${YELLOW}🔧 CDK 부트스트랩 확인 중...${NC}"
npx cdk bootstrap --require-approval never

# CDK 배포
echo -e "${YELLOW}🚀 CDK 배포 중...${NC}"
npx cdk deploy --require-approval never

echo -e "${GREEN}✅ 배포 완료!${NC}"
echo ""
echo "배포된 리소스:"
echo "- Lambda 함수: hometax-scraper"
echo "- EventBridge 스케줄: 매일 오전 8시 (KST)"
echo "- CloudWatch 로그: /aws/lambda/hometax-scraper"
echo ""
echo "수동 테스트:"
echo "aws lambda invoke --function-name hometax-scraper --payload '{}' response.json"
echo ""
echo "로그 확인:"
echo "aws logs tail /aws/lambda/hometax-scraper --follow"

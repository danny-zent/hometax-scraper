#!/bin/bash

# HomeTax Scraper 유틸리티 스크립트

# 색상 설정
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

FUNCTION_NAME="hometax-scraper"
LOG_GROUP="/aws/lambda/hometax-scraper"

case "$1" in
    "logs")
        echo -e "${BLUE}📋 Lambda 로그 확인 중...${NC}"
        aws logs tail $LOG_GROUP --follow
        ;;
    "test")
        echo -e "${YELLOW}🧪 Lambda 함수 수동 실행 중...${NC}"
        aws lambda invoke \
            --function-name $FUNCTION_NAME \
            --payload '{"source": "manual-test"}' \
            response.json
        echo -e "${GREEN}✅ 실행 완료. 응답:${NC}"
        cat response.json
        echo ""
        ;;
    "status")
        echo -e "${BLUE}📊 Lambda 함수 상태 확인${NC}"
        aws lambda get-function --function-name $FUNCTION_NAME --query 'Configuration.[FunctionName,State,LastModified,Runtime,MemorySize,Timeout]' --output table
        ;;
    "schedule")
        echo -e "${BLUE}📅 스케줄 상태 확인${NC}"
        aws events describe-rule --name hometax-scraper-daily-schedule --query '[Name,ScheduleExpression,State,Description]' --output table
        ;;
    "metrics")
        echo -e "${BLUE}📈 CloudWatch 메트릭 확인 (최근 24시간)${NC}"
        START_TIME=$(date -d '1 day ago' --iso-8601)
        END_TIME=$(date --iso-8601)
        
        echo "실행 횟수:"
        aws cloudwatch get-metric-statistics \
            --namespace AWS/Lambda \
            --metric-name Invocations \
            --dimensions Name=FunctionName,Value=$FUNCTION_NAME \
            --start-time $START_TIME \
            --end-time $END_TIME \
            --period 86400 \
            --statistics Sum \
            --query 'Datapoints[0].Sum' \
            --output text
        
        echo "에러 횟수:"
        aws cloudwatch get-metric-statistics \
            --namespace AWS/Lambda \
            --metric-name Errors \
            --dimensions Name=FunctionName,Value=$FUNCTION_NAME \
            --start-time $START_TIME \
            --end-time $END_TIME \
            --period 86400 \
            --statistics Sum \
            --query 'Datapoints[0].Sum' \
            --output text
        ;;
    "destroy")
        echo -e "${RED}🗑️  스택 삭제 중... (주의: 모든 리소스가 삭제됩니다)${NC}"
        read -p "정말로 삭제하시겠습니까? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            cd cdk
            npx cdk destroy
        else
            echo "삭제가 취소되었습니다."
        fi
        ;;
    "help"|*)
        echo -e "${BLUE}HomeTax Scraper 유틸리티${NC}"
        echo "=================================="
        echo "사용법: $0 <command>"
        echo ""
        echo "명령어:"
        echo "  logs      - Lambda 함수 로그 실시간 확인"
        echo "  test      - Lambda 함수 수동 실행"
        echo "  status    - Lambda 함수 상태 확인"
        echo "  schedule  - EventBridge 스케줄 상태 확인"
        echo "  metrics   - CloudWatch 메트릭 확인 (최근 24시간)"
        echo "  destroy   - 모든 리소스 삭제"
        echo "  help      - 이 도움말 표시"
        echo ""
        echo "예제:"
        echo "  $0 logs     # 로그 실시간 확인"
        echo "  $0 test     # 수동 테스트 실행"
        echo "  $0 status   # 함수 상태 확인"
        ;;
esac

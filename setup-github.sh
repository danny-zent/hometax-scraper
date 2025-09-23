#!/bin/bash

# GitHub Repository 생성 및 업로드 스크립트
set -e

# 색상 설정
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

REPO_NAME="hometax-scraper"
GITHUB_USERNAME="danny-zent"
REPO_URL="https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

echo -e "${BLUE}🚀 GitHub Repository 설정 시작${NC}"
echo "Repository: ${REPO_URL}"
echo "=================================="

# 1. GitHub에 수동으로 repository 생성하라고 안내
echo -e "${YELLOW}📋 Step 1: GitHub에서 새 Repository 생성${NC}"
echo ""
echo "다음 링크에서 새 repository를 생성해주세요:"
echo "https://github.com/new"
echo ""
echo "설정값:"
echo "  - Repository name: ${REPO_NAME}"
echo "  - Description: HomeTax banner scraper with AWS Lambda and CDK - 홈택스 배너 스크래핑 AWS Lambda 함수"
echo "  - Public repository"
echo "  - ❌ Add a README file (체크 해제)"
echo "  - ❌ Add .gitignore (체크 해제)"
echo "  - ❌ Choose a license (체크 해제)"
echo ""
read -p "Repository 생성이 완료되면 Enter를 눌러주세요..."

# 2. Git 초기화
echo -e "${YELLOW}📋 Step 2: Git 초기화${NC}"
if [ ! -d ".git" ]; then
    git init
    echo -e "${GREEN}✅ Git 초기화 완료${NC}"
else
    echo -e "${YELLOW}⚠️ Git이 이미 초기화되어 있습니다${NC}"
fi

# 3. Git 설정 확인
echo -e "${YELLOW}📋 Step 3: Git 설정 확인${NC}"
if ! git config user.name > /dev/null 2>&1; then
    echo "Git 사용자 이름을 설정해주세요:"
    read -p "Enter your name: " git_name
    git config user.name "$git_name"
fi

if ! git config user.email > /dev/null 2>&1; then
    echo "Git 이메일을 설정해주세요:"
    read -p "Enter your email: " git_email
    git config user.email "$git_email"
fi

echo "현재 Git 설정:"
echo "  Name: $(git config user.name)"
echo "  Email: $(git config user.email)"

# 4. 파일 추가
echo -e "${YELLOW}📋 Step 4: 파일 스테이징${NC}"
git add .
echo -e "${GREEN}✅ 모든 파일이 스테이징되었습니다${NC}"

# 5. 첫 번째 커밋
echo -e "${YELLOW}📋 Step 5: 첫 번째 커밋${NC}"
git commit -m "🚀 Initial commit: HomeTax scraper with AWS Lambda and CDK

Features:
- AWS CDK infrastructure (TypeScript)
- Lambda function with Docker container (Python)
- Playwright-based web scraping
- Daily schedule with EventBridge
- Slack notifications
- Comprehensive monitoring and logging

Components:
- CDK Stack: Lambda, EventBridge, CloudWatch
- Lambda: HomeTax banner scraping with Playwright
- Docker: Optimized container with Chromium
- Scripts: Deploy, test, and utility scripts"

echo -e "${GREEN}✅ 첫 번째 커밋 완료${NC}"

# 6. 브랜치 이름 설정
echo -e "${YELLOW}📋 Step 6: 기본 브랜치 설정${NC}"
git branch -M main
echo -e "${GREEN}✅ 브랜치 이름을 main으로 설정했습니다${NC}"

# 7. 원격 저장소 추가
echo -e "${YELLOW}📋 Step 7: 원격 저장소 추가${NC}"
if git remote get-url origin > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️ 원격 저장소가 이미 설정되어 있습니다. 제거하고 새로 추가합니다.${NC}"
    git remote remove origin
fi

git remote add origin $REPO_URL
echo -e "${GREEN}✅ 원격 저장소 추가 완료: ${REPO_URL}${NC}"

# 8. Push
echo -e "${YELLOW}📋 Step 8: GitHub에 업로드${NC}"
echo "GitHub 인증이 필요합니다. Personal Access Token을 사용해주세요."
echo ""
echo "Personal Access Token 생성 방법:"
echo "1. https://github.com/settings/tokens 이동"
echo "2. 'Generate new token' → 'Generate new token (classic)'"
echo "3. 'repo' 권한 체크"
echo "4. 생성된 토큰을 비밀번호 대신 사용"
echo ""
read -p "준비되면 Enter를 눌러 push를 시작합니다..."

if git push -u origin main; then
    echo -e "${GREEN}🎉 GitHub 업로드 완료!${NC}"
    echo ""
    echo "Repository URL: https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
    echo ""
    echo "다음 단계:"
    echo "1. Repository 페이지에서 README 확인"
    echo "2. GitHub Actions 설정 (선택사항)"
    echo "3. Issues/Projects 활성화 (선택사항)"
else
    echo -e "${RED}❌ Push 실패${NC}"
    echo ""
    echo "해결 방법:"
    echo "1. GitHub 인증 정보 확인"
    echo "2. Repository가 올바르게 생성되었는지 확인"
    echo "3. 네트워크 연결 확인"
    echo ""
    echo "수동으로 다시 시도:"
    echo "git push -u origin main"
fi

echo ""
echo "=================================="
echo -e "${BLUE}GitHub 설정 완료!${NC}"

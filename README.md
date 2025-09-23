# HomeTax Scraper 🚀

[![CI/CD Pipeline](https://github.com/danny-zent/hometax-scraper/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/danny-zent/hometax-scraper/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![AWS CDK](https://img.shields.io/badge/AWS%20CDK-2.100.0-orange.svg)](https://aws.amazon.com/cdk/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0.4-blue.svg)](https://www.typescriptlang.org/)

홈택스 메인 배너 이미지와 alt 값을 매일 오전 8시에 스크래핑하여 Slack으로 전송하는 AWS Lambda 함수입니다.

> 🏢 **Zent 사내 프로젝트**: 홈택스 배너 변경사항 모니터링을 위한 자동화 시스템

## 📁 프로젝트 구조

```
hometax-scraper/
├── cdk/                    # CDK TypeScript 인프라 코드
│   ├── lib/
│   │   └── hometax-scraper-stack.ts  # 메인 스택 정의
│   ├── bin/
│   │   └── app.ts                    # CDK 앱 진입점
│   ├── package.json
│   ├── cdk.json
│   └── tsconfig.json
├── lambda/                 # Lambda Python 코드
│   ├── src/
│   │   └── handler.py              # 메인 Lambda 핸들러
│   ├── Dockerfile                  # Docker 이미지 설정
│   └── requirements.txt            # Python 의존성
├── deploy.sh               # 원클릭 배포 스크립트
├── test-local.sh          # 로컬 테스트 스크립트
├── utils.sh               # 유틸리티 스크립트
└── README.md
```

## 🚀 빠른 시작

### 1. 사전 준비
```bash
# 1. AWS CLI 설치 및 설정
aws configure

# 2. Node.js 설치 (CDK 용)
# https://nodejs.org/

# 3. Python 3.11+ 설치 (테스트용)
python3 --version

# 4. Docker 설치 (Lambda 컨테이너 빌드용)
docker --version
```

### 2. Slack 웹훅 설정
1. Slack 워크스페이스에서 새 앱 생성: https://api.slack.com/apps
2. `Incoming Webhooks` 활성화
3. 채널에 웹훅 URL 생성
4. 환경 변수 설정:
```bash
export SLACK_WEBHOOK_URL="<your-slack-incoming-webhook-url>"
```

### 3. 원클릭 배포
```bash
git clone <repository-url>
cd hometax-scraper
./deploy.sh
```

## 🔧 상세 설정

### 환경 변수
| 이름 | 설명 | 필수 | 기본값 |
|------|------|------|--------|
| `SLACK_WEBHOOK_URL` | Slack 웹훅 URL | ✅ | - |
| `TIMEZONE` | 실행 타임존 | ❌ | Asia/Seoul |

### 스케줄링
- **실행 시간**: 매일 오전 8시 (KST)
- **EventBridge 규칙**: `cron(0 23 * * ? *)` (UTC 23:00 = KST 08:00)
- **자동 재시도**: AWS Lambda 기본 재시도 정책

### Lambda 함수 설정
- **런타임**: Python 3.11 (Docker 컨테이너)
- **메모리**: 1024 MB
- **타임아웃**: 5분
- **아키텍처**: x86_64

## 🧪 테스트

### 로컬 테스트
```bash
# Python 가상환경에서 테스트
./test-local.sh
```

### 배포된 함수 테스트
```bash
# 수동 실행
./utils.sh test

# 로그 실시간 확인
./utils.sh logs
```

## 📊 모니터링 및 관리

### 유틸리티 스크립트 사용
```bash
# 함수 상태 확인
./utils.sh status

# 스케줄 상태 확인
./utils.sh schedule

# 메트릭 확인 (최근 24시간)
./utils.sh metrics

# 로그 실시간 확인
./utils.sh logs

# 수동 테스트 실행
./utils.sh test

# 전체 스택 삭제
./utils.sh destroy
```

### CloudWatch
- **로그 그룹**: `/aws/lambda/hometax-scraper`
- **메트릭**: Invocations, Duration, Errors, Throttles
- **알람**: 오류 발생 시 자동 알림 (옵션)

## 🔍 스크래핑 상세 정보

### 대상 사이트
- **URL**: https://hometax.go.kr
- **타겟 요소**: `#mf_txppWframe_grpImgGrp li img`
- **추출 정보**:
  - 이미지 URL (`src`)
  - 대체 텍스트 (`alt`)
  - 제목 (`title`)
  - CSS 클래스 (`className`)

### Slack 알림 포맷
```
📊 홈택스 배너 스크래핑 결과

실행 시간: 2024-09-23 08:00:00 KST
상태: 성공
추출된 이미지 수: 6개

배너 1
Alt 텍스트: 세금포인트로 다양한 혜택을 누려보세요! ...
이미지 URL: https://hometax.speedycdn.net/img/comm/img/img_main_banner392.png

배너 2
...
```

## 🛠️ 개발 및 커스터마이징

### 코드 수정
1. **Lambda 함수 코드**: `lambda/src/handler.py`
2. **인프라 코드**: `cdk/lib/hometax-scraper-stack.ts`
3. **Docker 설정**: `lambda/Dockerfile`

### 재배포
```bash
# 코드 변경 후
cd cdk
npx cdk deploy
```

### 로컬 개발
```bash
cd lambda
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# 테스트 실행
cd src
python3 -c "from handler import lambda_handler; print(lambda_handler({}, None))"
```

## 📋 문제 해결

### 일반적인 문제들

1. **Playwright 브라우저 설치 실패**
   ```bash
   # 수동 설치
   playwright install chromium
   playwright install-deps
   ```

2. **Slack 웹훅 URL 오류**
   ```bash
   # 환경 변수 확인
   echo $SLACK_WEBHOOK_URL
   
   # 웹훅 테스트
   curl -X POST -H 'Content-type: application/json' \
     --data '{"text":"테스트 메시지"}' \
     $SLACK_WEBHOOK_URL
   ```

3. **CDK 배포 권한 오류**
   ```bash
   # AWS CLI 설정 확인
   aws sts get-caller-identity
   
   # 필요한 권한: CloudFormation, Lambda, EventBridge, IAM, Logs
   ```

### 로그 확인
```bash
# Lambda 로그
aws logs tail /aws/lambda/hometax-scraper --follow

# CDK 배포 로그
cd cdk && npx cdk deploy --verbose
```

## 🔒 보안 고려사항

- Slack Webhook URL은 환경 변수로 관리
- Lambda 함수는 최소 권한 원칙 적용
- CloudWatch Logs는 1주일 보존 후 자동 삭제
- Docker 이미지는 공식 AWS Lambda Python 베이스 사용

## 💰 비용 추정

**월 예상 비용 (Seoul 리전)**:
- Lambda 실행: ~$0.01 (일 1회, 5분 실행)
- CloudWatch Logs: ~$0.50 (로그 저장)
- EventBridge: ~$0.00 (무료 티어)
- **총 예상 비용**: ~$0.51/월

## 🤝 기여

### 개발 참여

1. **Fork** 이 repository
2. **Feature branch** 생성: `git checkout -b feature/amazing-feature`
3. **Commit** 변경사항: `git commit -m 'Add amazing feature'`
4. **Push** to branch: `git push origin feature/amazing-feature`
5. **Pull Request** 생성

### 개발 환경 설정
```bash
# 로컬 개발 환경 설정
git clone https://github.com/danny-zent/hometax-scraper.git
cd hometax-scraper

# Python 가상환경 설정
cd lambda
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# CDK 설정
cd ../cdk
npm install
```

### 코딩 스타일
- **Python**: PEP 8 준수
- **TypeScript**: ESLint 설정 따름
- **Commit**: [Conventional Commits](https://www.conventionalcommits.org/) 형식 사용

### 이슈 리포트
- **Bug Report**: [Bug Report Template](.github/ISSUE_TEMPLATE/bug_report.md)
- **Feature Request**: [Feature Request Template](.github/ISSUE_TEMPLATE/feature_request.md)

## 📊 프로젝트 통계

- **언어**: Python (Lambda), TypeScript (CDK)
- **클라우드**: AWS (Lambda, EventBridge, CloudWatch)
- **스크래핑**: Playwright + Chromium
- **알림**: Slack Webhooks
- **CI/CD**: GitHub Actions

## 🏗️ 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   EventBridge   │───▶│   AWS Lambda    │───▶│     Slack       │
│  (Daily 8 AM)   │    │  (Docker)       │    │   (Webhook)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  HomeTax.go.kr  │
                       │   (Playwright)  │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │ CloudWatch Logs │
                       │   (Monitoring)  │
                       └─────────────────┘
```

## 🔒 보안

이 프로젝트는 다음 보안 원칙을 따릅니다:
- **최소 권한**: Lambda 함수는 필요한 최소한의 AWS 권한만 보유
- **환경 변수**: 민감한 정보는 환경 변수로 관리
- **로그 보존**: CloudWatch 로그는 1주일 후 자동 삭제
- **보안 스캔**: GitHub Actions에서 Trivy로 취약점 검사

보안 이슈를 발견하신 경우, 공개 이슈 대신 이메일로 연락해 주세요.

## 📞 연락처

- **개발자**: Danny Kim ([@danny-zent](https://github.com/danny-zent))
- **회사**: Zent (Korean Fintech Company)
- **프로젝트**: Data Engineering Team

## 📄 라이선스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

<div align="center">
  <sub>Built with ❤️ by <a href="https://github.com/danny-zent">Danny Kim</a> at Zent</sub>
</div>

FROM public.ecr.aws/lambda/python:3.11

# 필요한 시스템 패키지 설치
RUN yum update -y && \
    yum install -y \
    wget \
    unzip \
    fontconfig \
    freetype \
    freetype-devel \
    fontconfig-devel \
    libstdc++ \
    && yum clean all

# Python 의존성 설치
COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.txt

# Playwright 브라우저 설치
RUN playwright install chromium
RUN playwright install-deps chromium

# Lambda 함수 코드 복사
COPY src/ ${LAMBDA_TASK_ROOT}/

# 환경 변수 설정
ENV PYTHONPATH="${LAMBDA_TASK_ROOT}"
ENV PLAYWRIGHT_BROWSERS_PATH="/var/task"

# Lambda 핸들러 지정
CMD ["handler.lambda_handler"]

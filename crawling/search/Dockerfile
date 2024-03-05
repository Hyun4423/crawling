FROM python:3.12.0

# Chrome 브라우저 및 드라이버 설치
RUN apt-get update
RUN apt-get install -y chromium-driver

# Selenium 및 종속성 설치
RUN pip install selenium
RUN pip install requests
RUN pip install BeautifulSoup4

# 작업 디렉토리 설정
WORKDIR /app

# 크롤링을 위한 스크립트 복사
COPY crawler.py .

# 크롤링 스크립트 실행
CMD ["python", "crawler.py"]

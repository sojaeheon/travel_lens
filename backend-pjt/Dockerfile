FROM python:3.11-slim

# 환경 변수 설정
# 이 설정은 python이 .pyc 파일(파이썬 바이트코드 파일)을 생성하지 않도록 한다
ENV PYTHONDONTWRITEBYTECODE 1
# 이 설정은 python이 출력하는 내용(print()문의 결과)을 버퍼링(buffering)하지 않도록 만듦
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY . /app/

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python","manage.py","runserver","0.0.0.0:8000"]

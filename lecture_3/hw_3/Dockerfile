FROM python:3.12

WORKDIR /app

COPY . ./
COPY ./requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

EXPOSE 8080

CMD ["uvicorn", "hw_service.main:app", "--port", "8080", "--host", "0.0.0.0"]
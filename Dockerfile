FROM python:3.10

WORKDIR /app

COPY . .

EXPOSE 3000

ENTRYPOINT ["python", "main.py"]

#docker run -p 3000:3000 -v /front-init:/app/front-init -d my_http_server
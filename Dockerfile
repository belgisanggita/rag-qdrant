FROM python:3.10.14-slim-bookworm
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN chmod a+x start.sh && apt update -y && apt install -y dos2unix && dos2unix start.sh
EXPOSE 8000
CMD ["./start.sh"]
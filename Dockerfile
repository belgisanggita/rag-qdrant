FROM python:3.10.14-slim-bookworm
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN chmod +x start.sh
EXPOSE 8000
CMD ["./start.sh"]
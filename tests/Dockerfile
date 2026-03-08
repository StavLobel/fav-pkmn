FROM python:3.12-slim

WORKDIR /tests

RUN pip install --no-cache-dir pytest playwright httpx && \
    playwright install --with-deps chromium

COPY . .

CMD ["pytest", "-v"]

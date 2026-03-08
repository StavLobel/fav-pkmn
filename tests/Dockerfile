FROM python:3.12-slim

WORKDIR /tests

RUN pip install --no-cache-dir \
    pytest playwright httpx \
    faker pytest-ordering pytest-randomly pytest-xdist \
    pytest-cov pytest-timeout pytest-asyncio \
    freezegun respx && \
    playwright install --with-deps chromium

COPY . .

CMD ["pytest", "-v"]

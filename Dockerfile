FROM python:3.14.2-slim-trixie

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir \
    asyncpg bcrypt fastapi PyJWT SQLAlchemy uvicorn

WORKDIR /src
COPY src .

CMD ["python3", "app.py"]

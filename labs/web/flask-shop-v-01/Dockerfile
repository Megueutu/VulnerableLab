FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 SHOP_DATABASE=/data/shop.sqlite3
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --create-home shop \
    && mkdir /data \
    && chown shop:shop /data
COPY app.py schema.sql ./
COPY templates/ ./templates/
COPY static/ ./static/
USER shop
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]

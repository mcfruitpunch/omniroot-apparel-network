FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_DB_PATH=/data/apparel.sqlite3
WORKDIR /srv/app
COPY platform/requirements.txt /srv/app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && mkdir -p /data
COPY platform/server.py /srv/app/server.py
COPY platform/site /srv/app/site
RUN useradd --system --uid 10001 omni && chown -R omni:omni /data /srv/app
USER omni
EXPOSE 8000
CMD ["uvicorn","server:app","--host","0.0.0.0","--port","8000"]

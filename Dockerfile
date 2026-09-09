FROM python:3.13-alpine@sha256:7415fbc3c9e4979cc717d92377ab2bc7b2b4a2af1ac03cc52b5f3f88efedaf3a AS dependencies
WORKDIR /build
COPY requirements.lock .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.lock

FROM python:3.13-alpine@sha256:7415fbc3c9e4979cc717d92377ab2bc7b2b4a2af1ac03cc52b5f3f88efedaf3a AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY --from=dependencies /wheels /wheels
COPY requirements.lock .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.lock \
    && pip uninstall -y pip setuptools wheel \
    && rm -rf /wheels \
    && addgroup -g 10001 app \
    && adduser -D -H -u 10001 -G app app
COPY --chown=10001:10001 app.py .
USER 10001:10001
EXPOSE 8080
HEALTHCHECK --interval=15s --timeout=10s --start-period=30s --retries=3   CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=2)" || exit 1
CMD ["gunicorn", "--bind=0.0.0.0:8080", "--workers=2", "--threads=2", "--worker-tmp-dir=/tmp", "--access-logfile=-", "--error-logfile=-", "app:app"]

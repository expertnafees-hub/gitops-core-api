FROM python:3.13-slim-bookworm@sha256:ed86c82274b3c69b52fb5820f358f0bd7df0b603332063cb5c6e32bd220c3e6e AS dependencies
WORKDIR /build
COPY requirements.lock .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.lock

FROM python:3.13-slim-bookworm@sha256:ed86c82274b3c69b52fb5820f358f0bd7df0b603332063cb5c6e32bd220c3e6e AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY --from=dependencies /wheels /wheels
COPY requirements.lock .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.lock     && rm -rf /wheels     && groupadd --gid 10001 app     && useradd --uid 10001 --gid 10001 --no-create-home app
COPY --chown=10001:10001 app.py .
USER 10001:10001
EXPOSE 8080
HEALTHCHECK --interval=15s --timeout=10s --start-period=30s --retries=3   CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=2)" || exit 1
CMD ["gunicorn", "--bind=0.0.0.0:8080", "--workers=2", "--threads=2", "--worker-tmp-dir=/tmp", "--access-logfile=-", "--error-logfile=-", "app:app"]

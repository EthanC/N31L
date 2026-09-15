FROM ghcr.io/astral-sh/uv:latest AS uv

FROM python:alpine AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /build

COPY --from=uv /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

FROM python:alpine AS runtime

ENV PATH="/n31l/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PUID=1000 \
    PGID=1000 \
    HOME=/data \
    N31L_HEALTHCHECK_FILE=/run/n31l/health

WORKDIR /n31l

COPY --from=builder /build/.venv ./.venv
COPY n31l.py ./
COPY core ./core
COPY extensions ./extensions
COPY container_entrypoint.py /usr/local/bin/container-entrypoint

RUN /usr/local/bin/python -m pip uninstall --yes pip \
    && mkdir -p /data /run/n31l \
    && chmod 0777 /data /run/n31l \
    && chmod 0555 /usr/local/bin/container-entrypoint \
    && chmod -R a-w /n31l

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD ["python", "-c", "import os,time; age=time.time()-os.stat(os.environ['N31L_HEALTHCHECK_FILE']).st_mtime; raise SystemExit(age > 90)"]

ENTRYPOINT ["/usr/local/bin/container-entrypoint"]
CMD ["python", "-OO", "n31l.py"]

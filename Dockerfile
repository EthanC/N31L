FROM python:3.12-slim-bookworm

WORKDIR /n31l
COPY . .

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
RUN uv sync --frozen --no-dev

CMD [ "uv", "run", "n31l.py", "-OO" ]

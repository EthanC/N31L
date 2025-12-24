FROM python:3.14-slim-trixie

WORKDIR /n31l
COPY . .

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
RUN uv sync --frozen --no-dev

CMD [ "uv", "run", "n31l.py", "-OO" ]

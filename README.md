# N31L

![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/EthanC/N31L/ci.yaml?branch=main) ![Docker Pulls](https://img.shields.io/docker/pulls/ethanchrisp/n31l?label=Docker%20Pulls) ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/ethanchrisp/n31l/latest?label=Docker%20Image%20Size)

N31L is a utilitarian Discord bot for the [Call of Duty server](https://discord.gg/CallofDuty).

<p align="center">
    <img src="https://i.imgur.com/geOC3Sz.png" draggable="false">
</p>

## Features

Notice: N31L is purpose-built, this means that its functionality is intended only for the Moderators of the [Call of Duty server](https://discord.gg/CallofDuty). This repository has been made open source for educational purposes, **N31L will likely not fit your needs**.

-   Modern, interaction-based Discord bot utilizing the application commands API
-   Designed to expand and enhance the Discord Moderator toolset
-   Thread and forum post management
-   LOTS of animal and food commands

## Setup

[Discord API](https://discord.com/developers/) credentials are required for functionality, and a [Discord Webhook](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks) is recommended for notifications.

### Docker (Recommended)

Rename `config_example.json` to `config.json`, then provide the configurable variables.

Modify the following `compose.yaml` example file, then run `docker compose up`.

```yml
services:
  n31l:
    container_name: n31l
    image: ethanchrisp/n31l:latest
    environment:
      LOG_LEVEL: INFO
      LOG_DISCORD_WEBHOOK_URL: https://discord.com/api/webhooks/XXXXXXXX/XXXXXXXX
      LOG_DISCORD_WEBHOOK_LEVEL: WARNING
      DISCORD_TOKEN: XXXXXXXX
      DISCORD_SERVER_ID: 0000000000
      CAT_API_KEY: XXXXXXXXXX
      DOG_API_KEY: XXXXXXXXXX
      REDDIT_USERNAME: XXXXXXXXXX
      REDDIT_PASSWORD: XXXXXXXXXX
      REDDIT_CLIENT_ID: XXXXXXXXXX
      REDDIT_CLIENT_SECRET: XXXXXXXXXX
    volumes:
      - /path/to/config.json:/n31l/config.json:ro
    restart: unless-stopped
```

### Standalone

N31L is built for [Python 3.12](https://www.python.org/) or greater.

1. Install required dependencies using [uv](https://github.com/astral-sh/uv): `uv sync`
2. Rename `.env.example` to `.env`, then provide the environment variables.
3. Rename `config_example.json` to `config.json`, then provide the configurable variables.
4. Start N31L: `python -OO n31l.py`

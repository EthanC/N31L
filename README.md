# N31L

![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/EthanC/N31L/main.yml?branch=main) ![Docker Pulls](https://img.shields.io/docker/pulls/ethanchrisp/n31l?label=Docker%20Pulls) ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/ethanchrisp/n31l/latest?label=Docker%20Image%20Size)

N31L is a utilitarian Discord bot for the [Call of Duty server](https://discord.gg/CallofDuty).

<p align="center">
    <img src="https://i.imgur.com/reqTkF4.png" draggable="false">
</p>

## Features

Notice: N31L is purpose-built, this means that its functionality is intended only for the Moderators of the [Call of Duty server](https://discord.gg/CallofDuty). This repository has been made open source for educational purposes, **N31L will likely not fit your needs**.

-   Modern, interaction-based Discord bot utilizing the application commands API
-   Designed to expand and enhance the Discord Moderator toolset
-   Granular protection against automated raids
-   Thread and forum post management
-   LOTS of animal and food commands

## Setup

[Discord API](https://discord.com/developers/) credentials are required for functionality, and a [Discord Webhook](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks) is recommended for notifications.

### Docker (Recommended)

Modify the following `docker-compose.yml` example file, then run `docker compose up`.

```yml
version: "3"
services:
  n31l:
    container_name: n31l
    image: ethanchrisp/n31l:latest
    volumes:
      - /path/to/config.json:/n31l/config.json:ro
    restart: unless-stopped
```

### Standalone

N31L is built for [Python 3.11](https://www.python.org/) or greater.

1. Install required dependencies using [Poetry](https://python-poetry.org/): `poetry install`
2. Rename `config_example.json` to `config.json`, then provide the configurable variables.
3. Start N31L: `python n31l.py -OO`

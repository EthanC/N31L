from dataclasses import dataclass
from datetime import datetime


@dataclass()
class State:
    """Dataclass object containing a temporary bot state."""

    botStart: datetime

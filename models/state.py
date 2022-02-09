from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from hikari import User


@dataclass()
class State:
    """Dataclass object containing a temporary bot state."""

    botStart: datetime

    raidOffense: bool
    raidOffAge: Optional[int]
    raidOffReason: Optional[str]
    raidOffActor: Optional[User]
    raidOffCount: Optional[int]

    raidDefense: bool

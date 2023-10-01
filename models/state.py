from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Union


@dataclass()
class State:
    """Dataclass object containing a temporary bot state."""

    botStart: datetime
    threadMessages: List[Dict[str, Union[int, str]]]

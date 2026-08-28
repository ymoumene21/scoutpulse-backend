"""
Pydantic schema for one row of raw match event data,
checked before it's allowed anywhere near Postgres.
Field names and rules mirror db/schema.sql exactly.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional

# Matches the CHECK constraint on match_events.event_type in db/schema.sql
ALLOWED_EVENT_TYPES = {
    "goal", "assist", "yellow_card", "red_card", "rating",
    "shot", "shot_on_target", "tackle", "foul",
    "substitution_in", "substitution_out",
}


class RawMatchEvent(BaseModel):
    match_id: int
    player_id: int
    event_type: str
    # Optional because the real table allows NULL here (e.g. goal/assist/card events
    # carry no numeric value — only 'rating' events do).
    event_value: Optional[float] = Field(default=None, ge=0)
    minute: Optional[int] = Field(default=None, ge=0, le=120)

    @field_validator("event_type")
    @classmethod
    def event_type_must_be_known(cls, value: str) -> str:
        if value not in ALLOWED_EVENT_TYPES:
            raise ValueError(f"event_type '{value}' is not one of {ALLOWED_EVENT_TYPES}")
        return value

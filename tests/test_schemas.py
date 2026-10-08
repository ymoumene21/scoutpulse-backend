import pytest
from pydantic import ValidationError

from ingestion.schemas import RawMatchEvent


def test_valid_row_is_accepted():
    event = RawMatchEvent.model_validate(
        {"match_id": "12", "player_id": "1", "event_type": "goal", "event_value": None, "minute": "23"}
    )
    assert event.match_id == 12      # "12" (text from CSV) was coerced to the int 12
    assert event.minute == 23


def test_empty_event_value_is_allowed():
    event = RawMatchEvent.model_validate(
        {"match_id": 12, "player_id": 1, "event_type": "goal", "event_value": None, "minute": 23}
    )
    assert event.event_value is None


def test_minute_over_120_is_rejected():
    with pytest.raises(ValidationError):
        RawMatchEvent.model_validate(
            {"match_id": 12, "player_id": 1, "event_type": "goal", "minute": 150}
        )


def test_unknown_event_type_is_rejected():
    with pytest.raises(ValidationError):
        RawMatchEvent.model_validate(
            {"match_id": 12, "player_id": 1, "event_type": "dribble", "minute": 23}
        )


def test_non_numeric_match_id_is_rejected():
    with pytest.raises(ValidationError):
        RawMatchEvent.model_validate(
            {"match_id": "abc", "player_id": 1, "event_type": "goal", "minute": 23}
        )
"""
Manual sanity check for RawMatchEvent -- mirrors the db_check.py pattern from Day 2.
Run this to prove Pydantic validation actually catches bad data before we
build it into the real ingestion pipeline.
"""

from pydantic import ValidationError
from ingestion.schemas import RawMatchEvent

# 1. A valid event -- every field is the right type. Should pass cleanly.
good_data = {
    "match_id": 1,
    "player_id": 5,
    "event_type": "goal",
    "event_value": 1,
    "minute": 23,
}
good_event = RawMatchEvent.model_validate(good_data)
print("VALID EVENT PASSED:")
print(good_event)
print()

# 2. match_id is a string that can't become a number.
bad_data = {
    "match_id": "not-a-number",
    "player_id": 5,
    "event_type": "goal",
    "event_value": 1,
    "minute": 23,
}
try:
    RawMatchEvent.model_validate(bad_data)
    print("BUG: bad event was NOT rejected.")
except ValidationError as e:
    print("BAD EVENT CORRECTLY REJECTED:")
    print(e)
print()

# 3. minute out of range
try:
    RawMatchEvent.model_validate({
        "match_id": 1, "player_id": 5, "event_type": "goal",
        "event_value": 1, "minute": 150,
    })
    print("BUG: bad minute was not caught.")
except ValidationError as e:
    print("BAD MINUTE CORRECTLY REJECTED:")
    print(e)
print()

# 4. unknown event_type
try:
    RawMatchEvent.model_validate({
        "match_id": 1, "player_id": 5, "event_type": "backflip",
        "event_value": 1, "minute": 23,
    })
    print("BUG: bad event_type was not caught.")
except ValidationError as e:
    print("BAD EVENT_TYPE CORRECTLY REJECTED:")
    print(e)
print()

# 5. A yellow card with no event_value -- this MUST pass, since the real
# table allows NULL here. If this fails, the schema is wrong, not the data.
card_event = RawMatchEvent.model_validate({
    "match_id": 1, "player_id": 5, "event_type": "yellow_card",
    "event_value": None, "minute": 41,
})
print("CARD EVENT WITH NO VALUE PASSED:")
print(card_event)

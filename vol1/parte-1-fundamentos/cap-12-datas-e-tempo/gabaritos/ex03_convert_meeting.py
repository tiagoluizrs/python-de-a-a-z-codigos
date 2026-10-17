"""Gabarito do exercício 3."""
import datetime as dt
from zoneinfo import ZoneInfo


def convert_meeting(local: dt.datetime, from_key: str, to_key: str,
                    *, fold: int = 0) -> dt.datetime:
    if local.tzinfo is not None:
        raise ValueError("local must be naive")
    source = ZoneInfo(from_key)
    moment = local.replace(tzinfo=source, fold=fold)
    # Ida e volta por UTC: se a hora de parede mudou, caiu no salto.
    roundtrip = moment.astimezone(dt.UTC).astimezone(source)
    if roundtrip.replace(tzinfo=None) != local:
        raise ValueError(f"{local} does not exist in {from_key}")
    return moment.astimezone(ZoneInfo(to_key))

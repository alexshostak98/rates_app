from datetime import datetime


def get_unix_timestamp(raw_datetime: datetime) -> int:
    return int(raw_datetime.replace(microsecond=0).timestamp())

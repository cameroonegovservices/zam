from datetime import date
from typing import Optional


def parse_date(rfc339_datetime_string: str) -> Optional[date]:
    if rfc339_datetime_string == "":
        return None
    return date(
        year=int(rfc339_datetime_string[0:4]),
        month=int(rfc339_datetime_string[5:7]),
        day=int(rfc339_datetime_string[8:10]),
    )

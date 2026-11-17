"""The current time, or SOURCE_DATE_EPOCH when it is set, so a build can be reproduced."""

import os
from datetime import datetime, timezone


def now() -> datetime:
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if epoch:
        return datetime.fromtimestamp(int(epoch), timezone.utc)
    return datetime.now(timezone.utc)

from dataclasses import dataclass

from core.modules.worker.utils.limit_args import LimitArgs


@dataclass(slots=True, frozen=True)
class Setting:
    timeout: float
    worker_count: int
    limited_args: LimitArgs | None = None
    timeout_reset: int = 180

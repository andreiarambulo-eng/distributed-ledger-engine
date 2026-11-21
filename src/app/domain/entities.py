from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class ServiceHealth:
    name: str
    status: str
    latency_ms: float | None = None
    details: str | None = None


@dataclass(frozen=True)
class SystemHealth:
    app_name: str
    environment: str
    status: str
    timestamp: datetime
    services: list[ServiceHealth] = field(default_factory=list)

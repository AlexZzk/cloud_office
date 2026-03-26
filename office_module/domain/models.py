from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class OfficeStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"


class ParticipantStatus(str, Enum):
    ONLINE = "ONLINE"
    AWAY = "AWAY"
    BUSY = "BUSY"


@dataclass
class CapacityRule:
    max_participants: int


@dataclass
class Seat:
    seat_id: str
    zone_id: str
    label: str


@dataclass
class Zone:
    zone_id: str
    name: str


@dataclass
class OfficeTemplate:
    template_id: str
    name: str
    version: int
    zones: List[Zone] = field(default_factory=list)
    seats: List[Seat] = field(default_factory=list)


@dataclass
class OfficeInstance:
    office_id: str
    template_id: str
    owner_org_id: str
    capacity_rule: CapacityRule
    status: OfficeStatus = OfficeStatus.INACTIVE


@dataclass
class SceneBinding:
    scene_binding_id: str
    target_office_id: str
    renderer_type: str
    scene_asset_ref: str
    mapping_rules: Dict[str, str]


@dataclass
class PresenceSession:
    session_id: str
    office_id: str
    subject_id: str
    position_token: str
    status: ParticipantStatus = ParticipantStatus.ONLINE

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class CreateTemplateInput:
    template_id: str
    name: str
    version: int
    zones: List[Dict[str, str]]
    seats: List[Dict[str, str]]


@dataclass
class CreateOfficeInput:
    office_id: str
    template_id: str
    owner_org_id: str
    max_participants: int


@dataclass
class BindSceneInput:
    scene_binding_id: str
    office_id: str
    renderer_type: str
    scene_asset_ref: str
    mapping_rules: Dict[str, str]


@dataclass
class EnterOfficeInput:
    session_id: str
    office_id: str
    subject_id: str
    position_token: str


@dataclass
class MoveInput:
    office_id: str
    subject_id: str
    position_token: str

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class SceneDimension(str, Enum):
    D2 = "2D"
    D3 = "3D"


@dataclass
class SceneLayer:
    layer_id: str
    name: str
    z_index: int


@dataclass
class SceneDefinition:
    scene_id: str
    name: str
    dimension: SceneDimension
    renderer_type: str
    asset_ref: str
    layers: List[SceneLayer] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class GatheredOfficeScene2D:
    scene_id: str
    renderer_type: str
    asset_ref: str
    nodes: List[Dict[str, str]]
    participants: List[Dict[str, str]]

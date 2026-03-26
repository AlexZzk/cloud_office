from __future__ import annotations

from typing import Dict, List

from office_module.scene.models import GatheredOfficeScene2D, SceneDefinition, SceneDimension
from office_module.scene.ports import SceneDefinitionRepoPort


class SceneDefinitionService:
    """Scene interface layer for both 2D and 3D definitions."""

    def __init__(self, repo: SceneDefinitionRepoPort) -> None:
        self.repo = repo

    def save_scene(self, scene: SceneDefinition) -> SceneDefinition:
        self.repo.save(scene)
        return scene

    def get_scene(self, scene_id: str) -> SceneDefinition:
        scene = self.repo.get(scene_id)
        if scene is None:
            raise ValueError("scene_not_found")
        return scene

    def list_2d_scenes(self) -> List[SceneDefinition]:
        return self.repo.list_by_dimension(SceneDimension.D2)

    def list_3d_scenes(self) -> List[SceneDefinition]:
        return self.repo.list_by_dimension(SceneDimension.D3)


class Office2DSceneGatherService:
    """Builds the first office 2D scene payload in gather style (layout + mapping + presence)."""

    def gather(
        self,
        scene: SceneDefinition,
        mapping_rules: Dict[str, str],
        layout: Dict[str, List[Dict[str, str]]],
        presence: List[Dict[str, str]],
    ) -> GatheredOfficeScene2D:
        if scene.dimension != SceneDimension.D2:
            raise ValueError("scene_dimension_not_supported")

        nodes = []
        for zone in layout.get("zones", []):
            zone_id = zone["zone_id"]
            mapped = mapping_rules.get(zone_id)
            if mapped is not None:
                nodes.append({"business_id": zone_id, "scene_node": mapped, "node_type": "ZONE"})

        for seat in layout.get("seats", []):
            seat_id = seat["seat_id"]
            mapped = mapping_rules.get(seat_id)
            if mapped is not None:
                nodes.append({"business_id": seat_id, "scene_node": mapped, "node_type": "SEAT"})

        participants = [
            {
                "subject_id": item["subject_id"],
                "position_token": item["position_token"],
                "status": item["status"],
            }
            for item in presence
        ]

        return GatheredOfficeScene2D(
            scene_id=scene.scene_id,
            renderer_type=scene.renderer_type,
            asset_ref=scene.asset_ref,
            nodes=nodes,
            participants=participants,
        )

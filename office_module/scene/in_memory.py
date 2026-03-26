from __future__ import annotations

from typing import Dict, List

from office_module.scene.models import SceneDefinition, SceneDimension


class InMemorySceneDefinitionRepo:
    def __init__(self) -> None:
        self._items: Dict[str, SceneDefinition] = {}

    def save(self, scene: SceneDefinition) -> None:
        self._items[scene.scene_id] = scene

    def get(self, scene_id: str) -> SceneDefinition | None:
        return self._items.get(scene_id)

    def list_by_dimension(self, dimension: SceneDimension) -> List[SceneDefinition]:
        return [scene for scene in self._items.values() if scene.dimension == dimension]

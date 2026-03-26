from __future__ import annotations

from typing import List, Protocol

from office_module.scene.models import SceneDefinition, SceneDimension


class SceneDefinitionRepoPort(Protocol):
    def save(self, scene: SceneDefinition) -> None: ...

    def get(self, scene_id: str) -> SceneDefinition | None: ...

    def list_by_dimension(self, dimension: SceneDimension) -> List[SceneDefinition]: ...

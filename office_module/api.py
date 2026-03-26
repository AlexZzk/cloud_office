from __future__ import annotations

from office_module.application.service import OfficeCommandService, OfficeQueryService
from office_module.infrastructure.in_memory import (
    InMemoryOfficeTemplateRepo,
    InMemoryOfficeInstanceRepo,
    InMemorySceneBindingRepo,
    InMemoryPresenceRepo,
    InMemoryEventBus,
)


class OfficeModule:
    """Standalone office module facade.

    Can run without Employee/Asset modules.
    """

    def __init__(self) -> None:
        self.template_repo = InMemoryOfficeTemplateRepo()
        self.office_repo = InMemoryOfficeInstanceRepo()
        self.scene_repo = InMemorySceneBindingRepo()
        self.presence_repo = InMemoryPresenceRepo()
        self.event_bus = InMemoryEventBus()

        self.command = OfficeCommandService(
            template_repo=self.template_repo,
            office_repo=self.office_repo,
            scene_repo=self.scene_repo,
            presence_repo=self.presence_repo,
            event_bus=self.event_bus,
        )
        self.query = OfficeQueryService(
            template_repo=self.template_repo,
            office_repo=self.office_repo,
            scene_repo=self.scene_repo,
            presence_repo=self.presence_repo,
        )

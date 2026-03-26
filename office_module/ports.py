from __future__ import annotations

from typing import Protocol, List

from office_module.domain.events import DomainEvent
from office_module.domain.models import OfficeTemplate, OfficeInstance, SceneBinding, PresenceSession


class OfficeTemplateRepoPort(Protocol):
    def save_template(self, template: OfficeTemplate) -> None: ...

    def get_template(self, template_id: str) -> OfficeTemplate | None: ...


class OfficeInstanceRepoPort(Protocol):
    def save_office(self, office: OfficeInstance) -> None: ...

    def get_office(self, office_id: str) -> OfficeInstance | None: ...


class SceneBindingRepoPort(Protocol):
    def save_binding(self, binding: SceneBinding) -> None: ...

    def get_binding(self, office_id: str) -> SceneBinding | None: ...


class PresenceRepoPort(Protocol):
    def save_session(self, session: PresenceSession) -> None: ...

    def get_session(self, office_id: str, subject_id: str) -> PresenceSession | None: ...

    def delete_session(self, office_id: str, subject_id: str) -> None: ...

    def list_sessions(self, office_id: str) -> List[PresenceSession]: ...


class EventBusPort(Protocol):
    def publish(self, event: DomainEvent) -> None: ...

    def list_events(self) -> List[DomainEvent]: ...

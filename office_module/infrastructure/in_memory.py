from __future__ import annotations

from typing import Dict, List, Tuple

from office_module.domain.events import DomainEvent
from office_module.domain.models import OfficeTemplate, OfficeInstance, SceneBinding, PresenceSession


class InMemoryOfficeTemplateRepo:
    def __init__(self) -> None:
        self._items: Dict[str, OfficeTemplate] = {}

    def save_template(self, template: OfficeTemplate) -> None:
        self._items[template.template_id] = template

    def get_template(self, template_id: str) -> OfficeTemplate | None:
        return self._items.get(template_id)


class InMemoryOfficeInstanceRepo:
    def __init__(self) -> None:
        self._items: Dict[str, OfficeInstance] = {}

    def save_office(self, office: OfficeInstance) -> None:
        self._items[office.office_id] = office

    def get_office(self, office_id: str) -> OfficeInstance | None:
        return self._items.get(office_id)


class InMemorySceneBindingRepo:
    def __init__(self) -> None:
        self._items: Dict[str, SceneBinding] = {}

    def save_binding(self, binding: SceneBinding) -> None:
        self._items[binding.target_office_id] = binding

    def get_binding(self, office_id: str) -> SceneBinding | None:
        return self._items.get(office_id)


class InMemoryPresenceRepo:
    def __init__(self) -> None:
        self._items: Dict[Tuple[str, str], PresenceSession] = {}

    def save_session(self, session: PresenceSession) -> None:
        self._items[(session.office_id, session.subject_id)] = session

    def get_session(self, office_id: str, subject_id: str) -> PresenceSession | None:
        return self._items.get((office_id, subject_id))

    def delete_session(self, office_id: str, subject_id: str) -> None:
        self._items.pop((office_id, subject_id), None)

    def list_sessions(self, office_id: str) -> List[PresenceSession]:
        return [s for (oid, _), s in self._items.items() if oid == office_id]


class InMemoryEventBus:
    def __init__(self) -> None:
        self._events: List[DomainEvent] = []

    def publish(self, event: DomainEvent) -> None:
        self._events.append(event)

    def list_events(self) -> List[DomainEvent]:
        return list(self._events)

from __future__ import annotations

from office_module.application.dto import (
    CreateTemplateInput,
    CreateOfficeInput,
    BindSceneInput,
    EnterOfficeInput,
    MoveInput,
)
from office_module.domain.events import DomainEvent
from office_module.domain.models import (
    OfficeTemplate,
    Zone,
    Seat,
    OfficeInstance,
    CapacityRule,
    OfficeStatus,
    PresenceSession,
    SceneBinding,
)
from office_module.ports import (
    OfficeTemplateRepoPort,
    OfficeInstanceRepoPort,
    SceneBindingRepoPort,
    PresenceRepoPort,
    EventBusPort,
)


class OfficeCommandService:
    def __init__(
        self,
        template_repo: OfficeTemplateRepoPort,
        office_repo: OfficeInstanceRepoPort,
        scene_repo: SceneBindingRepoPort,
        presence_repo: PresenceRepoPort,
        event_bus: EventBusPort,
    ) -> None:
        self.template_repo = template_repo
        self.office_repo = office_repo
        self.scene_repo = scene_repo
        self.presence_repo = presence_repo
        self.event_bus = event_bus

    def create_template(self, data: CreateTemplateInput) -> OfficeTemplate:
        template = OfficeTemplate(
            template_id=data.template_id,
            name=data.name,
            version=data.version,
            zones=[Zone(zone_id=z["zone_id"], name=z["name"]) for z in data.zones],
            seats=[
                Seat(seat_id=s["seat_id"], zone_id=s["zone_id"], label=s["label"])
                for s in data.seats
            ],
        )
        self.template_repo.save_template(template)
        self.event_bus.publish(DomainEvent(name="OfficeTemplateCreated", payload={"template_id": template.template_id}))
        return template

    def create_office(self, data: CreateOfficeInput) -> OfficeInstance:
        template = self.template_repo.get_template(data.template_id)
        if template is None:
            raise ValueError("template_not_found")

        office = OfficeInstance(
            office_id=data.office_id,
            template_id=data.template_id,
            owner_org_id=data.owner_org_id,
            capacity_rule=CapacityRule(max_participants=data.max_participants),
            status=OfficeStatus.INACTIVE,
        )
        self.office_repo.save_office(office)
        self.event_bus.publish(DomainEvent(name="OfficeCreated", payload={"office_id": office.office_id}))
        return office

    def activate_office(self, office_id: str) -> OfficeInstance:
        office = self._must_get_office(office_id)
        office.status = OfficeStatus.ACTIVE
        self.office_repo.save_office(office)
        self.event_bus.publish(DomainEvent(name="OfficeActivated", payload={"office_id": office_id}))
        return office

    def archive_office(self, office_id: str) -> OfficeInstance:
        office = self._must_get_office(office_id)
        office.status = OfficeStatus.ARCHIVED
        self.office_repo.save_office(office)
        self.event_bus.publish(DomainEvent(name="OfficeArchived", payload={"office_id": office_id}))
        return office

    def deactivate_office(self, office_id: str) -> OfficeInstance:
        office = self._must_get_office(office_id)
        office.status = OfficeStatus.INACTIVE
        self.office_repo.save_office(office)
        self.event_bus.publish(DomainEvent(name="OfficeDeactivated", payload={"office_id": office_id}))
        return office

    def bind_scene(self, data: BindSceneInput) -> SceneBinding:
        office = self._must_get_office(data.office_id)
        template = self.template_repo.get_template(office.template_id)
        assert template is not None

        required_nodes = {z.zone_id for z in template.zones}
        required_nodes.update(s.seat_id for s in template.seats)
        missing = sorted(node for node in required_nodes if node not in data.mapping_rules)
        if missing:
            raise ValueError(f"scene_mapping_missing:{','.join(missing)}")

        binding = SceneBinding(
            scene_binding_id=data.scene_binding_id,
            target_office_id=data.office_id,
            renderer_type=data.renderer_type,
            scene_asset_ref=data.scene_asset_ref,
            mapping_rules=data.mapping_rules,
        )
        self.scene_repo.save_binding(binding)
        self.event_bus.publish(DomainEvent(name="SceneBindingChanged", payload={"office_id": data.office_id}))
        return binding

    def enter_office(self, data: EnterOfficeInput) -> PresenceSession:
        office = self._must_get_office(data.office_id)
        if office.status != OfficeStatus.ACTIVE:
            raise ValueError("office_not_active")

        sessions = self.presence_repo.list_sessions(data.office_id)
        if len(sessions) >= office.capacity_rule.max_participants and self.presence_repo.get_session(
            data.office_id, data.subject_id
        ) is None:
            raise ValueError("office_capacity_exceeded")

        session = PresenceSession(
            session_id=data.session_id,
            office_id=data.office_id,
            subject_id=data.subject_id,
            position_token=data.position_token,
        )
        self.presence_repo.save_session(session)
        self.event_bus.publish(
            DomainEvent(name="ParticipantEnteredOffice", payload={"office_id": data.office_id, "subject_id": data.subject_id})
        )
        return session

    def move_participant(self, data: MoveInput) -> PresenceSession:
        session = self.presence_repo.get_session(data.office_id, data.subject_id)
        if session is None:
            raise ValueError("presence_session_not_found")

        session.position_token = data.position_token
        self.presence_repo.save_session(session)
        self.event_bus.publish(
            DomainEvent(name="ParticipantMoved", payload={"office_id": data.office_id, "subject_id": data.subject_id})
        )
        return session

    def leave_office(self, office_id: str, subject_id: str) -> None:
        session = self.presence_repo.get_session(office_id, subject_id)
        if session is None:
            return
        self.presence_repo.delete_session(office_id, subject_id)
        self.event_bus.publish(
            DomainEvent(name="ParticipantLeftOffice", payload={"office_id": office_id, "subject_id": subject_id})
        )

    def _must_get_office(self, office_id: str) -> OfficeInstance:
        office = self.office_repo.get_office(office_id)
        if office is None:
            raise ValueError("office_not_found")
        return office


class OfficeQueryService:
    def __init__(
        self,
        template_repo: OfficeTemplateRepoPort,
        office_repo: OfficeInstanceRepoPort,
        scene_repo: SceneBindingRepoPort,
        presence_repo: PresenceRepoPort,
    ) -> None:
        self.template_repo = template_repo
        self.office_repo = office_repo
        self.scene_repo = scene_repo
        self.presence_repo = presence_repo

    def get_office_detail(self, office_id: str) -> dict:
        office = self.office_repo.get_office(office_id)
        if office is None:
            raise ValueError("office_not_found")
        scene = self.scene_repo.get_binding(office_id)
        return {
            "office_id": office.office_id,
            "template_id": office.template_id,
            "owner_org_id": office.owner_org_id,
            "status": office.status.value,
            "capacity": office.capacity_rule.max_participants,
            "scene": scene.scene_asset_ref if scene else None,
        }

    def get_layout(self, office_id: str) -> dict:
        office = self.office_repo.get_office(office_id)
        if office is None:
            raise ValueError("office_not_found")
        template = self.template_repo.get_template(office.template_id)
        if template is None:
            raise ValueError("template_not_found")
        return {
            "zones": [{"zone_id": z.zone_id, "name": z.name} for z in template.zones],
            "seats": [{"seat_id": s.seat_id, "zone_id": s.zone_id, "label": s.label} for s in template.seats],
        }

    def list_presence(self, office_id: str) -> list[dict]:
        return [
            {
                "session_id": s.session_id,
                "subject_id": s.subject_id,
                "position_token": s.position_token,
                "status": s.status.value,
            }
            for s in self.presence_repo.list_sessions(office_id)
        ]

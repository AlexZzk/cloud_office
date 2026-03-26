import unittest

from office_module import OfficeModule
from office_module.application.dto import (
    CreateTemplateInput,
    CreateOfficeInput,
    BindSceneInput,
    EnterOfficeInput,
    MoveInput,
)


class OfficeModuleTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.module = OfficeModule()
        self.module.command.create_template(
            CreateTemplateInput(
                template_id="tpl_1",
                name="Default",
                version=1,
                zones=[{"zone_id": "ZONE_WORK", "name": "Work"}],
                seats=[{"seat_id": "SEAT_1", "zone_id": "ZONE_WORK", "label": "A1"}],
            )
        )
        self.module.command.create_office(
            CreateOfficeInput(
                office_id="office_1",
                template_id="tpl_1",
                owner_org_id="org_1",
                max_participants=2,
            )
        )

    def test_office_lifecycle_and_presence(self) -> None:
        self.module.command.activate_office("office_1")
        self.module.command.enter_office(
            EnterOfficeInput(
                session_id="sess_1",
                office_id="office_1",
                subject_id="u_1",
                position_token="ZONE_WORK.SEAT_1",
            )
        )

        moved = self.module.command.move_participant(
            MoveInput(office_id="office_1", subject_id="u_1", position_token="ZONE_WORK.SEAT_1")
        )
        self.assertEqual(moved.position_token, "ZONE_WORK.SEAT_1")
        self.assertEqual(len(self.module.query.list_presence("office_1")), 1)

        self.module.command.leave_office("office_1", "u_1")
        self.assertEqual(len(self.module.query.list_presence("office_1")), 0)

    def test_scene_switch_does_not_change_office_business_data(self) -> None:
        self.module.command.bind_scene(
            BindSceneInput(
                scene_binding_id="scene_1",
                office_id="office_1",
                renderer_type="pixi",
                scene_asset_ref="asset://scene/day",
                mapping_rules={"ZONE_WORK": "node-zone-work", "SEAT_1": "node-seat-a1"},
            )
        )
        before = self.module.query.get_office_detail("office_1")

        self.module.command.bind_scene(
            BindSceneInput(
                scene_binding_id="scene_2",
                office_id="office_1",
                renderer_type="pixi",
                scene_asset_ref="asset://scene/night",
                mapping_rules={"ZONE_WORK": "node-zone-work-2", "SEAT_1": "node-seat-a1-2"},
            )
        )
        after = self.module.query.get_office_detail("office_1")

        self.assertEqual(before["capacity"], after["capacity"])
        self.assertEqual(before["template_id"], after["template_id"])
        self.assertEqual(after["scene"], "asset://scene/night")

    def test_missing_scene_mapping_should_fail(self) -> None:
        with self.assertRaisesRegex(ValueError, "scene_mapping_missing"):
            self.module.command.bind_scene(
                BindSceneInput(
                    scene_binding_id="scene_1",
                    office_id="office_1",
                    renderer_type="pixi",
                    scene_asset_ref="asset://scene/day",
                    mapping_rules={"ZONE_WORK": "node-zone-work"},
                )
            )


if __name__ == "__main__":
    unittest.main()

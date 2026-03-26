from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from office_module import OfficeModule
from office_module.application.dto import BindSceneInput, CreateOfficeInput, CreateTemplateInput, EnterOfficeInput
from office_module.scene import (
    InMemorySceneDefinitionRepo,
    Office2DSceneGatherService,
    SceneDefinition,
    SceneDefinitionService,
    SceneDimension,
    SceneLayer,
)


class OfficeRuntime:
    def __init__(self) -> None:
        self.module = OfficeModule()
        self.scene_repo = InMemorySceneDefinitionRepo()
        self.scene_service = SceneDefinitionService(self.scene_repo)
        self.scene_gather = Office2DSceneGatherService()
        self._seed_default_data()

    def _seed_default_data(self) -> None:
        self.module.command.create_template(
            CreateTemplateInput(
                template_id="tpl_default",
                name="Default Template",
                version=1,
                zones=[
                    {"zone_id": "ZONE_WORK", "name": "Work Area"},
                    {"zone_id": "ZONE_MEET", "name": "Meeting Area"},
                ],
                seats=[
                    {"seat_id": "SEAT_A1", "zone_id": "ZONE_WORK", "label": "A1"},
                    {"seat_id": "SEAT_A2", "zone_id": "ZONE_WORK", "label": "A2"},
                ],
            )
        )
        self.module.command.create_office(
            CreateOfficeInput(
                office_id="office_demo",
                template_id="tpl_default",
                owner_org_id="org_demo",
                max_participants=20,
            )
        )
        self.module.command.activate_office("office_demo")
        self.module.command.bind_scene(
            BindSceneInput(
                scene_binding_id="bind_demo_2d",
                office_id="office_demo",
                renderer_type="pixi",
                scene_asset_ref="asset://scene/demo-office-2d",
                mapping_rules={
                    "ZONE_WORK": "node-zone-work",
                    "ZONE_MEET": "node-zone-meet",
                    "SEAT_A1": "node-seat-a1",
                    "SEAT_A2": "node-seat-a2",
                },
            )
        )
        self.scene_service.save_scene(
            SceneDefinition(
                scene_id="scene_demo_2d",
                name="Demo Office 2D",
                dimension=SceneDimension.D2,
                renderer_type="pixi",
                asset_ref="asset://scene/demo-office-2d",
                layers=[
                    SceneLayer(layer_id="base", name="Base", z_index=0),
                    SceneLayer(layer_id="actor", name="Actor", z_index=1),
                ],
                metadata={"theme": "day"},
            )
        )
        self.module.command.enter_office(
            EnterOfficeInput(
                session_id="sess_demo_1",
                office_id="office_demo",
                subject_id="u_demo_1",
                position_token="ZONE_WORK.SEAT_A1",
            )
        )

    def get_scene_payload(self) -> dict[str, Any]:
        layout = self.module.query.get_layout("office_demo")
        presence = self.module.query.list_presence("office_demo")
        binding = self.module.scene_repo.get_binding("office_demo")
        if binding is None:
            raise ValueError("scene_binding_not_found")
        scene = self.scene_service.get_scene("scene_demo_2d")
        gathered = self.scene_gather.gather(
            scene=scene,
            mapping_rules=binding.mapping_rules,
            layout=layout,
            presence=presence,
        )
        return {
            "scene": {
                "scene_id": gathered.scene_id,
                "renderer": gathered.renderer_type,
                "asset": gathered.asset_ref,
            },
            "nodes": gathered.nodes,
            "participants": gathered.participants,
        }


class OfficeHttpHandler(BaseHTTPRequestHandler):
    runtime: OfficeRuntime
    static_dir: Path

    def _send_json(self, payload: dict[str, Any], status: int = HTTPStatus.OK) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_file(self, path: Path, content_type: str) -> None:
        if not path.exists():
            self.send_error(HTTPStatus.NOT_FOUND, "file_not_found")
            return
        data = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        if self.path in {"/", "/index.html"}:
            return self._send_file(self.static_dir / "index.html", "text/html; charset=utf-8")
        if self.path == "/app.js":
            return self._send_file(self.static_dir / "app.js", "text/javascript; charset=utf-8")
        if self.path == "/health":
            return self._send_json({"ok": True})
        if self.path == "/api/office":
            return self._send_json(self.runtime.module.query.get_office_detail("office_demo"))
        if self.path == "/api/layout":
            return self._send_json(self.runtime.module.query.get_layout("office_demo"))
        if self.path == "/api/presence":
            return self._send_json({"items": self.runtime.module.query.list_presence("office_demo")})
        if self.path == "/api/scene/gathered":
            return self._send_json(self.runtime.get_scene_payload())

        self.send_error(HTTPStatus.NOT_FOUND, "not_found")


def run_server(host: str = "127.0.0.1", port: int = 8080) -> None:
    runtime = OfficeRuntime()
    static_dir = Path(__file__).resolve().parent.parent / "web"

    handler_cls = type(
        "OfficeRuntimeHandler",
        (OfficeHttpHandler,),
        {"runtime": runtime, "static_dir": static_dir},
    )
    server = ThreadingHTTPServer((host, port), handler_cls)
    print(f"Office demo server running at http://{host}:{port}")
    print("Open / to see the demo scene page, or /api/scene/gathered for JSON payload.")
    server.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Cloud Office demo server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    run_server(host=args.host, port=args.port)


if __name__ == "__main__":
    main()

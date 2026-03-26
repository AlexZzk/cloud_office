import unittest

from office_module.server import OfficeRuntime


class OfficeServerRuntimeTestCase(unittest.TestCase):
    def test_runtime_builds_gather_scene_payload(self) -> None:
        runtime = OfficeRuntime()
        payload = runtime.get_scene_payload()

        self.assertEqual(payload["scene"]["scene_id"], "scene_demo_2d")
        self.assertGreaterEqual(len(payload["nodes"]), 4)
        self.assertGreaterEqual(len(payload["participants"]), 1)


if __name__ == "__main__":
    unittest.main()

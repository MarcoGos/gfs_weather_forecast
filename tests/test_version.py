import json
import runpy
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class VersionTests(unittest.TestCase):
    def test_manifest_version_matches_device_software_version(self):
        manifest_path = ROOT / "custom_components/gfs_weather_forecast/manifest.json"
        constants_path = ROOT / "custom_components/gfs_weather_forecast/const.py"

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        constants = runpy.run_path(str(constants_path))

        self.assertEqual(manifest["version"], constants["VERSION"])

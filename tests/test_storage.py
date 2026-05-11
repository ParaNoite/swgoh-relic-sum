import tempfile
import unittest
from pathlib import Path

from app import build_default_data, load_data, save_data


class StorageTests(unittest.TestCase):
    def test_default_data_has_upgrade_slots(self):
        data = build_default_data()
        self.assertEqual(10, len(data["upgrade_material_costs"]))
        self.assertEqual("R1", data["upgrade_material_costs"][0]["升级阶段"])
        self.assertEqual("R10", data["upgrade_material_costs"][-1]["升级阶段"])
        self.assertEqual(10, data["upgrade_material_costs"][0]["金金金钱"])

    def test_load_save_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            data_file = Path(tmp_dir) / "upgrade.json"
            original = build_default_data()
            original["upgrade_material_costs"][0]["电路板"] = 123
            save_data(original, data_file)

            loaded = load_data(data_file)
            self.assertEqual(123, loaded["upgrade_material_costs"][0]["电路板"])

    def test_load_data_resets_invalid_json(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            data_file = Path(tmp_dir) / "upgrade.json"
            data_file.write_text("not json", encoding="utf-8")
            loaded = load_data(data_file)
            self.assertEqual(10, len(loaded["upgrade_material_costs"]))


if __name__ == "__main__":
    unittest.main()

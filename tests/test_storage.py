import tempfile
import unittest
from pathlib import Path

from app import build_default_data, load_data, save_data


class StorageTests(unittest.TestCase):
    def test_default_data_has_upgrade_slots(self):
        data = build_default_data()
        self.assertEqual(9, len(data["upgrade_material_costs"]))
        self.assertEqual(1, data["upgrade_material_costs"][0]["upgrade_index"])
        self.assertEqual(9, data["upgrade_material_costs"][-1]["upgrade_index"])

    def test_load_save_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            data_file = Path(tmp_dir) / "upgrade.json"
            original = build_default_data()
            original["upgrade_material_costs"][0]["carbonite_circuit_board"] = 123
            save_data(original, data_file)

            loaded = load_data(data_file)
            self.assertEqual(123, loaded["upgrade_material_costs"][0]["carbonite_circuit_board"])


if __name__ == "__main__":
    unittest.main()

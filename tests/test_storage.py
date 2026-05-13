import tempfile
import unittest
from pathlib import Path

from app import (
    build_default_data,
    calculate_eta_days,
    calculate_record_materials,
    calculate_total_materials,
    load_data,
    save_data,
)


class StorageTests(unittest.TestCase):
    def test_default_data_has_upgrade_slots(self):
        data = build_default_data()
        self.assertEqual(10, len(data["upgrade_material_costs"]))
        self.assertEqual("R1", data["upgrade_material_costs"][0]["升级阶段"])
        self.assertEqual("R10", data["upgrade_material_costs"][-1]["升级阶段"])
        self.assertEqual(10, data["upgrade_material_costs"][0]["金金金钱"])
        self.assertEqual([], data["upgrade_records"])
        self.assertEqual([], data["todo_list"])
        self.assertIn("daily_income", data)

    def test_load_save_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            data_file = Path(tmp_dir) / "upgrade.json"
            original = build_default_data()
            original["upgrade_material_costs"][0]["电路板"] = 123
            original["upgrade_records"].append({"角色": "CharacterA", "fromR": 1, "toR": 3})
            original["todo_list"].append({"角色": "CharacterA", "任务": "Farm gear", "状态": "未完成"})
            original["daily_income"]["电路板"] = 15
            save_data(original, data_file)

            loaded = load_data(data_file)
            self.assertEqual(123, loaded["upgrade_material_costs"][0]["电路板"])
            self.assertEqual("CharacterA", loaded["upgrade_records"][0]["角色"])
            self.assertEqual("Farm gear", loaded["todo_list"][0]["任务"])
            self.assertEqual(15, loaded["daily_income"]["电路板"])

    def test_load_data_resets_invalid_json(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            data_file = Path(tmp_dir) / "upgrade.json"
            data_file.write_text("not json", encoding="utf-8")
            loaded = load_data(data_file)
            self.assertEqual(10, len(loaded["upgrade_material_costs"]))
            self.assertEqual([], loaded["upgrade_records"])

    def test_material_sum_and_eta(self):
        data = build_default_data()
        record = {"角色": "CharacterA", "fromR": 1, "toR": 3}
        record_total = calculate_record_materials(record, data["upgrade_material_costs"])
        self.assertEqual(75, record_total["金金金钱"])
        self.assertEqual(35, record_total["灰信号"])

        total = calculate_total_materials([
            {"角色": "CharacterA", "fromR": 1, "toR": 3},
            {"角色": "CharacterB", "fromR": 1, "toR": 2},
        ], data["upgrade_material_costs"])
        self.assertEqual(100, total["金金金钱"])

        eta = calculate_eta_days(total, {"金金金钱": 9, "灰信号": 0})
        self.assertEqual(12, eta["金金金钱"])
        self.assertIsNone(eta["灰信号"])


if __name__ == "__main__":
    unittest.main()

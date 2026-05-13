import tempfile
import unittest
from pathlib import Path

from app import (
    MATERIAL_FIELDS,
    allowed_currencies_for_material,
    build_default_data,
    calculate_eta_days,
    calculate_record_materials,
    calculate_single_character_cultivation,
    calculate_total_materials,
    load_data,
    save_data,
)


def load_data_from_dict(data: dict) -> dict:
    with tempfile.TemporaryDirectory() as tmp_dir:
        data_file = Path(tmp_dir) / "upgrade.json"
        save_data(data, data_file)
        return load_data(data_file)


class StorageTests(unittest.TestCase):
    def test_default_material_labels_match_requirement(self):
        fields = [field for field, _label in MATERIAL_FIELDS]
        self.assertIn("断片", fields)
        self.assertIn("最牛逼那啥", fields)
        self.assertNotIn("两片东西", fields)
        self.assertNotIn("最牛逼那个", fields)

    def test_normalize_data_supports_legacy_material_keys(self):
        payload = build_default_data()
        payload["daily_income"].pop("断片", None)
        payload["daily_income"].pop("最牛逼那啥", None)
        payload["daily_income"]["两片东西"] = 8
        payload["daily_income"]["最牛逼那个"] = 9
        payload["material_inventory"].pop("断片", None)
        payload["material_inventory"].pop("最牛逼那啥", None)
        payload["material_inventory"]["两片东西"] = 11
        payload["material_inventory"]["最牛逼那个"] = 12
        payload["exchange_rates"].pop("断片", None)
        payload["exchange_rates"].pop("最牛逼那啥", None)
        payload["exchange_rates"]["两片东西"] = {"currency": "raidmk3", "price": 88}
        payload["exchange_rates"]["最牛逼那个"] = {"currency": "raidmk3", "price": 777}
        for row in payload["upgrade_material_costs"]:
            row.pop("断片", None)
            row.pop("最牛逼那啥", None)
            row["两片东西"] = 6
            row["最牛逼那个"] = 7

        normalized = load_data_from_dict(payload)
        self.assertEqual(8, normalized["daily_income"]["断片"])
        self.assertEqual(9, normalized["daily_income"]["最牛逼那啥"])
        self.assertEqual(11, normalized["material_inventory"]["断片"])
        self.assertEqual(12, normalized["material_inventory"]["最牛逼那啥"])
        self.assertEqual(88, normalized["exchange_rates"]["断片"]["price"])
        self.assertEqual(777, normalized["exchange_rates"]["最牛逼那啥"]["price"])
        self.assertEqual(6, normalized["upgrade_material_costs"][0]["断片"])
        self.assertEqual(7, normalized["upgrade_material_costs"][0]["最牛逼那啥"])

    def test_exchange_restrictions_by_material(self):
        self.assertEqual({"guildmk1", "guildmk2", "guildmk3"}, allowed_currencies_for_material("灰信号"))
        self.assertEqual({"raidmk1", "raidmk2", "raidmk3"}, allowed_currencies_for_material("脉冲放大"))
        self.assertIn("红能量", allowed_currencies_for_material("电路板"))

    def test_default_data_has_upgrade_slots(self):
        data = build_default_data()
        self.assertEqual(10, len(data["upgrade_material_costs"]))
        self.assertEqual("R1", data["upgrade_material_costs"][0]["升级阶段"])
        self.assertEqual("R10", data["upgrade_material_costs"][-1]["升级阶段"])
        self.assertEqual(10, data["upgrade_material_costs"][0]["金金金钱"])
        self.assertEqual([], data["upgrade_records"])
        self.assertEqual([], data["todo_list"])
        self.assertIn("daily_income", data)
        self.assertIn("currency_income", data)
        self.assertIn("currency_inventory", data)
        self.assertIn("material_inventory", data)
        self.assertIn("exchange_rates", data)
        self.assertIn("exchange_limits", data)

    def test_load_save_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            data_file = Path(tmp_dir) / "upgrade.json"
            original = build_default_data()
            original["upgrade_material_costs"][0]["电路板"] = 123
            original["upgrade_records"].append({"角色": "CharacterA", "fromR": 1, "toR": 3})
            original["todo_list"].append(
                {
                    "角色": "CharacterA",
                    "fromR": 1,
                    "toR": 3,
                    "fromSharp": 2,
                    "toSharp": 5,
                    "注释": "Farm gear",
                    "状态": "未完成",
                }
            )
            original["daily_income"]["电路板"] = 15
            original["currency_income"]["红能量"]["daily"] = 20
            original["currency_inventory"]["红能量"] = 150
            original["material_inventory"]["灰信号"] = 3
            original["exchange_rates"]["灰信号"]["price"] = 0.8
            original["exchange_limits"]["raidmk1"] = 99
            save_data(original, data_file)

            loaded = load_data(data_file)
            self.assertEqual(123, loaded["upgrade_material_costs"][0]["电路板"])
            self.assertEqual("CharacterA", loaded["upgrade_records"][0]["角色"])
            self.assertEqual("Farm gear", loaded["todo_list"][0]["注释"])
            self.assertEqual(15, loaded["daily_income"]["电路板"])
            self.assertEqual(20, loaded["currency_income"]["红能量"]["daily"])
            self.assertEqual(150, loaded["currency_inventory"]["红能量"])
            self.assertEqual(3, loaded["material_inventory"]["灰信号"])
            self.assertEqual(0.8, loaded["exchange_rates"]["灰信号"]["price"])
            self.assertEqual(99, loaded["exchange_limits"]["raidmk1"])

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
            {"角色": "CharacterA", "fromR": 1, "toR": 3, "状态": "未完成"},
            {"角色": "CharacterB", "fromR": 1, "toR": 2, "状态": "完成"},
        ], data["upgrade_material_costs"])
        self.assertEqual(75, total["金金金钱"])

        eta = calculate_eta_days(total, {"金金金钱": 9, "灰信号": 0})
        self.assertEqual(9, eta["金金金钱"])
        self.assertIsNone(eta["灰信号"])

    def test_single_character_cultivation_days(self):
        data = build_default_data()
        records = [
            {"角色": "CharacterA", "fromR": 1, "toR": 3, "状态": "未完成"},
            {"角色": "CharacterA", "fromR": 3, "toR": 4, "状态": "未完成"},
            {"角色": "CharacterB", "fromR": 1, "toR": 2, "状态": "完成"},
        ]
        daily_income = {field: 1000 for field, _label in MATERIAL_FIELDS}
        daily_income["金金金钱"] = 10
        result = calculate_single_character_cultivation(
            records,
            data["upgrade_material_costs"],
            daily_income,
            "CharacterA",
        )
        self.assertEqual("CharacterA", result["name"])
        self.assertEqual(2, result["record_count"])
        self.assertEqual(150, result["total_materials"]["金金金钱"])
        self.assertEqual(15, result["max_days"])
        self.assertEqual(15, result["eta"]["金金金钱"])

    def test_single_character_cultivation_days_infinite_when_income_missing(self):
        data = build_default_data()
        records = [{"角色": "CharacterA", "fromR": 1, "toR": 2, "状态": "未完成"}]
        result = calculate_single_character_cultivation(
            records,
            data["upgrade_material_costs"],
            {"金金金钱": 1},
            "CharacterA",
        )
        self.assertIsNone(result["max_days"])


if __name__ == "__main__":
    unittest.main()

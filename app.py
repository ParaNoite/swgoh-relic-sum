from __future__ import annotations

import json
import math
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import messagebox, ttk
except ModuleNotFoundError:  # pragma: no cover
    tk = None
    messagebox = None
    ttk = None

DATA_FILE = Path(__file__).resolve().parent / "data" / "upgrade_material_costs.json"
RELIC_TIERS = [f"R{i}" for i in range(1, 11)]
MATERIAL_FIELDS = [
    ("金金金钱", "金金金钱"),
    ("灰信号", "灰信号"),
    ("绿信号", "绿信号"),
    ("蓝信号", "蓝信号"),
    ("暗信号", "暗信号"),
    ("电路板", "电路板"),
    ("青铜线缆", "青铜线缆"),
    ("铬晶体管", "铬晶体管"),
    ("奥罗德散热器", "奥罗德散热器"),
    ("电金导体", "电金导体"),
    ("金必得卡牌", "金必得卡牌"),
    ("脉冲放大", "脉冲放大"),
    ("航空放大", "航空放大"),
    ("键盘", "键盘"),
    ("两片东西", "两片东西"),
    ("最牛逼那个", "最牛逼那个"),
]
DEFAULT_COSTS = [
    [10, 0, 0, 0, 0, 40, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [25, 15, 0, 0, 0, 30, 40, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [50, 20, 15, 0, 0, 30, 40, 20, 0, 0, 0, 0, 0, 0, 0, 0],
    [75, 20, 25, 0, 0, 30, 40, 40, 0, 0, 0, 0, 0, 0, 0, 0],
    [100, 20, 25, 15, 0, 30, 40, 30, 20, 0, 0, 0, 0, 0, 0, 0],
    [250, 20, 25, 25, 0, 20, 30, 30, 20, 20, 0, 0, 0, 0, 0, 0],
    [500, 20, 25, 35, 0, 20, 30, 20, 20, 20, 10, 0, 0, 0, 0, 0],
    [1000, 20, 25, 45, 0, 0, 0, 20, 20, 20, 20, 20, 20, 0, 0, 0],
    [1500, 0, 30, 55, 0, 0, 0, 0, 0, 20, 20, 20, 20, 20, 20, 0],
    [2000, 0, 25, 45, 15, 0, 0, 0, 0, 0, 0, 20, 20, 20, 20, 20],
]


def build_default_data() -> dict:
    rows = []
    for tier, costs in zip(RELIC_TIERS, DEFAULT_COSTS):
        row = {"升级阶段": tier}
        for (field, _label), value in zip(MATERIAL_FIELDS, costs):
            row[field] = value
        rows.append(row)

    return {
        "model_info": "预留：请在此填写你使用的模型说明",
        "upgrade_material_costs": rows,
        "upgrade_records": [],
        "daily_income": {field: 0 for field, _label in MATERIAL_FIELDS},
    }


def as_int(value: object) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def ensure_data_file(data_file: Path = DATA_FILE) -> None:
    data_file.parent.mkdir(parents=True, exist_ok=True)
    if not data_file.exists():
        save_data(build_default_data(), data_file)


def normalize_data(data: dict) -> dict:
    default = build_default_data()

    if not isinstance(data, dict):
        return default

    rows = data.get("upgrade_material_costs")
    if not isinstance(rows, list) or len(rows) != len(RELIC_TIERS):
        rows = default["upgrade_material_costs"]

    normalized_rows = []
    for idx, fallback_row in enumerate(default["upgrade_material_costs"]):
        source = rows[idx] if idx < len(rows) and isinstance(rows[idx], dict) else {}
        row = {"升级阶段": str(source.get("升级阶段", fallback_row["升级阶段"]))}
        for field, _label in MATERIAL_FIELDS:
            row[field] = as_int(source.get(field, fallback_row[field]))
        normalized_rows.append(row)

    records = data.get("upgrade_records")
    normalized_records = []
    if isinstance(records, list):
        for item in records:
            if not isinstance(item, dict):
                continue
            name = str(item.get("角色", "")).strip()
            from_r = as_int(item.get("fromR", 0))
            to_r = as_int(item.get("toR", 0))
            if name and 1 <= from_r <= 10 and 1 <= to_r <= 10 and to_r > from_r:
                normalized_records.append({"角色": name, "fromR": from_r, "toR": to_r})

    daily_income = data.get("daily_income")
    normalized_income = {field: 0 for field, _label in MATERIAL_FIELDS}
    if isinstance(daily_income, dict):
        for field, _label in MATERIAL_FIELDS:
            normalized_income[field] = as_int(daily_income.get(field, 0))

    return {
        "model_info": str(data.get("model_info", default["model_info"])),
        "upgrade_material_costs": normalized_rows,
        "upgrade_records": normalized_records,
        "daily_income": normalized_income,
    }


def load_data(data_file: Path = DATA_FILE) -> dict:
    ensure_data_file(data_file)
    try:
        loaded = json.loads(data_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        default = build_default_data()
        save_data(default, data_file)
        return default

    normalized = normalize_data(loaded)
    save_data(normalized, data_file)
    return normalized


def save_data(data: dict, data_file: Path = DATA_FILE) -> None:
    data_file.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def empty_material_totals() -> dict:
    return {field: 0 for field, _label in MATERIAL_FIELDS}


def calculate_record_materials(record: dict, cost_rows: list[dict]) -> dict:
    totals = empty_material_totals()
    from_r = as_int(record.get("fromR"))
    to_r = as_int(record.get("toR"))
    if not (1 <= from_r <= 10 and 1 <= to_r <= 10 and to_r > from_r):
        return totals

    for target_tier in range(from_r + 1, to_r + 1):
        row = cost_rows[target_tier - 1]
        for field, _label in MATERIAL_FIELDS:
            totals[field] += as_int(row.get(field, 0))
    return totals


def calculate_total_materials(records: list[dict], cost_rows: list[dict]) -> dict:
    totals = empty_material_totals()
    for record in records:
        record_total = calculate_record_materials(record, cost_rows)
        for field, _label in MATERIAL_FIELDS:
            totals[field] += record_total[field]
    return totals


def calculate_eta_days(total_materials: dict, daily_income: dict) -> dict:
    result = {}
    for field, _label in MATERIAL_FIELDS:
        need = as_int(total_materials.get(field, 0))
        income = as_int(daily_income.get(field, 0))
        if need == 0:
            result[field] = 0
        elif income == 0:
            result[field] = None
        else:
            result[field] = math.ceil(need / income)
    return result


if tk is not None:

    class DesktopApp(tk.Tk):
        def __init__(self) -> None:
            super().__init__()
            self.title("SWGOH Relic 材料汇总")
            self.geometry("1450x760")

            self.data = load_data()
            self.records = list(self.data.get("upgrade_records", []))
            self.daily_income_vars = {
                field: tk.StringVar(value=str(self.data["daily_income"].get(field, 0)))
                for field, _label in MATERIAL_FIELDS
            }

            self.name_var = tk.StringVar()
            self.from_var = tk.StringVar(value="1")
            self.to_var = tk.StringVar(value="2")

            self._build_ui()
            self.refresh_records_view()
            self.refresh_result_view()

        def _build_ui(self) -> None:
            input_frame = ttk.LabelFrame(self, text="角色升级输入")
            input_frame.pack(fill="x", padx=10, pady=8)

            ttk.Label(input_frame, text="角色名字").grid(row=0, column=0, padx=5, pady=8)
            ttk.Entry(input_frame, textvariable=self.name_var, width=24).grid(row=0, column=1, padx=5, pady=8)

            ttk.Label(input_frame, text="fromR").grid(row=0, column=2, padx=5, pady=8)
            ttk.Entry(input_frame, textvariable=self.from_var, width=6).grid(row=0, column=3, padx=5, pady=8)

            ttk.Label(input_frame, text="toR").grid(row=0, column=4, padx=5, pady=8)
            ttk.Entry(input_frame, textvariable=self.to_var, width=6).grid(row=0, column=5, padx=5, pady=8)

            ttk.Button(input_frame, text="添加记录", command=self.add_record).grid(row=0, column=6, padx=8, pady=8)
            ttk.Button(input_frame, text="删除选中", command=self.delete_selected_record).grid(row=0, column=7, padx=8, pady=8)

            records_frame = ttk.LabelFrame(self, text="已存储升级记录")
            records_frame.pack(fill="x", padx=10, pady=8)

            self.records_tree = ttk.Treeview(records_frame, columns=("角色", "fromR", "toR"), show="headings", height=6)
            self.records_tree.heading("角色", text="角色")
            self.records_tree.heading("fromR", text="fromR")
            self.records_tree.heading("toR", text="toR")
            self.records_tree.column("角色", width=220, anchor="center")
            self.records_tree.column("fromR", width=80, anchor="center")
            self.records_tree.column("toR", width=80, anchor="center")
            self.records_tree.pack(fill="x", padx=8, pady=8)

            income_frame = ttk.LabelFrame(self, text="每日材料收入")
            income_frame.pack(fill="x", padx=10, pady=8)

            for idx, (field, _label) in enumerate(MATERIAL_FIELDS):
                row = idx // 8
                col = (idx % 8) * 2
                ttk.Label(income_frame, text=field).grid(row=row, column=col, padx=4, pady=4, sticky="e")
                ttk.Entry(income_frame, textvariable=self.daily_income_vars[field], width=8).grid(
                    row=row,
                    column=col + 1,
                    padx=4,
                    pady=4,
                    sticky="w",
                )

            action_frame = ttk.Frame(self)
            action_frame.pack(fill="x", padx=10, pady=8)
            ttk.Button(action_frame, text="保存数据", command=self.save_all_data).pack(side="left", padx=6)
            ttk.Button(action_frame, text="重新计算", command=self.refresh_result_view).pack(side="left", padx=6)

            result_frame = ttk.LabelFrame(self, text="材料总需求 + 攒齐时间")
            result_frame.pack(fill="both", expand=True, padx=10, pady=8)

            self.result_tree = ttk.Treeview(
                result_frame,
                columns=("材料", "总需求", "每日收入", "攒齐天数"),
                show="headings",
                height=14,
            )
            for col, width in (("材料", 150), ("总需求", 120), ("每日收入", 120), ("攒齐天数", 120)):
                self.result_tree.heading(col, text=col)
                self.result_tree.column(col, width=width, anchor="center")
            self.result_tree.pack(fill="both", expand=True, padx=8, pady=8)

        def add_record(self) -> None:
            name = self.name_var.get().strip()
            from_r = as_int(self.from_var.get())
            to_r = as_int(self.to_var.get())

            if not name:
                messagebox.showwarning("输入错误", "请先输入角色名字")
                return
            if not (1 <= from_r <= 10 and 1 <= to_r <= 10 and to_r > from_r):
                messagebox.showwarning("输入错误", "fromR / toR 必须在 1~10 且 toR > fromR")
                return

            self.records.append({"角色": name, "fromR": from_r, "toR": to_r})
            self.refresh_records_view()
            self.refresh_result_view()

        def delete_selected_record(self) -> None:
            selected = self.records_tree.selection()
            if not selected:
                return

            indexes = sorted((self.records_tree.index(item) for item in selected), reverse=True)
            for idx in indexes:
                if 0 <= idx < len(self.records):
                    self.records.pop(idx)

            self.refresh_records_view()
            self.refresh_result_view()

        def refresh_records_view(self) -> None:
            for item in self.records_tree.get_children():
                self.records_tree.delete(item)

            for record in self.records:
                self.records_tree.insert(
                    "",
                    "end",
                    values=(record.get("角色", ""), record.get("fromR", 0), record.get("toR", 0)),
                )

        def _collect_daily_income(self) -> dict:
            return {field: as_int(var.get()) for field, var in self.daily_income_vars.items()}

        def refresh_result_view(self) -> None:
            daily_income = self._collect_daily_income()
            totals = calculate_total_materials(self.records, self.data["upgrade_material_costs"])
            eta = calculate_eta_days(totals, daily_income)

            for item in self.result_tree.get_children():
                self.result_tree.delete(item)

            for field, _label in MATERIAL_FIELDS:
                days = eta[field]
                days_text = "∞" if days is None else str(days)
                self.result_tree.insert("", "end", values=(field, totals[field], daily_income[field], days_text))

        def save_all_data(self) -> None:
            self.data["upgrade_records"] = list(self.records)
            self.data["daily_income"] = self._collect_daily_income()
            save_data(self.data)
            messagebox.showinfo("保存成功", f"已保存到 {DATA_FILE}")


def run_app() -> None:
    if tk is None:
        raise RuntimeError("当前 Python 环境缺少 tkinter，无法启动桌面 GUI。")
    app = DesktopApp()
    app.mainloop()


if __name__ == "__main__":
    run_app()

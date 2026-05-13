from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import messagebox, ttk
except ModuleNotFoundError:  # pragma: no cover
    tk = None
    messagebox = None
    ttk = None

def get_user_data_dir() -> Path:
    if os.name == "nt":
        base = os.environ.get("APPDATA")
        base_path = Path(base) if base else Path.home() / "AppData" / "Roaming"
    elif sys.platform == "darwin":
        base_path = Path.home() / "Library" / "Application Support"
    else:
        base = os.environ.get("XDG_DATA_HOME")
        base_path = Path(base) if base else Path.home() / ".local/share"
    return base_path / "swgoh-relic-sum"


def get_default_data_file() -> Path:
    if getattr(sys, "frozen", False):
        return get_user_data_dir() / "upgrade_material_costs.json"
    return Path(__file__).resolve().parent / "data" / "upgrade_material_costs.json"


DATA_FILE = get_default_data_file()
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
TODO_STATUS_OPTIONS = ["未完成", "完成"]


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
        "todo_list": [],
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

    todo_list = data.get("todo_list")
    normalized_todos = []
    if isinstance(todo_list, list):
        for item in todo_list:
            if not isinstance(item, dict):
                continue
            name = str(item.get("角色", "")).strip()
            task = str(item.get("任务", "")).strip()
            status = str(item.get("状态", "未完成")).strip()
            if not task:
                continue
            if status not in TODO_STATUS_OPTIONS:
                status = "未完成"
            normalized_todos.append({"角色": name, "任务": task, "状态": status})

    return {
        "model_info": str(data.get("model_info", default["model_info"])),
        "upgrade_material_costs": normalized_rows,
        "upgrade_records": normalized_records,
        "todo_list": normalized_todos,
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
            self.geometry("1500x820")

            self.data = load_data()
            self.records = list(self.data.get("upgrade_records", []))
            self.todo_items = list(self.data.get("todo_list", []))
            self.daily_income_vars = {
                field: tk.StringVar(value=str(self.data["daily_income"].get(field, 0)))
                for field, _label in MATERIAL_FIELDS
            }

            self.selected_record_index = None
            self.selected_todo_index = None
            self.name_var = tk.StringVar()
            self.from_var = tk.StringVar(value="1")
            self.to_var = tk.StringVar(value="2")
            self.todo_name_var = tk.StringVar()
            self.todo_task_var = tk.StringVar()
            self.todo_status_var = tk.StringVar(value=TODO_STATUS_OPTIONS[0])
            self.rank_sort_var = tk.StringVar(value="总材料")
            self.rank_order_var = tk.StringVar(value="降序")

            self._build_ui()
            self.refresh_records_view()
            self.refresh_todo_view()
            self.refresh_result_view()
            self.protocol("WM_DELETE_WINDOW", self.on_close)

        def _build_ui(self) -> None:
            header_frame = ttk.Frame(self)
            header_frame.pack(fill="x", padx=10, pady=(8, 0))
            ttk.Label(header_frame, text=f"数据文件: {DATA_FILE}").pack(side="left")

            notebook = ttk.Notebook(self)
            notebook.pack(fill="both", expand=True, padx=10, pady=8)

            record_tab = ttk.Frame(notebook)
            todo_tab = ttk.Frame(notebook)
            stats_tab = ttk.Frame(notebook)
            ranking_tab = ttk.Frame(notebook)
            notebook.add(record_tab, text="升级记录")
            notebook.add(todo_tab, text="Todo")
            notebook.add(stats_tab, text="材料统计")
            notebook.add(ranking_tab, text="排行")

            input_frame = ttk.LabelFrame(record_tab, text="角色升级输入")
            input_frame.pack(fill="x", padx=10, pady=8)

            ttk.Label(input_frame, text="角色名字").grid(row=0, column=0, padx=5, pady=6)
            ttk.Entry(input_frame, textvariable=self.name_var, width=24).grid(row=0, column=1, padx=5, pady=6)

            ttk.Label(input_frame, text="fromR").grid(row=0, column=2, padx=5, pady=6)
            ttk.Entry(input_frame, textvariable=self.from_var, width=6).grid(row=0, column=3, padx=5, pady=6)

            ttk.Label(input_frame, text="toR").grid(row=0, column=4, padx=5, pady=6)
            ttk.Entry(input_frame, textvariable=self.to_var, width=6).grid(row=0, column=5, padx=5, pady=6)

            record_action_frame = ttk.Frame(input_frame)
            record_action_frame.grid(row=1, column=0, columnspan=6, padx=5, pady=(0, 8), sticky="w")
            ttk.Button(record_action_frame, text="添加记录", command=self.add_record).pack(side="left", padx=4)
            ttk.Button(record_action_frame, text="更新选中", command=self.update_selected_record).pack(side="left", padx=4)
            ttk.Button(record_action_frame, text="删除选中", command=self.delete_selected_record).pack(side="left", padx=4)
            ttk.Button(record_action_frame, text="清空选择", command=self.clear_record_selection).pack(side="left", padx=4)

            records_frame = ttk.LabelFrame(record_tab, text="已存储升级记录")
            records_frame.pack(fill="both", expand=True, padx=10, pady=8)

            records_container = ttk.Frame(records_frame)
            records_container.pack(fill="both", expand=True, padx=8, pady=8)
            self.records_tree = ttk.Treeview(records_container, columns=("角色", "fromR", "toR"), show="headings", height=8)
            self.records_tree.heading("角色", text="角色")
            self.records_tree.heading("fromR", text="fromR")
            self.records_tree.heading("toR", text="toR")
            self.records_tree.column("角色", width=220, anchor="center")
            self.records_tree.column("fromR", width=80, anchor="center")
            self.records_tree.column("toR", width=80, anchor="center")
            record_scroll = ttk.Scrollbar(records_container, orient="vertical", command=self.records_tree.yview)
            self.records_tree.configure(yscrollcommand=record_scroll.set)
            self.records_tree.pack(side="left", fill="both", expand=True)
            record_scroll.pack(side="right", fill="y")
            self.records_tree.bind("<<TreeviewSelect>>", self.on_record_select)

            todo_input_frame = ttk.LabelFrame(todo_tab, text="角色 Todo 输入")
            todo_input_frame.pack(fill="x", padx=10, pady=8)
            ttk.Label(todo_input_frame, text="角色名字").grid(row=0, column=0, padx=5, pady=6)
            ttk.Entry(todo_input_frame, textvariable=self.todo_name_var, width=20).grid(row=0, column=1, padx=5, pady=6)
            ttk.Label(todo_input_frame, text="任务内容").grid(row=0, column=2, padx=5, pady=6)
            ttk.Entry(todo_input_frame, textvariable=self.todo_task_var, width=40).grid(row=0, column=3, padx=5, pady=6)
            ttk.Label(todo_input_frame, text="状态").grid(row=0, column=4, padx=5, pady=6)
            ttk.Combobox(
                todo_input_frame,
                textvariable=self.todo_status_var,
                values=TODO_STATUS_OPTIONS,
                width=8,
                state="readonly",
            ).grid(row=0, column=5, padx=5, pady=6)

            todo_action_frame = ttk.Frame(todo_input_frame)
            todo_action_frame.grid(row=1, column=0, columnspan=6, padx=5, pady=(0, 8), sticky="w")
            ttk.Button(todo_action_frame, text="添加任务", command=self.add_todo).pack(side="left", padx=4)
            ttk.Button(todo_action_frame, text="更新选中", command=self.update_selected_todo).pack(side="left", padx=4)
            ttk.Button(todo_action_frame, text="删除选中", command=self.delete_selected_todo).pack(side="left", padx=4)
            ttk.Button(todo_action_frame, text="清空选择", command=self.clear_todo_selection).pack(side="left", padx=4)

            todo_frame = ttk.LabelFrame(todo_tab, text="Todo 列表")
            todo_frame.pack(fill="both", expand=True, padx=10, pady=8)
            todo_container = ttk.Frame(todo_frame)
            todo_container.pack(fill="both", expand=True, padx=8, pady=8)
            self.todo_tree = ttk.Treeview(todo_container, columns=("角色", "任务", "状态"), show="headings", height=8)
            self.todo_tree.heading("角色", text="角色")
            self.todo_tree.heading("任务", text="任务")
            self.todo_tree.heading("状态", text="状态")
            self.todo_tree.column("角色", width=200, anchor="center")
            self.todo_tree.column("任务", width=480, anchor="w")
            self.todo_tree.column("状态", width=120, anchor="center")
            todo_scroll = ttk.Scrollbar(todo_container, orient="vertical", command=self.todo_tree.yview)
            self.todo_tree.configure(yscrollcommand=todo_scroll.set)
            self.todo_tree.pack(side="left", fill="both", expand=True)
            todo_scroll.pack(side="right", fill="y")
            self.todo_tree.bind("<<TreeviewSelect>>", self.on_todo_select)

            income_frame = ttk.LabelFrame(stats_tab, text="每日材料收入")
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

            result_frame = ttk.LabelFrame(stats_tab, text="材料总需求 + 攒齐时间")
            result_frame.pack(fill="both", expand=True, padx=10, pady=8)
            result_container = ttk.Frame(result_frame)
            result_container.pack(fill="both", expand=True, padx=8, pady=8)
            self.result_tree = ttk.Treeview(
                result_container,
                columns=("材料", "总需求", "每日收入", "攒齐天数"),
                show="headings",
                height=14,
            )
            for col, width in (("材料", 150), ("总需求", 120), ("每日收入", 120), ("攒齐天数", 120)):
                self.result_tree.heading(col, text=col)
                self.result_tree.column(col, width=width, anchor="center")
            result_scroll = ttk.Scrollbar(result_container, orient="vertical", command=self.result_tree.yview)
            self.result_tree.configure(yscrollcommand=result_scroll.set)
            self.result_tree.pack(side="left", fill="both", expand=True)
            result_scroll.pack(side="right", fill="y")

            ranking_control = ttk.Frame(ranking_tab)
            ranking_control.pack(fill="x", padx=10, pady=8)
            ttk.Label(ranking_control, text="排序依据").pack(side="left", padx=4)
            ttk.Combobox(
                ranking_control,
                textvariable=self.rank_sort_var,
                values=["总材料", "记录数", "最慢天数"],
                width=10,
                state="readonly",
            ).pack(side="left", padx=4)
            ttk.Label(ranking_control, text="顺序").pack(side="left", padx=4)
            ttk.Combobox(
                ranking_control,
                textvariable=self.rank_order_var,
                values=["降序", "升序"],
                width=6,
                state="readonly",
            ).pack(side="left", padx=4)
            ttk.Button(ranking_control, text="刷新排行", command=self.refresh_ranking_view).pack(side="left", padx=6)

            ranking_frame = ttk.LabelFrame(ranking_tab, text="角色排行")
            ranking_frame.pack(fill="both", expand=True, padx=10, pady=8)
            ranking_container = ttk.Frame(ranking_frame)
            ranking_container.pack(fill="both", expand=True, padx=8, pady=8)
            self.ranking_tree = ttk.Treeview(
                ranking_container,
                columns=("排名", "角色", "记录数", "总材料", "最慢天数"),
                show="headings",
                height=12,
            )
            for col, width in (
                ("排名", 80),
                ("角色", 200),
                ("记录数", 100),
                ("总材料", 120),
                ("最慢天数", 120),
            ):
                self.ranking_tree.heading(col, text=col)
                self.ranking_tree.column(col, width=width, anchor="center")
            ranking_scroll = ttk.Scrollbar(ranking_container, orient="vertical", command=self.ranking_tree.yview)
            self.ranking_tree.configure(yscrollcommand=ranking_scroll.set)
            self.ranking_tree.pack(side="left", fill="both", expand=True)
            ranking_scroll.pack(side="right", fill="y")

            action_frame = ttk.Frame(self)
            action_frame.pack(fill="x", padx=10, pady=(0, 8))
            ttk.Button(action_frame, text="保存数据", command=self.save_all_data).pack(side="left", padx=6)
            ttk.Button(
                action_frame,
                text="重新计算",
                command=lambda: self.refresh_result_view(save=True),
            ).pack(side="left", padx=6)

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
            self.persist_data()
            self.clear_record_selection()

        def update_selected_record(self) -> None:
            if self.selected_record_index is None:
                messagebox.showwarning("操作提示", "请先选择需要更新的记录")
                return

            name = self.name_var.get().strip()
            from_r = as_int(self.from_var.get())
            to_r = as_int(self.to_var.get())
            if not name:
                messagebox.showwarning("输入错误", "请先输入角色名字")
                return
            if not (1 <= from_r <= 10 and 1 <= to_r <= 10 and to_r > from_r):
                messagebox.showwarning("输入错误", "fromR / toR 必须在 1~10 且 toR > fromR")
                return

            if 0 <= self.selected_record_index < len(self.records):
                self.records[self.selected_record_index] = {"角色": name, "fromR": from_r, "toR": to_r}
            self.refresh_records_view()
            self.refresh_result_view()
            self.persist_data()
            self.clear_record_selection()

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
            self.persist_data()
            self.clear_record_selection()

        def clear_record_selection(self) -> None:
            for item in self.records_tree.selection():
                self.records_tree.selection_remove(item)
            self.selected_record_index = None
            self.name_var.set("")
            self.from_var.set("1")
            self.to_var.set("2")

        def on_record_select(self, _event: object = None) -> None:
            selected = self.records_tree.selection()
            if not selected:
                self.selected_record_index = None
                return
            idx = self.records_tree.index(selected[0])
            if 0 <= idx < len(self.records):
                record = self.records[idx]
                self.selected_record_index = idx
                self.name_var.set(record.get("角色", ""))
                self.from_var.set(str(record.get("fromR", 1)))
                self.to_var.set(str(record.get("toR", 2)))

        def refresh_records_view(self) -> None:
            for item in self.records_tree.get_children():
                self.records_tree.delete(item)

            for record in self.records:
                self.records_tree.insert(
                    "",
                    "end",
                    values=(record.get("角色", ""), record.get("fromR", 0), record.get("toR", 0)),
                )

        def add_todo(self) -> None:
            name = self.todo_name_var.get().strip()
            task = self.todo_task_var.get().strip()
            status = self.todo_status_var.get().strip()
            if not task:
                messagebox.showwarning("输入错误", "请填写任务内容")
                return
            if status not in TODO_STATUS_OPTIONS:
                status = TODO_STATUS_OPTIONS[0]

            self.todo_items.append({"角色": name, "任务": task, "状态": status})
            self.refresh_todo_view()
            self.persist_data()
            self.clear_todo_selection()

        def update_selected_todo(self) -> None:
            if self.selected_todo_index is None:
                messagebox.showwarning("操作提示", "请先选择需要更新的任务")
                return
            name = self.todo_name_var.get().strip()
            task = self.todo_task_var.get().strip()
            status = self.todo_status_var.get().strip()
            if not task:
                messagebox.showwarning("输入错误", "请填写任务内容")
                return
            if status not in TODO_STATUS_OPTIONS:
                status = TODO_STATUS_OPTIONS[0]

            if 0 <= self.selected_todo_index < len(self.todo_items):
                self.todo_items[self.selected_todo_index] = {"角色": name, "任务": task, "状态": status}
            self.refresh_todo_view()
            self.persist_data()
            self.clear_todo_selection()

        def delete_selected_todo(self) -> None:
            selected = self.todo_tree.selection()
            if not selected:
                return

            indexes = sorted((self.todo_tree.index(item) for item in selected), reverse=True)
            for idx in indexes:
                if 0 <= idx < len(self.todo_items):
                    self.todo_items.pop(idx)
            self.refresh_todo_view()
            self.persist_data()
            self.clear_todo_selection()

        def clear_todo_selection(self) -> None:
            for item in self.todo_tree.selection():
                self.todo_tree.selection_remove(item)
            self.selected_todo_index = None
            self.todo_name_var.set("")
            self.todo_task_var.set("")
            self.todo_status_var.set(TODO_STATUS_OPTIONS[0])

        def on_todo_select(self, _event: object = None) -> None:
            selected = self.todo_tree.selection()
            if not selected:
                self.selected_todo_index = None
                return
            idx = self.todo_tree.index(selected[0])
            if 0 <= idx < len(self.todo_items):
                item = self.todo_items[idx]
                self.selected_todo_index = idx
                self.todo_name_var.set(item.get("角色", ""))
                self.todo_task_var.set(item.get("任务", ""))
                self.todo_status_var.set(item.get("状态", TODO_STATUS_OPTIONS[0]))

        def refresh_todo_view(self) -> None:
            for item in self.todo_tree.get_children():
                self.todo_tree.delete(item)

            for todo in self.todo_items:
                self.todo_tree.insert(
                    "",
                    "end",
                    values=(todo.get("角色", ""), todo.get("任务", ""), todo.get("状态", "")),
                )

        def _collect_daily_income(self) -> dict:
            return {field: as_int(var.get()) for field, var in self.daily_income_vars.items()}

        def refresh_result_view(self, save: bool = False) -> None:
            daily_income = self._collect_daily_income()
            totals = calculate_total_materials(self.records, self.data["upgrade_material_costs"])
            eta = calculate_eta_days(totals, daily_income)

            for item in self.result_tree.get_children():
                self.result_tree.delete(item)

            for field, _label in MATERIAL_FIELDS:
                days = eta[field]
                days_text = "∞" if days is None else str(days)
                self.result_tree.insert("", "end", values=(field, totals[field], daily_income[field], days_text))
            self.refresh_ranking_view()
            if save:
                self.persist_data()

        def _build_ranking_rows(self) -> list[dict]:
            per_character: dict[str, dict] = {}
            for record in self.records:
                name = str(record.get("角色", "")).strip()
                if not name:
                    continue
                entry = per_character.setdefault(
                    name,
                    {"record_count": 0, "materials": empty_material_totals()},
                )
                entry["record_count"] += 1
                record_total = calculate_record_materials(record, self.data["upgrade_material_costs"])
                for field, _label in MATERIAL_FIELDS:
                    entry["materials"][field] += record_total[field]

            daily_income = self._collect_daily_income()
            rows = []
            for name, entry in per_character.items():
                total_materials = sum(entry["materials"].values())
                eta = calculate_eta_days(entry["materials"], daily_income)
                max_days = 0
                has_infinite = False
                for field, _label in MATERIAL_FIELDS:
                    days = eta[field]
                    if days is None:
                        has_infinite = True
                    else:
                        max_days = max(max_days, days)
                rows.append(
                    {
                        "name": name,
                        "record_count": entry["record_count"],
                        "total_materials": total_materials,
                        "max_days": None if has_infinite else max_days,
                    }
                )
            return rows

        def refresh_ranking_view(self) -> None:
            rows = self._build_ranking_rows()
            sort_key_map = {"总材料": "total_materials", "记录数": "record_count", "最慢天数": "max_days"}
            sort_key = sort_key_map.get(self.rank_sort_var.get(), "total_materials")
            reverse = self.rank_order_var.get() == "降序"

            def sort_value(item: dict) -> float:
                value = item[sort_key]
                if value is None:
                    return math.inf
                return value

            rows.sort(key=sort_value, reverse=reverse)

            for item in self.ranking_tree.get_children():
                self.ranking_tree.delete(item)

            for idx, row in enumerate(rows, start=1):
                days = row["max_days"]
                days_text = "∞" if days is None else str(days)
                self.ranking_tree.insert(
                    "",
                    "end",
                    values=(idx, row["name"], row["record_count"], row["total_materials"], days_text),
                )

        def persist_data(self, show_message: bool = False) -> None:
            self.data["upgrade_records"] = list(self.records)
            self.data["todo_list"] = list(self.todo_items)
            self.data["daily_income"] = self._collect_daily_income()
            save_data(self.data)
            if show_message:
                messagebox.showinfo("保存成功", f"已保存到 {DATA_FILE}")

        def save_all_data(self) -> None:
            self.persist_data(show_message=True)

        def on_close(self) -> None:
            self.persist_data()
            self.destroy()


def run_app() -> None:
    if tk is None:
        raise RuntimeError("当前 Python 环境缺少 tkinter，无法启动桌面 GUI。")
    app = DesktopApp()
    app.mainloop()


if __name__ == "__main__":
    run_app()

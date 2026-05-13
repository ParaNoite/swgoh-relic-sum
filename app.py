from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import font as tkfont
    from tkinter import messagebox, ttk
except ModuleNotFoundError:  # pragma: no cover
    tk = None
    tkfont = None
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
    ("断片", "断片"),
    ("最牛逼那啥", "最牛逼那啥"),
]
CURRENCY_FIELDS = [
    ("黄能量", "黄能量"),
    ("红能量", "红能量"),
    ("蓝能量", "蓝能量"),
    ("raidmk1", "raidmk1"),
    ("raidmk2", "raidmk2"),
    ("raidmk3", "raidmk3"),
    ("guildmk1", "guildmk1"),
    ("guildmk2", "guildmk2"),
    ("guildmk3", "guildmk3"),
]
CURRENCY_PERIODS = [
    ("daily", "每日"),
    ("weekly", "每周"),
    ("monthly", "每月"),
]
DEFAULT_EXCHANGE_LIMITS = {
    "raidmk1": 75,
    "raidmk2": 10,
    "raidmk3": 5,
}
DEFAULT_MATERIAL_EXCHANGE = {
    "灰信号": ("guildmk1", 0.6666),
    "绿信号": ("guildmk2", 1.0),
    "蓝信号": ("guildmk3", 1.5),
    "暗信号": ("guildmk3", 0),
    "青铜线缆": ("raidmk1", 35),
    "铬晶体管": ("raidmk1", 40),
    "奥罗德散热器": ("raidmk1", 50),
    "电金导体": ("raidmk1", 55),
    "金必得卡牌": ("raidmk2", 75),
    "脉冲放大": ("raidmk2", 100),
    "航空放大": ("raidmk3", 285),
    "键盘": ("raidmk3", 200),
    "断片": ("raidmk3", 85),
    "最牛逼那啥": ("raidmk3", 750),
}
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
LEGACY_MATERIAL_FIELD_ALIASES = {
    "断片": "两片东西",
    "最牛逼那啥": "最牛逼那个",
}
SIGNAL_EXCHANGE_CURRENCIES = {"guildmk1", "guildmk2", "guildmk3"}
RAID_EXCHANGE_CURRENCIES = {"raidmk1", "raidmk2", "raidmk3"}
SIGNAL_MATERIAL_FIELDS = {"灰信号", "绿信号", "蓝信号", "暗信号"}
RAID_MATERIAL_FIELDS = {
    "青铜线缆",
    "铬晶体管",
    "奥罗德散热器",
    "电金导体",
    "金必得卡牌",
    "脉冲放大",
    "航空放大",
    "键盘",
    "断片",
    "最牛逼那啥",
}
TODO_STATUS_OPTIONS = ["未完成", "完成"]


def build_default_exchange_rates() -> dict:
    default_currency = {field: "红能量" for field, _label in MATERIAL_FIELDS}
    for material, (currency, _price) in DEFAULT_MATERIAL_EXCHANGE.items():
        default_currency[material] = currency
    rates = {}
    for material, _label in MATERIAL_FIELDS:
        currency = default_currency[material]
        price = DEFAULT_MATERIAL_EXCHANGE.get(material, (currency, 0.0))[1]
        rates[material] = {"currency": currency, "price": price}
    return rates


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
        "currency_income": {
            currency: {period: 0 for period, _label in CURRENCY_PERIODS}
            for currency, _label in CURRENCY_FIELDS
        },
        "currency_inventory": {currency: 0 for currency, _label in CURRENCY_FIELDS},
        "material_inventory": {field: 0 for field, _label in MATERIAL_FIELDS},
        "exchange_rates": build_default_exchange_rates(),
        "exchange_limits": dict(DEFAULT_EXCHANGE_LIMITS),
    }


def as_int(value: object) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def as_float(value: object) -> float:
    try:
        return max(0.0, float(value))
    except (TypeError, ValueError):
        return 0.0


def get_material_value(source: dict, field: str, fallback: object = 0) -> object:
    if not isinstance(source, dict):
        return fallback
    if field in source:
        return source.get(field, fallback)
    legacy_field = LEGACY_MATERIAL_FIELD_ALIASES.get(field)
    if legacy_field and legacy_field in source:
        return source.get(legacy_field, fallback)
    return fallback


def allowed_currencies_for_material(material: str) -> set[str]:
    if material in SIGNAL_MATERIAL_FIELDS:
        return set(SIGNAL_EXCHANGE_CURRENCIES)
    if material in RAID_MATERIAL_FIELDS:
        return set(RAID_EXCHANGE_CURRENCIES)
    return {currency for currency, _label in CURRENCY_FIELDS}


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
            row[field] = as_int(get_material_value(source, field, fallback_row[field]))
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
            normalized_income[field] = as_float(get_material_value(daily_income, field, 0))

    todo_list = data.get("todo_list")
    normalized_todos = []
    if isinstance(todo_list, list):
        for item in todo_list:
            if not isinstance(item, dict):
                continue
            name = str(item.get("角色", "")).strip()
            from_r = as_int(item.get("fromR", 0))
            to_r = as_int(item.get("toR", 0))
            from_sharp = as_int(item.get("fromSharp", 0))
            to_sharp = as_int(item.get("toSharp", 0))
            note = str(item.get("注释", item.get("任务", ""))).strip()
            status = str(item.get("状态", "未完成")).strip()
            deducted = bool(item.get("已扣除", False))
            if status not in TODO_STATUS_OPTIONS:
                status = "未完成"
            normalized_todos.append(
                {
                    "角色": name,
                    "fromR": from_r,
                    "toR": to_r,
                    "fromSharp": from_sharp,
                    "toSharp": to_sharp,
                    "注释": note,
                    "状态": status,
                    "已扣除": deducted,
                }
            )

    if normalized_records:
        existing_keys = {
            (item.get("角色", ""), item.get("fromR", 0), item.get("toR", 0))
            for item in normalized_todos
        }
        for record in normalized_records:
            key = (record["角色"], record["fromR"], record["toR"])
            if key in existing_keys:
                continue
            normalized_todos.append(
                {
                    "角色": record["角色"],
                    "fromR": record["fromR"],
                    "toR": record["toR"],
                    "fromSharp": 0,
                    "toSharp": 0,
                    "注释": "",
                    "状态": "未完成",
                    "已扣除": False,
                }
            )

    currency_names = {currency for currency, _label in CURRENCY_FIELDS}
    currency_income = data.get("currency_income")
    normalized_currency_income = {
        currency: {period: 0 for period, _label in CURRENCY_PERIODS}
        for currency, _label in CURRENCY_FIELDS
    }
    if isinstance(currency_income, dict):
        for currency, _label in CURRENCY_FIELDS:
            entry = currency_income.get(currency)
            if isinstance(entry, dict):
                for period, _label in CURRENCY_PERIODS:
                    normalized_currency_income[currency][period] = as_float(entry.get(period, 0))

    currency_inventory = data.get("currency_inventory")
    normalized_currency_inventory = {currency: 0 for currency, _label in CURRENCY_FIELDS}
    if isinstance(currency_inventory, dict):
        for currency, _label in CURRENCY_FIELDS:
            normalized_currency_inventory[currency] = as_float(currency_inventory.get(currency, 0))

    material_inventory = data.get("material_inventory")
    normalized_material_inventory = {field: 0 for field, _label in MATERIAL_FIELDS}
    if isinstance(material_inventory, dict):
        for field, _label in MATERIAL_FIELDS:
            normalized_material_inventory[field] = as_float(get_material_value(material_inventory, field, 0))

    exchange_rates = data.get("exchange_rates")
    normalized_exchange_rates = build_default_exchange_rates()
    if isinstance(exchange_rates, dict):
        for field, _label in MATERIAL_FIELDS:
            entry = get_material_value(exchange_rates, field)
            if isinstance(entry, dict):
                currency = str(entry.get("currency", normalized_exchange_rates[field]["currency"])).strip()
                allowed_currencies = allowed_currencies_for_material(field)
                if currency not in currency_names or currency not in allowed_currencies:
                    currency = normalized_exchange_rates[field]["currency"]
                price = as_float(entry.get("price", normalized_exchange_rates[field]["price"]))
                normalized_exchange_rates[field] = {"currency": currency, "price": price}

    exchange_limits = data.get("exchange_limits")
    normalized_exchange_limits = dict(DEFAULT_EXCHANGE_LIMITS)
    if isinstance(exchange_limits, dict):
        for currency, default_limit in DEFAULT_EXCHANGE_LIMITS.items():
            normalized_exchange_limits[currency] = as_int(exchange_limits.get(currency, default_limit))

    return {
        "model_info": str(data.get("model_info", default["model_info"])),
        "upgrade_material_costs": normalized_rows,
        "upgrade_records": normalized_records,
        "todo_list": normalized_todos,
        "daily_income": normalized_income,
        "currency_income": normalized_currency_income,
        "currency_inventory": normalized_currency_inventory,
        "material_inventory": normalized_material_inventory,
        "exchange_rates": normalized_exchange_rates,
        "exchange_limits": normalized_exchange_limits,
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


def is_todo_pending(item: dict) -> bool:
    status = str(item.get("状态", "未完成")).strip()
    return status != "完成"


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
        if not is_todo_pending(record):
            continue
        record_total = calculate_record_materials(record, cost_rows)
        for field, _label in MATERIAL_FIELDS:
            totals[field] += record_total[field]
    return totals


def calculate_single_character_cultivation(
    records: list[dict],
    cost_rows: list[dict],
    daily_income: dict,
    character_name: str,
) -> dict:
    name = str(character_name).strip()
    selected_records = [
        item
        for item in records
        if str(item.get("角色", "")).strip() == name and is_todo_pending(item)
    ]
    totals = calculate_total_materials(selected_records, cost_rows)
    eta = calculate_eta_days(totals, daily_income)
    max_days = 0
    has_infinite = False
    for field, _label in MATERIAL_FIELDS:
        days = eta[field]
        if days is None:
            has_infinite = True
        else:
            max_days = max(max_days, days)
    return {
        "name": name,
        "record_count": len(selected_records),
        "total_materials": totals,
        "eta": eta,
        "max_days": None if has_infinite else max_days,
    }


def calculate_eta_days(total_materials: dict, daily_income: dict) -> dict:
    result = {}
    for field, _label in MATERIAL_FIELDS:
        need = as_int(total_materials.get(field, 0))
        income = as_float(daily_income.get(field, 0))
        if need == 0:
            result[field] = 0
        elif income <= 0:
            result[field] = None
        else:
            result[field] = math.ceil(need / income)
    return result


def calculate_currency_daily_income(currency_income: dict) -> dict:
    result = {}
    for currency, _label in CURRENCY_FIELDS:
        entry = currency_income.get(currency, {}) if isinstance(currency_income, dict) else {}
        daily = as_float(entry.get("daily", 0))
        weekly = as_float(entry.get("weekly", 0))
        monthly = as_float(entry.get("monthly", 0))
        result[currency] = daily + weekly / 7 + monthly / 30
    return result


def calculate_currency_material_income(
    required_materials: dict,
    currency_daily_income: dict,
    exchange_rates: dict,
    exchange_limits: dict,
) -> dict:
    income = {field: 0.0 for field, _label in MATERIAL_FIELDS}
    materials_by_currency: dict[str, list[tuple[str, float]]] = {}
    for field, _label in MATERIAL_FIELDS:
        rate = exchange_rates.get(field, {}) if isinstance(exchange_rates, dict) else {}
        currency = str(rate.get("currency", "")).strip()
        price = as_float(rate.get("price", 0))
        if not currency or price <= 0:
            continue
        materials_by_currency.setdefault(currency, []).append((field, price))

    for currency, materials in materials_by_currency.items():
        total_cost = 0.0
        material_costs = {}
        for field, price in materials:
            required = as_int(required_materials.get(field, 0))
            cost = required * price
            material_costs[field] = cost
            total_cost += cost
        if total_cost <= 0:
            continue

        currency_amount = as_float(currency_daily_income.get(currency, 0))
        if currency_amount <= 0:
            continue

        material_units = {}
        total_units = 0.0
        for field, price in materials:
            share = material_costs[field] / total_cost
            units = (currency_amount * share) / price if price > 0 else 0.0
            material_units[field] = units
            total_units += units

        limit = exchange_limits.get(currency)
        if limit is not None:
            limit_value = as_float(limit)
            if limit_value > 0 and total_units > limit_value:
                scale = limit_value / total_units
                for field in material_units:
                    material_units[field] *= scale

        for field, units in material_units.items():
            income[field] += units

    return income


def calculate_effective_daily_income(
    material_daily_income: dict,
    currency_income: dict,
    exchange_rates: dict,
    exchange_limits: dict,
    required_materials: dict,
) -> dict:
    currency_daily_income = calculate_currency_daily_income(currency_income)
    currency_material_income = calculate_currency_material_income(
        required_materials,
        currency_daily_income,
        exchange_rates,
        exchange_limits,
    )
    effective = {}
    for field, _label in MATERIAL_FIELDS:
        effective[field] = as_float(material_daily_income.get(field, 0)) + as_float(
            currency_material_income.get(field, 0)
        )
    return effective


if tk is not None:

    class DesktopApp(tk.Tk):
        def __init__(self) -> None:
            super().__init__()
            self.title("SWGOH Relic 材料汇总")
            self.geometry("1500x820")

            self.data = load_data()
            self.todo_items = list(self.data.get("todo_list", []))
            self.daily_income_vars = {
                field: tk.StringVar(value=str(self.data["daily_income"].get(field, 0)))
                for field, _label in MATERIAL_FIELDS
            }
            self.currency_income_vars = {
                currency: {
                    period: tk.StringVar(
                        value=str(self.data["currency_income"][currency].get(period, 0))
                    )
                    for period, _label in CURRENCY_PERIODS
                }
                for currency, _label in CURRENCY_FIELDS
            }
            self.currency_inventory_vars = {
                currency: tk.StringVar(value=str(self.data["currency_inventory"].get(currency, 0)))
                for currency, _label in CURRENCY_FIELDS
            }
            self.material_inventory_vars = {
                field: tk.StringVar(value=str(self.data["material_inventory"].get(field, 0)))
                for field, _label in MATERIAL_FIELDS
            }
            self.exchange_rate_vars = {
                field: {
                    "currency": tk.StringVar(
                        value=str(self.data["exchange_rates"][field].get("currency", "红能量"))
                    ),
                    "price": tk.StringVar(
                        value=str(self.data["exchange_rates"][field].get("price", 0))
                    ),
                }
                for field, _label in MATERIAL_FIELDS
            }
            self.exchange_limit_vars = {
                currency: tk.StringVar(value=str(self.data["exchange_limits"].get(currency, 0)))
                for currency, _label in CURRENCY_FIELDS
                if currency in DEFAULT_EXCHANGE_LIMITS
            }

            self.selected_todo_index = None
            self.name_var = tk.StringVar()
            self.from_var = tk.StringVar(value="1")
            self.to_var = tk.StringVar(value="2")
            self.from_sharp_var = tk.StringVar(value="0")
            self.to_sharp_var = tk.StringVar(value="0")
            self.note_var = tk.StringVar()
            self.todo_status_var = tk.StringVar(value=TODO_STATUS_OPTIONS[0])
            self.single_character_var = tk.StringVar()
            self.single_character_result_var = tk.StringVar(value="请先添加角色计划")
            self.rank_sort_var = tk.StringVar(value="总材料")
            self.rank_order_var = tk.StringVar(value="降序")

            self._setup_styles()
            self._build_ui()
            self.refresh_todo_view()
            self.refresh_result_view()
            self.protocol("WM_DELETE_WINDOW", self.on_close)

        def _setup_styles(self) -> None:
            self.configure(bg="#f5f5f7")
            style = ttk.Style(self)
            try:
                style.theme_use("clam")
            except tk.TclError as exc:
                print(f"[style] clam theme unavailable: {exc}", file=sys.stderr)

            font_family = "TkDefaultFont"
            if tkfont is not None:
                available_fonts = set(tkfont.families())
                for candidate in ("SF Pro Text", "Helvetica Neue", "Segoe UI", "PingFang SC", "Arial"):
                    if candidate in available_fonts:
                        font_family = candidate
                        break

            style.configure(".", background="#f5f5f7", foreground="#1d1d1f", font=(font_family, 10))
            style.configure("TFrame", background="#f5f5f7")
            style.configure("TLabel", background="#f5f5f7", foreground="#1d1d1f")
            style.configure("TLabelframe", background="#f5f5f7")
            style.configure("TLabelframe.Label", background="#f5f5f7", foreground="#1d1d1f", font=(font_family, 10, "bold"))
            style.configure("TButton", padding=(10, 6), font=(font_family, 10))
            style.configure("TEntry", padding=6)
            style.configure("TCombobox", padding=4)
            style.configure("TNotebook", background="#f5f5f7", borderwidth=0)
            style.configure("TNotebook.Tab", padding=(16, 8), font=(font_family, 10, "bold"))
            style.map("TNotebook.Tab", background=[("selected", "#ffffff"), ("!selected", "#e9e9ee")])
            style.configure(
                "Treeview",
                background="#ffffff",
                fieldbackground="#ffffff",
                foreground="#1d1d1f",
                rowheight=28,
                borderwidth=0,
            )
            style.configure("Treeview.Heading", background="#ececf1", foreground="#1d1d1f", font=(font_family, 10, "bold"))

        def _build_ui(self) -> None:
            header_frame = ttk.Frame(self)
            header_frame.pack(fill="x", padx=10, pady=(8, 0))
            ttk.Label(header_frame, text=f"数据文件: {DATA_FILE}").pack(side="left")

            notebook = ttk.Notebook(self)
            notebook.pack(fill="both", expand=True, padx=10, pady=8)

            work_tab = ttk.Frame(notebook)
            stats_tab = ttk.Frame(notebook)
            ranking_tab = ttk.Frame(notebook)
            settings_tab = ttk.Frame(notebook)
            notebook.add(work_tab, text="升级与Todo")
            notebook.add(stats_tab, text="材料统计")
            notebook.add(ranking_tab, text="排行")
            notebook.add(settings_tab, text="设置")

            input_frame = ttk.LabelFrame(work_tab, text="角色计划输入")
            input_frame.pack(fill="x", padx=10, pady=8)

            ttk.Label(input_frame, text="角色名字").grid(row=0, column=0, padx=5, pady=6)
            ttk.Entry(input_frame, textvariable=self.name_var, width=18).grid(row=0, column=1, padx=5, pady=6)

            ttk.Label(input_frame, text="fromR").grid(row=0, column=2, padx=5, pady=6)
            ttk.Entry(input_frame, textvariable=self.from_var, width=6).grid(row=0, column=3, padx=5, pady=6)

            ttk.Label(input_frame, text="toR").grid(row=0, column=4, padx=5, pady=6)
            ttk.Entry(input_frame, textvariable=self.to_var, width=6).grid(row=0, column=5, padx=5, pady=6)

            ttk.Label(input_frame, text="fromSharp").grid(row=0, column=6, padx=5, pady=6)
            ttk.Entry(input_frame, textvariable=self.from_sharp_var, width=6).grid(row=0, column=7, padx=5, pady=6)

            ttk.Label(input_frame, text="toSharp").grid(row=0, column=8, padx=5, pady=6)
            ttk.Entry(input_frame, textvariable=self.to_sharp_var, width=6).grid(row=0, column=9, padx=5, pady=6)

            ttk.Label(input_frame, text="注释").grid(row=1, column=0, padx=5, pady=6)
            ttk.Entry(input_frame, textvariable=self.note_var, width=52).grid(
                row=1,
                column=1,
                columnspan=5,
                padx=5,
                pady=6,
                sticky="w",
            )
            ttk.Label(input_frame, text="状态").grid(row=1, column=6, padx=5, pady=6)
            ttk.Combobox(
                input_frame,
                textvariable=self.todo_status_var,
                values=TODO_STATUS_OPTIONS,
                width=8,
                state="readonly",
            ).grid(row=1, column=7, padx=5, pady=6, sticky="w")

            record_action_frame = ttk.Frame(input_frame)
            record_action_frame.grid(row=2, column=0, columnspan=10, padx=5, pady=(0, 8), sticky="w")
            ttk.Button(record_action_frame, text="添加计划", command=self.add_todo).pack(side="left", padx=4)
            ttk.Button(record_action_frame, text="更新选中", command=self.update_selected_todo).pack(side="left", padx=4)
            ttk.Button(record_action_frame, text="删除选中", command=self.delete_selected_todo).pack(side="left", padx=4)
            ttk.Button(record_action_frame, text="清空选择", command=self.clear_todo_selection).pack(side="left", padx=4)

            todo_frame = ttk.LabelFrame(work_tab, text="Todo 列表")
            todo_frame.pack(fill="both", expand=True, padx=10, pady=8)
            todo_container = ttk.Frame(todo_frame)
            todo_container.pack(fill="both", expand=True, padx=8, pady=8)
            self.todo_tree = ttk.Treeview(
                todo_container,
                columns=("角色", "fromR", "toR", "fromSharp", "toSharp", "注释", "状态"),
                show="headings",
                height=10,
            )
            self.todo_tree.heading("角色", text="角色")
            self.todo_tree.heading("fromR", text="fromR")
            self.todo_tree.heading("toR", text="toR")
            self.todo_tree.heading("fromSharp", text="fromSharp")
            self.todo_tree.heading("toSharp", text="toSharp")
            self.todo_tree.heading("注释", text="注释")
            self.todo_tree.heading("状态", text="状态")
            self.todo_tree.column("角色", width=160, anchor="center")
            self.todo_tree.column("fromR", width=80, anchor="center")
            self.todo_tree.column("toR", width=80, anchor="center")
            self.todo_tree.column("fromSharp", width=90, anchor="center")
            self.todo_tree.column("toSharp", width=90, anchor="center")
            self.todo_tree.column("注释", width=360, anchor="w")
            self.todo_tree.column("状态", width=120, anchor="center")
            todo_scroll = ttk.Scrollbar(todo_container, orient="vertical", command=self.todo_tree.yview)
            self.todo_tree.configure(yscrollcommand=todo_scroll.set)
            self.todo_tree.pack(side="left", fill="both", expand=True)
            todo_scroll.pack(side="right", fill="y")
            self.todo_tree.bind("<<TreeviewSelect>>", self.on_todo_select)

            single_character_frame = ttk.LabelFrame(stats_tab, text="单角色培养天数")
            single_character_frame.pack(fill="both", padx=10, pady=8)
            ttk.Label(single_character_frame, text="角色").grid(row=0, column=0, padx=5, pady=6)
            self.single_character_combo = ttk.Combobox(
                single_character_frame,
                textvariable=self.single_character_var,
                width=24,
                state="readonly",
            )
            self.single_character_combo.grid(row=0, column=1, padx=5, pady=6)
            ttk.Button(
                single_character_frame,
                text="计算单角色培养天数",
                command=self.calculate_single_character_days,
            ).grid(row=0, column=2, padx=6, pady=6, sticky="w")
            ttk.Label(single_character_frame, textvariable=self.single_character_result_var).grid(
                row=1,
                column=0,
                columnspan=3,
                padx=5,
                pady=(0, 6),
                sticky="w",
            )
            single_char_detail_container = ttk.Frame(single_character_frame)
            single_char_detail_container.grid(row=2, column=0, columnspan=3, padx=5, pady=(0, 6), sticky="nsew")
            single_character_frame.rowconfigure(2, weight=1)
            single_character_frame.columnconfigure(0, weight=1)
            self.single_char_detail_tree = ttk.Treeview(
                single_char_detail_container,
                columns=("材料", "总需求", "每日收入", "攒齐天数"),
                show="headings",
                height=6,
            )
            for col, width in (("材料", 150), ("总需求", 120), ("每日收入", 120), ("攒齐天数", 120)):
                self.single_char_detail_tree.heading(col, text=col)
                self.single_char_detail_tree.column(col, width=width, anchor="center")
            single_char_detail_scroll = ttk.Scrollbar(
                single_char_detail_container, orient="vertical", command=self.single_char_detail_tree.yview
            )
            self.single_char_detail_tree.configure(yscrollcommand=single_char_detail_scroll.set)
            self.single_char_detail_tree.pack(side="left", fill="both", expand=True)
            single_char_detail_scroll.pack(side="right", fill="y")

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

            currency_income_frame = ttk.LabelFrame(stats_tab, text="货币收入（每日/每周/每月）")
            currency_income_frame.pack(fill="x", padx=10, pady=8)
            ttk.Label(currency_income_frame, text="货币").grid(row=0, column=0, padx=4, pady=4)
            ttk.Label(currency_income_frame, text="每日").grid(row=0, column=1, padx=4, pady=4)
            ttk.Label(currency_income_frame, text="每周").grid(row=0, column=2, padx=4, pady=4)
            ttk.Label(currency_income_frame, text="每月").grid(row=0, column=3, padx=4, pady=4)
            for idx, (currency, _label) in enumerate(CURRENCY_FIELDS, start=1):
                ttk.Label(currency_income_frame, text=currency).grid(row=idx, column=0, padx=4, pady=4, sticky="e")
                ttk.Entry(
                    currency_income_frame,
                    textvariable=self.currency_income_vars[currency]["daily"],
                    width=10,
                ).grid(row=idx, column=1, padx=4, pady=4, sticky="w")
                ttk.Entry(
                    currency_income_frame,
                    textvariable=self.currency_income_vars[currency]["weekly"],
                    width=10,
                ).grid(row=idx, column=2, padx=4, pady=4, sticky="w")
                ttk.Entry(
                    currency_income_frame,
                    textvariable=self.currency_income_vars[currency]["monthly"],
                    width=10,
                ).grid(row=idx, column=3, padx=4, pady=4, sticky="w")

            result_frame = ttk.LabelFrame(stats_tab, text="全部角色 材料总需求 + 攒齐时间")
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
                columns=("排名", "角色", "记录数", "总材料", "最慢天数", "最慢材料"),
                show="headings",
                height=12,
            )
            for col, width in (
                ("排名", 80),
                ("角色", 200),
                ("记录数", 100),
                ("总材料", 120),
                ("最慢天数", 120),
                ("最慢材料", 150),
            ):
                self.ranking_tree.heading(col, text=col)
                self.ranking_tree.column(col, width=width, anchor="center")
            ranking_scroll = ttk.Scrollbar(ranking_container, orient="vertical", command=self.ranking_tree.yview)
            self.ranking_tree.configure(yscrollcommand=ranking_scroll.set)
            self.ranking_tree.pack(side="left", fill="both", expand=True)
            ranking_scroll.pack(side="right", fill="y")

            rates_frame = ttk.LabelFrame(settings_tab, text="货币-材料汇率")
            rates_frame.pack(fill="x", padx=10, pady=8)
            ttk.Label(rates_frame, text="材料").grid(row=0, column=0, padx=4, pady=4)
            ttk.Label(rates_frame, text="货币").grid(row=0, column=1, padx=4, pady=4)
            ttk.Label(rates_frame, text="单价").grid(row=0, column=2, padx=4, pady=4)
            for idx, (field, _label) in enumerate(MATERIAL_FIELDS, start=1):
                currency_options = sorted(allowed_currencies_for_material(field))
                ttk.Label(rates_frame, text=field).grid(row=idx, column=0, padx=4, pady=4, sticky="e")
                ttk.Combobox(
                    rates_frame,
                    textvariable=self.exchange_rate_vars[field]["currency"],
                    values=currency_options,
                    width=10,
                    state="readonly",
                ).grid(row=idx, column=1, padx=4, pady=4, sticky="w")
                ttk.Entry(
                    rates_frame,
                    textvariable=self.exchange_rate_vars[field]["price"],
                    width=8,
                ).grid(row=idx, column=2, padx=4, pady=4, sticky="w")

            limit_frame = ttk.LabelFrame(settings_tab, text="每日兑换上限")
            limit_frame.pack(fill="x", padx=10, pady=8)
            limit_currencies = [
                (currency, _label)
                for currency, _label in CURRENCY_FIELDS
                if currency in DEFAULT_EXCHANGE_LIMITS
            ]
            for idx, (currency, _label) in enumerate(limit_currencies):
                ttk.Label(limit_frame, text=currency).grid(row=0, column=idx * 2, padx=4, pady=4, sticky="e")
                ttk.Entry(limit_frame, textvariable=self.exchange_limit_vars[currency], width=8).grid(
                    row=0,
                    column=idx * 2 + 1,
                    padx=4,
                    pady=4,
                    sticky="w",
                )

            inventory_frame = ttk.LabelFrame(settings_tab, text="库存设置")
            inventory_frame.pack(fill="both", expand=True, padx=10, pady=8)
            material_inventory_frame = ttk.LabelFrame(inventory_frame, text="材料库存")
            material_inventory_frame.pack(fill="x", padx=8, pady=6)
            for idx, (field, _label) in enumerate(MATERIAL_FIELDS):
                row = idx // 8
                col = (idx % 8) * 2
                ttk.Label(material_inventory_frame, text=field).grid(
                    row=row,
                    column=col,
                    padx=4,
                    pady=4,
                    sticky="e",
                )
                ttk.Entry(
                    material_inventory_frame,
                    textvariable=self.material_inventory_vars[field],
                    width=8,
                ).grid(row=row, column=col + 1, padx=4, pady=4, sticky="w")

            currency_inventory_frame = ttk.LabelFrame(inventory_frame, text="货币库存")
            currency_inventory_frame.pack(fill="x", padx=8, pady=6)
            for idx, (currency, _label) in enumerate(CURRENCY_FIELDS):
                row = idx // 5
                col = (idx % 5) * 2
                ttk.Label(currency_inventory_frame, text=currency).grid(
                    row=row,
                    column=col,
                    padx=4,
                    pady=4,
                    sticky="e",
                )
                ttk.Entry(
                    currency_inventory_frame,
                    textvariable=self.currency_inventory_vars[currency],
                    width=8,
                ).grid(row=row, column=col + 1, padx=4, pady=4, sticky="w")

            action_frame = ttk.Frame(self)
            action_frame.pack(fill="x", padx=10, pady=(0, 8))
            ttk.Button(action_frame, text="保存数据", command=self.save_all_data).pack(side="left", padx=6)
            ttk.Button(
                action_frame,
                text="重新计算",
                command=lambda: self.refresh_result_view(save=True),
            ).pack(side="left", padx=6)

        def add_todo(self) -> None:
            name = self.name_var.get().strip()
            from_r = as_int(self.from_var.get())
            to_r = as_int(self.to_var.get())
            from_sharp = as_int(self.from_sharp_var.get())
            to_sharp = as_int(self.to_sharp_var.get())
            note = self.note_var.get().strip()
            status = self.todo_status_var.get().strip()
            if not name:
                messagebox.showwarning("输入错误", "请先输入角色名字")
                return
            if not (1 <= from_r <= 10 and 1 <= to_r <= 10 and to_r > from_r):
                messagebox.showwarning("输入错误", "fromR / toR 必须在 1~10 且 toR > fromR")
                return
            if to_sharp and to_sharp < from_sharp:
                messagebox.showwarning("输入错误", "toSharp 需要大于等于 fromSharp")
                return
            if status not in TODO_STATUS_OPTIONS:
                status = TODO_STATUS_OPTIONS[0]

            item = {
                "角色": name,
                "fromR": from_r,
                "toR": to_r,
                "fromSharp": from_sharp,
                "toSharp": to_sharp,
                "注释": note,
                "状态": status,
                "已扣除": False,
            }
            if status == "完成":
                item["已扣除"] = self.apply_todo_completion(item)
            self.todo_items.append(item)
            self.refresh_todo_view()
            self.refresh_result_view()
            self.persist_data()
            self.clear_todo_selection()

        def update_selected_todo(self) -> None:
            if self.selected_todo_index is None:
                messagebox.showwarning("操作提示", "请先选择需要更新的计划")
                return
            name = self.name_var.get().strip()
            from_r = as_int(self.from_var.get())
            to_r = as_int(self.to_var.get())
            from_sharp = as_int(self.from_sharp_var.get())
            to_sharp = as_int(self.to_sharp_var.get())
            note = self.note_var.get().strip()
            status = self.todo_status_var.get().strip()
            if not name:
                messagebox.showwarning("输入错误", "请先输入角色名字")
                return
            if not (1 <= from_r <= 10 and 1 <= to_r <= 10 and to_r > from_r):
                messagebox.showwarning("输入错误", "fromR / toR 必须在 1~10 且 toR > fromR")
                return
            if to_sharp and to_sharp < from_sharp:
                messagebox.showwarning("输入错误", "toSharp 需要大于等于 fromSharp")
                return
            if status not in TODO_STATUS_OPTIONS:
                status = TODO_STATUS_OPTIONS[0]

            if 0 <= self.selected_todo_index < len(self.todo_items):
                previous = self.todo_items[self.selected_todo_index]
                deducted = bool(previous.get("已扣除", False))
                updated = {
                    "角色": name,
                    "fromR": from_r,
                    "toR": to_r,
                    "fromSharp": from_sharp,
                    "toSharp": to_sharp,
                    "注释": note,
                    "状态": status,
                    "已扣除": deducted,
                }
                if status == "完成" and not deducted:
                    updated["已扣除"] = self.apply_todo_completion(updated)
                self.todo_items[self.selected_todo_index] = updated
            self.refresh_todo_view()
            self.refresh_result_view()
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
            self.refresh_result_view()
            self.persist_data()
            self.clear_todo_selection()

        def clear_todo_selection(self) -> None:
            for item in self.todo_tree.selection():
                self.todo_tree.selection_remove(item)
            self.selected_todo_index = None
            self.name_var.set("")
            self.from_var.set("1")
            self.to_var.set("2")
            self.from_sharp_var.set("0")
            self.to_sharp_var.set("0")
            self.note_var.set("")
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
                self.name_var.set(item.get("角色", ""))
                self.from_var.set(str(item.get("fromR", 1)))
                self.to_var.set(str(item.get("toR", 2)))
                self.from_sharp_var.set(str(item.get("fromSharp", 0)))
                self.to_sharp_var.set(str(item.get("toSharp", 0)))
                self.note_var.set(item.get("注释", ""))
                self.todo_status_var.set(item.get("状态", TODO_STATUS_OPTIONS[0]))

        def refresh_todo_view(self) -> None:
            for item in self.todo_tree.get_children():
                self.todo_tree.delete(item)

            for todo in self.todo_items:
                self.todo_tree.insert(
                    "",
                    "end",
                    values=(
                        todo.get("角色", ""),
                        todo.get("fromR", 0),
                        todo.get("toR", 0),
                        todo.get("fromSharp", 0),
                        todo.get("toSharp", 0),
                        todo.get("注释", ""),
                        todo.get("状态", ""),
                    ),
                )
            self._refresh_single_character_options()

        def apply_todo_completion(self, item: dict) -> bool:
            required = calculate_record_materials(item, self.data["upgrade_material_costs"])
            material_inventory = self._collect_material_inventory()
            currency_inventory = self._collect_currency_inventory()
            exchange_rates = self._collect_exchange_rates()

            for field, amount in required.items():
                if amount <= 0:
                    continue
                available = as_float(material_inventory.get(field, 0))
                if available >= amount:
                    material_inventory[field] = available - amount
                    missing = 0
                else:
                    missing = amount - available
                    material_inventory[field] = 0

                rate = exchange_rates.get(field, {})
                currency = str(rate.get("currency", "")).strip()
                price = as_float(rate.get("price", 0))
                if missing > 0 and currency and price > 0:
                    currency_inventory[currency] = max(
                        0.0,
                        as_float(currency_inventory.get(currency, 0)) - missing * price,
                    )

            for field, value in material_inventory.items():
                self.material_inventory_vars[field].set(self._format_number(value))
            for currency, value in currency_inventory.items():
                if currency in self.currency_inventory_vars:
                    self.currency_inventory_vars[currency].set(self._format_number(value))
            return True

        def _refresh_single_character_options(self) -> None:
            names = sorted(
                {
                    str(record.get("角色", "")).strip()
                    for record in self.todo_items
                    if str(record.get("角色", "")).strip()
                }
            )
            self.single_character_combo["values"] = names
            if self.single_character_var.get() not in names:
                self.single_character_var.set(names[0] if names else "")
                if names:
                    self.single_character_result_var.set("请选择角色后计算培养天数")
                else:
                    self.single_character_result_var.set("请先添加角色计划")

        def calculate_single_character_days(self) -> None:
            name = self.single_character_var.get().strip()
            if not name:
                messagebox.showwarning("操作提示", "请先选择一个角色")
                return
            selected_records = [
                item
                for item in self.todo_items
                if str(item.get("角色", "")).strip() == name and is_todo_pending(item)
            ]
            for item in self.single_char_detail_tree.get_children():
                self.single_char_detail_tree.delete(item)
            if not selected_records:
                self.single_character_result_var.set(f"{name} 暂无升级计划")
                return
            totals = calculate_total_materials(selected_records, self.data["upgrade_material_costs"])
            daily_income = self._calculate_effective_daily_income(totals)
            result = calculate_single_character_cultivation(
                selected_records,
                self.data["upgrade_material_costs"],
                daily_income,
                name,
            )
            days = result["max_days"]
            total_count = sum(result["total_materials"].values())
            days_text = "∞" if days is None else str(days)
            self.single_character_result_var.set(
                f"{name}：计划 {result['record_count']} 条，材料总量 {total_count}，预计培养天数 {days_text} 天"
            )
            eta = result["eta"]
            for field, _label in MATERIAL_FIELDS:
                need = totals[field]
                if need == 0:
                    continue
                days_val = eta[field]
                days_str = "∞" if days_val is None else str(days_val)
                income_str = self._format_number(daily_income[field])
                self.single_char_detail_tree.insert("", "end", values=(field, need, income_str, days_str))

        def _collect_daily_income(self) -> dict:
            return {field: as_float(var.get()) for field, var in self.daily_income_vars.items()}

        def _collect_currency_income(self) -> dict:
            return {
                currency: {
                    period: as_float(self.currency_income_vars[currency][period].get())
                    for period, _label in CURRENCY_PERIODS
                }
                for currency, _label in CURRENCY_FIELDS
            }

        def _collect_exchange_rates(self) -> dict:
            currency_names = {currency for currency, _label in CURRENCY_FIELDS}
            default_rates = build_default_exchange_rates()
            rates = {}
            for field, _label in MATERIAL_FIELDS:
                currency = self.exchange_rate_vars[field]["currency"].get().strip()
                price = as_float(self.exchange_rate_vars[field]["price"].get())
                allowed_currencies = allowed_currencies_for_material(field)
                if not currency or currency not in currency_names or currency not in allowed_currencies:
                    currency = default_rates[field]["currency"]
                rates[field] = {"currency": currency, "price": price}
            return rates

        def _collect_exchange_limits(self) -> dict:
            return {
                currency: as_float(self.exchange_limit_vars[currency].get())
                for currency in self.exchange_limit_vars
            }

        def _collect_material_inventory(self) -> dict:
            return {field: as_float(var.get()) for field, var in self.material_inventory_vars.items()}

        def _collect_currency_inventory(self) -> dict:
            return {currency: as_float(var.get()) for currency, var in self.currency_inventory_vars.items()}

        def _calculate_effective_daily_income(self, totals: dict) -> dict:
            return calculate_effective_daily_income(
                self._collect_daily_income(),
                self._collect_currency_income(),
                self._collect_exchange_rates(),
                self._collect_exchange_limits(),
                totals,
            )

        @staticmethod
        def _format_number(value: float) -> str:
            if value is None:
                return ""
            return str(int(round(value)))

        def refresh_result_view(self, save: bool = False) -> None:
            totals = calculate_total_materials(self.todo_items, self.data["upgrade_material_costs"])
            daily_income = self._calculate_effective_daily_income(totals)
            eta = calculate_eta_days(totals, daily_income)

            for item in self.result_tree.get_children():
                self.result_tree.delete(item)

            for field, _label in MATERIAL_FIELDS:
                days = eta[field]
                days_text = "∞" if days is None else str(days)
                income_text = self._format_number(daily_income[field])
                self.result_tree.insert("", "end", values=(field, totals[field], income_text, days_text))
            self.refresh_ranking_view(daily_income)
            if save:
                self.persist_data()

        def _build_ranking_rows(self, daily_income: dict) -> list[dict]:
            per_character: dict[str, dict] = {}
            for record in self.todo_items:
                if not is_todo_pending(record):
                    continue
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

            rows = []
            for name, entry in per_character.items():
                total_materials = sum(entry["materials"].values())
                eta = calculate_eta_days(entry["materials"], daily_income)
                max_days = 0
                max_field = ""
                has_infinite = False
                for field, _label in MATERIAL_FIELDS:
                    days = eta[field]
                    if days is None:
                        if not has_infinite:
                            has_infinite = True
                            max_field = field
                    elif not has_infinite and days > max_days:
                        max_days = days
                        max_field = field
                rows.append(
                    {
                        "name": name,
                        "record_count": entry["record_count"],
                        "total_materials": total_materials,
                        "max_days": None if has_infinite else max_days,
                        "max_field": max_field,
                    }
                )
            return rows

        def refresh_ranking_view(self, daily_income: dict | None = None) -> None:
            if daily_income is None:
                totals = calculate_total_materials(self.todo_items, self.data["upgrade_material_costs"])
                daily_income = self._calculate_effective_daily_income(totals)
            rows = self._build_ranking_rows(daily_income)
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
                    values=(idx, row["name"], row["record_count"], row["total_materials"], days_text, row.get("max_field", "")),
                )

        def persist_data(self, show_message: bool = False) -> None:
            self.data["todo_list"] = list(self.todo_items)
            self.data["upgrade_records"] = [
                {"角色": item.get("角色", ""), "fromR": item.get("fromR", 0), "toR": item.get("toR", 0)}
                for item in self.todo_items
                if str(item.get("角色", "")).strip()
            ]
            self.data["daily_income"] = self._collect_daily_income()
            self.data["currency_income"] = self._collect_currency_income()
            self.data["currency_inventory"] = self._collect_currency_inventory()
            self.data["material_inventory"] = self._collect_material_inventory()
            self.data["exchange_rates"] = self._collect_exchange_rates()
            self.data["exchange_limits"] = self._collect_exchange_limits()
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

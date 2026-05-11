from __future__ import annotations

import html
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

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
    }


def ensure_data_file(data_file: Path = DATA_FILE) -> None:
    data_file.parent.mkdir(parents=True, exist_ok=True)
    if not data_file.exists():
        save_data(build_default_data(), data_file)


def load_data(data_file: Path = DATA_FILE) -> dict:
    ensure_data_file(data_file)
    try:
        return json.loads(data_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        default_data = build_default_data()
        save_data(default_data, data_file)
        return default_data


def save_data(data: dict, data_file: Path = DATA_FILE) -> None:
    data_file.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def as_int(value: str | None) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def render_table_rows(rows: list[dict]) -> str:
    rendered_rows = []
    for row_index, row in enumerate(rows, start=1):
        cells = [
            (
                f'<td><input type="number" min="0" name="{html.escape(field)}_{row_index}" '
                f'value="{as_int(str(row.get(field, 0)))}"></td>'
            )
            for field, _label in MATERIAL_FIELDS
        ]
        rendered_rows.append(
            "<tr>"
            f'<td><input type="text" name="升级阶段_{row_index}" '
            f'value="{html.escape(str(row.get("升级阶段", f"R{row_index}")))}"></td>'
            + "".join(cells)
            + "</tr>"
        )
    return "\n".join(rendered_rows)


def render_page(data: dict, message: str = "") -> bytes:
    header = "".join(f"<th>{html.escape(label)}</th>" for _field, label in MATERIAL_FIELDS)
    notice = f'<p class="notice">{html.escape(message)}</p>' if message else ""
    page = f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8">
    <title>SWGOH Relic 材料容器</title>
    <style>
      body {{ font-family: Arial, sans-serif; margin: 20px; }}
      table {{ border-collapse: collapse; width: 100%; font-size: 12px; }}
      th, td {{ border: 1px solid #ddd; padding: 6px; text-align: center; }}
      th {{ background: #f0f0f0; }}
      input[type='number'] {{ width: 70px; }}
      input[type='text'] {{ width: 60px; }}
      .notice {{ color: #1a7f37; font-weight: bold; }}
      .model-box {{ margin: 12px 0; }}
      .model-box input {{ width: 460px; }}
    </style>
  </head>
  <body>
    <h1>SWGOH 升级材料容器（本地）</h1>
    <p>模型说明（预留，可本地修改）：</p>
    {notice}
    <form method="post" action="/save">
      <div class="model-box">
        <input type="text" name="model_info" value="{html.escape(str(data.get("model_info", "")))}">
      </div>
      <table>
        <thead>
          <tr>
            <th>升级阶段</th>{header}
          </tr>
        </thead>
        <tbody>
          {render_table_rows(data.get("upgrade_material_costs", []))}
        </tbody>
      </table>
      <p><button type="submit">保存到本地 JSON</button></p>
    </form>
  </body>
</html>
"""
    return page.encode("utf-8")


class MaterialCostHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        """Render the local table GUI, auto-initializing/resetting invalid data when needed."""
        data = load_data()
        body = render_page(data)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802
        """Handle /save form submission; return 404 for non-/save POST paths."""
        if self.path != "/save":
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        length = int(self.headers.get("Content-Length", "0"))
        payload = self.rfile.read(length).decode("utf-8")
        form = parse_qs(payload)

        rows = []
        for idx in range(1, len(RELIC_TIERS) + 1):
            row = {
                "升级阶段": form.get(f"升级阶段_{idx}", [f"R{idx}"])[0] or f"R{idx}",
            }
            for field, _label in MATERIAL_FIELDS:
                row[field] = as_int(form.get(f"{field}_{idx}", ["0"])[0])
            rows.append(row)

        data = {
            "model_info": form.get("model_info", [""])[0],
            "upgrade_material_costs": rows,
        }
        save_data(data)

        body = render_page(data, message="已保存")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    ensure_data_file()
    server = ThreadingHTTPServer((host, port), MaterialCostHandler)
    display_host = "127.0.0.1" if host == "0.0.0.0" else host
    print(f"Open http://{display_host}:{port} in your browser")
    server.serve_forever()


if __name__ == "__main__":
    run_server()

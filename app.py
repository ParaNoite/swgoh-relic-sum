from __future__ import annotations

import html
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

DATA_FILE = Path(__file__).resolve().parent / "data" / "upgrade_material_costs.json"
MATERIAL_COLUMNS = [
    "carbonite_circuit_board",
    "bronze_wiring",
    "chromium_transistor",
    "auerodium_heatsink",
    "electrium_conductor",
    "zinbiddle_card",
    "impulse_detector",
    "aeromagnifier",
    "gyrda_keypad",
    "droid_brain",
]


def build_default_data() -> dict:
    return {
        "model_info": "预留：请在此填写你使用的模型说明",
        "upgrade_material_costs": [
            {"upgrade_index": idx, **{material: 0 for material in MATERIAL_COLUMNS}}
            for idx in range(1, 10)
        ],
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


def as_int(value: str) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def render_table_rows(rows: list[dict]) -> str:
    rendered_rows = []
    for row in rows:
        cells = [
            (
                f'<td><input type="number" min="0" name="{html.escape(material)}_{row["upgrade_index"]}" '
                f'value="{as_int(str(row.get(material, 0)))}"></td>'
            )
            for material in MATERIAL_COLUMNS
        ]
        rendered_rows.append(
            "<tr>"
            f'<td><input type="number" min="1" name="upgrade_index_{row["upgrade_index"]}" '
            f'value="{as_int(str(row["upgrade_index"]))}"></td>'
            + "".join(cells)
            + "</tr>"
        )
    return "\n".join(rendered_rows)


def render_page(data: dict, message: str = "") -> bytes:
    header = "".join(f"<th>{html.escape(material)}</th>" for material in MATERIAL_COLUMNS)
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
      input[type='number'] {{ width: 78px; }}
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
            <th>upgrade_index</th>{header}
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
        for idx in range(1, 10):
            parsed_upgrade_index = as_int(form.get(f"upgrade_index_{idx}", [str(idx)])[0])
            row = {"upgrade_index": parsed_upgrade_index if parsed_upgrade_index >= 1 else idx}
            for material in MATERIAL_COLUMNS:
                row[material] = as_int(form.get(f"{material}_{idx}", ["0"])[0])
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
    open_host = "127.0.0.1" if host == "0.0.0.0" else host
    print(f"Open http://{open_host}:{port} in your browser")
    server.serve_forever()


if __name__ == "__main__":
    run_server()

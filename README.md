# swgoh-relic-sum

Python 本地桌面升级材料管理工具（可打包 EXE）。

## 功能
- 输入角色名 + `fromR` + `toR`，存储多条升级记录
- 基于 `R1 ~ R10` 材料表，自动汇总所有记录的总材料需求
- 单独录入每个材料的每日收入，自动计算攒齐天数
- 本地保存数据到 `data/upgrade_material_costs.json`

## 本地运行
```bash
python app.py
```

## 打包 EXE（Windows）
```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed app.py
```

产物在 `dist/app.exe`。

# swgoh-relic-sum

Python 本地桌面升级材料管理工具（可打包 EXE）。

## 功能
- 输入角色名 + `fromR` + `toR`，存储多条升级记录
- 升级记录支持选中后编辑与删除
- 角色 Todo 列表支持添加、编辑、保存
- 基于 `R1 ~ R10` 材料表，自动汇总所有记录的总材料需求
- 单独录入每个材料的每日收入，自动计算攒齐天数
- 角色排行按总材料/记录数/最慢天数排序
- 本地保存数据（源码运行时默认在 `data/upgrade_material_costs.json`）

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
EXE 模式会将数据保存到用户目录（避免写入不可写的程序目录）：
- Windows: `%APPDATA%\\swgoh-relic-sum\\upgrade_material_costs.json`
- macOS: `~/Library/Application Support/swgoh-relic-sum/upgrade_material_costs.json`
- Linux: `~/.local/share/swgoh-relic-sum/upgrade_material_costs.json`

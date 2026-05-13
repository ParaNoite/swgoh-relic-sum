# swgoh-relic-sum

Python 本地桌面升级材料管理工具（可打包 EXE）。

## 功能
- 角色计划输入支持 `fromR / toR / fromSharp / toSharp` + 注释，并自动生成 Todo 列表
- Todo 支持标记完成并自动扣除材料/货币库存
- 基于 `R1 ~ R10` 材料表，自动汇总未完成计划的总材料需求
- 支持按单个角色计算培养天数（最慢材料所需天数）
- 同时录入材料每日收入与货币每日/每周/每月收入，换算后计算攒齐天数
- 设置区统一维护汇率、每日兑换上限与库存
- 角色排行按总材料/记录数/最慢天数排序
- 默认采用更现代化的浅色风格 UI（圆角感、柔和色彩、统一字体）
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

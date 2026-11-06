# 地图拼装候选独立交接 · 2026-10-27

本批仅新增 `exports/01-率土之滨/map-assembly-v1/`、`records/01-率土之滨/map-assembly-v1/` 与 `work/*map_assembly*v1*` 脚本。未修改 README、旧 catalog、Git、phase2 冻结快照或既有 Unity 包。未调用新图／视频／收费 API。

当前入口是 `exports/01-率土之滨/map-assembly-v1/playable-preview.html`（约2.1MB，自包含离线 HTML）。WASD／方向键、点击寻路、E 演示交互；步兵仅固定东南向静态 PNG 平移。原始资源 PNG 字节未改。`assembled-preview-current.png` 是当前拼装；无 current 后缀是保留的首轮预览，敌营曾遮挡桥口，现已移远。

当前使用6种已有地图裁切（草地、石路、直河、主城、桥、敌营）和1种既有64h步兵PNG，35地块实例+3道具。世界1440×960，地形统一0.72倍、主城0.65、桥1.15、敌营0.75；源锚点、地图支点与手工桥面中心分开记录。地形缩放仅是已有图显示派生，不称原生新细节。

`map-bundle.json` 来源哈希/结构校验通过；导航6/6目标可达，去掉唯一桥通行区后4目标按预期不可达，负控FAIL保留。当前导航仍有 `unreachable_walkable_area` WARN：2个微小孤立口袋，共3个4px导航格。碰撞/道路是手工 provisional 数据，未宣称与画面最终一致。

实际Chrome 156.0.8078.48验证：所有6条路线、4方向键、点击桥中点、E城门/敌营交互均通过；真实步兵256方画布/64高轮廓、源脚点[128,224]，6个位置脚点有效且实际像素可见；0页面错误、0外部请求，5图均加载。官方工具默认Playwright Chromium缺失，verify SKIPPED保留；独立验证改用实际安装Chrome。基线像素遮挡探针返回SKIPPED（无满足条件的opaque采样点），最初自写汇总误把缺ok字段计为false，原false报告保留。真实步兵页面自身通过；不把该探针称为通过。

关键WARN：独立带石沿地块接缝／重复花丛；5个河块镜像后的光照和岸接缝；单张桥未分前栏（全桥低于玩家排序）；屋顶无逐像素遮挡提示；静态SE人物无行走/方向动画；尺度与碰撞待验收；原生alpha=1余边保留。全部逐项原值与阈值见 `records/01-率土之滨/map-assembly-v1/review.json`。历史schema遗漏/负控FAIL报告原样保留；已保留有效初始布局/placements的准确字节快照，但schema修复前和第一次负控JSON未保留原始字节，重建哈希不符已拒收，并作为metadata WARN写入historical-input-index。当前JSON和所有PNG的源/派生哈希复核完整。所有本批PNG都有相邻derivation，包含源哈希、操作与QA状态。

最小补图需求：同相机无独立石沿、共享边/接口的草地基础；匹配两轴的连续直河/河岸与桥头接口；若要连续道路，需两轴+转角透明道路覆盖；正式桥上遮挡需独立前栏/桥面分层。当前不额外生图。完整清单在 layout-plan.json 与 assembly-manifest.json。

当前清单 `exports/01-率土之滨/map-assembly-v1/assembly-manifest.json`；浅深底与6脚点拼图在本交接同目录。此批是下一批独立候选，不进入已冻结phase2公开快照；待根决定新批整体验收/发布。未制作新Unity扩展，若后续需要先确认工程上下文。

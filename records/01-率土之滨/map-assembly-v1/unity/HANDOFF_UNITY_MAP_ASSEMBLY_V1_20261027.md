# 地图拼装Unity扩展独立交接 · 2026-10-27

实际导出包：`exports/01-率土之滨/map-assembly-v1/unity/WuxingSLGMapAssemblyPreview-20261027.unitypackage`。大小1,000,922 bytes，SHA256 `1020e1364bd4cc7c1b89fd0dff3272258bde1b1091e1c02c1e19a1cdfbe7fd92`。独立资产根 `Assets/WuxingSLGMapAssemblyPreview/`，场景 `Scenes/MapAssemblyPreview.unity`。未操作Git/README/catalog或旧Unity包。

真实Unity6000.6.0f1（FileVersion6000.6.0.16251117）源工程导出及新空工程回导均通过：7原生PNG字节/hash/alpha统计/尺寸/自定义pivot/无压缩NPOT-none等设置，39SpriteRenderer实例的坐标/scale/flip/sort/contact脚点，8路径点引用、scene/camera存在、无missing-script。PPU100是预览约定；源y-down转Unityy-up。包仅用既有6地图裁切+1单位PNG，不含拼板PNG或历史角色。

实际PlayMode在D3D11/NVIDIA GeForceRTX3070Ti运行，观察275个LateUpdate帧；固定路线完成，全程九点脚碰撞/路线/投影/恒定SE Sprite/scale/sort及步进预算通过（最大2.500041px，名义2.5px，浮点容差0.02px）。实际暂停窗口4次LateUpdate观察稳定（含触发帧，随后3次Update确实暂停）、组件重启回spawn通过。5个实际脚点×浅深底10张原生1440×960Camera.Render截图，GPU同帧隐藏单位作背景像素差，单位可见且pivot投影对齐。截图不是手工贴图或编辑器创建冒充运行。见 actual-playmode-gpu-report.json 与 gpu-footpoints-light-dark.png。

6/6目标可达与去桥4目标不可达仍沿用既有canonical导航数据，带hash存入包Data；Unity没有重做A*。本次Unity另实测去掉桥region后中点不可站立。runtime只是固定SE静态图沿8点已验证路线平移，无行走动画、combat events、physics或动态寻路。Space/R为legacy输入条件映射，未注入原生按键测试；实际组件暂停/重启方法已测。

保留既有WARN：花丛重复与地形/河岸接缝、镜像光照、单层桥无前栏、无roof actor cue、provisional碰撞/尺度、alpha1余边。新增WARN：原生Sprite GPUbilinear不同于PIL圆整LANCZOS拼板；3:2/1440×960推荐Game view，空工程默认aspect1.333而投影/GPU明确设1.5，任意纵横比/移动端未验；固定路线非新Unity导航；原生键盘未注入。未称客户端/最终游戏或性能验收。

首次启动在依赖解析阶段失败：不存在`com.unity.modules.inputlegacy@1.0.0`条目，尚未进入编译/场景/运行。移除后用安装自带InputLegacyModule DLL和已有最小依赖通过，未下载字体/新框架或新图。原FAIL摘要 attempt1-dependency-failure.json保留；raw Unity日志仅work本地，公开compile-diagnostics.json不含许可/会话行。

包已作内存tar/gzip检查（无落盘解包），7PNG/source-index/runtime字节和scene YAML均吻合，无凭据模式。每张GPU/QA PNG都有相邻derivation。总索引 `exports/01-率土之滨/map-assembly-v1/unity/unity-preview-manifest.json`；完整验证 `records/01-率土之滨/map-assembly-v1/unity/verification.json`。本批待root phase3统一发布，未自行推送。

编辑器构建工具有6类CS0618过时API警告，source日志重复12行、回导24行，原文均保留在compile-diagnostics.json及verification.json。均为包外Assets/Editor工具；包内runtime脚本不调用这些API。无编译错误。GUI启动器立即返回码未当作Unity退出码；实际passed回执与进程结束分别记录。

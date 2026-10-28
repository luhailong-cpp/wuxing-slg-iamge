# 2026-10-30 接续：52人物、100兵种帧与750×750世界

完整游戏美术尚未完成。用户要求完整率土名册与全部三国人物，道家Q版；金木水火土仅为五种普通兵种。

## 当前内容

52身份母稿候选、260张五规格UI派生。本轮新群雄4人：董卓、袁绍、张角、张宝，原画已实际查看，浅深底与头像裁切已检查。52源图和260派生PNG哈希核对一致。张角头像窗口已缩窄，排除被切成碎片的法杖；原始RGBA未清理。四张新原画均有原生留白不足8%、alpha1和最高alpha254的WARN，不声称原生透明品质已终验。程秉选hist1/v2，夏侯渊选wei1/v2。统一入口exports/01-率土之滨/art-review-20261029/index.html，支持本批群雄4人筛选。全部卡面变体、545个候选personID消歧、原典全集人物分母仍未闭合。

五兵种SE待机4/攻击6/受击4/战败6，共100独立帧和300规格PNG。浏览器播放已检查，时间比较页共享金兵时间基准，不等于每兵动作时序或Unity验收。行走仍未通过，多方向尚缺。

## 地图范围

按用户最新要求，仅率土地图四分之一面积。采用网易官方应用介绍225万格口径，本项目选择750×750=562500格。750是本项目制作选择，不声称为已测量的官方赛季边长。32×32格数据分块为24×24=576区块，末行列14格；已逐格核对562500地址无重复或漏格。这是数据范围校验，没有完成576张原生地形图。具体见QUARTER_WORLD_SCOPE_20261030.md及records/quarter-world-20261030/world-scope-contract.json。

1672×941图world-overview-v1只作为区域场景布局草案：5据点、4桥、2关隘，非比例准确的整个世界；东北院落有烘焙人物细节、部分入城道路需修，细地形/连通/导航/无缝tile/Unity缩放尚未完成。地图04河岸底板原有斜缝已修并静态组合检查通过，但不能等同整个地图通过。不要套用旧MMO主城16×16原生4K合同。

## Unity

2026-10-30独立工程实际接入通过：基线253 PNG/8FX Clip/2Prefab，新增326 PNG/20兵种Clip/5Prefab，合计579 PNG、28Clip、7Prefab。基线592文件/GUID仍严格匹配，新增326 PNG和全部RGBA/alpha像素、轴心、尺寸均严格匹配。20Clip内100帧区间全部通过带有效Animator的Unity AnimationMode采样，各兵自己的时序独立，10ms末端时长问题已修正。新场景Assets/Project/Scenes/TroopFrameReview20261030.unity。

基线桥前后及草地共3张原RGBA哈希仍有差异，仅在alpha0 RGB，已用源alpha及canonical哈希证据确认为WARN；PNG、alpha和所有alpha>0 RGB保持精确，原差异事实保留。新增批关闭alphaIsTransparency，全部原始RGBA直接匹配。基线验证器只接受已通过新批报告且PNG/GUID仍一致的扩展清单，其他PNG仍为unexpected，当前全局0个未登记PNG。

D3D11/RTX3070Ti实际生成五兵四动作×浅深底8张GPU图，两张原像素裁切contact已查看。一次GPU采样须将5兵放在同一Begin/EndSampling区间，并在End后断言所有Sprite，避免前4兵被还原。截图为编辑器采样，runtimePlayModeTested=false，不冒充正式战斗或流畅动画验证。

完整证据在Unity Docs/ArtImport/NEW_BATCH_RESULTS_20261030.md、new-art-validation-20261030.json、validation-report.json、new-troop-gpu-capture-20261030.json。本库概要records/unity-integration-20261030.json。Pending/20261030/new-art-plan.json是固定运行前输入，不能在运行后改status导致planSha失效。共享重型时段已提前释放，本项目当前无Unity进程在途。

## 发布

本次状态同步前，已核验美术快照57cc0ee2a213043e3dae7dbe6fd4591cc1da4f97，tree e64185bdd65b4f82d198fb78c01b30c7bc5f4fa9，4277文件、父提交0。含52人物/260UI/100兵种帧和750×750世界范围合同、区域布局草案。当前正同步后续Unity实际通过的文字记录；最终美术远端以忽略目录records/publication-local/published-receipt-20261030.json为准。

Unity私有仓库已发布并核验ba6fd27989338dc579cf55266cfc1adb398fdfdb，tree b90d9fde924e33e282f9de1fc9e718652ca802d7，2171文件、父提交0，远端完整文件树一致，临时上传分支已删。包含326新PNG和20兵种Clip实际校验与GPU证据，不再是未导入计划。发布回执在Unity忽略目录Logs/Publication/published-receipt-20261030.json。完整游戏美术仍未完成。

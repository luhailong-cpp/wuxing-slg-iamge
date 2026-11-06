# 桥面与前栏分层候选

2026-10-28。仅补齐桥的前景遮挡，旧地图工程未改。生成入口为宿主内置 image_gen，母图原生1774×887 RGBA；实际模型/画质未披露，配置目标仍为 GPT Image2.5 / max。

## 文件

- bridge-back.png：桥面、桥基、后栏、台阶与植物。
- bridge-front.png：独立前栏。
- bridge-composite-reference.png：两层在共同原点叠合的静态参考。
- bridge-depth-preview.html：可离线打开，切换浅深底、前栏、三脚点及金兵静态诊断。
- bridge-depth-manifest.json：原生裁切、整数配准、alpha、脚点与限制。
- unity/WuxingSLGBridgeDepth-20261028.unitypackage：独立2Sprite+双层Prefab。实际验证以 项目 records/map-depth-20261028/final-review.json 为准。

## 接入

两层均1000×1000，共同锚点（左上坐标）[500,900]；Unity pivot(0.5,0.1)，100PPU，FullRect、无压缩、无mipmap、无NPOT缩放、输入alpha。两层保持相同position/scale，不按各自bbox再次居中。Prefab中后层order0、前栏order2；桥上角色放order1。桥外角色仍需正常场景深度/区域判定，不能把前栏全局压在所有角色上。头像和兵种母版没有打入本包。

## 已检查

桥体源像素只裁切与整数平移，没有缩放、透明阈值擦除或程序补画。源图没有按提示词的两等格注册，因此使用x=1000的实际透明间隔划分：后层crop[0,0,1000,887]放[0,64]，前层crop[1000,0,1774,887]放[55,39]。这两个坐标是人工实测配准，不是声称生成天然对齐。

三脚点[244,422]、[500,447]、[760,670]分别在浅深背景检查；中性标记和新金兵静态母版的下部均能由前栏遮挡。金兵201px诊断图来自最新母版等比缩小，动作帧数0，脚点和比例均非正式兵种合同。Chrome实测三按钮、前栏开关与960横屏无横向溢出。

## 保留限制

1. 新桥与旧小桥同身份/拓扑，但不是像素一致的旧桥拆分，实际地图替换必须重新测桥头、跨度、相机与碰撞。
2. 原生softalpha/alpha1保留；后层alpha1=11251，前层=4286，四边alpha>16均0。浅深底可检查，未作alpha清洗。
3. 本次只修桥层次，未修草地重复接缝、河岸/道路接口、屋顶遮挡、地图动态寻路或移动端性能。
4. 不是正式客户端集成，也不是人物动画验收。所有userApproved=false、clientIntegrated=false。

## 证据

提示词与请求/返回在项目 prompts/01-率土之滨/map-depth-20261028、records/map-depth-20261028；原生母图在 designs/01-率土之滨/assets/map-depth-20261028。Unity源工程和日志仅在work/map-depth-20261028；公开记录不包含许可/会话日志。

Unity6000.6.0f1源导出与独立空工程回导2Sprite/Prefab通过；D3D11真实静态Camera.Render六图已审阅，不等同PlayMode。正常UPM在Node子进程入口失败，cmd.exe直接启动Python runner回导成功；全部失败证据保留。

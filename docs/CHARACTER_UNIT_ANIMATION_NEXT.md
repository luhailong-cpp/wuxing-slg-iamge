> **2026-10-28 当前要求已纠正：横版；金木水火土是五种兵种，不是五系角色；其他系统与武将身份按率土之滨参考，保持道家Q版。以下冲突的旧判断仅作历史。见 [当前要求](CURRENT_REQUIREMENTS_20261028.md)。**

# 角色与单位动作接续合同（候选）

核验日期：2026-10-27。根目录：`D:/work/wuxing-slg-iamge`。目标：Unity。本文是下一阶段可执行提案，动作数量、称号、设备规格、时长、帧率和正式采用尚未成为用户确认的玩法合同。

## 当前真实结论

**新角色/单位视频生成状态：`blocked_capability`。** 当前工具清单有宿主`image_gen`，没有原生image-to-video；专用Forge运行器的实际resolver返回`no-route`。xAI、BytePlus、fal视频key配置均为no，Grok CLI未安装；没有调用新视频、收费API或CLI生成，没有安装、登录、UI自动登录或Git操作。只标本项能力阻塞，没有把整个美术任务/goal改为blocked。

**提供视频后的本地处理能力已可用。** 实际运行器`D:/luyuan/image-skills/runtime/agent-sprite-forge/forge.ps1`使用独立Python3.12.15与便携FFmpeg9.0.2；`video2dsprite.py doctor`实际通过VP9 alpha、libx264及PNG处理检查。之前裸PATH中缺FFmpeg的结果不能推广到此专用环境。此次离线codec回环探针不是角色动作视频。

本次resolver的实际进程退出码为1，stdout明确为`no-route`；没有把文档中的退出码3冒充实测结果。工具目录列出的provider支持是本机路由声明，未连接账户验证额度、计费或服务端模型可用性。完整无密钥能力记录见[核验JSON](../records/character-animation-capability-20261027.json)。

## 已核对的8张静态母版

以下每个SHA256均在本轮重算，并与图旁generation记录一致。全部仍为候选、`userApproved=false`、`clientIntegrated=false`。五位hero均1024×1536 RGBA；三类单位均1254×1254 RGBA。当前hero动作帧0、单位动作帧0；没有正式`generate2dsprite.master.v1`的master.json。这些PNG不能自动当作已批准的动作母版。

表中余边顺序为左/上/右/下，按本轮只读alpha>16轮廓测量，未擦除原生alpha；它是静态诊断，不是动画运动包络通过。

| 对象 | 实际母版路径（相对根目录） | SHA256 | 余边px L/T/R/B |
|---|---|---|---|
| 金·铸锋使 | `designs/01-率土之滨/characters/five-elements/01-metal-envoy-v1.png` | `555c1757f7ee88ed26961366043ef32f4743c0607972fedf6e38e4d4deb88208` | 59/75/42/72 |
| 木·青蘅使 | `designs/01-率土之滨/characters/five-elements/02-wood-envoy-v1.png` | `8be021e9382b885ba64a5f883dd4a435e9a0cd8739b570110d667314f928e07c` | 123/200/39/124 |
| 水·沧澜使 | `designs/01-率土之滨/characters/five-elements/03-water-envoy-v1.png` | `322e4d90a21b20fadac2eb9babc03763723fe7178a3a3c931ef134c6654c68b5` | 25/87/20/58 |
| 火·焰翎使 | `designs/01-率土之滨/characters/five-elements/04-fire-envoy-v1.png` | `0b334b77d2eabba1f68b1d12984006f1df2be7e035bb992b9357df6b4b6b800b` | 50/88/57/68 |
| 土·玄垣使 | `designs/01-率土之滨/characters/five-elements/05-earth-envoy-v1.png` | `e87e703421833da4678a6eb8aee7c9d5a5cd14180a41f5fe526b2f0f84dd0021` | 75/176/44/140 |
| 步兵SE | `designs/01-率土之滨/assets/units/01-dao-infantry-master-v1.png` | `901880ee5681e69107cba1f8557f2f2c060025e2ca4c337e577db3c9ea35723a` | 241/219/240/184 |
| 弓兵SE | `designs/01-率土之滨/assets/units/02-dao-archer-master-v1.png` | `e907349d5c3ee1582669aa3e85dad9f2fcaa3b1d2be85133acf011d4352c5e18` | 324/194/208/169 |
| 骑兵SE | `designs/01-率土之滨/assets/units/03-dao-cavalry-master-v1.png` | `f5a98a34a33cb3699f8fb12a341f1bc267df1afe2d292aa617d8091b0fa6cf8a` | 292/148/186/90 |

五位hero的余边未达到此前宽阔留白目标，水的右侧20px、木39px、金42px较紧；3类单位也均未严格达到各边15%，骑兵底部约90px最紧。当前可见主体完整，但动作输入必须另定安全运动范围，不能据静态不裁切推断动作不裁切。原生低值alpha与五hero最大alpha254仍保留，未程序抹除或归一。

## 身份、相机、脚点与尺度

每个动作都携带同一张已选母版及其完整身份描述；同一视图不能在动作间改脸、头身比、衣装结构、兵器/法器或配色。现有整屏UI、卡面、集合参考图和64/128高显示派生不作为新动作的唯一身份母图。
- 金系铸锋使：短银灰发、暖金花簪与玉珠流苏、米白短袍/玉绿内衬、金护臂、腰侧工具袋、短符尺和折叠阵盘；两件法器数量与形状保持。
- 木系青蘅使：棕色半束发和叶簪、嫩叶短披肩、米白玉绿袍、竹节法杖、腰侧种子囊与双短靴；法杖不能变长或变成历史人物拐杖。
- 水系沧澜使：深蓝双辫、蓝白短斗篷、银边与水滴发饰、实体水纹环和小葫芦；双辫、圆环和葫芦都保留。
- 火系焰翎使：赤棕蓬短发与短发束、朱砂披肩、米白玉绿短袍、护腿、两枚火纹实体符牌；不是持双剑的历史武将。
- 土系玄垣使：深色低发髻、暖赭/米白/玉绿宽袖外套、方形山钮石印、护阵盾、宽圆稳重面部与短靴。
- SE步兵：圆顶玉绿米白头盔、深棕短发、玉绿金边轻甲、米白短袍、右侧圆云纹盾与另一手短枪；固定盾枪数量和轮廓。
- SE弓兵：棕发高束、玉绿抹额与短披肩、米白短袍、背箭袋与一张金玉长弓；弓弦/箭袋保持，不多生弓或把弓换剑。
- SE骑兵：玉绿圆盔骑手、金玉短杖、栗色马、深棕鬃尾、米白马鼻/小腿、玉金缰具和鞍毯；马/骑手作为一个身份，四蹄、双耳、单尾、缰绳完整。

Hero保持当前近正面三分之二展示视图、固定镜头和取景尺度；这些母版不是SE地图动作视图。单位沿现有SE斜俯视，清单的约40°是画法约定，尚未相机标定。需要其他方向时为该方向另建母版，不把镜像或模型自动转身冒充新方向验收。

Hero正式鞋接地点尚未测定。制作准备时人工标定脚下root/接地中点与rest-body-height，再把每个动作的输入、裁切、补边和source-to-display变换写入同一角色profile。单位现有定位只是地图放置候选：

| 单位 | 原生master中的暂定anchor（左上原点px） | 当前native crop内anchor | 已有显示派生 |
|---|---|---|---|
| infantry | [627.5, 1072] | [404.5, 871] | 256×256画布；轮廓高64/128；anchor(128,224) |
| archer | [685.0, 1088] | [379.0, 911] | 256×256画布；轮廓高64/128；anchor(128,224) |
| cavalry | [680.0, 1168] | [406.0, 1038] | 256×256画布；轮廓高64/128；anchor(128,224) |

这些单位anchor来自已有静态crop与manifest，不能直接宣称是动画的已校准接地点。步弓需审定脚接地线；骑兵需审定马的足迹中心与四蹄投影，骑手和马作为同一整体注册。64/128的整轮廓统一高度是地图标识约定，不表示骑马人物与步兵实际物理比例。

所有动作使用一个rest尺度profile与一个共同root。宽动作通过同一角色的固定运动包络/透明补边容纳，不让武器伸出就逐帧缩小人物。禁止每帧按alpha bbox裁切、缩放或贴底；保留合法抬脚、压低、马步和衣发摆动。行军用in-place循环，由游戏Transform移动；不要求行军时每只脚永远钉住，不把真实步态冻住。当前Unity预览PPU=100可作工程起点，最终地图比例、角色显示高度和PPU仍需目标场景审定。

## 动作清单提案

先做金系idle与步兵march两个试作，验证身份、视图、接地与后处理，再扩展；这只是制作顺序，不代表两个动作即首发范围。

| 对象组 | 首轮动作提案 | 后续按玩法决定 | 运动要求 |
|---|---|---|---|
| 五位hero各自 | idle循环、cast单次、hurt单次 | guard、victory、defeat；battle使用时另列walk/run | idle可读呼吸；cast使用现有法器做一次动作并回母版姿态；hurt短促后恢复 |
| 步兵SE | idle循环、march循环、attack单次 | guard、hurt、retreat/defeat | 盾枪不增生；原地交替迈步；攻击一次短枪动作、回到ready |
| 弓兵SE | idle循环、march循环、attack单次 | hurt、retreat/defeat | 弓与箭袋形状恒定；一次拉弦释放动作；箭实体/命中特效由独立层处理 |
| 骑兵SE | idle循环、march循环、attack单次 | gallop、hurt、retreat/defeat | 马蹄交替、缰绳与骑手耦合；攻击保持已有短杖身份；不凭空增枪 |

若全部采用，首轮提案为hero15条、单位9条，共24条动作视频，不是已授权计费批次，也不是已完成数量。跳跃、连击、多方向和特定技能动作仅在玩法明确后另列。

每动作恰好一条image-to-video片段，从同一角色/同一视图母版出发；需要重试时每个take独立保留请求、真实返回与拒绝原因。idle和单次回姿动作在路线实际支持时使用同图首尾约束；不支持必须记录，不伪造`lastFrameUsed=true`。先保留原片FPS/时长，再根据实际动作采样和节奏确定Unity输出帧率，不能把模型时长或现有FX0.8秒照抄为角色时长。

不能用8张互不连续的静态图证明角色/单位动画，也不能把已有FX8相位候选算作这些动作。角色片段内不烘焙技能光、斩击弧、箭轨、烟尘与伤害数字；动画、FX与战斗事件分层。

## 能继续真实动作制作的具体输入

以下任一路线可解除“没有新视频来源”的能力阻塞；本轮未自动选择provider或计费方案。

1. **提供动作源片段。** 按`actorId/actionId/view`提供原始MP4/MOV、带alpha的视频，或连续PNG序列；每条一个动作、同一母版身份、固定镜头与尺度、角色完整入画，并提供母版hash、真实FPS/时长/帧序及alpha/背景说明。原片可用纯净且与服饰不冲突的单色底；先对母版做key-plan再确定背景与保护色。现有专用环境可直接进入解码、matte、注册和包装，不要求新账号。

2. **明确采用新视频provider。** 用户选择provider与计费来源、制作范围和预算/调用上限，凭据只在本机环境或受控用户配置中设置，不在聊天/项目粘贴完整key。之后先重跑只读resolver，核实真实可用路线，再按项目模型政策授权执行；当前三个视频provider均未配置，未获本记录批准。

3. **用户准备可用Grok/宿主视频工具。** 当前Grok CLI未安装、无原生image-to-video。若用户自行准备并授权该路线或宿主后来提供视频工具，先做只读能力复核并明确额度来源；本轮没有安装或登录，也没为“验证”而提交有成本视频。

母版方向/采用与运动包络也需形成明确记录；当前候选不能被写成用户已批准。在没有视频路线/动作源片段时，可以继续细化动作提示词、身份profile和导入合同；状态保持`blocked_capability`，不宣称已生成动作，也不擅用代码摆动静态图替代人物动画。

## Unity交付与验收门槛

第一交付路径以带真实alpha的PNG连续帧、来源/派生链和manifest为主，配AnimationClip、Animator Controller、Prefab及独立预览场景候选。WebM/packed视频是可选运输形式：packed H.264是RGB/alpha并排编码，需要专用合成，不称透明MP4。

每个动作manifest至少记录`actorId/actionId/view/masterFile/masterSha256/sourceClipSha256/route/model实际值/durationsMs/fpsRational/sourceSize/sourceAnchor/sourceRect/固定canvas/pivot/scaleProfile/loop/事件映射/QA`。未知provider型号、质量与时间保持未知，配置目标不倒填实际返回。当前Unity工程预览的Sprite设置可作为导入起点，不在本轮改共享代码；左上原点anchor转换Unity pivot时明确坐标约定。

验收依次完成：真实视频与逐take来源→解码/soft-matte报告与浅深底→固定身份/镜头/原生比例和动作包络→脚点/步态/循环接缝或单次起落→同角色跨动作尺度与颜色lineup→Unity包导入和真实播放截图/回执。任何逐帧裁切、缩放或alpha后处理都写派生证据；不能用补边掩盖源视频已裁掉的鞋、蹄、法器。

动作可审阅后才绑定释放点、命中/治疗事件、击停、位移或碰撞；当前没有这些游戏规则回执。包编译或离线codec通过只能证明对应技术检查，不证明角色动作、地图尺度、玩法或整游戏美术全部通过。

本文仅核实角色/单位视频能力与动作接续缺口。其余UI、地图、FX候选、Unity整合与最终用户验收以各自记录为准；此报告不宣称其他美术已全部完成。

## 证据入口

- [角色动画能力记录](../records/character-animation-capability-20261027.json)
- [金木母版QA](../records/01-率土之滨/five-elements/metal-wood-master-review-20261027.json)
- [水火土母版QA](../records/01-率土之滨/five-elements-water-fire-earth-review-20261027.json)
- [单位manifest](../exports/01-率土之滨/units/units-manifest.json) 与 [独立复核](../records/01-率土之滨/units-native-and-display-review-20261027.json)
- 本轮依据本机video2dsprite技能、runtime/route、sprite-set与motion-prompts说明及实际只读探针；没有把安装文档当成已登录provider的证据。

# 地图、静态特效与本子任务接续

收束日期：2026-10-27。项目：`D:/work/wuxing-slg-iamge`。本子任务不操作 Git。用户要求新窗口接续并归档本窗口后，已停止新生图；没有把未完素材算完成。

## 主题与当前规则

用户明确游戏主题为 **金、木、水、火、土五行**，率土之滨只作功能与布局参考。`01-率土之滨` 是此前使用的存储路径，暂保留以维持真实来源链，不代表游戏正式名称或三国题材。三国角色是错误候选，须按五行原创身份重新设计；不要只改名字或当作已完成五行角色。已将 `FULL_GAME_ART_SCOPE.md` 和机器审计中的历史人物名单提案撤回，初始审计文件数保持原截点事实。

新窗口先读根 `AGENTS.md`、`config/image-generation.json`、`docs/IMAGE_MODEL_POLICY.md`、`docs/UI_STYLE_GUIDE.md`，实际查看邮件与组队两张主参考。继续玉绿、米白、暖金、圆润精细手绘道家Q版。内置实际模型／画质未披露时保持 null。未授权新付费入口。

## 已落盘

地图母表，v1和v2各一张及各自 `.png.generation.json`：

- `designs/01-率土之滨/assets/map-kit/01-city-types-sheet-v1.png`、`01-city-types-sheet-v2.png`：1254×1254 RGBA，3×3九类城池候选，顺序主城／分城／戍城／要塞／军营／县城／郡城／州府／国都。
- `designs/01-率土之滨/assets/map-kit/02-buildings-sheet-v1.png`、`02-buildings-sheet-v2.png`：1448×1086 RGBA，4×3十二建筑候选，顺序城主府／校场／募兵所／仓库／民居／集市／作坊／城墙短段／城门／桥／敌营／残破仓库。
- `designs/01-率土之滨/assets/map-kit/03-terrain-resources-sheet-v1.png`、`03-terrain-resources-sheet-v2.png`：1448×1086 RGBA，4×3十二地形候选，顺序草地／石路／林地／山地／麦田／矿地／采石／河弯／河直／河岸／野渡／空建地。
- `designs/01-率土之滨/assets/fx/01-effects-sheet-v1.png`、`01-effects-sheet-v2.png`：1774×887 RGBA，4×2八类**静态**FX候选，顺序斩击弧／谋略符阵／治疗光／增益云纹／减益紫雾／火焰／占领光圈／奖励光芒。动画帧数0。

逐图提示词位于 `prompts/01-率土之滨/<stem>.prompt.txt`，请求／返回证据位于 `records/01-率土之滨/<stem>.tool-request.json` 与 `.tool-response.json`。

v1均有完整当时记录。v2为同一母表的AI边距修图：4张原生PNG均已从宿主实际输出目录找到并原样复制、实际查看、核对哈希和alpha。宿主执行 cell 17 在恢复时已不存在，无法重新取得完整原始返回与精确调用结束时间；v2响应记录明确为 `recovered_native_file_after_exec_cell_unavailable`，`callCompletedAt`、`generatedAt` 保持 null，另外记录真实PNG文件mtime及其依据。不能把mtime改称模型生成时间，也不能把恢复记录改成完整原始回执。

v1是v2实际编辑输入，当前留作来源链与候选比较；暂不删除。所有母表仍为候选，未用户验收、未客户端集成。

本子任务此前完成6张静态UI方向稿及完整逐图记录：`designs/01-率土之滨/ui/25-login-server-ui-v1.png` 至 `30-settings-help-ui-v1.png`，分别登录选服、同盟、邮件、聊天、任务、设置帮助，均1916×821 RGB。检查入口 `records/01-率土之滨/full-completion-social-review.json`。主题、示例文案和角色头像仍需以用户五行设定作整体差异复核，不把方向稿当客户端资源。

## 在途与未提交

4张v2原生输出均已归档，无可等待的执行cell，不再提交任何新调用。不能据“cell不存在”声称调用原始回执完整。

步兵、弓兵、骑兵3张独立静态master **均未生成**。只有以下提示词已落盘，未有工具请求或返回：

- `prompts/01-率土之滨/01-infantry-v1.prompt.txt`
- `prompts/01-率土之滨/02-archer-v1.prompt.txt`

骑兵提示词未实际落盘，不应按已准备文件或在途调用统计。三类兵种需承接五行主题重新检查再生产。

## 精确未完项

当前本批：地图独立导出0件，FX独立导出0件，兵种master0件，动画0帧。4张母表意图包含33个地图物件和8类静态FX，此数量是母表内容意图，不是41件合格交付资源。

1. v1留白不足，部分物件贴边；v2间隔改善，但城市个别底面、建筑边缘和FX光晕仍靠近网格边界。需逐格确定 ownership/cropBox，检查轮廓完整、无邻格混入，不能盲目等分裁切后宣称通过。
2. alpha通道已证实存在0透明像素，但半透明范围很大，查看时有彩色边缘残留；需浅／深背景复核。当前没有通过透明边缘验收，不授权程序重绘或去背修补。
3. 尚未裁切地图／建筑／地形33件与静态FX8件，尚无对应派生记录、锚点清单、`exports/01-率土之滨/map-kit/map-kit-manifest.json` 或 `exports/01-率土之滨/fx/fx-manifest.json`。
4. 未来裁切只保留原生像素，逐件记录原图路径／hash／generationRecord、operation=crop、cropBox、实际尺寸、alpha结果，锚点底中。缩放标为派生，不能称原生高清。
5. 单位3张master、原生裁切、64/128px派生、units manifest尚未做。原计划朝向SE、static=true、animations=0；五行身份／变体仍需明确，不把静态master算动画。
6. 五系颜色、身份、建筑或资源的主题变体还未系统制作。地图地块没有无缝、碰撞或导航通过承诺；FX未定义动画时长／相位／循环；真实客户端集成全部未验证。

QA机器入口：`records/01-率土之滨/full-completion-mapfx-review.json`。

辅助工具 `tools/finalize_image_record.py` 可用于后续具有真实完整调用返回的新图原样复制与记录；它拒绝覆盖并要求真实完成时间。此次v2恢复记录单独明确证据缺口，勿用虚构时间满足helper校验。

上传与Git由根协调窗口负责。本子任务没有上传、提交或修改共享Git状态。

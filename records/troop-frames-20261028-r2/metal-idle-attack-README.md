# 金兵待机与攻击候选帧（2026-10-28 r2）

实际生成3张：idle v1、idle v2、attack v1；idle做1次定向布局修正，attack v2仅准备请求但未调用。当前选用idle v2（1254×1254，4格627×627）与attack v1（1536×1024，6格512×512）。全部来自内置image_gen，实际模型/质量未披露。母版userApproved=false，生成稿和候选帧均未用户验收。

原生图在designs/01-率土之滨/troop-frames-20261028-r2；逐图generation、request、QA以及提示词文件由对应JSON关联。源图字节复制不改。浅深背景及原生图都实际查看。

严格spill：idle WARN faint_specks；attack WARN safe_frame/faint_specks；均无failed检查。严格process使用native_alpha、alpha-hygiene none、component all、registered、scale1、offset0、无边修剪：idle4帧与attack6帧都技术通过。10帧PNG放对应metal-*-native-frames目录。所有alpha字节及alpha>0处RGB逐像素匹配源裁块，alpha=0隐藏RGB被处理器规范化。处理器还自动输出轻量PIL GIF预览，但PNG才是透明通道依据，未用FFmpeg/Unity。

注意process共享origin为原生格中心；anchor_y_std=0只说明声明的网格原点固定，不能证明脚底固定。候选真实脚底root估计、每帧时长与PNG SHA见metal-idle-v2-candidate-frames.json、metal-attack-v1-candidate-frames.json；人工估计未应用，未校准为正式引擎pivot。

待机建议4×250ms循环；攻击建议120/100/100/70/100/160ms单次，始终正序，不倒放。时长未经过运行播放验收。待机保留约6px行间脚底差；攻击下排较上排脚底高27–35px，第4帧站位明显改变，需根点/时序审查。所有刀盾保持左刀右盾，无明显主体裁断或格间串入。

两个动作同一scale0.84、512×512、root256,420尝试严格失败且未发布输出：idle左越81px+底20px；attack左越59px。原生微弱alpha残留保留与自动stance根点造成容器边界越界，没有放宽检查、清alpha、逐帧fit或强制裁断。现有10帧是原生候选，不是正式512归一包或已验收动画；后续需在完整alpha保留、共享身体尺度和准确根点之间明确最终画布/注册合同。

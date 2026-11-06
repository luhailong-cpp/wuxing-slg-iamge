# 五行角色 UI 派生预览 v1

仅使用现有五张原创透明母版，25张静态PNG：每人原生脸部、原生胸像、128/256头像、768×1152卡面预览。没有AI重画、抠图擦除、新绘边框或动作帧。

128和256头像共用方形透明容器、各留8/16像素基础内边；源矩形裁切等比以预乘alpha LANCZOS下采样，整数居中。128头像脸部约41–64像素宽；水系为保留向外辫梢，脸部略小。原生脸部/胸像不缩放，故各人尺寸不同。卡面完整源画布缩至704×1056，放入768×1152透明画布，偏移32/48；没有按每人alpha框单独拉伸。

这些是矩形肖像构图候选。脸部裁切旁边可见同一角色法器的局部，胸像下边有意截断衣服、木杖或土盾；没有把边缘片段擦掉冒充完整抠像。完整人物和法器以卡面预览为准。头像尚需用户确认是否采用这种构图，不能当作最终独立头部轮廓。

原生soft alpha与alpha1残留保留；下采样会重新分配alpha。浅深底与128/256实际像素预览已经逐项查看；每图的cropBox、resizeTo、实际XY比例、透明padding、pasteOffset、sourceSHA和WARN均在相邻.derivation.json。QA图仅为纯背景复核，无新增产品边框。

母版、称号、首发名单和各派生图均未获用户批准。userApproved=false、officialLaunchAdopted=false、clientIntegrated=false。此批无角色动画。

清单：`hero-ui-manifest.json`。QA：`records/01-率土之滨/hero-ui-v1-derived-review-20261027.json`。独立Unity扩展将采用Assets/WuxingSLGHeroSkillUIPreview/目录，避免覆盖基础V2或FX包；实际导出/回导证据另记。

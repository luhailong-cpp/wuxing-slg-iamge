> **2026-10-28 当前要求已纠正：横版；金木水火土是五种兵种，不是五系角色；其他系统与武将身份按率土之滨参考，保持道家Q版。以下冲突的旧判断仅作历史。见 [当前要求](CURRENT_REQUIREMENTS_20261028.md)。**

# Unity 交付约定（当前候选）
 
用户已明确选择 **Unity 导入包**。实际验证编辑器是 Unity 6000.6.0f1；这个版本是本机验证环境，不替代用户实际客户端版本。现有包都附源图/派生记录和哈希，仍待美术确认及正式客户端验收。

| 当前包 | 内容 | 实际验证 |
|---|---|---|
| [基础 V2](../exports/01-率土之滨/unity/WuxingSLGArtPreviewV2-20261027.unitypackage) | 111 Sprite：新版36 UI切片与既有地图、单位、徽记、角色母版等 | 源工程导出、独立空工程回导111通过；控件另有D3D11实际渲染 |
| [FX 动画](../exports/01-率土之滨/unity/WuxingSLGFXAnimationPreview-20261027.unitypackage) | 64独特帧、8 AnimationClip，每Clip 8 key、约0.8秒 | 源导出与空工程回导；真实GPU PlayMode按00→07播放，清除另由调用方实现 |
| [角色与技能 UI](../exports/01-率土之滨/hero-ui-v1/unity/WuxingSLGHeroSkillUIPreview-20261027.unitypackage) | 25角色静态派生＋20技能图标，共45 Sprite | 源导出与独立空工程回导45通过；与基础/FX路径及GUID无冲突 |
| [FX GPU 示例](../exports/01-率土之滨/fx-gpu-playback-v1/WuxingSLGFXGpuPlaybackDemo-20261027.unitypackage) | 录制场景、调用脚本及8 Controller；不复制64帧 | 须先导入FX动画包；空工程依次导入后8Clip、64Sprite和场景引用解析通过 |
| [地图拼装示例](../exports/01-率土之滨/map-assembly-v1/unity/WuxingSLGMapAssemblyPreview-20261027.unitypackage) | 7个复用Sprite、39实例、相机/场景/固定路线脚本 | 实际导出及空工程回导；D3D11真实PlayMode275帧、5脚点×浅深10截图检查 |

前三个资产包合计220个Sprite、8个绘制相位Clip；地图示例另有7个复用源像素的Sprite，并非7个新绘艺术资产。FX示例是可选技术录制场景。旧111包仅为历史版本，当前基础包使用V2。独立资源根分别为 Assets/WuxingSLGArtPreviewV2/、Assets/WuxingSLGFXAnimationPreview/、Assets/WuxingSLGHeroSkillUIPreview/；两个示例根为 Assets/WuxingSLGFXGpuPlaybackDemo/、Assets/WuxingSLGMapAssemblyPreview/。

导入采用100 PPU、Single/FullRect、输入alpha、无压缩RGBA32、无mipmap和NPOT缩放。源PNG尺寸与alpha保留；头像/图标不设置九宫格边距。UI的候选边距只用于已验证的固定204高横向控件，500→900宽的角部比对通过；500×300纵向拉伸不接受。四组控件仍按固定高度使用，不能据此把全部UI判为任意九宫格可用。

五位角色的face/bust为矩形构图，会截衣缘和同人物法器；128/256头像有透明容器，完整立绘使用768×1152卡面。没有擦除重画。技能32仅作小标识，主展示建议64或以上。soft alpha、残余alpha1、法器碎边和原始safe-frame WARN见各manifest/usage；技术导入通过不表示这些视觉限制消失。

FX仍只有8个原生绘制相位，约10FPS，不因60Hz录制变成60个新绘制帧。0.8秒时正式调用方须hide/recycle；原Clip末帧非空。GPU示例实际每效果每背景记录60次捕获，1秒游戏时钟约9.2秒墙钟；这是确定性录制，不是设备60FPS性能结果。浮点键边界诊断与源图相位WARN保留，详见[播放验证](../records/fx-gpu-playback-v1/final-review.json)。

[地图拼装预览](../exports/01-率土之滨/map-assembly-v1/playable-preview.html)复用6种地形/物件和1步兵，35地块；碰撞/道路另写provisional数据，Chrome实际6/6路线通过。Unity示例验证7PNG/39实例/8路线点，真实GPU固定路线、暂停/重启和脚点通过；6目标与去桥4不可达沿用canonical数据，并非Unity新A*。场景只固定SE静态平移，3:2/1440×960采样，原生键盘未注入。地块接缝、桥前栏、遮挡、任意纵横比和移动端均非最终验收。[地图Unity完整验证](../records/01-率土之滨/map-assembly-v1/unity/verification.json)。

尚待明确或完成：目标设备/分辨率与safe area、首发五行角色与NPC名单、正式技能和数值、字体与动态文字层、完整适用状态、真实角色/兵种动作源片、实际Unity工程及客户端视觉验收。已选择Unity，不再将“引擎未定”列作阻塞。当前所有 userApproved=false、clientIntegrated=false，完整游戏美术仍未完成。


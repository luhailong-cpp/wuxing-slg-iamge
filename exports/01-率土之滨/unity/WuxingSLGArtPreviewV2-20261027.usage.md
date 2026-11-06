# WuxingSLGArtPreviewV2 使用限制

本包是111个静态 Sprite 的导入预览候选：36个修正 UI 替换旧36个，其余75个源PNG沿用。Unity6000.6.0f1实际导出与独立空工程回导均验证111个 Sprite 通过。美术仍待用户确认，未集成实际客户端。

## 控件尺寸限制

16个控件均以500×204透明画布、中心250/102注册。**固定204像素高，仅作横向伸缩候选；实际测试宽500与900两个端点。纵向500×300不支持，未通过视觉检查。** 其他宽度、连续范围和实际 Canvas 布局未经验证。

| 控件组 | 数量 | 500×204 | 900×204 | 500×300 |
| --- | ---: | --- | --- | --- |
| primary 主按钮 | 4 | 完整轮廓候选 | 角饰保留，中心材质拉伸 | 侧玉珠/卷饰明显纵向拉长，不支持 |
| secondary 次按钮 | 4 | 完整轮廓候选 | 角饰保留，中心材质拉伸 | 侧玉珠/卷饰明显纵向拉长，不支持 |
| tab 页签 | 4 | 完整轮廓候选 | 角饰保留，中心材质拉伸 | 侧玉珠/卷饰明显纵向拉长，不支持 |
| card-row 卡片行 | 4 | 完整轮廓候选 | 角饰保留，中心材质拉伸 | 纸面/边缘材质纵向拉伸，未接受；同样固定204高 |

候选 border 为left/right128、top/bottom90。48张真实GPU Camera.Render图均非空；这只证明实际渲染产出。32项放大比较的四角128×90像素完全相同，不代表边中饰件不变形，更不代表九宫格全面通过。若需要改变高度，应后续独立处理饰件与可拉伸底板并重新验收。

36个UI保留原生alpha1残留，13个存在较窄可见余边WARN。所有36个输出alpha>16边缘为0；21个重切与15个原样复制均与声明的源像素操作一致。没有程序重画、缩放源图、去背或修改alpha。

clientVerified=false；userApproved=false；clientIntegrated=false。本包不含动画。原111包及独立FX动画包保持各自路径。

实际验证与限制详见项目记录：
- `records/01-率土之滨/runtime-ui-v2-unity-final-review-20261027.json`
- `records/01-率土之滨/unity-ui-v2-source-import-validation-20261027.json`
- `records/01-率土之滨/unity-ui-v2-roundtrip-validation-20261027.json`
- `records/01-率土之滨/unity-ui-v2-sliced-render-20261027.json`
- `records/01-率土之滨/qa/runtime-ui-v2-sliced-group1-light.png` 至 group4 的浅深底图

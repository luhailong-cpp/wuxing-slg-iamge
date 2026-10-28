# 连续草地底板（候选）

这次实际修复了旧草格的独立石圈和花围边，提供一张原生连续草地。单张画面可承接城池和单位；重复拼接仍未通过，不能当作无缝图块。

- 原生导出：continuous-grass-plate-native.png，1774 × 887，RGBA，未缩放、未重绘、未修改 alpha。
- 独立预览：continuous-grass-preview.html，离线打开；可查看单张、城池/金兵静态脚点、3 × 3 接缝及透明缝标记。
- Unity 包：unity/WuxingSLGContinuousGrass-20261028.unitypackage，1 Sprite + 1 Prefab。Assets/WuxingSLGContinuousGrass20261028 为独立根。
- Unity 6000.6.0f1 源工程导出与独立空工程回导通过，PNG 哈希一致。100 PPU、Single/FullRect、无压缩、无 mipmap、无 NPOT 缩放、中心 pivot (0.5,0.5)，Prefab sort order -100。没有 GPU 或 PlayMode 验证声明。

3 × 3 使用原像素和整数位移 (806,397)、(-806,397)。深底可见斜向细缝；预期内部有 1,440 像素 alpha ≤ 16、8,181 像素 alpha < 128。对边 RGB 样本只是辅助诊断；实际未通过结论也有图像证据。14,245 个原生 alpha=1 像素原样保留。不要通过过度缩放、模糊或改 alpha 把此素材冒充无缝格。

主城保留旧素材原像素，金兵仅在静态 QA 中缩到 100 × 100。它们不包含在草地 Unity 包中，静态摆放不代表兵种动作通过。单张底板覆盖有限区域；河岸、道路接口与桥头仍待制作。没有更新旧地图，亦没有碰撞、寻路或正式客户端验收结论。

调用、参考图、哈希和真实参数见原生图旁 generation.json；派生见各图旁 derivation.json。完整 evidence 在 records/terrain-continuity-20261028，主清单为 continuous-grass-manifest.json。配置目标模型/质量为 gpt-image-2.5-sunburst / max，内置工具不暴露选项或实际元数据，因此实际模型/质量仍标未核实。

# 五行兵种独立 Unity 静态资源包

20 Sprite：金、木、水、火、土各有1254×1254原生副本、256×256的64h/128h显示图，以及128×128图标。以源troops-manifest.json的sprites数组为合同，原生pivot为逐兵种视觉脚点，64h/128h为(0.5,0.125)，图标为(0.5,0.5)。这些脚点尚未做物理或动画校准。

导入到独立 Assets/WuxingSLGFiveElementTroopsV1/，100PPU、Single FullRect、RGBA32、NPOT None、无mipmap/压缩，保留原始透明RGB与alpha，包括alpha1残留。源PNG与来源JSON内嵌；5个native与母版逐字节相同。包制作阶段没有生图、缩放、抠图或像素修改。

完整合同、warnings、派生过程见包内Provenance及同目录source-index.json。原始18%余边提示未达标；alpha>1轮廓未截断，警告保留。仅SE静态；动画帧0，不含新方向、战斗规则、动画、客户端接入或最终用户美术验收。

实际Unity导入、空工程回导与完整RGBA像素哈希结果见 records/troops-20261028/unity。使用资源包不代表实际游戏客户端或GPU布局已验收。

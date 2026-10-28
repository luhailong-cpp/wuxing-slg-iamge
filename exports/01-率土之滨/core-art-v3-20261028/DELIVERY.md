# 基础候选包 V3 交付

74 Sprite：36公共UI、33地图资源、5原生兵种徽记。来源清单和源PNG均未修改。74直接来源记录及22上游记录，共96份独立来源JSON，随包保留；直接记录在便捷查阅目录和完整来源链目录各有副本，副本不计为新增来源记录。

Unity6000.6.0f1 实际源工程导出与另一空工程回导均通过，74张完整RGBA像素、PNG字节、alpha统计、尺寸、pivot、border和来源记录匹配。包内仅有合同要求的74张PNG；未含旧三兵种、五系英雄或技能图。

16控件仍限制204高，既有GPU只测试500与900宽的横向候选；纵向拉伸未接受。面板、UI图标、兵种徽记、地图不设九宫格。新包技术导入并非新GPU、客户端或用户视觉验收；余边、低alpha、地图接缝/碰撞/导航和历史回执限制继续保留。

完整证据：records/core-art-v3-20261028/delivery-summary.json、unity-source-validation.json、unity-roundtrip-validation.json、unity-package-archive-audit.json。具体使用条件见USAGE.md与usage-constraints.json。

这是当前正确合同的基础候选包，不是整款游戏美术完成。

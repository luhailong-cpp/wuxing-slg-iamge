# 五行兵 Unity 交付

5 兵种，20 张静态 Sprite：原生副本、64h显示、128h显示、128图标各5张。独立导入根为 Assets/WuxingSLGFiveElementTroopsV1/，已在 Unity6000.6.0f1 实际导出并回导到另一个空工程。

两次验证的20张完整RGBA像素哈希（含透明RGB）、PNG字节、尺寸、alpha统计、pivot、border和导入设置均匹配。逐图来源记录内嵌；母版、源清单及源派生图未修改。包旁来源JSON及 records/troops-20261028/unity/delivery-summary.json 为验证入口。

原生18%余边未达标与alpha1残留警告保留；只含SE静态视角，动画帧0。未新增静态场景，也未声明GPU、实际客户端或用户最终美术验收完成。

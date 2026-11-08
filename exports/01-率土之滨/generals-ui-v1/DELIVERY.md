# 三国武将 UI 包交付记录

12 位已有人物，60 张静态 RGBA PNG：每位 native 脸部、native 胸像、128 头像、256 头像、768×1152 完整立绘卡面各 1 张。新生成图为 0，母版未改。

交付入口：`generals-ui-manifest.json`、`USAGE.md`、`unity/WuxingSLGGeneralsUIV1-20261028.unitypackage` 及包旁的来源 JSON。逐图旁有独立 derivation JSON。

Unity 6000.6.0f1 实际源工程导入导出及独立空工程回导均通过，60 Sprite 的字节、尺寸、alpha、pivot、border 和设置匹配。28 张浅深 QA 已人工查看，记录在 `records/generals-ui-20261028/final-visual-review.json`；完整汇总为同目录 `delivery-summary.json`。

头像是矩形取景，保留持物局部，长兵器和羽冠可能被取景框截断。孙权、赵云源图余边不足、吕布历史生成回执不全、原图低 alpha 像素保留。包内早期检查记录保留其当时状态，最终完整视觉检查以外部 final-visual-review.json 为准。

这是可回导的静态美术候选包，未含动画、客户端接入、GPU 布局测试或最终用户美术验收；12 人也不等于整款游戏的完整武将名单。技术通过不代表整款游戏美术完成。

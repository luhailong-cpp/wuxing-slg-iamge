# 2026-11-11 五行问鼎美术接续

当前真人要求：**不要用 computer use；告诉我审核就行。** 禁止 Computer Use、CUA、sky 及其他浏览器或桌面 GUI 自动化。继续生图、导出、文件检查和授权 Git 同步。画风、动作实速、界面显示与游戏效果由用户审核；技术通过不视为用户视觉通过。保留有效历史记录。

本轮实际制作五批、15张原生1024×1536 RGBA人物母图和75张UI派生。全部为 **待用户视觉审核候选**，尚无新增用户采用项。人物库现在为历史90名加15名待审候选，共105身份母稿候选、525张UI；不能作为完整名册或整款完成证明。

| 批次 | 新人物 | 导出 |
| --- | --- | --- |
| heroes7 | 公孙瓒、马腾、诸葛瑾 | 15 UI |
| heroes8 | 田丰、徐盛、吴夫人 | 15 UI |
| heroes9 | 张绣、曹洪、蒋钦 | 15 UI |
| heroes10 | 孙桓、董袭、丁奉 | 15 UI |
| heroes11 | 刘虞、刘焉、刘表 | 15 UI |

请审核这一批：[静态审核页](../records/user-review-20261111/index.html)、[浅底总览](../records/user-review-20261111/summary-light.png)、[深底总览](../records/user-review-20261111/summary-dark.png)。页面可分别打开完整原画、实际128头像与各批浅深预览。检查画风与人物辨识、肢体和持物完整性、浅深底边缘。未调用GUI检查或代用户确认。

每人五种规格：face-native与bust-native为不改像素的原生RGBA裁切；avatar-128/256等比预乘Alpha Lanczos缩放；card-full为768×1024等比整身卡面。原图保持宿主返回字节，未对alpha阈值清理。各图的prompt/request/response、真实附图与哈希、原生尺寸、生成和派生链均已保存。宿主工具没有model/quality选择器；配置目标仍按配置快照保存，实际model/quality均为null，不声称已锁定型号或质量。

技术检查覆盖15原图、75派生、30原生裁切；统一105人物无重复personID，历史90人物条目保留。审核包109条本地文件链接、字体35个姓名字符无缺字的静态检查已完成。详见[最终数据复核](../records/production-20261111/final-integrity.json)。本批没有新增动作，不作实速播放或客户端通过声明。

49项WARN逐文件、数值与阈值完整保留于各批manifest和[审核包元数据](../records/user-review-20261111/summary-metadata.json)：15项SOURCE_ALPHA1_RETAINED（阈值0）、15项SOURCE_MAX_ALPHA_BELOW255（值254、阈值255）、14项SOURCE_MARGIN_UNDER8PCT（阈值0.08）和5项INTENTIONAL_PORTRAIT_WINDOW（值true、阈值false）。完整原图没有边缘实体截断；头像和半身本来就是肖像窗口。提示不是用户批准，整身留边也不被后处理冒充原生修复。

源游戏已核实为《率土之滨》；可靠本地依据是2026-10-29网易官方配置冻结快照。现有证据不能核定客户端版本，请勿将URL中的v=9_29_4参数当作版本。见[源游戏和版本边界](SOURCE_VERSION_SCOPE_20261111.md)。没有下载不明客户端或启用付费API。截图6–9原件已在库，1–5仍缺。

[最新机器清单](../records/current-art-catalog-20261111.json)区分待审身份母稿、卡号独立图、完整名册、UI、地图与Unity。430公开配置卡中164卡关联身份母稿候选（23卡关联本轮待审人物），194卡仍需身份母稿；另有身份疑义、组合、通用与联动卡，不能把194称为全部缺口。独立逐卡图仍仅2张。名册全量逐卡、三国原典逐卷逐回对账尚未完成。

继续制作人物，先处理[27名证据就绪且未有母稿的候选](../records/production-20261111/next-production-candidates.json)，并跟进本轮用户审核意见。张姬身份、三个张恭实体继续分开待核。人物完成后再做六组新参考界面，目前六组新图仍为0；地图750×750世界、五兵行走/多方向、正式战斗、全状态客户端验收仍未完成。Unity接入按用户要求顺延，本轮75张不冒充已导入。

仅使用 E:/work/wuxing-slg-iamge。发布依当前用户授权采用正常commit与正常push，不force、不reset/clean、不改写历史。真实远端SHA和LFS适用情况见本机 records/publication-local/published-receipt-20261111.json；不存在回执时不得称已上传。本库目前没有LFS跟踪文件，不能编造LFS上传数量。

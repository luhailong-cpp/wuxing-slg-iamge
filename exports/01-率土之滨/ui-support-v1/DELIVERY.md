# UI 补充组件交付

16组件、32RGBA PNG（16原生、16个128容器）、32逐图来源记录、10浅深QA、1独立Unity包。原生16裁片与母图对应区域逐像素一致；母图413945个alpha>16像素全部恰归属一次，遗漏/重复/邻项混入均为0。alpha阈值只用于检测，未用于清理输出。

Unity6000.6.0f1实际导出与独立空工程回导都通过；32完整RGBA像素哈希、字节、尺寸、alpha、pivot及border均匹配。原始母图与生成侧记保持不变。

原生及128浅深共10视图已逐张查看。checkbox/toggle两态几何不同，progress未验证拼合、裁剪、任意拉伸或九宫格；scrollbar行程和点击区未校准。所有border0，长条保持比例。输入/数据层、状态逻辑、真实客户端和最终用户美术验收未完成。

证据：records/ui-support-20261028/export-ownership-validation.json、export-visual-review.json、unity/delivery-summary.json。具体用法见USAGE.md。

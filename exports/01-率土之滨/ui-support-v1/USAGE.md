# 通用 UI 补充组件

16项静态组件、32张RGBA：每项native原生裁切和128×128透明容器各一张。search/close/back/settings；checkbox-checked/unchecked、toggle-on/off；scrollbar-thumb/track、progress-frame/fill；tutorial-hand/warning/mail/notification。

16原生切片逐像素来自同一1254母图；16显示图将整个裁框用预乘alpha LANCZOS等比缩小至112×112内，再居中于128容器。没有擦除、key、阈值清alpha或重绘。alpha>16仅用于检测：413945可见像素全部恰归属一次，没有漏裁/重复/邻项混入；裁框外alpha<=16背景残留未纳入资源。

Unity独立根 Assets/WuxingSLGUISupportV1/，Single FullRect、100PPU、中心pivot、border0、RGBA32、无压缩/mipmap/NPOT缩放，输入alpha和透明RGB保留。来源记录、归属检查和人工浅深QA报告内嵌。

checkbox两态云饰与框形并非同几何；toggle两态轮廓与宽度也不同，切换需要独立布局，未做像素配准或点击区验收。scrollbar滑块/轨道尺寸与行程未校准。progress两层未验证拼合、裁剪、任意拉伸或九宫格，当前全32资源border0。128长条图保留细长比例，不代表控件实际高度或可任意伸缩。notification为红色宝石样式。

本包仅静态美术候选，不含输入/数据行为、补齐hover/pressed/disabled状态、真实客户端或用户最终视觉验收；动画0。技术验证入口 records/ui-support-20261028/unity，视觉与归属检查在 records/ui-support-20261028/export-*。

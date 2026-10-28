# 金兵4动作20帧统一接地候选

当前导出20帧：idle4、attack6、hurt4、defeat6。walk未通过，未混入。本次没有生图、Unity或FFmpeg；仅读取4张现存母sheet作确定性配准。

共60 PNG：每帧3份。native1024为整格原生RGBA加整数平移，源格每一个RGBA字节（含弱alpha和透明区RGB）都保留；normalized1024为每动作唯一比例的预乘alpha Lanczos缩小与整数平移；map128h为整个1024画布统一缩到384。源图和逐图生成记录不改。

公共根点：1024画布(512,768)，384画布(192,288)，Unity底左归一pivot均(0.5,0.25)。根点取人工逐帧圈定的两只靴底/膝底接地点中点；先在原始坐标登记，再移动整帧。每动作只一个缩小比例，以中立帧硬质头盔含耳板的宽度统一到约180px，排除羽冠、刀盾和全身姿态bbox。没有逐帧fit、逐帧拉伸、擦alpha或裁掉弱alpha。缩小不可逐像素保真，但没有额外透明度阈值处理，全部重采样后的源矩形都保留；原生版是逐像素依据。

测得四动作头盔宽179.90–180.09px，接地中点的数值误差最大0.705px；该误差不含人工接地和头盔量测的不确定性。母版map128h可见轮廓实际128px。倒下动作规范版轮廓从315逐步降至201px，跪地并未拉成站高。

已实际查看4源图、20帧接地标点、各动作浅/深背景与384画布实尺寸，以及全20帧浅深总览。刀左盾右保持、无输出画布alpha触边、所有完整源矩形均在容器内。可证明接地配准/保全/尺度计算成立；单靴步幅与支撑线角度变化仍来自原图，未作重画。动作流畅度、提议时长、母版身份用户认可及Unity回导尚未验收。

manifest.json记录源SHA、逐图记录SHA、人工接地ROI、接地点、root、各帧整数offset、动作唯一scale、PNG SHA和alpha统计；clips.json提供候选时长和相对路径。正式接入选normalized1024或map128h，native1024用于保全与溯源，不能混用为统一比例运行帧。

总览：
- ../../../../records/troop-frames-20261028-r2/metal-grounded-20-overview-light.png
- ../../../../records/troop-frames-20261028-r2/metal-grounded-20-overview-dark.png

脚本和人工坐标在 records/troop-frames-20261028-r2/metal-ground-*。可复用入口metal-grounded-frames-export-reusable.py仅接受已人工审查的measured manifest；必须为每动作提供头盔宽度和每帧接地坐标，不能自动把姿势bbox当尺度。输出目录必须新建，禁止覆盖。调用参数说明见同目录脚本README。

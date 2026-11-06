# 接地候选帧的可复用轻量方法

执行目录必须显式为当前美术项目根。入口 metal-grounded-frames-export-reusable.py 接受已经人工核对的 measured manifest；不负责猜脚底、不生成姿势、不逐帧fit。金兵实际执行的固定输入版本为metal-ground-export.py，保留原执行代码；通用参数入口仅通过AST语法解析，未额外重复导出60张。

固定公共合同：native与normalized都是1024×1024，top-left根点(512,768)；每动作一个缩小比例，将中立参考帧硬质头盔含耳板宽度标定到180px，不把羽冠/刀盾或弯膝后的全身bbox用于归一。map128h为整张1024→384，根点(192,288)，Unity归一pivot(0.5,0.25)。母版站立轮廓参考实测128px，不强迫每个动作都128高。

制作顺序：
1. 实际看每张源sheet，逐帧手动标出两只靴/膝接地区域。以金兵metal-ground-registration-input.json为结构样例。
2. 可用metal-ground-measure-contacts.py的contact函数在选定ROI内找底5px支撑范围的中心。该脚本目前是金兵固定入口；其他兵必须换自己的新输入和输出路径，不能直接覆盖金兵记录。必须实际查看每个接地标点，拒绝刀尖/盾缘等误归属。
3. measured manifest给每帧sourceRect、groundRootInteger、contactMeasurements、durationMs；每动作提供helmetWidth及uniformActionScaleTo180Helmet=180/helmetWidth。提供source/sourceRecord/sha及行列信息。每个动作的所有帧用同一scale，若头盔自身绘制尺寸漂移，保留并报告，不能逐帧fit。
4. 调用通用导出器，输出目录必须新建；完整源格先整数平移，随后只以动作唯一比例缩小并整数平移，最后整画布map派生。所有完整矩形必须在画布内；像素校验失败即停止。
5. 看浅深背景、根点标线和实际显示尺寸，更新候选状态；Unity仍暂停，技术配准不能替代用户或动画播放验收。

通用入口示例（替换成该兵的人工坐标清单和全新输出目录；不要原样覆盖金兵）：
```powershell
# cwd: D:/work/wuxing-slg-iamge
$env:PYTHONUTF8='1'
& 'D:/luyuan/image-skills/runtime/agent-sprite-forge/.venv/Scripts/python.exe' 'records/troop-frames-20261028-r2/metal-grounded-frames-export-reusable.py' --project-root 'D:/work/wuxing-slg-iamge' --input-manifest 'records/NEW-BATCH/element-ground-measured.json' --output-dir 'exports/01-率土之滨/NEW-BATCH/element-grounded-candidate-v1' --record-dir 'records/NEW-BATCH' --prefix 'element-ground' --character-id 'troop-element' --master-root '700,1160'
```

上述master-root仅是金兵示例，其他兵必须人工测量；同样不能复制金兵靴底ROI或头盔宽度。源坐标定义是左上原点。根点为两接地点的投影中点，透视下两脚可以一高一低；固定中点不会伪造单脚无滑动。

所有原生RGBA像素在native1024版逐字节保全，包括alpha1和透明区RGB。缩小版进行正常预乘重采样/8位量化，不额外清alpha，不裁掉像素域。图像缩小本身不能声称保留每个原生像素。

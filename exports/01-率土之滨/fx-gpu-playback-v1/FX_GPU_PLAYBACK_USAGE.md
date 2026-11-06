# FX 实际 GPU 连续播放证据 v1

Unity6000.6.0f1 的真实 PlayMode、Direct3D11、NVIDIA GeForce RTX3070Ti 已运行现有8个 AnimationClip。Animator Normal 自动推进每个原始 Clip，没有逐相位手工指定 Sprite，也没有改变源图。

`records/fx-gpu-playback-v1/video/all8-light.mp4` 和 `all8-dark.mp4` 是实际GPU序列的4×2总览。阅读顺序：slash-arc、strategy-array、healing-light、buff-cloud；debuff-mist、fire、capture-circle、reward-glow。同目录有16个单效果/背景的512×512录制。`montages/` 是8相位、caller clear、末后清除的实际截帧对照，标签为实际游戏时钟。

录制采用Time.captureFramerate=60。每个效果/背景60次实际GPU捕获，共960张；1秒游戏时钟耗约9.2秒墙钟。这是允许GPU读回与PNG写盘的确定性录制，不是设备60FPS性能测试。MP4以60Hz编码60张连续实际捕获，视频时间0对应源游戏时钟1/60秒；没有补间。原始8个绘制相位仍约10FPS。

8种都观察到frame00→07，world anchor固定0、scale固定1、相机orthographicSize6.4、PPU100；所有锚点投影固定256/256。0.8秒时由演示调用方禁用renderer/Animator并清空Sprite，随后每背景连续13张截图均与GPU空背景逐像素相同。**原Clip本身仍保留非空末帧，不会自动消失；正式客户端必须自行实现hide/recycle。**

浮点键边界有保留的48条epsilon期望相位诊断，距离名义键时间最大约0.228微秒；752个可见样本都在实际所示相位区间的1微秒容差内。实际相位采样数为5–7张，不宣称每相位恰好6次捕获。详见`timing-analysis.json`与未经改写的`actual-playmode-capture.json`。

完整960张GPU原始PNG及2张空背景原始图留在本地`work/unity-fx-gpu-playback-v1-20261027/CaptureRaw`，未公开。公开材料包含18个MP4、16张相位/清除montage、48张选中的原生phase03/phase07/caller-clear截图及2张空背景。各自旁记记录源捕获哈希、时钟与操作；对work原始路径的引用明确为本地QA，不是远端可下载文件。

## 演示扩展包

先导入原包`exports/01-率土之滨/unity/WuxingSLGFXAnimationPreview-20261027.unitypackage`（SHA256 `18919229cf380d5cbd16cc6fa76fcb5197f94315d62af06d6b8c6ae54ea9e018`），再导入本目录`WuxingSLGFXGpuPlaybackDemo-20261027.unitypackage`。

新增资源仅在`Assets/WuxingSLGFXGpuPlaybackDemo/`，依赖旧FX包的64 Sprite/8 Clip GUID；不复制或覆盖这些资源。打开`Assets/WuxingSLGFXGpuPlaybackDemo/FXGpuPlayback.unity`并Play，会通过离屏Camera.Render连续录制并演示0.8秒清除，约1秒游戏时钟后停止。默认输出位于当前Unity项目的`FxGpuPlaybackOutput/`；这是自动捕获场景，不是游戏客户端或交互图库。

新空工程已依次实际导入依赖FX与演示包，8案例、8 Clip、8 Controller、64 Sprite引用全部解析。源工程实际GPU播放与扩展包独立回导分别记录，后者为headless引用验证，不冒充第二次GPU测试。

来源余边、低alpha和相位拓扑变化WARN继续有效。这里只验证播放顺序、注册、渲染与生命周期；finalSmoothnessApproved=false、userApproved=false、clientIntegrated=false。未修改旧FX包、manifest、README/catalog或Git。

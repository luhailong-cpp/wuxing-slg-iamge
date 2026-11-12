# Heroes10 — awaiting user visual review

本批实际制作孙桓、董袭、丁奉 3 张宿主内置 image_gen 原画及 15 张 UI 派生。原图均为实际 1024×1536 RGBA PNG，未重采样、未清理 alpha，来源与宿主输出逐字节哈希匹配。实际模型、质量未披露，记录为 null。

`technical-check.json` 只证明文件哈希、来源链、原生裁切像素、尺寸与透明通道检查通过，不代表视觉通过。`visual-review.json` 的 passed=false、technicalOnly=true、userApproved=false、rootVisualReviewPassed=false；当前状态为 awaiting_user_visual_review。浅深检查图和实际128像素头像已备齐供用户亲自审核。未使用 computer use、CUA、sky 或任何 GUI 自动化。

所有来源原生 alpha-1、alpha 最高254、边距小于8%的提示和有意的头像/半身裁切均保留在 manifest 和 technical-check 的 warnings。没有角色动作、方向、实速、Unity或客户端验收。

- 母图：`designs/01-率土之滨/characters/roster-expansion-20261111-heroes10/`
- 导出：`exports/01-率土之滨/roster-expansion-20261111-heroes10/`
- 提示词：`prompts/01-率土之滨/roster-expansion-20261111-heroes10/`
- 预览：本目录 `generals-ui-light.png`、`generals-ui-dark.png`，及导出目录3张 `*-avatar-128.png`。

未运行 register-reviewed.py，未改共享 roster、catalog、README 或 Git。复制的 register-reviewed.py 属旧内部登记流程，本批待用户视觉审核前不得运行。

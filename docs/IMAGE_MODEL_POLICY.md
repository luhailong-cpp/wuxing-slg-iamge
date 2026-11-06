# 模型、质量与逐图记录

## 设置与执行

[config/image-generation.json](../config/image-generation.json) 是本项目唯一默认设置入口。用户本次明确选择 GPT Image 2.5，目标产品、API 型号、质量档位和核验日期均读取该配置；不因其他技能中的旧默认值静默降级。同一批次保存启动时的设置快照。

新任务核对官方正式版本和最高画质能力。用户明确指定的型号优先；没有指定时，最新正式型号和更高质量档位在当前入口支持后更新配置用于新图，历史记录不改写。2026-10-26（America/New_York）已实际打开并核验：

- [官方模型页](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst)列出 Sunburst 型号、2026-09-08 快照及支持的画质。
- [生成指南](https://developers.openai.com/api/docs/guides/image-generation)列出 `low`、`medium`、`high`、`xhigh`、`max` 和 `auto`，`max` 是当前最高可明确选择的画质档位。
- [产品公告](https://openai.com/index/introducing-chatgpt-images-2-5/)说明 ChatGPT Images 2.5 已向 ChatGPT、ChatGPT Work 和 Codex 开放。

优先使用宿主内置 `image_gen`，无需 API 密钥。当前工具没有 `model`、`quality` 参数；产品开放公告和提示词目标均不能证明本次调用已显式锁定 API 的 Sunburst 分支或 `max`。继续使用宿主管理入口，按本次结果和可核实元数据记录实际版本。若之后工具提供真实选择器，再显式传入配置值。

API／CLI 是用户明确选择的备用路线，默认读取本项目配置；新的单独计费路线、订阅、预算或凭证变更需用户明确授权。参考图读取故障先排查输入通道，不据此要求配置 API 密钥。

## 逐图生成记录

每张生成图、候选稿、重试版本和 AI 编辑图独立记录。优先放在图旁 `<文件名>.generation.json`，也可放在对应游戏的 `records` 目录，由交付索引准确关联。必须包含：

| 字段 | 内容 |
|---|---|
| `file`、`sha256` | 图片相对项目路径与最终文件哈希 |
| `generatedAt` | 生成时间，ISO 8601 且含时区；原始时间未知时明确未知 |
| `width`、`height`、`format` | 实际原生尺寸和文件格式，导出尺寸另记 |
| `tool`、`route`、`resultId` | 实际入口和可得的调用／结果标识 |
| `configSnapshot` | 本次配置的 model、quality、builtin_product、verified_on、sources；用户显式覆盖另记 |
| `submittedParameters` | 真实提交参数；没有选择器的 model、quality 写 `null` |
| `actualModel`、`actualQuality` | 仅填本次返回或可靠来源证据确认的值，未确认写 `null` |
| `evidence`、`unverifiedReason` | 结果、receipt、C2PA 等证据位置和字段；缺失时写明「宿主管理，工具未披露／无可核实元数据」 |
| `prompt`、`references` | 实际提示词路径；每张参考图路径、哈希与用途；编辑另关联编辑前图片及其记录 |

实际返回快照时原样记录；仅返回系列名时仅记系列名。配置目标、提示词和公告都不能替代实际模型证据。交付索引逐张列出图片、记录和确认状态。

裁切、缩放、拼接等未再次调用生成模型的派生图记录 `derivedFrom`（来源路径、SHA256、记录）与 `operation`；多来源逐一列出。原生尺寸、处理步骤与导出尺寸分别记录，不把后处理称为模型新生成或原生高清细节。

复制进来的历史主参考以[参考清单](../records/style-reference-manifest.json)关联原始记录。只保留已有证据，原始模型／质量未披露就标记历史未核实，不按当前配置回填。素材清理遵守 [AGENTS.md](../AGENTS.md)，删除旧图仍保留必要来源文字和清理记录。

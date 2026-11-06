# 《率土之滨》官方名册来源与三国人物分母研究

研究日期：2026-10-29。实际项目：D:/work/wuxing-slg-iamge。仅只读联网、公开文本解析及轻量记录；没有启动 Unity、浏览器、FFmpeg、构建或 Git，没有抓取官方人物画像。采用 research 技能，本文件为受托后台研究交付。

## 可直接采用的结论

已经得到可复算的官方公开配置快照，及官方社区列表本身的筛选规则。**430 是该快照按官方页面规则得到的卡牌条目数，309 是不同显示名字符串数；二者都不是“全部三国人物”数量。** 原始配置共有975个唯一 hero_id，不能将内部配置总行数视为可收集武将数量。数据来源是官网导向的率土百家社及其公开 CDN，而非第三方攻略。[官网](https://stzb.163.com/index.html)、[官方社区](https://stbj.163.com/pc/1/01?from=gw)、[官方武将配置](https://g0.gph.netease.com/ngsocial/community/stzb/cfg/hero.json?gameid=g10)。

| 层级 | 本次计数 | 准确含义 |
|---|---:|---|
| 配置行 / 唯一 hero_id |975 / 975|包含 is_release=0、通用单位和占位记录|
| 配置中 is_release=1 |642|只是官方字段标记，不代表642个独立人物|
| 官方公开列表 |430|应用官方前端的三条件筛选|
| 列表不同显示名 |309|同名异卡合并后的字符串，未做历史身份消歧|
| 列表通用兵 |32卡 / 5名|禁军、精兵、官兵、军士、武官|
| 列表多人/群体 |9卡 / 8名|组合卡需要单独画面或成员拆解|
| 列表单体名称候选 |389卡 / 296名|仍含非三国、非人物实体，不能当历史人物分母|
| 全部 is_release=1 单体名称候选 |300名|额外包括董旻、牛辅、郭汜、李傕；未做别名/同名消歧|

以上均为本次对官方事实表进行的本地计算。卡牌行逐条保留源 URL、源 SHA、原始数组位置、cardid/name/faction、quality、season/is_sp_card/is_season_card/base_hero_id/icon_hero_id。**实际规范人物总数仍为 null，最新客户端全覆盖尚未证实。**

## 官方证据链与可复算口径

1. 官网 /index.html 实际提供“武将库” /card_list.html 与“百家社”链接。桌面、移动武将库页面返回200，但它们引用的 stzb.res.netease.com 数据脚本本次连接重置，未获得旧站名册交叉核对。[桌面武将库](https://stzb.163.com/card_list.html)、[移动武将库](https://stzb.163.com/m/card_list.html)。
2. 官方社区 HTML 标题与 publisher 指向网易；它加载 /pc/config/module.js，该公开配置指定 cdnHost 为 g0.gph.netease.com/ngsocial/community/stzb。[社区配置](https://stbj.163.com/pc/config/module.js)。
3. 社区实际加载的 index-CoxhlTyj.js 构造 /cfg/hero.json?gameid=g10，并在武将网格组件中筛选 name 不等于侍卫、is_season_card 不等于1、is_release 等于1。相同脚本有阵营字典 1汉/2魏/3蜀/4吴/5群/6晋、quality星级筛选1–5以及SP标签条件。[官方前端脚本](https://g0-web.gsf.netease.com/community/stbj/js/index-CoxhlTyj.js)。
4. 官方 hero.json 在2026-10-29T08:12:49.582Z成功读取418426字节；随后按前端的月_日_小时缓存参数再次读取，字节哈希相同。SHA-256：2aea5138afdd31a6876cafa5aa1e3f56a5df14e0a6771f051da6ccad75ed2dbe。服务器未提供本任务可用的“全客户端版本/名册完结”声明；抓取时间不是游戏数据更新时间。

本次没有执行官方 JavaScript，只按文本核对公开路径、字典及筛选式。页面自身规则不保证客户端图鉴完整，因此同时交付全部975事实行以免过滤掉潜在合法人物。公开网页代码与HTML缓存移入 work/roster-20261029，records只保留事实、来源与覆盖记录。

## 卡牌、人物、组合与皮肤必须分层

官方列表星级分布为1星18、2星14、3星68、4星156、5星174；阵营分布汉76、魏73、蜀66、吴70、群112、晋33；season原值分布N345、S2 20、SP21、S3 14、XP30。以上是同一430卡口径。

刘备就是同人异卡的具体例子：100044为汉4星，100016为蜀5星，100803为汉5星；三行均进入当前公开列表。130016和130803的season为SP、is_season_card=1，虽标记is_release=1却被页面过滤；配置内另有is_release=0的刘备记录。本项目现有刘备4星稿不能声称覆盖全部刘备卡面，但可以作为同一人物的身份母版。[事实来源](https://g0.gph.netease.com/ngsocial/community/stzb/cfg/hero.json?gameid=g10)。

保留season、is_sp_card与is_season_card三个字段，不能把season=SP一律解释成同一种正式SP卡：本表中season=SP但is_sp_card=0的赛季复用记录确实存在。base_hero_id和icon_hero_id能支持关联判断，但不是跨名人物合并或独立皮肤数量的充分证据。

多人/群体显示名为：十常侍、关兴＆张苞、袁氏兄弟、小乔＆大乔、赵统＆赵广、颜良＆文丑、蒯良＆蒯越、蜀三相。先保留独立组合实体，再依据史料/卡面说明建立成员映射；本轮没有凭记忆把集合展开成人数。

董旻130658、牛辅130660、郭汜130662、李傕130663为is_release=1但is_season_card=1的记录；四个显示名没有进入430卡列表，故单独列入候选补查。不得用“页面没有显示”推断这些人不属于范围。

麦子、九色鹿、妲己、刘秀等也实际出现于官方表；其游戏身份应保留，但是否属于“三国历史/演义人物”必须另判。不能将游戏的跨时代/联动范围直接等同三国。官方源表中的步/弓/骑字段仅用于证据，不映射为本项目兵种；我们的兵种仍是金木水火土，人物与兵种分离。

## 完整三国人物补充库：建议固定语料后计算分母

建议分为两条可审计主线，最后按经确认的person_id求并集，不使用网络流传的某个“总人数”：

- 历史主线：以陈寿《三国志》65卷及裴松之注为固定核心语料。国家图书馆目录明确记载卷数、作者与注者；逐卷登记版次、正文/注引、卷页/段落定位、人名及同名消歧。[国家图书馆目录](https://guji.nlc.cn/resource/resourceDetail?id=1016560&type=ziyuan)。[中国哲学书电子化计划文本入口](https://ctext.org/sanguozhi/zhs)可作为检索候选，本次直接打开403，未完成65卷索引，不能说已穷尽。
- 演义主线：固定一个完整120回版本，逐回抽取具名人物、别名、称号与初次出现位置，并标明仅小说/兼有史证。[演义文本入口](https://ctext.org/sanguo-yanyi/zhs)。国家图书馆出版社对作品首回至第120回的说明支持该范围，但链接产品只选32回，**不能拿这份选本当全本**。[出版社说明](https://www.nlcpress.com/ProductView.aspx?Id=11790)。本次未读取全120回。
- 可选交叉核查：CBDB用于别名、同名和来源定位，其官方覆盖说明主要在7世纪到20世纪初，不宜作为三国全集分母，本轮不下载整库。[CBDB覆盖说明](https://cbdb.hsites.harvard.edu/coverage-cbdb)、[官方下载入口](https://cbdb.hsites.harvard.edu/download-cbdb-standalone-database)。

建议历史核心时间范围先采用公元184–280年有活动记载者；这是制作范围提案，不是已确认的用户边界。上溯祖先、后裔、引文中的更早人物单独标记而不静默删除；匿名角色、官职通称、群体和神怪另建实体类别。历史真人与同名小说角色可共享identity，但历史造型证据与小说追加情节分开记录。

最小人物行应有canonicalPersonId、canonicalName、aliases、history/novel/both/game_only、版本、卷/回、sourceURL、段落定位、同名区分、组合成员、纳入决定与理由。完成分母的条件是65/65卷与120/120回覆盖台账闭合，全部候选完成别名/同名复核，仍有争议者留pending而非强行合并。当前完整三国分母为未计算。

## 可立即落到生产的下一步

先用430卡作为“官方公开列表快照覆盖”的清单；从296单体名称候选中逐个确定identity，复用现有合格母版，再为异星级/阵营/SP卡建立variant条目。并行处理8组合显示名与4个被页面过滤的单体候选。非三国/非人条目保留官方来源状态，另列美术需求，不隐去。新增全三国人物以固定语料扩展，不用候选300倒推“所有人物已齐”。

皮肤/画像、周年新增卡、当前客户端可见性还需独立核验；本次没有官方画像下载，没有客户端验证，没有认定全名册完成。官网显示2026-10-28新闻及9月30日XP下放预告，但对应社区文章只返回应用壳，本轮不能拿标题作新卡明细证据。[官网新闻入口](https://stzb.163.com/index.html)。

## 交付文件

- records/roster-20261029/OFFICIAL_ROSTER_FACTS_20261029.json：975逐卡事实、源链、筛选、汇总。
- records/roster-20261029/OFFICIAL_PUBLIC_LIST_430_20261029.json：430卡公开列表快照。
- records/roster-20261029/OFFICIAL_DISPLAY_NAME_CANDIDATES_20261029.json：314个已发布标记显示名，其中300个单体实体名称候选；全部identityResolved=false。
- records/roster-20261029/RESEARCH_EVIDENCE_AND_GAPS_20261029.json：证据、排除规则、覆盖缺口和历史/演义分母方案。
- records/roster-20261029/http-evidence.json：成功和失败的只读HTTP记录、时间、尺寸与SHA。

本文件不是总美术索引，没有修改其他制作窗口的资产或名册。
# 五行角色与技能 UI Unity 预览包

45个静态Sprite：25个现有五行母版派生角色预览（每人原生脸部、原生胸像、128/256头像、768×1152整身卡面）和20个技能图标（5native＋各32/64/128）。没有动画或新生成人物。全部未获用户批准，未纳入正式首发，未接入实际客户端。

独立资产根Assets/WuxingSLGHeroSkillUIPreview/；不依赖或覆盖baseV2与FX包的assetpath/GUID，全部PNG和逐图来源JSON随包嵌入。角色/技能母图只作为仓库溯源，不是运行时依赖。导入约定：100PPU、Single/FullRect、无压缩RGBA32、无mipmap/NPOT缩放、保留输入alpha、中心pivot、border0；不要将其当作九宫格资源。

角色头像/胸像是矩形构图预览，会截断衣缘与同一人物法器；部分法器碎边仍可见。没有擦除或重画。完整人物与器物使用整身卡面。128头像脸部约41–64像素宽，水系保留向外辫梢而脸稍小。更详细裁切与缩放见相邻hero-ui-manifest及逐图derivation记录。

技能5张native采用手工归属框；所有sourcealpha>1像素恰覆盖一次、无重叠，裁切未清alpha。保留rawQC WARN：boundary_band=17 threshold0；safe_frame=5 threshold0；faint_specks={floor_px:68154,detached_components:9} threshold0。生成未满足96px原生余边，空第6格仍有259个alpha1像素。32像素仅作小标识，细金饰不作可读要求。技能语义、名称和玩法合同未确认。

所有softalpha/alpha1残留如实保留。源像素、尺寸、alpha计数、pivot、来源JSON哈希在Unity实际导出/空工程回导另行验证。技术导入通过不代表GPU播放、实际UI布局、最终头像构图或用户美术验收。clientIntegrated=false、userApproved=false。

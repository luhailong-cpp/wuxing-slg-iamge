import json,pathlib,hashlib,datetime
ROOT=pathlib.Path(__file__).resolve().parents[2]
UNITY=pathlib.Path('D:/work/wuxing-slg-unity')
BATCH='roster-expansion-20261102-heroes2'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
g=read(ROOT/'exports/01-率土之滨/art-review-20261029/generals-manifest.json')
assert len(g['people'])==72 and sum(len(p['assets']) for p in g['people'])==360
assert len({p['personID'] for p in g['people']})==72
for p in g['people']:
    assert sha(ROOT/p['master'])==p['masterSha256']
    for a in p['assets']:
        assert sha(ROOT/a['file'])==a['sha256']
        assert (ROOT/a['record']).is_file()
new=[p for p in g['people'] if p['batch']==BATCH]
assert len(new)==12 and sum(p['clientIntegrated'] for p in g['people'])==60
overlay=read(ROOT/'records/roster-20261029/CURRENT_PRODUCTION_OVERLAY_20261102.json')
overlay.update(updatedAtUtc=now,masterPeople=72,uiDerivatives=360,fullRosterComplete=False)
overlay['entries']=[p for p in overlay['entries'] if p['id'] not in {x['id'] for x in new}]
overlay['entries'] += [{k:p[k] for k in ['id','name','personID','master','masterSha256']} | {'uiDerivativeCount':5,'unityUiImported':False,'status':'master_and_UI_candidates_reviewed_Unity_license_pending','officialCardVariantsComplete':False,'userFinalAccepted':False} for p in new]
write(ROOT/'records/roster-20261029/CURRENT_PRODUCTION_OVERLAY_20261102.json',overlay)
catalog=read(ROOT/'records/current-art-catalog-20261102.json')
catalog['updatedAtUtc']=now
catalog['roster'].update(currentExistingMasterPeople=72,newMasters=[p['master'] for p in new],newThisBatchPeople=12,UIderivatives=360,clientUiDerivativesImported=300,newSinceBaseline12=60,pendingClientUiDerivatives=60)
catalog['troopFrames'].update(walkStatus='metal v4/v5 six-phase trial still fails near/far lead alternation;0 new usable walk frames',walkReview='records/troop-walk-20261102/current-review.json')
catalog['ui']['chineseFont']={'manifest':'records/chinese-font-20261102/font-provenance.json','subsetCodepoints':7026,'requiredCodepoints':6891,'missingRequired':0,'sourceQueueNameStringsCovered':560,'currentNamesRasterChecked':72,'rasterReview':'records/chinese-font-20261102/raster-proof.json','unityGlyphChecked':False,'userFinalAccepted':False}
catalog['map']['newTerrainKit']={'plan':'records/world-terrain-20261102-kit/production-plan.json','generatedImages':0,'failure':'records/world-terrain-20261102-kit/water-v1.failure.json','status':'quota_exhausted; four materials not generated'}
catalog['engine'].update(finalValidationPassed=False,newBatchImported=False,pendingNewBatchPng=60,importedPng=621,newImporterPreparedNotCompiled=False,newImporterExternalCompilePassed=True,newImporterEditorCompiled=False,lastImportedInventoryPassed=True,finalValidationScope='last successful621 inventory remains valid; new60 and font unexecuted because startup198',integrationReport='records/unity-heroes2-pending-20261102.json',currentBlock='Unity license startup198; user will activate later')
catalog['publication']={'capturedBeforePublication':True,'previousVerifiedArtCommit':'fcbf23762b228477324563d328a96637f80f2c05','previousVerifiedArtTree':'4a22ee8f6dd6521a289b921c4159bdf88b91d45f','previousPublishedIdentityCount':60,'localAddedPeopleThisCapture':12,'previousVerifiedUnityCommit':'d5a40c4337e8f6c2f00033b1ae3ec555fb73544c','latestArtReceipt':'records/publication-local/published-receipt-20261102.json','latestUnityReceipt':'D:/work/wuxing-slg-unity/Logs/Publication/published-receipt-20261102.json','note':'This tracked file is fixed before network publication; actual publication requires commit/tree receipt.'}
write(ROOT/'records/current-art-catalog-20261102.json',catalog)
integration={'updatedAtUtc':now,'batch':BATCH,'sourcePeople':12,'sourceUi':60,'sourceAndDerivationHashChecksPassed':True,'currentTotalPeople':72,'currentTotalUi':360,'currentImportedPeople':60,'currentImportedUi':300,'currentUnityPng':621,'expectedAfterImportPng':681,'newUnityPngImported':0,'fontUnityValidated':False,'gpuPassed':False,'externalCompiler':read(UNITY/'Docs/ArtImport/heroes2-compiler-20261102.json'),'startup':read(UNITY/'Docs/ArtImport/heroes2-startup-block-20261102.json'),'planSha256':sha(UNITY/'Docs/ArtImport/Pending/20261102-heroes2/plan.json'),'fullGameArtComplete':False}
write(ROOT/'records/unity-heroes2-pending-20261102.json',integration)
resume=read(UNITY/'Docs/ArtImport/RESUME_STATUS_20261102.json')
resume.update(updatedAtUtc=now,sourceIdentityPeople=72,sourceIdentityUi=360,pendingNewUi=60,newUiImported=0,chineseFontUnityChecked=False,currentBlock='startup license198; user replied later',newImporterExternalCompilePassed=True,newImporterEditorExecuted=False)
write(UNITY/'Docs/ArtImport/RESUME_STATUS_20261102.json',resume)
readme=ROOT/'README.md';text=readme.read_text(encoding='utf-8')
text=text.replace('12 名既有身份候选加48名新增，共60名、300张UI导出','12 名既有身份候选加60名新增，共72名、360张UI导出，其中300张已接入Unity、新60张待接入').replace('当前60名不是完工分母','当前72名不是完工分母')
text=text.replace('正式中文字体、设备适配','中文字体Unity检查（本轮已提供Wuxing UI子集和FreeType实绘证据）、设备适配')
text=text.replace('| 最终验证 |','| 中文字体 | 新增Wuxing UI Regular改名静态子集，7026字符、6891必需字符无缺，72姓名实绘已查看；保留OFL，Unity字形/GPU待许可恢复 |\n| 最终验证 |')
note='\n本轮新十二人（太史慈、黄盖、程普、韩当、周泰、凌统、张昭、顾雍、法正、钟会、文鸯、张郃）及60张UI已保存检查；Unity启动198，新增导入0，现有仍621 PNG。用户稍后激活。四种新地表计划遇生图额度429，实际新地表0；未切换收费入口。见[本批记录](records/roster-expansion-20261102-heroes2/visual-review.json)和[待导入状态](records/unity-heroes2-pending-20261102.json)。\n'
anchor='## 视觉与来源'
if '本轮新十二人（太史慈' not in text:text=text.replace(anchor,note+'\n'+anchor)
readme.write_text(text,encoding='utf-8')
write(ROOT/'records/roster-expansion-20261102-heroes2/delivery-integrity.json',{'checkedAtUtc':now,'sourceMastersHashMatched':72,'uiHashMatched':360,'uiDerivationRecordsExist':360,'uniquePersonIDs':72,'newSourceAndGenerationHashes':24,'newAssetAndDerivationHashes':120,'fullGameArtComplete':False,'newUnityImported':False})
print(json.dumps({'people':72,'ui':360,'importedUnityPng':621,'pendingUi':60,'fullGameArtComplete':False}))

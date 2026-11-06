from pathlib import Path
from PIL import Image
import json, hashlib, shutil, datetime, sys
sys.stdout.reconfigure(encoding='utf-8')
root=Path('D:/work/wuxing-slg-iamge')
base=root/'records/01-率土之滨'
char=root/'designs/01-率土之滨/characters'
stem='11-lv-bu-v2'
source=Path('C:/Users/luyua/.codex/generated_images/01a1772a-98d5-7941-8861-130d582ca739/exec-b032149f-aa09-4761-9534-1048eb96b0a1.png')
assert source.is_file()
target=char/(stem+'.png')
assert not target.exists(), 'Do not overwrite existing image'
shutil.copyfile(source,target)
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
prompt=(root/f'prompts/01-率土之滨/{stem}.prompt.txt').read_text(encoding='utf-8-sig')
refs=[str(char/'11-lv-bu-v1.png'),str(root/'designs/mail-ui-v1/01-mail-event.png'),str(root/'designs/team-ui-v2/team-ui-v2.png')]
refs=[r.replace('\\','/') for r in refs]
request={'schemaVersion':1,'tool':'image_gen.imagegen','route':'builtin','art_source':'host_image','executionCellId':'28','callStartedAt':'2026-10-26T21:06:59.296Z','modelParameterExposed':False,'qualityParameterExposed':False,'submittedParameters':{'model':None,'quality':None,'prompt':prompt,'referenced_image_paths':refs,'transparent_background':True},'receiptRecoveryNote':'请求依据已保存的原始prompt及当前任务连续摘要恢复；未再次调用生成。'}
response={'schemaVersion':1,'tool':'image_gen.imagegen','route':'builtin','executionCellId':'28','callStartedAt':'2026-10-26T21:06:59.296Z','callCompletedAt':None,'returnedFields':['image_url','output_hint'],'output_hint':None,'toolOutputPath':source.as_posix(),'imageDataOmitted':True,'model':None,'quality':None,'resultId':None,'metadataDisclosure':'实际返回的图片已在上下文压缩前显示；临时tool结果未跨上下文保留，因此不伪造完整output_hint或完成时间。当前连续摘要记有output路径和cell。','recoveredAt':now,'sourceFileLastWriteUtc':datetime.datetime.fromtimestamp(source.stat().st_mtime,datetime.timezone.utc).isoformat(),'sourceFileLastWriteUtcBasis':'只作文件时间证据，不替代工具调用完成时间。','returnedImageKnown':True,'returnedMetadataRecoveredExactly':False}
for suffix,obj in [('tool-request',request),('tool-response',response)]:
 (base/f'{stem}.{suffix}.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'copied':target.as_posix(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'sourceIdentical':target.read_bytes()==source.read_bytes(),'receiptRecoveryGap':True},ensure_ascii=False))

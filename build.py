"""Regenerate web data, Markdown volumes, and standalone offline edition."""
from pathlib import Path
import base64,json,re
from collections import Counter
ROOT=Path(__file__).resolve().parent
questions=json.loads((ROOT/'content/questions.json').read_text('utf-8'))
sources=json.loads((ROOT/'content/sources.json').read_text('utf-8'))
reading_map=json.loads((ROOT/'content/reading-map.json').read_text('utf-8'))
assert [q['id'] for q in questions]==list(range(1,101)), 'IDs must be 1-100'
source_ids={s['id'] for s in sources}
questions_by_id={q['id']:q for q in questions}
for raw_id,extra in reading_map.items():
    q=questions_by_id[int(raw_id)]
    q['reference']['sourceIds']=list(dict.fromkeys(q['reference']['sourceIds']+extra['sourceIds']))
    if '延伸阅读' not in q['reference']['kind']:
        q['reference']['kind']+=' · 延伸阅读'
    prior=q['reference'].get('readingNote','').strip()
    q['reference']['readingNote']=' '.join(part for part in (prior,extra['note'].strip()) if part)
for q in questions:
    for field in ('title','verdict','firstAction','say','cost','gain','limit','body','reference'):assert q[field],f"Q{q['id']} missing {field}"
    assert len(q['say'].strip('“” '))>10,f"Q{q['id']} broken script"
    assert all(n!=q['id'] and 1<=n<=100 for n in q['related'])
    assert all(s in source_ids for s in q['reference']['sourceIds'])
    assert 'evidenceLevel' not in q
    assert len(q['worksheet'])==4 and all(q['worksheet']),f"Q{q['id']} action card missing"
new=questions[30:]
assert len({q['say'] for q in new})==70,'Rewritten scripts must be unique'
long_paras=[p for q in new for p in q['body'] if len(p)>55]
assert max(Counter(long_paras).values())==1,'No duplicated long paragraph in rewritten content'
(ROOT/'data.js').write_text('window.ZHICHANG_ITEMS = '+json.dumps(questions,ensure_ascii=False,separators=(',',':'))+';\n','utf-8')
(ROOT/'evidence.js').write_text('window.ZHICHANG_SOURCES = '+json.dumps(sources,ensure_ascii=False,separators=(',',':'))+';\n','utf-8')
by_source={s['id']:s for s in sources};book=ROOT/'book';book.mkdir(exist_ok=True)
intro='# 职场拆局100问\n\n少一点内耗，多一点选择。\n\n不用一次读完，也不用全部照做。时间为编辑对准备动作的估计，不包含等待与正式程序；收益是可能改善，不是保证。多数内容是编辑判断，规则与延伸阅读范围逐题说明。\n\n'
def entry(q):
    lines=[f"<a id=\"q{q['id']}\"></a>\n\n## {q['id']:02d}｜{q['title']}",'', '**先判断**：'+q['verdict'],'','**先做一件事**：'+q['firstAction'],'','**投入**：'+q['cost'],'','**可能换回**：'+q['gain'],'','**示例表达**：\n\n> '+q['say'],'']
    for p in q['body']:
        match=re.match(r'^【([^】]+)】(.*)$',p)
        lines += ['### '+match[1],'',match[2],''] if match else [p,'']
    lines += ['### 沟通前，填一张行动卡','']+[f'- {field}' for field in q['worksheet']]+['','**适用边界**：'+q['limit'],'','**参考范围**：'+q['reference']['note'],'']
    for k in ('ruleNote','readingNote'):
        if q['reference'].get(k):lines += [q['reference'][k],'']
    for s in q['reference']['sourceIds']:
        ref=by_source[s];lines += [f"- [{ref['title']}]({ref['url']}) — {ref['status']}",'']
    lines += ['**一起看**：'+ ' · '.join(f"[第{n}问](#q{n})" for n in q['related']),'','---','']
    return '\n'.join(lines)
all_text=intro+'\n'.join(entry(q) for q in questions)
(book/'完整正文.md').write_text(all_text,'utf-8')
for v,title in [(1,'基础应对'),(2,'协作进阶'),(3,'高阶判断与选择')]:
    # Cross references in each volume point to the complete book.
    text=intro+'\n'.join(entry(q) for q in questions if q['volume']==v)
    text=re.sub(r'\]\(#q(\d+)\)',r'](完整正文.md#q\1)',text)
    (book/f'{v:02d}-{title}.md').write_text(text,'utf-8')
offline=(ROOT/'index.html').read_text('utf-8')
offline=re.sub(r'<link rel="stylesheet" href="style.css[^\"]*">','<style>'+(ROOT/'style.css').read_text('utf-8')+'</style>',offline)
for file in ('evidence.js','data.js','app.js'):
    code=(ROOT/file).read_text('utf-8').replace('</script','<\\/script')
    offline=re.sub(fr'<script src="{re.escape(file)}[^\"]*"></script>',lambda m:'<script>'+code+'</script>',offline)
# A single-file edition must not depend on neighboring download files or expose a repository entrance.
offline=re.sub(r'<nav aria-label="工具">[\s\S]*?</nav>','<nav aria-label="工具"><a href="#detail">开始阅读 ↓</a></nav>',offline,count=1)
offline=offline.replace('<section class="about">','<section class="about" id="source-note">',1)
offline=offline.replace('href="docs/来源与核验.md"','href="#source-note"')
qr_data=base64.b64encode((ROOT/'assets/wechat-qr.png').read_bytes()).decode('ascii')
offline=offline.replace('src="assets/wechat-qr.png"',f'src="data:image/png;base64,{qr_data}"')
(ROOT/'offline.html').write_text(offline,'utf-8')
print(json.dumps({'questions':100,'extended_reading_questions':len(reading_map),'rewritten_unique_scripts':70,'rewritten_unique_long_paragraphs':len(long_paras),'body_chars':sum(sum(map(len,q['body'])) for q in questions),'offline_bytes':len(offline.encode('utf-8'))},ensure_ascii=False))

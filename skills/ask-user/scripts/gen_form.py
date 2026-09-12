#!/usr/bin/env python3
"""
ask-questionnaire v2: 生成可交互的单页问卷 HTML
用户在聊天内直接填写、点击选择、一键提交。
提交后自动生成结构化文本，用户复制发送即可。

用法:
  python3 gen_form.py '{"title":"...","questions":[...]}'
  python3 gen_form.py task="帮我做一个网站"     # 自动匹配模板
"""
import sys, json, os, re, html as h

# ── 预置任务模板 ──────────────────────────────────────────────
TEMPLATES = {
    "网站|web|site|网页|做一个网站": {
        "title": "做一个网站",
        "subtitle": "填写以下信息，让我精准理解你的需求",
        "questions": [
            {"id":"用途","type":"text","label":"🌐 网站的用途/主题","placeholder":"产品展示 / 个人博客 / 公司官网 / 活动页面…","required":True},
            {"id":"受众","type":"text","label":"👥 目标受众是谁","placeholder":"领导 / 客户 / 普通用户 / 内部团队…","required":True},
            {"id":"风格","type":"radio","label":"🎨 视觉风格","options":["🍎 苹果风 — 纯白留白 高级感","💻 终端风 — 暗黑极客 代码风","📊 PPT风 — 结构清晰 数据图表","🎵 抖音风 — 大色块 潮流感"],"required":True},
            {"id":"页面","type":"radio","label":"📄 页面数量","options":["单页","3-5 页","10 页以上"],"required":False},
            {"id":"后端","type":"radio","label":"⚙️ 需要后端功能吗","options":["不需要 纯静态即可","简单后端 — 表单提交","完整后端 — 登录+数据库"],"required":False},
            {"id":"补充","type":"text","label":"💡 其他补充说明","placeholder":"有特殊要求可以在这里补充…","required":False},
        ]
    },
    "邮件|mail|email|发邮件": {
        "title": "写一封邮件",
        "subtitle": "填写以下信息，帮你精准起草",
        "questions": [
            {"id":"收件人","type":"text","label":"👤 收件人是谁","placeholder":"邮箱地址或人名","required":True},
            {"id":"主题","type":"text","label":"📋 邮件主题","placeholder":"例如：项目进度汇报…","required":True},
            {"id":"内容","type":"text","label":"📝 核心要传达什么信息","placeholder":"一两句话概括核心信息","required":True},
            {"id":"语气","type":"radio","label":"🎭 语气风格","options":["🤝 正式商务","😊 友好亲切","📋 简洁直接"],"required":False},
        ]
    },
    "海报|poster|banner|图片": {
        "title": "设计一张海报",
        "subtitle": "填写以下信息，帮你设计出满意的海报",
        "questions": [
            {"id":"用途","type":"text","label":"🎯 海报用途","placeholder":"活动宣传 / 朋友圈 / 会议展示…","required":True},
            {"id":"文字","type":"text","label":"✏️ 海报上显示什么文字","placeholder":"例如：新春特惠 低至5折","required":True},
            {"id":"风格","type":"radio","label":"🎨 视觉风格","options":["🏮 传统中国风","✨ 现代简约","🎉 活泼热闹"],"required":True},
            {"id":"尺寸","type":"radio","label":"📐 尺寸","options":["📱 手机竖屏","🖥️ 横屏","⬜ 方形"],"required":False},
        ]
    },
    "脚本|script|程序|python|代码": {
        "title": "写一个脚本/程序",
        "subtitle": "填写以下信息，帮你精准开发",
        "questions": [
            {"id":"功能","type":"text","label":"⚡ 这个脚本要做什么","placeholder":"具体功能描述","required":True},
            {"id":"输入","type":"text","label":"📥 输入是什么","placeholder":"接收什么数据/格式","required":True},
            {"id":"输出","type":"text","label":"📤 输出结果是什么","placeholder":"期望得到什么","required":True},
            {"id":"语言","type":"radio","label":"💻 用什么语言","options":["🐍 Python","📦 JavaScript/Node","🔧 Shell/Bash"],"required":False},
        ]
    },
    "PPT|ppt|演示|汇报": {
        "title": "做一个 PPT",
        "subtitle": "填写以下信息，帮你制作演示文稿",
        "questions": [
            {"id":"主题","type":"text","label":"📌 PPT 主题是什么","required":True},
            {"id":"页数","type":"text","label":"📄 大概多少页","placeholder":"例如 10-15 页","required":True},
            {"id":"受众","type":"text","label":"👥 给谁看的","placeholder":"领导 / 客户 / 团队…","required":True},
            {"id":"风格","type":"radio","label":"🎨 风格","options":["🏢 商务正式","🎨 创意活泼","📊 数据驱动"],"required":False},
        ]
    },
    "文档|document|报告|report": {
        "title": "写一个文档/报告",
        "subtitle": "填写以下信息，帮你撰写文档",
        "questions": [
            {"id":"主题","type":"text","label":"📌 文档主题是什么","required":True},
            {"id":"读者","type":"text","label":"👥 目标读者是谁","required":True},
            {"id":"格式","type":"radio","label":"📄 格式偏好","options":["📝 Word 文档","📄 PDF","📋 Markdown"],"required":False},
            {"id":"篇幅","type":"radio","label":"📏 篇幅","options":["简短 1-2 页","中等 3-5 页","详细 10 页以上"],"required":False},
        ]
    },
}

DEFAULT_TEMPLATE = {
    "title": "明确你的需求",
    "subtitle": "填写以下信息，让我精准理解你想做什么",
    "questions": [
        {"id":"具体需求","type":"text","label":"🎯 你想要做的具体是什么","placeholder":"详细描述一下你的需求","required":True},
        {"id":"特殊要求","type":"text","label":"⚙️ 有什么特殊要求或约束","placeholder":"风格 / 语言 / 限制条件等","required":False},
        {"id":"优先级","type":"radio","label":"🏆 优先级","options":["速度优先 先出结果","质量优先 精雕细琢","创意优先 探索多种可能"],"required":False},
    ]
}

def match_template(user_input):
    for pattern, tpl in TEMPLATES.items():
        if re.search(pattern, user_input, re.IGNORECASE):
            return tpl
    return DEFAULT_TEMPLATE

# ── HTML 生成 ──────────────────────────────────────────────
def gen_html(data):
    title = h.escape(data.get("title","需求确认"))
    subtitle = h.escape(data.get("subtitle","请填写以下信息"))
    questions = data.get("questions",[])
    out = data.get("outputPath","/workspace/ask_questionnaire.html")
    
    q_html = ""
    for i, q in enumerate(questions):
        qid = h.escape(q["id"])
        label = h.escape(q["label"])
        req = ' <span class="req">*</span>' if q.get("required") else ""
        ph = h.escape(q.get("placeholder",""))
        
        if q["type"] == "text":
            q_html += f'''<div class="q" data-id="{qid}">
<label class="ql">{label}{req}</label>
<input class="fi" id="f_{qid}" placeholder="{ph}" {'required' if q.get('required') else ''}>
</div>'''
        elif q["type"] == "radio":
            opts = q.get("options",[])
            radio_html = ""
            for j, opt in enumerate(opts):
                ck = ' checked' if j == 0 else ''
                radio_html += f'''<label class="opt">
<input type="radio" name="r_{qid}" value="{h.escape(opt)}"{ck}>
<span>{h.escape(opt)}</span>
</label>\n'''
            q_html += f'''<div class="q" data-id="{qid}">
<label class="ql">{label}{req}</label>
<div class="rg">{radio_html}</div>
</div>'''

    # Build all JS question data for dynamic generation
    q_json = json.dumps(questions, ensure_ascii=False)
    
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:system-ui,-apple-system,sans-serif;background:#0a0a0f;color:#e0e0e0;padding:12px;max-width:540px;margin:0 auto}}
.card{{background:#13131b;border:1px solid #222;border-radius:16px;overflow:hidden}}
.hdr{{padding:18px 18px 10px;background:linear-gradient(135deg,rgba(108,92,231,.1),rgba(0,206,201,.06))}}
.hdr h2{{font-size:1.15rem;margin-bottom:3px}}
.hdr p{{font-size:.78rem;color:#777}}
.hdr .progress{{margin-top:10px;height:3px;background:#1a1a2a;border-radius:3px;overflow:hidden}}
.hdr .progress .bar{{height:100%;background:linear-gradient(90deg,#6c5ce7,#00cec9);border-radius:3px;transition:width .4s;width:0%}}
.q{{padding:14px 18px;border-top:1px solid #1a1a2a;transition:opacity .3s}}
.q.done{{opacity:.55}}
.q.done .ql::after{{content:' ✓';color:#00b894;font-weight:700}}
.ql{{display:block;font-size:.88rem;font-weight:600;margin-bottom:8px;color:#bbb}}
.req{{color:#ff6b6b}}
.fi{{width:100%;padding:10px 12px;border-radius:8px;border:1px solid #2a2a3a;background:#0c0c14;color:#e0e0e0;font-size:.88rem;outline:none;transition:border .2s}}
.fi:focus{{border-color:#6c5ce7}}
.fi::placeholder{{color:#444}}
.rg{{display:flex;flex-wrap:wrap;gap:6px}}
.opt{{display:flex;align-items:center;gap:7px;padding:8px 12px;border-radius:8px;border:1px solid #2a2a3a;cursor:pointer;transition:all .15s;font-size:.84rem;user-select:none;flex:1 1 calc(50% - 3px)}}
.opt:has(input:checked){{border-color:#6c5ce7;background:rgba(108,92,231,.1);color:#fff}}
.opt input{{accent-color:#6c5ce7;width:16px;height:16px;flex-shrink:0}}
.sub{{padding:14px 18px;border-top:1px solid #1a1a2a}}
.btn{{width:100%;padding:12px;border-radius:10px;border:none;font-size:.92rem;font-weight:700;cursor:pointer;transition:all .2s}}
.btn-go{{background:linear-gradient(135deg,#6c5ce7,#a29bfe);color:#fff}}
.btn-go:hover{{opacity:.9;transform:translateY(-1px)}}
.btn-go:disabled{{opacity:.4;cursor:not-allowed;transform:none}}
.result{{display:none;padding:14px 18px;border-top:1px solid #1a1a2a}}
.result pre{{background:#0c0c14;padding:12px;border-radius:8px;font-size:.8rem;line-height:1.6;white-space:pre-wrap;word-break:break-all;color:#a29bfe;border:1px solid #2a2a3a}}
.copy{{margin-top:10px;width:100%;padding:10px;border-radius:8px;border:1px solid #6c5ce7;background:transparent;color:#a29bfe;font-size:.84rem;font-weight:600;cursor:pointer}}
.copy:hover{{background:rgba(108,92,231,.12)}}
</style>
</head>
<body>
<div class="card">
  <div class="hdr">
    <h2>📋 {title}</h2>
    <p>{subtitle}</p>
    <div class="progress"><div class="bar" id="bar"></div></div>
  </div>
  <div id="form">{q_html}</div>
  <div class="sub">
    <button class="btn btn-go" id="submitBtn" onclick="submit()">✅ 提交全部</button>
  </div>
  <div class="result" id="result">
    <pre id="output"></pre>
    <button class="copy" onclick="copyResult()">📋 复制结果并发送给小万</button>
  </div>
</div>
<script>
const QS = {q_json};
function updateProgress(){{
  let total=QS.length, done=0;
  QS.forEach(q=>{{
    if(q.type==='text'){{
      const el=document.getElementById('f_'+q.id);
      if(el && el.value.trim()) done++;
    }}else if(q.type==='radio'){{
      const checked=document.querySelector('input[name="r_'+q.id+'"]:checked');
      if(checked && checked.value) done++;
    }}
  }});
  document.getElementById('bar').style.width=(done/total*100)+'%';
  // Mark questions as done
  QS.forEach(q=>{{
    const div=document.querySelector('.q[data-id="'+q.id+'"]');
    if(!div)return;
    let filled=false;
    if(q.type==='text'){{
      const el=document.getElementById('f_'+q.id);
      filled=el && el.value.trim()!;
    }}else if(q.type==='radio'){{
      const checked=document.querySelector('input[name="r_'+q.id+'"]:checked');
      filled=!!checked;
    }}
    div.classList.toggle('done',filled);
  }});
}}
document.addEventListener('input',updateProgress);
document.addEventListener('change',updateProgress);

function submit(){{
  let text='📋 需求汇总\\n━━━━━━━━━━━━━━\\n\\n';
  let allGood=true;
  QS.forEach(q=>{{
    let val='';
    if(q.type==='text'){{
      val=document.getElementById('f_'+q.id).value.trim();
      if(!val && q.required){{allGood=false;val='⚠️ 未填写'}}
      else if(!val) val='（未填写）';
    }}else if(q.type==='radio'){{
      const checked=document.querySelector('input[name="r_'+q.id+'"]:checked');
      val=checked?checked.value:'（未选择）';
    }}
    text+=`✅ ${{q.label.replace(/^[^\\u4e00-\\u9fff]*/,'').trim()}}: ${{val}}\\n`;
  }});
  text+='\\n━━━━━━━━━━━━━━\\n请小万继续处理！';
  document.getElementById('output').textContent=text;
  document.getElementById('result').style.display='block';
  document.getElementById('submitBtn').textContent='✅ 已提交！复制结果发给小万';
  updateProgress();
}}
function copyResult(){{
  const t=document.getElementById('output').textContent;
  navigator.clipboard.writeText(t).then(()=>{{
    const b=document.querySelector('.copy');
    b.textContent='✅ 已复制！粘贴发送给小万';b.style.color='#00b894';b.style.borderColor='#00b894';
    setTimeout(()=>{{b.textContent='📋 复制结果并发送给小万';b.style.color='#a29bfe';b.style.borderColor='#6c5ce7'}},3000);
  }});
}}
</script>
</body>
</html>'''

if __name__ == "__main__":
    raw = sys.argv[1] if len(sys.argv)>1 else "{}"
    if raw.startswith("{"):
        data = json.loads(raw)
    else:
        # Quick mode: python3 gen_form.py task="帮我做一个网站"
        data = {}
        for arg in sys.argv[1:]:
            if "=" in arg:
                k,v = arg.split("=",1)
                data[k] = v
        task = data.pop("task","")
        tpl = match_template(task)
        data = {**tpl, **data, "outputPath": "/workspace/ask_questionnaire.html"}
    
    out_path = data.pop("outputPath", "/workspace/ask_questionnaire.html")
    html = gen_html(data)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Generated: {out_path} ({len(html):,} bytes)")

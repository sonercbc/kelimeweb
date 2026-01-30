from __future__ import annotations
import json, os, random
from flask import Flask, request, redirect, url_for, render_template_string

app = Flask(__name__)
DATA_FILE = "kelimeler.json"

def load_words():
    if not os.path.exists(DATA_FILE):
        words = [
    {"ing": "apple", "tr": "elma", "level": "A1", "d": 0, "y": 0},
    {"ing": "book", "tr": "kitap", "level": "A1", "d": 0, "y": 0},
]

        save_words(words)
        return words
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_words(words):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=2)

def pick_word(words, last=None):
    pool = words if not last else [w for w in words if w["ing"] != last] or words
    word = random.choice(pool)
    direction = random.choice(["EN_TR", "TR_EN"])
    answer = word["tr"] if direction == "EN_TR" else word["ing"]
    question = f"{word['ing']} → Türkçe?" if direction == "EN_TR" else f"{word['tr']} → İngilizce?"
    return word, direction, question, answer

HTML = """
<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Kelime Quiz</title>
  <style>
    :root{
      --bg:#0b1220;
      --card:#121b2e;
      --muted:#93a4c7;
      --text:#eaf0ff;
      --accent:#6ee7ff;
      --accent2:#a78bfa;
      --ok:#22c55e;
      --bad:#ef4444;
      --line:rgba(255,255,255,.08);
      --shadow: 0 12px 30px rgba(0,0,0,.35);
      --radius:18px;
    }
    *{box-sizing:border-box}
    body{
      margin:0;
      font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial;
      background: radial-gradient(900px 500px at 10% 0%, rgba(110,231,255,.14), transparent 60%),
                  radial-gradient(900px 500px at 90% 10%, rgba(167,139,250,.14), transparent 60%),
                  var(--bg);
      color:var(--text);
      min-height:100vh;
      display:flex;
      align-items:center;
      justify-content:center;
      padding:24px;
    }
    .wrap{width:min(980px,100%)}
    header{
      display:flex;
      align-items:center;
      justify-content:space-between;
      gap:12px;
      margin-bottom:14px;
    }
    .brand{
      display:flex; align-items:center; gap:10px;
      font-weight:700; letter-spacing:.2px;
    }
    .logo{
      width:38px; height:38px; border-radius:12px;
      background: linear-gradient(135deg, rgba(110,231,255,.9), rgba(167,139,250,.9));
      box-shadow: var(--shadow);
    }
    .sub{color:var(--muted); font-size:13px}
    .card{
      background: linear-gradient(180deg, rgba(255,255,255,.06), rgba(255,255,255,.03));
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      overflow:hidden;
    }
    .grid{
      display:grid;
      grid-template-columns: 1.2fr .8fr;
    }
    @media (max-width: 860px){
      .grid{grid-template-columns: 1fr}
    }
    .panel{padding:22px}
    .panel + .panel{border-left:1px solid var(--line)}
    @media (max-width: 860px){
      .panel + .panel{border-left:none; border-top:1px solid var(--line)}
    }
    .qtitle{font-size:14px; color:var(--muted); margin:0 0 8px}
    .question{
      font-size:28px;
      margin:0 0 18px;
      line-height:1.2;
    }
    .pill{
      display:inline-flex; align-items:center; gap:8px;
      padding:8px 12px;
      border:1px solid var(--line);
      border-radius:999px;
      color:var(--muted);
      font-size:13px;
      background: rgba(0,0,0,.18);
    }
    .row{display:flex; gap:10px; align-items:center; flex-wrap:wrap}
    input{
      width:100%;
      padding:12px 14px;
      border-radius:14px;
      border:1px solid rgba(255,255,255,.12);
      outline:none;
      background: rgba(0,0,0,.20);
      color:var(--text);
      font-size:15px;
    }
    input::placeholder{color:rgba(234,240,255,.45)}
    .btn{
      cursor:pointer;
      border:none;
      padding:12px 14px;
      border-radius:14px;
      font-weight:700;
      color:#07111f;
      background: linear-gradient(135deg, rgba(110,231,255,.95), rgba(167,139,250,.95));
      box-shadow: 0 10px 20px rgba(110,231,255,.12);
      transition: transform .08s ease, filter .12s ease;
      white-space:nowrap;
    }
    .btn:active{transform: translateY(1px)}
    .btn.secondary{
      background: rgba(255,255,255,.08);
      color:var(--text);
      border:1px solid var(--line);
      box-shadow:none;
    }
    .hint{
      margin-top:12px;
      color:var(--muted);
      font-size:13px;
      line-height:1.4;
    }
    .alert{
      margin-top:14px;
      padding:12px 14px;
      border-radius:14px;
      border:1px solid rgba(239,68,68,.35);
      background: rgba(239,68,68,.10);
      color: #ffd2d2;
      display:flex;
      justify-content:space-between;
      align-items:center;
      gap:10px;
    }
    .alert code{
      background: rgba(0,0,0,.25);
      padding:3px 8px;
      border-radius:10px;
      border:1px solid rgba(255,255,255,.10);
      color:#fff;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size:13px;
    }
    .sectionTitle{
      display:flex;
      align-items:center;
      justify-content:space-between;
      gap:10px;
      margin:0 0 12px;
    }
    .sectionTitle h3{margin:0; font-size:15px}
    a.link{
      color: var(--accent);
      text-decoration:none;
      font-weight:700;
    }
    a.link:hover{text-decoration:underline}
    .formGrid{
      display:grid;
      grid-template-columns: 1fr 1fr auto;
      gap:10px;
    }
    @media (max-width: 520px){
      .formGrid{grid-template-columns: 1fr}
      .btn{width:100%}
    }
    .footer{
      margin-top:12px;
      display:flex;
      justify-content:space-between;
      gap:12px;
      flex-wrap:wrap;
      color:var(--muted);
      font-size:12px;
    }
    .kbd{
      border:1px solid rgba(255,255,255,.14);
      padding:2px 7px;
      border-radius:8px;
      background: rgba(0,0,0,.22);
      color: rgba(234,240,255,.85);
      font-weight:700;
      font-size:12px;
    }
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <div>
        <div class="brand"><div class="logo"></div>Kelime Quiz</div>
        <div class="sub">Hızlı tekrar • yanlışta doğruyu gösterir • kayıtlar arkada saklanır</div>
      </div>
      <a class="link" href="/stats?level={{level}}">İstatistik →</a>


<div style="display:flex; gap:8px; flex-wrap:wrap; justify-content:flex-end;">
  <a class="btn secondary" href="/?level=A1">A1</a>
  <a class="btn secondary" href="/?level=A2">A2</a>
  <a class="btn secondary" href="/?level=B1">B1</a>
  <a class="btn secondary" href="/?level=B2">B2</a>
  <a class="btn secondary" href="/?level=C1">C1</a>
  <a class="btn secondary" href="/?level=C2">C2</a>
</div>


    </header>

    <div class="card">
      <div class="grid">
        <!-- SOL: SORU -->
        <div class="panel">
          <p class="qtitle">Soru</p>
          <h1 class="question">{{question}}</h1>

          <form method="post" action="/?level={{level}}">

  <div class="row" style="width:100%">
    <div style="flex:1; min-width:220px">
      <input name="answer" autofocus placeholder="Cevabını yaz..." />
      <input type="hidden" name="ing" value="{{word.ing}}">
      <input type="hidden" name="direction" value="{{direction}}">
      <input type="hidden" name="correct_answer" value="{{correct_answer}}">
    </div>
    <button class="btn" type="submit">Kontrol</button>
  </div>
</form>

{% if right %}
<div class="alert" style="border-color: rgba(34,197,94,.35); background: rgba(34,197,94,.10); color:#c9fddc;">
  <div>Doğru ✅</div>
</div>
{% endif %}


          {% if wrong %}
          <div class="alert">
            <div>Yanlış ❌ Doğru cevap: <code>{{correct}}</code></div>
            <span class="pill">Devam et</span>
          </div>
          {% endif %}

          <div class="hint">
            İpucu: Cevabı yazıp <span class="kbd">Enter</span> ile gönderebilirsin.
          </div>

          <div class="footer">
            <div>Rastgele sorar (bazen TR→EN, bazen EN→TR)</div>
            <div>Uygulama: <span class="pill">kelimeweb</span></div>
          </div>
        </div>

        <!-- SAĞ: YENİ KELİME -->
        <div class="panel">
          <div class="sectionTitle">
            <h3>Yeni kelime ekle</h3>
          </div>

          <form action="/add" method="post">
<input type="hidden" name="level" value="{{level}}">

            <div class="formGrid">
              <input name="ing" placeholder="İngilizce (örn: moon)" />
              <input name="tr" placeholder="Türkçe (örn: ay)" />
              <button class="btn secondary" type="submit">Ekle</button>
            </div>
          </form>

          <div class="hint" style="margin-top:14px">
            Eklediğin kelimeler otomatik kaydolur. İstatistik ekranında doğru/yanlış sayılarını görürsün.
          </div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    # seviye seçimi
    level = request.args.get("level", "A1").upper()
    if level not in ["A1", "A2", "B1", "B2", "C1", "C2"]:
        level = "A1"

    # tüm kelimeler (kaydetme işlemi bunun üstünden yapılacak)
    all_words = load_words()

    # seçili seviyedeki kelimeler (soru bunun içinden seçilecek)
    level_words = [w for w in all_words if w.get("level", "A1").upper() == level]
    if not level_words:
        level_words = all_words  # o seviyede hiç kelime yoksa fallback

    last = None
    wrong = False
    right = False
    show_correct = ""

    def norm(s: str) -> str:
        return (s or "").strip().casefold()

    if request.method == "POST":
        ing = request.form.get("ing", "")
        user_answer = norm(request.form.get("answer", ""))

        correct_answer_raw = request.form.get("correct_answer", "")
        correct_answer = norm(correct_answer_raw)

        # DİKKAT: kelimeyi tüm listeden buluyoruz ki JSON bozulmasın
        w = next((x for x in all_words if x.get("ing") == ing), None)

        if w:
            if user_answer == correct_answer:
                w["d"] = int(w.get("d", 0)) + 1
                right = True
            else:
                w["y"] = int(w.get("y", 0)) + 1
                wrong = True
                show_correct = correct_answer_raw

            save_words(all_words)
            last = ing

    # yeni soru seç (seçili seviyeden)
    word, direction, question, correct_answer_raw = pick_word(level_words, last)

    return render_template_string(
        HTML,
        question=question,
        word=type("obj", (object,), word),
        wrong=wrong,
        right=right,
        correct=show_correct,
        direction=direction,
        correct_answer=correct_answer_raw,
        level=level
    )




@app.route("/add", methods=["POST"])
def add():
    all_words = load_words()

    ing = request.form.get("ing", "").strip().lower()
    tr = request.form.get("tr", "").strip().lower()
    level = request.form.get("level", "A1").upper()

    if level not in ["A1", "A2", "B1", "B2", "C1", "C2"]:
        level = "A1"

    if ing and tr:
        all_words.append({"ing": ing, "tr": tr, "level": level, "d": 0, "y": 0})
        save_words(all_words)

    return redirect(url_for("index", level=level))


@app.route("/stats")
def stats():
    # seviye seçimi (querystring)
    level = request.args.get("level", "ALL").upper()
    valid_levels = ["A1", "A2", "B1", "B2", "C1", "C2", "ALL"]
    if level not in valid_levels:
        level = "ALL"

    words = load_words()

    # filtre
    if level != "ALL":
        filtered = [w for w in words if w.get("level", "A1").upper() == level]
    else:
        filtered = words

    rows = ""
    for w in filtered:
        total = int(w.get("d", 0)) + int(w.get("y", 0))
        pct = int((int(w.get("d", 0)) / total) * 100) if total else 0

        rows += f"""
        <tr>
            <td><b>{w['ing']}</b></td>
            <td>{w['tr']}</td>
            <td>{w.get('level','A1')}</td>
            <td>{w.get('d',0)}</td>
            <td>{w.get('y',0)}</td>
            <td>%{pct}</td>
        </tr>
        """

    # butonlar (ALL dahil)
   def lvl_btn(lvl):
    cls = "btn active" if level == lvl else "btn secondary"
    return f'<a class="{cls}" href="/stats?level={lvl}">{lvl}</a>'

level_buttons = f"""
<div style="display:flex; gap:8px; flex-wrap:wrap; justify-content:flex-end;">
  <a class="{'btn active' if level=='ALL' else 'btn secondary'}" href="/stats?level=ALL">ALL</a>
  {lvl_btn('A1')}
  {lvl_btn('A2')}
  {lvl_btn('B1')}
  {lvl_btn('B2')}
  {lvl_btn('C1')}
  {lvl_btn('C2')}
</div>
"""


    return f"""
<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>İstatistik • Kelime Quiz</title>
  <style>
    :root{{
      --bg:#0b1220; --muted:#93a4c7; --text:#eaf0ff;
      --accent:#6ee7ff; --accent2:#a78bfa;
      --line:rgba(255,255,255,.08); --shadow:0 12px 30px rgba(0,0,0,.35);
      --radius:18px;
    }}
    *{{box-sizing:border-box}}
    body{{
      margin:0;
      font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial;
      background: radial-gradient(900px 500px at 10% 0%, rgba(110,231,255,.14), transparent 60%),
                  radial-gradient(900px 500px at 90% 10%, rgba(167,139,250,.14), transparent 60%),
                  var(--bg);
      color:var(--text);
      min-height:100vh;
      display:flex;
      justify-content:center;
      padding:24px;
    }}
    .wrap{{width:min(980px,100%)}}
    header{{display:flex; align-items:flex-start; justify-content:space-between; gap:12px; margin-bottom:14px; flex-wrap:wrap;}}
    .brand{{display:flex; align-items:center; gap:10px; font-weight:700; letter-spacing:.2px;}}
    .logo{{width:38px; height:38px; border-radius:12px;
      background: linear-gradient(135deg, rgba(110,231,255,.9), rgba(167,139,250,.9));
      box-shadow: var(--shadow);
    }}
    .sub{{color:var(--muted); font-size:13px}}
    a.link{{color:var(--accent); text-decoration:none; font-weight:700}}
    a.link:hover{{text-decoration:underline}}

    .btn{{
      cursor:pointer;
      border:none;
      padding:10px 12px;
      border-radius:14px;
      font-weight:700;
      white-space:nowrap;
    }}
    .btn.secondary{{
      background: rgba(255,255,255,.08);
      color:var(--text);
      border:1px solid var(--line);
    }}

/* AKTİF SEVİYE BUTONU */
.btn.active{
  background: linear-gradient(135deg, rgba(110,231,255,.95), rgba(167,139,250,.95));
  color:#07111f;
  box-shadow: 0 10px 20px rgba(110,231,255,.18);
  border:none;
}


    .card{{
      background: linear-gradient(180deg, rgba(255,255,255,.06), rgba(255,255,255,.03));
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      overflow:hidden;
    }}
    .top{{padding:16px 18px; border-bottom:1px solid var(--line); display:flex; justify-content:space-between; flex-wrap:wrap; gap:10px}}
    .pill{{
      display:inline-flex; align-items:center; gap:8px;
      padding:8px 12px; border:1px solid var(--line); border-radius:999px;
      color:var(--muted); font-size:13px; background: rgba(0,0,0,.18);
    }}
    .tableWrap{{padding:14px 16px 18px}}
    table{{width:100%; border-collapse:separate; border-spacing:0 10px}}
    th{{text-align:left; color:var(--muted); font-size:12px; font-weight:700; padding:0 12px 6px}}
    td{{background: rgba(0,0,0,.18); border:1px solid var(--line); padding:12px; font-size:14px}}
    tr td:first-child{{border-radius:14px 0 0 14px}}
    tr td:last-child{{border-radius:0 14px 14px 0}}
    @media (max-width:720px){{ th:nth-child(2), td:nth-child(2){{display:none}} }}
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <div>
        <div class="brand"><div class="logo"></div>İstatistik</div>
        <div class="sub">Seçili seviye: <b>{level}</b> • Doğru/yanlış ve başarı yüzdesi</div>
      </div>

      <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap; justify-content:flex-end;">
        {level_buttons}
        <a class="link" href="/">← Quiz’e dön</a>
      </div>
    </header>

    <div class="card">
      <div class="top">
        <div class="pill">Gösterilen kelime: <b style="color:var(--text)">{len(filtered)}</b></div>
        <div class="pill">İpucu: düşük yüzdeli kelimeleri tekrar et</div>
      </div>

      <div class="tableWrap">
        <table>
          <thead>
            <tr>
              <th>İngilizce</th>
              <th>Türkçe</th>
              <th>Seviye</th>
              <th>Doğru</th>
              <th>Yanlış</th>
              <th>Başarı</th>
            </tr>
          </thead>
          <tbody>
            {rows}
          </tbody>
        </table>
      </div>
    </div>
  </div>
</body>
</html>
"""




if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)


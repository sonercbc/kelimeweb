from __future__ import annotations
import json, os, random
from flask import Flask, request, redirect, url_for, render_template_string

app = Flask(__name__)
DATA_FILE = "kelimeler.json"

def load_words():
    if not os.path.exists(DATA_FILE):
        words = [
            {"ing": "apple", "tr": "elma", "d": 0, "y": 0},
            {"ing": "book", "tr": "kitap", "d": 0, "y": 0},
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
      <a class="link" href="/stats">İstatistik →</a>
    </header>

    <div class="card">
      <div class="grid">
        <!-- SOL: SORU -->
        <div class="panel">
          <p class="qtitle">Soru</p>
          <h1 class="question">{{question}}</h1>

          <form method="post">
            <div class="row" style="width:100%">
              <div style="flex:1; min-width:220px">
                <input name="answer" autofocus placeholder="Cevabını yaz..." />
                <input type="hidden" name="ing" value="{{word.ing}}">
              </div>
              <button class="btn" type="submit">Kontrol</button>
            </div>
          </form>

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
    words = load_words()
    last = None
    wrong = False
    correct = ""

    if request.method == "POST":
        ing = request.form["ing"]
        answer = request.form["answer"].strip().lower()
        for w in words:
            if w["ing"] == ing:
                correct_ans = w["tr"] if answer != w["tr"] else w["ing"]
                if answer in (w["tr"], w["ing"]):
                    w["d"] += 1
                else:
                    w["y"] += 1
                    wrong = True
                    correct = correct_ans
                save_words(words)
                last = ing
                break

    word, direction, question, answer = pick_word(words, last)
    return render_template_string(
        HTML,
        question=question,
        word=type("obj",(object,),word),
        wrong=wrong,
        correct=answer
    )

@app.route("/add", methods=["POST"])
def add():
    words = load_words()
    ing = request.form["ing"].strip().lower()
    tr = request.form["tr"].strip().lower()
    if ing and tr:
        words.append({"ing": ing, "tr": tr, "d": 0, "y": 0})
        save_words(words)
    return redirect(url_for("index"))

@app.route("/stats")
def stats():
    rows = ""
for w in words:
    total = w["d"] + w["y"]
    pct = int((w["d"] / total) * 100) if total else 0
    rows += f"""
    <tr>
        <td>{w['ing']}</td>
        <td>{w['tr']}</td>
        <td>{w['d']}</td>
        <td>{w['y']}</td>
        <td>%{pct}</td>
    </tr>
    """

return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>İstatistik</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: #f4f6f8;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 800px;
            margin: 40px auto;
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        h2 {{
            text-align: center;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 10px;
            text-align: center;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #4CAF50;
            color: white;
        }}
        a {{
            display: block;
            text-align: center;
            margin-top: 20px;
            text-decoration: none;
            color: #4CAF50;
            font-weight: bold;
        }}
    </style>
</head>
<body>

<div class="container">
    <h2>📊 Kelime İstatistikleri</h2>

    <table>
        <tr>
            <th>İngilizce</th>
            <th>Türkçe</th>
            <th>Doğru</th>
            <th>Yanlış</th>
            <th>Başarı</th>
        </tr>
        {rows}
    </table>

    <a href="/">⬅ Ana sayfaya dön</a>
</div>

</body>
</html>
"""


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)


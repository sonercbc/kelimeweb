from __future__ import annotations

import json
import os
import random
from functools import wraps

from flask import Flask, request, redirect, url_for, render_template_string, session, Response
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

USERS_FILE = "users.json"


# ----------------- USER HELPERS -----------------
def load_users():
    if not os.path.exists(USERS_FILE):
        save_users({})
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


def current_user():
    return session.get("user")


def data_file_for(username: str):
    return f"kelimeler_{username}.json"


# ----------------- BOOTSTRAP / ADMIN -----------------
def bootstrap_users():
    """İlk kurulum: users.json yoksa örnek kullanıcıları oluştur."""
    if os.path.exists(USERS_FILE):
        return

    users = {
        "soner": {"pw": generate_password_hash("1234"), "role": "admin"},
        "ali": {"pw": generate_password_hash("1234"), "role": "user"},
        "ayse": {"pw": generate_password_hash("1234"), "role": "user"},
    }
    save_users(users)


def ensure_admin():
    """ENV ile admin'i her açılışta garanti et. (ADMIN_USER / ADMIN_PASS)"""
    admin_user = os.environ.get("ADMIN_USER")
    admin_pass = os.environ.get("ADMIN_PASS")
    if not admin_user or not admin_pass:
        return

    users = load_users()
    uname = admin_user.strip().lower()

    users[uname] = {
        "pw": generate_password_hash(admin_pass),
        "role": "admin",
    }

    # ✅ ÖNEMLİ: kaydı burada yap
    save_users(users)


# ----------------- AUTH DECORATORS -----------------
def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user():
            return redirect(url_for("login"))
        return fn(*args, **kwargs)

    return wrapper


def is_admin(username: str | None = None) -> bool:
    username = username or current_user()
    if not username:
        return False
    users = load_users()
    u = users.get(username, {})
    return u.get("role") == "admin"


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user():
            return redirect(url_for("login"))
        if not is_admin():
            return "403 Forbidden (admin only)", 403
        return fn(*args, **kwargs)

    return wrapper


# ----------------- WORD HELPERS (per user) -----------------
def load_words():
    username = current_user()
    if not username:
        return []

    data_file = data_file_for(username)

    if not os.path.exists(data_file):
        # yeni kullanıcıya başlangıç kelimeleri
        words = [
            {"ing": "apple", "tr": "elma", "level": "A1", "d": 0, "y": 0},
            {"ing": "water", "tr": "su", "level": "A1", "d": 0, "y": 0},
            {"ing": "bread", "tr": "ekmek", "level": "A1", "d": 0, "y": 0},
            {"ing": "milk", "tr": "süt", "level": "A1", "d": 0, "y": 0},
            {"ing": "house", "tr": "ev", "level": "A1", "d": 0, "y": 0},
            {"ing": "car", "tr": "araba", "level": "A1", "d": 0, "y": 0},
            {"ing": "dog", "tr": "köpek", "level": "A1", "d": 0, "y": 0},
            {"ing": "cat", "tr": "kedi", "level": "A1", "d": 0, "y": 0},
            {"ing": "book", "tr": "kitap", "level": "A1", "d": 0, "y": 0},
            {"ing": "pen", "tr": "kalem", "level": "A1", "d": 0, "y": 1},
            {"ing": "table", "tr": "masa", "level": "A1", "d": 0, "y": 0},
            {"ing": "chair", "tr": "sandalye", "level": "A1", "d": 0, "y": 0},
            {"ing": "door", "tr": "kapı", "level": "A1", "d": 0, "y": 0},
            {"ing": "window", "tr": "pencere", "level": "A1", "d": 0, "y": 0},
            {"ing": "phone", "tr": "telefon", "level": "A1", "d": 0, "y": 0},
            {"ing": "school", "tr": "okul", "level": "A1", "d": 0, "y": 0},
            {"ing": "teacher", "tr": "öğretmen", "level": "A1", "d": 0, "y": 0},
            {"ing": "student", "tr": "öğrenci", "level": "A1", "d": 0, "y": 0},
            {"ing": "friend", "tr": "arkadaş", "level": "A1", "d": 0, "y": 0},
            {"ing": "family", "tr": "aile", "level": "A1", "d": 0, "y": 0},
            {"ing": "mother", "tr": "anne", "level": "A1", "d": 0, "y": 0},
            {"ing": "father", "tr": "baba", "level": "A1", "d": 0, "y": 0},
            {"ing": "brother", "tr": "erkek kardeş", "level": "A1", "d": 0, "y": 0},
            {"ing": "sister", "tr": "kız kardeş", "level": "A1", "d": 0, "y": 0},
            {"ing": "food", "tr": "yemek", "level": "A1", "d": 0, "y": 0},
            {"ing": "drink", "tr": "içecek", "level": "A1", "d": 0, "y": 0},
            {"ing": "city", "tr": "şehir", "level": "A1", "d": 0, "y": 0},
            {"ing": "street", "tr": "sokak", "level": "A1", "d": 0, "y": 0},
            {"ing": "shop", "tr": "mağaza", "level": "A1", "d": 0, "y": 0},
            {"ing": "money", "tr": "para", "level": "A1", "d": 0, "y": 0},
            {"ing": "time", "tr": "zaman", "level": "A1", "d": 0, "y": 0},
            {"ing": "day", "tr": "gün", "level": "A1", "d": 0, "y": 0},
            {"ing": "night", "tr": "gece", "level": "A1", "d": 0, "y": 0},
            {"ing": "morning", "tr": "sabah", "level": "A1", "d": 0, "y": 0},
            {"ing": "good", "tr": "iyi", "level": "A1", "d": 0, "y": 0},
            {"ing": "bad", "tr": "kötü", "level": "A1", "d": 0, "y": 0},
            {"ing": "big", "tr": "büyük", "level": "A1", "d": 0, "y": 0},
            {"ing": "small", "tr": "küçük", "level": "A1", "d": 0, "y": 0},
            {"ing": "new", "tr": "yeni", "level": "A1", "d": 0, "y": 0},
            {"ing": "old", "tr": "eski", "level": "A1", "d": 0, "y": 0},

            {"ing": "answer", "tr": "cevap", "level": "A2", "d": 0, "y": 0},
            {"ing": "question", "tr": "soru", "level": "A2", "d": 0, "y": 0},
            {"ing": "problem", "tr": "problem", "level": "A2", "d": 0, "y": 0},
            {"ing": "idea", "tr": "fikir", "level": "A2", "d": 0, "y": 0},
            {"ing": "job", "tr": "iş", "level": "A2", "d": 0, "y": 0},
            {"ing": "work", "tr": "çalışmak / iş", "level": "A2", "d": 0, "y": 0},
            {"ing": "office", "tr": "ofis", "level": "A2", "d": 0, "y": 0},
            {"ing": "company", "tr": "şirket", "level": "A2", "d": 0, "y": 0},
            {"ing": "meeting", "tr": "toplantı", "level": "A2", "d": 0, "y": 0},
            {"ing": "plan", "tr": "plan", "level": "A2", "d": 0, "y": 0},

            {"ing": "travel", "tr": "seyahat etmek", "level": "A2", "d": 0, "y": 0},
            {"ing": "holiday", "tr": "tatil", "level": "A2", "d": 0, "y": 0},
            {"ing": "ticket", "tr": "bilet", "level": "A2", "d": 0, "y": 0},
            {"ing": "hotel", "tr": "otel", "level": "A2", "d": 0, "y": 0},
            {"ing": "airport", "tr": "havaalanı", "level": "A2", "d": 0, "y": 0},
            {"ing": "weather", "tr": "hava durumu", "level": "A2", "d": 0, "y": 0},
            {"ing": "season", "tr": "mevsim", "level": "A2", "d": 0, "y": 0},
            {"ing": "temperature", "tr": "sıcaklık", "level": "A2", "d": 0, "y": 0},
            {"ing": "rain", "tr": "yağmur", "level": "A2", "d": 0, "y": 0},
            {"ing": "snow", "tr": "kar", "level": "A2", "d": 0, "y": 0},
        ]
        save_words(words)
        return words

    with open(data_file, "r", encoding="utf-8") as f:
        return json.load(f)


def save_words(words):
    username = current_user()
    if not username:
        return
    data_file = data_file_for(username)
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=2)


def pick_word(words, last=None):
    pool = words if not last else [w for w in words if w["ing"] != last] or words
    word = random.choice(pool)
    direction = random.choice(["EN_TR", "TR_EN"])
    answer = word["tr"] if direction == "EN_TR" else word["ing"]
    question = f"{word['ing']} → Türkçe?" if direction == "EN_TR" else f"{word['tr']} → İngilizce?"
    return word, direction, question, answer


# ----------------- AUTH HTML -----------------
LOGIN_HTML = """
<!doctype html><html lang="tr"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Giriş</title>
<style>
body{font-family:system-ui;background:#0b1220;color:#eaf0ff;display:flex;min-height:100vh;align-items:center;justify-content:center;padding:24px}
.card{width:min(420px,100%);background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);border-radius:18px;padding:18px}
input{width:100%;padding:12px 14px;border-radius:14px;border:1px solid rgba(255,255,255,.12);background:rgba(0,0,0,.2);color:#eaf0ff;margin-top:10px}
button{width:100%;padding:12px 14px;border-radius:14px;border:none;margin-top:12px;font-weight:700;background:linear-gradient(135deg, rgba(110,231,255,.95), rgba(167,139,250,.95));color:#07111f}
a{color:#6ee7ff;text-decoration:none;font-weight:700}
.err{margin-top:10px;color:#ffd2d2}
</style></head><body>
<div class="card">
  <h2 style="margin:0 0 6px">Giriş</h2>
  <div style="color:#93a4c7;font-size:13px;margin-bottom:10px">Kelime Quiz hesabınla giriş yap</div>
  <form method="post">
    <input name="username" placeholder="Kullanıcı adı" required>
    <input name="password" type="password" placeholder="Şifre" required>
    <button type="submit">Giriş</button>
  </form>
  {% if error %}<div class="err">{{error}}</div>{% endif %}
  <div style="margin-top:12px;color:#93a4c7;font-size:13px">Hesabın yok mu? <a href="/register">Kayıt ol</a></div>
</div>
</body></html>
"""

REGISTER_HTML = (
    LOGIN_HTML.replace("Giriş", "Kayıt Ol")
    .replace("Kelime Quiz hesabınla giriş yap", "Yeni hesap oluştur")
    .replace("Giriş</button>", "Kayıt Ol</button>")
    .replace('Hesabın yok mu? <a href="/register">Kayıt ol</a>', 'Hesabın var mı? <a href="/login">Giriş</a>')
)


# ----------------- QUIZ HTML -----------------
HTML = """<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Kelime Quiz</title>
  <style>
    :root{
      --bg:#0b1220;
      --muted:#93a4c7;
      --text:#eaf0ff;
      --accent:#6ee7ff;
      --accent2:#a78bfa;
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
      flex-wrap:wrap;
    }
    .brand{display:flex; align-items:center; gap:10px; font-weight:700;}
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
    .grid{display:grid; grid-template-columns: 1.2fr .8fr;}
    @media (max-width: 860px){ .grid{grid-template-columns: 1fr} }
    .panel{padding:22px}
    .panel + .panel{border-left:1px solid var(--line)}
    @media (max-width: 860px){ .panel + .panel{border-left:none; border-top:1px solid var(--line)} }
    .qtitle{font-size:14px; color:var(--muted); margin:0 0 8px}
    .question{font-size:28px; margin:0 0 18px; line-height:1.2;}
    .pill{
      display:inline-flex; align-items:center; gap:8px;
      padding:8px 12px; border:1px solid var(--line); border-radius:999px;
      color:var(--muted); font-size:13px; background: rgba(0,0,0,.18);
    }
    .row{display:flex; gap:10px; align-items:center; flex-wrap:wrap}
    input{
      width:100%; padding:12px 14px; border-radius:14px;
      border:1px solid rgba(255,255,255,.12); outline:none;
      background: rgba(0,0,0,.20); color:var(--text); font-size:15px;
    }
    input::placeholder{color:rgba(234,240,255,.45)}
    .btn{
      cursor:pointer; border:none; padding:12px 14px; border-radius:14px;
      font-weight:700; color:#07111f;
      background: linear-gradient(135deg, rgba(110,231,255,.95), rgba(167,139,250,.95));
      box-shadow: 0 10px 20px rgba(110,231,255,.12);
      white-space:nowrap; display:inline-block; text-decoration:none;
    }
    .btn.secondary{background: rgba(255,255,255,.08); color:var(--text); border:1px solid var(--line); box-shadow:none;}
    .btn.active{background: linear-gradient(135deg, rgba(110,231,255,.95), rgba(167,139,250,.95)); color:#07111f; border:none;}
    .hint{margin-top:12px; color:var(--muted); font-size:13px; line-height:1.4;}
    .alert{
      margin-top:14px; padding:12px 14px; border-radius:14px;
      border:1px solid rgba(239,68,68,.35); background: rgba(239,68,68,.10);
      color:#ffd2d2; display:flex; justify-content:space-between; align-items:center; gap:10px;
    }
    .alert code{
      background: rgba(0,0,0,.25); padding:3px 8px; border-radius:10px;
      border:1px solid rgba(255,255,255,.10); color:#fff;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size:13px;
    }
    a.link{color: var(--accent); text-decoration:none; font-weight:700;}
    a.link:hover{text-decoration:underline}
    .formGrid{display:grid; grid-template-columns: 1fr 1fr auto; gap:10px;}
    @media (max-width: 520px){ .formGrid{grid-template-columns: 1fr} .btn{width:100%} }
    .footer{margin-top:12px; display:flex; justify-content:space-between; gap:12px; flex-wrap:wrap; color:var(--muted); font-size:12px;}
    .kbd{border:1px solid rgba(255,255,255,.14); padding:2px 7px; border-radius:8px; background: rgba(0,0,0,.22); color: rgba(234,240,255,.85); font-weight:700; font-size:12px;}
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <div>
        <div class="brand"><div class="logo"></div>Kelime Quiz</div>
        <div class="sub">Hızlı tekrar • yanlışta doğruyu gösterir • kayıtlar kullanıcıya göre saklanır</div>
        <div class="sub">Kullanıcı: <b>{{user}}</b> • <a class="link" href="/logout">Çıkış</a></div>
      </div>

      <div style="display:flex; gap:12px; align-items:center; flex-wrap:wrap; justify-content:flex-end;">
        <a class="link" href="/stats?level={{level}}">İstatistik →</a>

        <div style="display:flex; gap:8px; flex-wrap:wrap; justify-content:flex-end;">
          <a class="btn {{ 'active' if level=='A1' else 'secondary' }}" href="/?level=A1">A1</a>
          <a class="btn {{ 'active' if level=='A2' else 'secondary' }}" href="/?level=A2">A2</a>
          <a class="btn {{ 'active' if level=='B1' else 'secondary' }}" href="/?level=B1">B1</a>
          <a class="btn {{ 'active' if level=='B2' else 'secondary' }}" href="/?level=B2">B2</a>
          <a class="btn {{ 'active' if level=='C1' else 'secondary' }}" href="/?level=C1">C1</a>
          <a class="btn {{ 'active' if level=='C2' else 'secondary' }}" href="/?level=C2">C2</a>
        </div>
      </div>
    </header>

    <div class="card">
      <div class="grid">
        <div class="panel">
          <p class="qtitle">Soru</p>
          <h1 class="question">{{question}}</h1>

          <form method="post" action="/?level={{level}}">
            <div class="row" style="width:100%">
              <div style="flex:1; min-width:220px">
                <input name="answer" autofocus placeholder="Cevabını yaz..." />
                <input type="hidden" name="ing" value="{{word.ing}}">
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

        <div class="panel">
          <div style="display:flex; align-items:center; justify-content:space-between; gap:10px; margin:0 0 12px;">
            <h3 style="margin:0; font-size:15px">Yeni kelime ekle</h3>
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
            Eklediğin kelimeler kullanıcıya özel kaydolur. İstatistik ekranında doğru/yanlış sayılarını görürsün.
          </div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>
"""


# ----------------- ROUTES -----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")

        users = load_users()
        user = users.get(username)
        if not user or not check_password_hash(user["pw"], password):
            error = "Kullanıcı adı veya şifre yanlış."
        else:
            session["user"] = username
            return redirect(url_for("index"))

    return render_template_string(LOGIN_HTML, error=error)


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")

        if len(username) < 3:
            error = "Kullanıcı adı en az 3 karakter olsun."
        elif len(password) < 4:
            error = "Şifre en az 4 karakter olsun."
        else:
            users = load_users()
            if username in users:
                error = "Bu kullanıcı adı zaten var."
            else:
                users[username] = {"pw": generate_password_hash(password), "role": "user"}
                save_users(users)
                session["user"] = username
                return redirect(url_for("index"))

    return render_template_string(REGISTER_HTML, error=error)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    level = request.args.get("level", "A1").upper()
    if level not in ["A1", "A2", "B1", "B2", "C1", "C2"]:
        level = "A1"

    all_words = load_words()
    level_words = [w for w in all_words if w.get("level", "A1").upper() == level]
    if not level_words:
        level_words = all_words

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
        level=level,
        user=current_user(),
    )


@app.route("/add", methods=["POST"])
@login_required
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
@login_required
def stats():
    level = request.args.get("level", "ALL").upper()
    valid_levels = ["A1", "A2", "B1", "B2", "C1", "C2", "ALL"]
    if level not in valid_levels:
        level = "ALL"

    words = load_words()

    if level == "ALL":
        filtered = words
    else:
        filtered = [w for w in words if w.get("level", "A1").upper() == level]

    rows = ""
    for w in filtered:
        d = int(w.get("d", 0))
        y = int(w.get("y", 0))
        total = d + y
        pct = int((d / total) * 100) if total else 0

        rows += f"""
        <tr>
            <td><b>{w.get('ing','')}</b></td>
            <td>{w.get('tr','')}</td>
            <td>{w.get('level','A1')}</td>
            <td>{d}</td>
            <td>{y}</td>
            <td>%{pct}</td>
        </tr>
        """

    def btn(lvl, text=None):
        text = text or lvl
        cls = "btn active" if level == lvl else "btn secondary"
        return f'<a class="{cls}" href="/stats?level={lvl}">{text}</a>'

    level_buttons = (
        '<div style="display:flex; gap:8px; flex-wrap:wrap; justify-content:flex-end;">'
        + btn("ALL", "ALL")
        + btn("A1")
        + btn("A2")
        + btn("B1")
        + btn("B2")
        + btn("C1")
        + btn("C2")
        + "</div>"
    )

    return f"""
<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>İstatistik • Kelime Quiz</title>
  <style>
    body{{font-family:system-ui;background:#0b1220;color:#eaf0ff;min-height:100vh;padding:24px}}
    a{{color:#6ee7ff;text-decoration:none;font-weight:700}}
    table{{width:100%;border-collapse:collapse;margin-top:14px}}
    th,td{{border-bottom:1px solid rgba(255,255,255,.1);padding:10px;text-align:left}}
    .wrap{{max-width:980px;margin:0 auto}}
    .btn{{padding:8px 10px;border-radius:12px;border:1px solid rgba(255,255,255,.14);background:rgba(255,255,255,.08);color:#eaf0ff;font-weight:700;text-decoration:none}}
    .btn.active{{background: linear-gradient(135deg, rgba(110,231,255,.95), rgba(167,139,250,.95));color:#07111f;border:none}}
  </style>
</head>
<body>
  <div class="wrap">
    <div style="display:flex; justify-content:space-between; gap:12px; flex-wrap:wrap; align-items:center;">
      <div>
        <h2 style="margin:0">İstatistik</h2>
        <div style="opacity:.8">Kullanıcı: <b>{current_user()}</b> • Seviye: <b>{level}</b></div>
      </div>
      <div style="display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
        {level_buttons}
        <a href="/" style="color:#6ee7ff;font-weight:700">← Quiz</a>
      </div>
    </div>

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
</body>
</html>
"""


# ----------------- ADMIN PANEL -----------------
ADMIN_USERS_HTML = """
<!doctype html><html lang="tr"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Admin • Kullanıcılar</title>
<style>
body{font-family:system-ui;background:#0b1220;color:#eaf0ff;min-height:100vh;padding:24px}
.card{max-width:900px;margin:0 auto;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);border-radius:18px;padding:18px}
a{color:#6ee7ff;text-decoration:none;font-weight:700}
table{width:100%;border-collapse:separate;border-spacing:0 10px}
th{color:#93a4c7;font-size:12px;text-align:left}
td{background:rgba(0,0,0,.18);border:1px solid rgba(255,255,255,.08);padding:12px}
tr td:first-child{border-radius:14px 0 0 14px}
tr td:last-child{border-radius:0 14px 14px 0}
.btn{padding:8px 10px;border-radius:12px;border:1px solid rgba(255,255,255,.14);background:rgba(255,255,255,.08);color:#eaf0ff;font-weight:700;cursor:pointer}
.btn.danger{border-color:rgba(239,68,68,.35);background:rgba(239,68,68,.12)}
.small{color:#93a4c7;font-size:13px}
</style></head><body>
<div class="card">
  <h2 style="margin:0 0 6px">Admin Panel • Kullanıcılar</h2>
  <div class="small">Giriş yapan: <b>{{admin}}</b> • <a href="/">Quiz</a> • <a href="/logout">Çıkış</a></div>
  <div style="margin-top:12px; display:flex; gap:10px; flex-wrap:wrap;">
    <a class="btn" href="/admin/export/users">Users JSON indir</a>
  </div>

  <table style="margin-top:14px">
    <thead>
      <tr>
        <th>Kullanıcı</th>
        <th>Rol</th>
        <th>Kelime dosyası</th>
        <th>İşlem</th>
      </tr>
    </thead>
    <tbody>
      {% for u in users %}
      <tr>
        <td><b>{{u.username}}</b></td>
        <td>{{u.role}}</td>
        <td>{{u.data_file}}</td>
        <td>
          {% if u.username != admin %}
            <form method="post" action="/admin/delete/{{u.username}}" onsubmit="return confirm('Silinsin mi?');" style="margin:0">
              <button class="btn danger" type="submit">Sil</button>
            </form>
          {% else %}
            <span class="small">Kendini silemezsin</span>
          {% endif %}
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
</body></html>
"""


@app.route("/admin/users")
@admin_required
def admin_users():
    users = load_users()
    rows = []
    for uname, data in sorted(users.items()):
        rows.append(
            {
                "username": uname,
                "role": data.get("role", "user"),
                "data_file": data_file_for(uname),
            }
        )
    return render_template_string(ADMIN_USERS_HTML, users=rows, admin=current_user())


@app.route("/admin/export/users")
@admin_required
def admin_export_users():
    users = load_users()
    payload = json.dumps(users, ensure_ascii=False, indent=2)
    return Response(
        payload,
        mimetype="application/json; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="users_export.json"'},
    )


@app.route("/admin/delete/<username>", methods=["POST"])
@admin_required
def admin_delete_user(username):
    username = (username or "").strip().lower()
    if not username or username == current_user():
        return redirect(url_for("admin_users"))

    users = load_users()
    if username in users:
        users.pop(username, None)
        save_users(users)

        df = data_file_for(username)
        try:
            if os.path.exists(df):
                os.remove(df)
        except Exception:
            pass

    return redirect(url_for("admin_users"))


# ----------------- STARTUP -----------------
bootstrap_users()
ensure_admin()

if __name__ == "__main__":
    # (Geliştirme sırasında) debug istersen:
    # app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=True)
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)

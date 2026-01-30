from __future__ import annotations

import os, random, sqlite3
from functools import wraps
from datetime import datetime

from flask import Flask, request, redirect, url_for, render_template_string, session, g
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

# SQLite db path (Render'da kalıcılık için /var/data gibi disk mount edilebilir)
DB_PATH = os.environ.get("DB_PATH", "app.db")

# Basit admin anahtarı (istersen env'e koy: ADMIN_KEY)
ADMIN_KEY = os.environ.get("ADMIN_KEY", "1234")


# ----------------- DB HELPERS -----------------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH, check_same_thread=False)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        pw_hash TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    db.execute("""
    CREATE TABLE IF NOT EXISTS words (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        ing TEXT NOT NULL,
        tr TEXT NOT NULL,
        level TEXT NOT NULL,
        d INTEGER NOT NULL DEFAULT 0,
        y INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        UNIQUE(user_id, ing),
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    db.commit()

@app.before_request
def _ensure_db():
    init_db()


# ----------------- AUTH HELPERS -----------------
def current_user():
    return session.get("user")

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user():
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

def get_user_row(username: str):
    db = get_db()
    return db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

def get_current_user_id():
    u = current_user()
    if not u:
        return None
    row = get_user_row(u)
    return row["id"] if row else None


# ----------------- WORD HELPERS (SQLite) -----------------
def ensure_seed_words_for_user(user_id: int):
    db = get_db()
    cnt = db.execute(
        "SELECT COUNT(*) AS c FROM words WHERE user_id = ?",
        (user_id,)
    ).fetchone()["c"]
    if cnt != 0:
        return

    now = datetime.utcnow().isoformat()

    seed = [
        ("apple", "elma", "A1", 0, 0, now),
        ("water", "su", "A1", 0, 0, now),
        ("bread", "ekmek", "A1", 0, 0, now),
        ("milk", "süt", "A1", 0, 0, now),
        ("house", "ev", "A1", 0, 0, now),
        ("car", "araba", "A1", 0, 0, now),
        ("dog", "köpek", "A1", 0, 0, now),
        ("cat", "kedi", "A1", 0, 0, now),
        ("book", "kitap", "A1", 0, 0, now),
        ("pen", "kalem", "A1", 0, 1, now),

        ("table", "masa", "A1", 0, 0, now),
        ("chair", "sandalye", "A1", 0, 0, now),
        ("door", "kapı", "A1", 0, 0, now),
        ("window", "pencere", "A1", 0, 0, now),
        ("phone", "telefon", "A1", 0, 0, now),
        ("school", "okul", "A1", 0, 0, now),
        ("teacher", "öğretmen", "A1", 0, 0, now),
        ("student", "öğrenci", "A1", 0, 0, now),
        ("friend", "arkadaş", "A1", 0, 0, now),
        ("family", "aile", "A1", 0, 0, now),

        ("mother", "anne", "A1", 0, 0, now),
        ("father", "baba", "A1", 0, 0, now),
        ("brother", "erkek kardeş", "A1", 0, 0, now),
        ("sister", "kız kardeş", "A1", 0, 0, now),
        ("food", "yemek", "A1", 0, 0, now),
        ("drink", "içecek", "A1", 0, 0, now),
        ("city", "şehir", "A1", 0, 0, now),
        ("street", "sokak", "A1", 0, 0, now),
        ("shop", "mağaza", "A1", 0, 0, now),
        ("money", "para", "A1", 0, 0, now),

        ("time", "zaman", "A1", 0, 0, now),
        ("day", "gün", "A1", 0, 0, now),
        ("night", "gece", "A1", 0, 0, now),
        ("morning", "sabah", "A1", 0, 0, now),
        ("good", "iyi", "A1", 0, 0, now),
        ("bad", "kötü", "A1", 0, 0, now),
        ("big", "büyük", "A1", 0, 0, now),
        ("small", "küçük", "A1", 0, 0, now),
        ("new", "yeni", "A1", 0, 0, now),
        ("old", "eski", "A1", 0, 0, now),

        # A2 (problem tek)
        ("answer", "cevap", "A2", 0, 0, now),
        ("question", "soru", "A2", 0, 0, now),
        ("idea", "fikir", "A2", 0, 0, now),
        ("job", "iş", "A2", 0, 0, now),
        ("work", "çalışmak / iş", "A2", 0, 0, now),
        ("office", "ofis", "A2", 0, 0, now),
        ("company", "şirket", "A2", 0, 0, now),
        ("meeting", "toplantı", "A2", 0, 0, now),
        ("plan", "plan", "A2", 0, 0, now),
        ("travel", "seyahat etmek", "A2", 0, 0, now),
        ("holiday", "tatil", "A2", 0, 0, now),
        ("ticket", "bilet", "A2", 0, 0, now),
        ("hotel", "otel", "A2", 0, 0, now),
        ("airport", "havaalanı", "A2", 0, 0, now),
        ("weather", "hava durumu", "A2", 0, 0, now),
        ("season", "mevsim", "A2", 0, 0, now),
        ("temperature", "sıcaklık", "A2", 0, 0, now),
        ("rain", "yağmur", "A2", 0, 0, now),
        ("snow", "kar", "A2", 0, 0, now),
        ("health", "sağlık", "A2", 0, 0, now),
        ("doctor", "doktor", "A2", 0, 0, now),
        ("hospital", "hastane", "A2", 0, 0, now),
        ("medicine", "ilaç", "A2", 0, 0, now),
        ("problem", "sorun", "A2", 0, 0, now),
        ("help", "yardım etmek", "A2", 0, 0, now),
        ("learn", "öğrenmek", "A2", 0, 0, now),
        ("teach", "öğretmek", "A2", 0, 0, now),
        ("practice", "pratik yapmak", "A2", 0, 0, now),
        ("remember", "hatırlamak", "A2", 0, 0, now),
        ("buy", "satın almak", "A2", 0, 0, now),
        ("sell", "satmak", "A2", 0, 0, now),
        ("price", "fiyat", "A2", 0, 0, now),
        ("cheap", "ucuz", "A2", 0, 0, now),
        ("expensive", "pahalı", "A2", 0, 0, now),
        ("choose", "seçmek", "A2", 0, 0, now),
        ("decide", "karar vermek", "A2", 0, 0, now),
        ("wait", "beklemek", "A2", 0, 0, now),
        ("arrive", "varmak", "A2", 0, 0, now),
        ("leave", "ayrılmak", "A2", 0, 0, now),  

("experience", "deneyim", "B1", 0, 0, now),
    ("improve", "geliştirmek", "B1", 0, 0, now),
    ("increase", "artırmak", "B1", 0, 0, now),
    ("reduce", "azaltmak", "B1", 0, 0, now),
    ("result", "sonuç", "B1", 0, 0, now),
    ("reason", "sebep", "B1", 0, 0, now),
    ("effect", "etki", "B1", 0, 0, now),
    ("success", "başarı", "B1", 0, 0, now),
    ("fail", "başarısız olmak", "B1", 0, 0, now),
    ("goal", "hedef", "B1", 0, 0, now),

    ("chance", "şans / ihtimal", "B1", 0, 0, now),
    ("risk", "risk", "B1", 0, 0, now),
    ("choice", "seçim", "B1", 0, 0, now),
    ("decision", "karar", "B1", 0, 0, now),
    ("opinion", "fikir", "B1", 0, 0, now),
    ("agree", "katılmak", "B1", 0, 0, now),
    ("disagree", "katılmamak", "B1", 0, 0, now),
    ("explain", "açıklamak", "B1", 0, 0, now),
    ("describe", "tanımlamak", "B1", 0, 0, now),
    ("suggest", "önermek", "B1", 0, 0, now),

    ("support", "desteklemek", "B1", 0, 0, now),
    ("manage", "yönetmek", "B1", 0, 0, now),
    ("control", "kontrol etmek", "B1", 0, 0, now),
    ("organize", "düzenlemek", "B1", 0, 0, now),
    ("prepare", "hazırlamak", "B1", 0, 0, now),
    ("develop", "geliştirmek", "B1", 0, 0, now),
    ("solve", "çözmek", "B1", 0, 0, now),
    ("discover", "keşfetmek", "B1", 0, 0, now),
    ("expect", "ummak / beklemek", "B1", 0, 0, now),
    ("avoid", "kaçınmak", "B1", 0, 0, now),

    ("compare", "karşılaştırmak", "B1", 0, 0, now),
    ("depend", "bağlı olmak", "B1", 0, 0, now),
    ("allow", "izin vermek", "B1", 0, 0, now),
    ("refuse", "reddetmek", "B1", 0, 0, now),
    ("protect", "korumak", "B1", 0, 0, now),
    ("accept", "kabul etmek", "B1", 0, 0, now),
    ("continue", "devam etmek", "B1", 0, 0, now),
    ("quit", "bırakmak", "B1", 0, 0, now),
    ("require", "gerektirmek", "B1", 0, 0, now),
    ("achieve", "başarmak", "B1", 0, 0, now),

            ("analyze", "analiz etmek", "B2", 0, 0, now),
    ("assume", "varsaymak", "B2", 0, 0, now),
    ("estimate", "tahmin etmek", "B2", 0, 0, now),
    ("evaluate", "değerlendirmek", "B2", 0, 0, now),
    ("interpret", "yorumlamak", "B2", 0, 0, now),
    ("conclude", "sonuca varmak", "B2", 0, 0, now),
    ("predict", "öngörmek", "B2", 0, 0, now),
    ("determine", "belirlemek", "B2", 0, 0, now),
    ("identify", "tanımlamak / belirlemek", "B2", 0, 0, now),
    ("recognize", "fark etmek / tanımak", "B2", 0, 0, now),

    ("approach", "yaklaşım", "B2", 0, 0, now),
    ("strategy", "strateji", "B2", 0, 0, now),
    ("process", "süreç", "B2", 0, 0, now),
    ("structure", "yapı", "B2", 0, 0, now),
    ("method", "yöntem", "B2", 0, 0, now),
    ("feature", "özellik", "B2", 0, 0, now),
    ("issue", "sorun / konu", "B2", 0, 0, now),
    ("challenge", "zorluk", "B2", 0, 0, now),
    ("solution", "çözüm", "B2", 0, 0, now),
    ("outcome", "sonuç", "B2", 0, 0, now),

    ("requirement", "gereksinim", "B2", 0, 0, now),
    ("resource", "kaynak", "B2", 0, 0, now),
    ("efficiency", "verimlilik", "B2", 0, 0, now),
    ("performance", "performans", "B2", 0, 0, now),
    ("capacity", "kapasite", "B2", 0, 0, now),
    ("impact", "etki", "B2", 0, 0, now),
    ("benefit", "fayda", "B2", 0, 0, now),
    ("drawback", "dezavantaj", "B2", 0, 0, now),
    ("alternative", "alternatif", "B2", 0, 0, now),
    ("priority", "öncelik", "B2", 0, 0, now),

    ("maintain", "sürdürmek / korumak", "B2", 0, 0, now),
    ("implement", "uygulamak", "B2", 0, 0, now),
    ("optimize", "optimize etmek", "B2", 0, 0, now),
    ("eliminate", "ortadan kaldırmak", "B2", 0, 0, now),
    ("adapt", "uyum sağlamak", "B2", 0, 0, now),
    ("monitor", "izlemek", "B2", 0, 0, now),
    ("resolve", "çözümlemek", "B2", 0, 0, now),
    ("justify", "haklı çıkarmak", "B2", 0, 0, now),
    ("negotiate", "müzakere etmek", "B2", 0, 0, now),
    ("emphasize", "vurgulamak", "B2", 0, 0, now),

            
       ("advocate", "savunmak / desteklemek", "C1", 0, 0, now),
    ("allocate", "tahsis etmek", "C1", 0, 0, now),
    ("anticipate", "öngörmek", "C1", 0, 0, now),
    ("articulate", "net ifade etmek", "C1", 0, 0, now),
    ("assess", "değerlendirmek", "C1", 0, 0, now),
    ("attribute", "atfetmek", "C1", 0, 0, now),
    ("coherent", "tutarlı", "C1", 0, 0, now),
    ("comprehensive", "kapsamlı", "C1", 0, 0, now),
    ("conceive", "tasarlamak / düşünmek", "C1", 0, 0, now),
    ("constrain", "kısıtlamak", "C1", 0, 0, now),

    ("derive", "türetmek / elde etmek", "C1", 0, 0, now),
    ("diminish", "azalmak / azaltmak", "C1", 0, 0, now),
    ("elaborate", "detaylandırmak", "C1", 0, 0, now),
    ("empirical", "deneysel", "C1", 0, 0, now),
    ("endeavor", "çaba / girişim", "C1", 0, 0, now),
    ("enhance", "geliştirmek", "C1", 0, 0, now),
    ("explicit", "açık / net", "C1", 0, 0, now),
    ("feasible", "uygulanabilir", "C1", 0, 0, now),
    ("fundamental", "temel", "C1", 0, 0, now),
    ("hypothesis", "hipotez", "C1", 0, 0, now),

    ("implicit", "örtük", "C1", 0, 0, now),
    ("inevitable", "kaçınılmaz", "C1", 0, 0, now),
    ("integrate", "entegre etmek", "C1", 0, 0, now),
    ("justify", "gerekçelendirmek", "C1", 0, 0, now),
    ("manifest", "belirgin / ortaya koymak", "C1", 0, 0, now),
    ("notion", "kavram", "C1", 0, 0, now),
    ("paradigm", "paradigma", "C1", 0, 0, now),
    ("predominant", "baskın", "C1", 0, 0, now),
    ("preliminary", "ön", "C1", 0, 0, now),
    ("profound", "derin", "C1", 0, 0, now),

    ("rationale", "gerekçe", "C1", 0, 0, now),
    ("refine", "iyileştirmek", "C1", 0, 0, now),
    ("reinforce", "pekiştirmek", "C1", 0, 0, now),
    ("subsequent", "sonraki", "C1", 0, 0, now),
    ("sufficient", "yeterli", "C1", 0, 0, now),
    ("synthesize", "sentezlemek", "C1", 0, 0, now),
    ("theoretical", "teorik", "C1", 0, 0, now),
    ("ultimately", "nihayetinde", "C1", 0, 0, now),
    ("validate", "doğrulamak", "C1", 0, 0, now),
    ("whereas", "oysa / -iken", "C1", 0, 0, now),

("abide", "uymak", "C2", 0, 0, now),
    ("acquiesce", "sessizce kabul etmek", "C2", 0, 0, now),
    ("ameliorate", "iyileştirmek", "C2", 0, 0, now),
    ("arbitrary", "keyfi", "C2", 0, 0, now),
    ("assertive", "iddialı / kendinden emin", "C2", 0, 0, now),
    ("belligerent", "saldırgan", "C2", 0, 0, now),
    ("candor", "açıklık / dürüstlük", "C2", 0, 0, now),
    ("circumvent", "etrafından dolaşmak / aşmak", "C2", 0, 0, now),
    ("coerce", "zorlamak", "C2", 0, 0, now),
    ("convoluted", "karmaşık", "C2", 0, 0, now),

    ("corroborate", "doğrulamak", "C2", 0, 0, now),
    ("cryptic", "üstü kapalı / gizemli", "C2", 0, 0, now),
    ("detrimental", "zararlı", "C2", 0, 0, now),
    ("disparity", "eşitsizlik / fark", "C2", 0, 0, now),
    ("elusive", "zor yakalanan", "C2", 0, 0, now),
    ("embezzle", "zimmete geçirmek", "C2", 0, 0, now),
    ("exacerbate", "kötüleştirmek", "C2", 0, 0, now),
    ("exemplify", "örneklemek", "C2", 0, 0, now),
    ("fastidious", "aşırı titiz", "C2", 0, 0, now),
    ("fortuitous", "şans eseri", "C2", 0, 0, now),

    ("hackneyed", "basmakalıp", "C2", 0, 0, now),
    ("idiosyncrasy", "kendine özgü özellik", "C2", 0, 0, now),
    ("impeccable", "kusursuz", "C2", 0, 0, now),
    ("incessant", "aralıksız", "C2", 0, 0, now),
    ("juxtapose", "yan yana koymak", "C2", 0, 0, now),
    ("lucid", "açık / berrak", "C2", 0, 0, now),
    ("meticulous", "çok dikkatli", "C2", 0, 0, now),
    ("nonchalant", "umursamaz", "C2", 0, 0, now),
    ("obfuscate", "bilerek karmaşıklaştırmak", "C2", 0, 0, now),
    ("ostentatious", "gösterişli", "C2", 0, 0, now),

    ("pervasive", "yaygın", "C2", 0, 0, now),
    ("pragmatic", "pragmatik", "C2", 0, 0, now),
    ("quintessential", "en tipik", "C2", 0, 0, now),
    ("resilient", "dayanıklı", "C2", 0, 0, now),
    ("scrutinize", "didik didik incelemek", "C2", 0, 0, now),
    ("spurious", "asılsız", "C2", 0, 0, now),
    ("tenuous", "zayıf / belirsiz", "C2", 0, 0, now),
    ("ubiquitous", "her yerde bulunan", "C2", 0, 0, now),
    ("unwarranted", "yersiz", "C2", 0, 0, now),
    ("vindicate", "aklamak / haklı çıkarmak", "C2", 0, 0, now),
            
       db.executemany(
        "INSERT OR IGNORE INTO words (user_id, ing, tr, level, d, y, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        [(user_id, ing, tr, lvl, d, y, created_at) for (ing, tr, lvl, d, y, created_at) in seed],
    )
    db.commit()

def fetch_words(user_id: int, level: str | None = None):
    db = get_db()
    if level and level != "ALL":
        return db.execute(
            "SELECT * FROM words WHERE user_id = ? AND UPPER(level)=? ORDER BY id DESC",
            (user_id, level.upper())
        ).fetchall()
    return db.execute(
        "SELECT * FROM words WHERE user_id = ? ORDER BY id DESC",
        (user_id,)
    ).fetchall()

def add_word(user_id: int, ing: str, tr: str, level: str):
    db = get_db()
    now = datetime.utcnow().isoformat()
    # UNIQUE(user_id, ing) olduğu için aynı kelime eklenirse hata verir -> try/except
    try:
        db.execute(
            "INSERT INTO words (user_id, ing, tr, level, d, y, created_at) VALUES (?, ?, ?, ?, 0, 0, ?)",
            (user_id, ing, tr, level, now)
        )
        db.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def inc_stat(user_id: int, ing: str, is_correct: bool):
    db = get_db()
    if is_correct:
        db.execute("UPDATE words SET d = d + 1 WHERE user_id = ? AND ing = ?", (user_id, ing))
    else:
        db.execute("UPDATE words SET y = y + 1 WHERE user_id = ? AND ing = ?", (user_id, ing))
    db.commit()

def pick_word(rows, last_ing=None):
    # rows: sqlite Row list
    pool = rows if not last_ing else [r for r in rows if r["ing"] != last_ing] or rows
    w = random.choice(pool)
    direction = random.choice(["EN_TR", "TR_EN"])
    answer = w["tr"] if direction == "EN_TR" else w["ing"]
    question = f"{w['ing']} → Türkçe?" if direction == "EN_TR" else f"{w['tr']} → İngilizce?"
    return w, direction, question, answer


# ----------------- HTML -----------------
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

REGISTER_HTML = LOGIN_HTML.replace("Giriş", "Kayıt Ol")\
    .replace("Kelime Quiz hesabınla giriş yap", "Yeni hesap oluştur")\
    .replace("Giriş</button>", "Kayıt Ol</button>")\
    .replace('Hesabın yok mu? <a href="/register">Kayıt ol</a>', 'Hesabın var mı? <a href="/login">Giriş</a>')

QUIZ_HTML = """
<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Kelime Quiz</title>
  <style>
    :root{
      --bg:#0b1220; --muted:#93a4c7; --text:#eaf0ff;
      --accent:#6ee7ff; --accent2:#a78bfa;
      --line:rgba(255,255,255,.08); --shadow: 0 12px 30px rgba(0,0,0,.35);
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
      min-height:100vh; display:flex; align-items:center; justify-content:center; padding:24px;
    }
    .wrap{width:min(980px,100%)}
    header{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:14px;flex-wrap:wrap}
    .brand{display:flex;align-items:center;gap:10px;font-weight:700}
    .logo{width:38px;height:38px;border-radius:12px;background:linear-gradient(135deg, rgba(110,231,255,.9), rgba(167,139,250,.9));box-shadow:var(--shadow)}
    .sub{color:var(--muted);font-size:13px}
    .card{background:linear-gradient(180deg, rgba(255,255,255,.06), rgba(255,255,255,.03));border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow);overflow:hidden}
    .grid{display:grid;grid-template-columns:1.2fr .8fr}
    @media (max-width:860px){.grid{grid-template-columns:1fr}}
    .panel{padding:22px}
    .panel + .panel{border-left:1px solid var(--line)}
    @media (max-width:860px){.panel + .panel{border-left:none;border-top:1px solid var(--line)}}
    .qtitle{font-size:14px;color:var(--muted);margin:0 0 8px}
    .question{font-size:28px;margin:0 0 18px;line-height:1.2}
    .row{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
    input{width:100%;padding:12px 14px;border-radius:14px;border:1px solid rgba(255,255,255,.12);outline:none;background:rgba(0,0,0,.20);color:var(--text);font-size:15px}
    .btn{
      cursor:pointer;border:none;padding:12px 14px;border-radius:14px;font-weight:700;
      background:linear-gradient(135deg, rgba(110,231,255,.95), rgba(167,139,250,.95));
      color:#07111f;box-shadow:0 10px 20px rgba(110,231,255,.12);white-space:nowrap;text-decoration:none;display:inline-block
    }
    .btn.secondary{background:rgba(255,255,255,.08);color:var(--text);border:1px solid var(--line);box-shadow:none}
    .btn.active{background:linear-gradient(135deg, rgba(110,231,255,.95), rgba(167,139,250,.95));color:#07111f;box-shadow:0 10px 20px rgba(110,231,255,.18);border:none}
    a.link{color:var(--accent);text-decoration:none;font-weight:700}
    .alert{margin-top:14px;padding:12px 14px;border-radius:14px;border:1px solid rgba(239,68,68,.35);background:rgba(239,68,68,.10);color:#ffd2d2;display:flex;justify-content:space-between;align-items:center;gap:10px}
    .alert code{background:rgba(0,0,0,.25);padding:3px 8px;border-radius:10px;border:1px solid rgba(255,255,255,.10);color:#fff}
    .hint{margin-top:12px;color:var(--muted);font-size:13px;line-height:1.4}
    .formGrid{display:grid;grid-template-columns:1fr 1fr auto;gap:10px}
    @media (max-width:520px){.formGrid{grid-template-columns:1fr}.btn{width:100%}}
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <div>
        <div class="brand"><div class="logo"></div>Kelime Quiz</div>
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
                <input type="hidden" name="ing" value="{{ing}}">
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
          </div>
          {% endif %}

          <div class="hint">İpucu: Enter ile gönderebilirsin.</div>
        </div>

        <div class="panel">
          <h3 style="margin:0 0 12px">Yeni kelime ekle</h3>
          <form action="/add" method="post">
            <input type="hidden" name="level" value="{{level}}">
            <div class="formGrid">
              <input name="ing" placeholder="İngilizce (örn: moon)" />
              <input name="tr" placeholder="Türkçe (örn: ay)" />
              <button class="btn secondary" type="submit">Ekle</button>
            </div>
          </form>
          {% if add_msg %}
            <div class="hint">{{add_msg}}</div>
          {% endif %}
        </div>
      </div>
    </div>

    <div style="margin-top:10px;color:#93a4c7;font-size:12px">
      Admin kullanıcı listesi: <a class="link" href="/admin/users?key={{admin_key}}">/admin/users</a>
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

        row = get_user_row(username)
        if not row or not check_password_hash(row["pw_hash"], password):
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
            db = get_db()
            try:
                db.execute(
                    "INSERT INTO users (username, pw_hash, created_at) VALUES (?, ?, ?)",
                    (username, generate_password_hash(password), datetime.utcnow().isoformat())
                )
                db.commit()
                session["user"] = username
                return redirect(url_for("index"))
            except sqlite3.IntegrityError:
                error = "Bu kullanıcı adı zaten var."
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

    user_id = get_current_user_id()
    ensure_seed_words_for_user(user_id)

    add_msg = None
    wrong = False
    right = False
    show_correct = ""
    last = None

    def norm(s: str) -> str:
        return (s or "").strip().casefold()

    # POST = cevap kontrol
    if request.method == "POST":
        ing = request.form.get("ing", "")
        user_answer = norm(request.form.get("answer", ""))

        correct_raw = request.form.get("correct_answer", "")
        correct = norm(correct_raw)

        if user_answer == correct:
            inc_stat(user_id, ing, True)
            right = True
        else:
            inc_stat(user_id, ing, False)
            wrong = True
            show_correct = correct_raw
        last = ing

    # kelimeleri getir
    level_rows = fetch_words(user_id, level)
    if not level_rows:
        level_rows = fetch_words(user_id, "ALL")

    w, direction, question, correct_answer_raw = pick_word(level_rows, last_ing=last)

    return render_template_string(
        QUIZ_HTML,
        question=question,
        ing=w["ing"],
        correct_answer=correct_answer_raw,
        wrong=wrong,
        right=right,
        correct=show_correct,
        level=level,
        user=current_user(),
        add_msg=add_msg,
        admin_key=ADMIN_KEY
    )

@app.route("/add", methods=["POST"])
@login_required
def add():
    user_id = get_current_user_id()
    ing = request.form.get("ing", "").strip().lower()
    tr = request.form.get("tr", "").strip().lower()
    level = request.form.get("level", "A1").upper()
    if level not in ["A1", "A2", "B1", "B2", "C1", "C2"]:
        level = "A1"

    if ing and tr:
        ok = add_word(user_id, ing, tr, level)
        # mesajı indexte göstermedik; direkt redirect
    return redirect(url_for("index", level=level))

@app.route("/stats")
@login_required
def stats():
    level = request.args.get("level", "ALL").upper()
    valid_levels = ["A1", "A2", "B1", "B2", "C1", "C2", "ALL"]
    if level not in valid_levels:
        level = "ALL"

    user_id = get_current_user_id()
    ensure_seed_words_for_user(user_id)

    rows = fetch_words(user_id, level)

    def btn(lvl, text=None):
        text = text or lvl
        cls = "btn active" if level == lvl else "btn secondary"
        return f'<a class="{cls}" href="/stats?level={lvl}">{text}</a>'

    level_buttons = (
        '<div style="display:flex; gap:8px; flex-wrap:wrap; justify-content:flex-end;">'
        + btn("ALL", "ALL")
        + btn("A1") + btn("A2") + btn("B1") + btn("B2") + btn("C1") + btn("C2")
        + "</div>"
    )

    table_rows = ""
    for w in rows:
        d = int(w["d"])
        y = int(w["y"])
        total = d + y
        pct = int((d / total) * 100) if total else 0
        table_rows += f"""
        <tr>
          <td><b>{w['ing']}</b></td>
          <td>{w['tr']}</td>
          <td>{w['level']}</td>
          <td>{d}</td>
          <td>{y}</td>
          <td>%{pct}</td>
        </tr>
        """

    return f"""
<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>İstatistik</title>
<style>
body{{font-family:system-ui;background:#0b1220;color:#eaf0ff;min-height:100vh;display:flex;justify-content:center;padding:24px}}
.wrap{{width:min(980px,100%)}}
a.link{{color:#6ee7ff;text-decoration:none;font-weight:700}}
.card{{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);border-radius:18px;overflow:hidden}}
.top{{padding:14px 16px;border-bottom:1px solid rgba(255,255,255,.1);display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px}}
.tableWrap{{padding:14px 16px 18px}}
table{{width:100%;border-collapse:separate;border-spacing:0 10px}}
th{{text-align:left;color:#93a4c7;font-size:12px;padding:0 12px 6px}}
td{{background:rgba(0,0,0,.18);border:1px solid rgba(255,255,255,.08);padding:12px}}
tr td:first-child{{border-radius:14px 0 0 14px}}
tr td:last-child{{border-radius:0 14px 14px 0}}
.btn{{cursor:pointer;border:none;padding:10px 12px;border-radius:14px;font-weight:700;white-space:nowrap;display:inline-block;text-decoration:none}}
.btn.secondary{{background:rgba(255,255,255,.08);color:#eaf0ff;border:1px solid rgba(255,255,255,.08)}}
.btn.active{{background:linear-gradient(135deg, rgba(110,231,255,.95), rgba(167,139,250,.95));color:#07111f;border:none}}
</style>
</head>
<body>
  <div class="wrap">
    <div style="display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;align-items:flex-start;margin-bottom:12px">
      <div>
        <div style="font-weight:800;font-size:18px">İstatistik</div>
        <div style="color:#93a4c7;font-size:13px">Kullanıcı: <b>{current_user()}</b> • Seçili seviye: <b>{level}</b></div>
      </div>
      <div style="display:flex;gap:10px;flex-wrap:wrap;justify-content:flex-end;align-items:center">
        {level_buttons}
        <a class="link" href="/">← Quiz’e dön</a>
      </div>
    </div>

    <div class="card">
      <div class="top">
        <div style="color:#93a4c7">Gösterilen kelime: <b style="color:#eaf0ff">{len(rows)}</b></div>
        <div style="color:#93a4c7">İpucu: düşük yüzdelileri tekrar et</div>
      </div>
      <div class="tableWrap">
        <table>
          <thead>
            <tr>
              <th>İngilizce</th><th>Türkçe</th><th>Seviye</th><th>Doğru</th><th>Yanlış</th><th>Başarı</th>
            </tr>
          </thead>
          <tbody>
            {table_rows}
          </tbody>
        </table>
      </div>
    </div>
  </div>
</body>
</html>
"""


# ----------------- ADMIN: user list -----------------
@app.route("/admin/users")
def admin_users():
    key = request.args.get("key", "")
    if key != ADMIN_KEY:
        return "Forbidden", 403

    db = get_db()
    users = db.execute("""
        SELECT u.id, u.username, u.created_at,
               (SELECT COUNT(*) FROM words w WHERE w.user_id=u.id) AS word_count
        FROM users u
        ORDER BY u.created_at DESC
    """).fetchall()

    rows = ""
    for u in users:
        rows += f"""
        <tr>
          <td>{u['id']}</td>
          <td><b>{u['username']}</b></td>
          <td>{u['created_at']}</td>
          <td>{u['word_count']}</td>
        </tr>
        """

    return f"""
<!doctype html><html lang="tr"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Admin • Users</title>
<style>
body{{font-family:system-ui;background:#0b1220;color:#eaf0ff;min-height:100vh;display:flex;justify-content:center;padding:24px}}
.wrap{{width:min(980px,100%)}}
.card{{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);border-radius:18px;overflow:hidden}}
.tableWrap{{padding:14px 16px 18px}}
table{{width:100%;border-collapse:separate;border-spacing:0 10px}}
th{{text-align:left;color:#93a4c7;font-size:12px;padding:0 12px 6px}}
td{{background:rgba(0,0,0,.18);border:1px solid rgba(255,255,255,.08);padding:12px}}
tr td:first-child{{border-radius:14px 0 0 14px}}
tr td:last-child{{border-radius:0 14px 14px 0}}
a{{color:#6ee7ff;text-decoration:none;font-weight:700}}
</style></head><body>
<div class="wrap">
  <div style="display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;align-items:flex-start;margin-bottom:12px">
    <div>
      <div style="font-weight:800;font-size:18px">Admin • Kullanıcılar</div>
      <div style="color:#93a4c7;font-size:13px">Toplam kullanıcı: <b>{len(users)}</b></div>
    </div>
    <div><a href="/">← Quiz</a></div>
  </div>

  <div class="card">
    <div class="tableWrap">
      <table>
        <thead>
          <tr><th>ID</th><th>Kullanıcı</th><th>Oluşturma</th><th>Kelime</th></tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
  </div>
</div>
</body></html>
"""


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)

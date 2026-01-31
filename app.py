from __future__ import annotations

import json, os, random
from functools import wraps

from flask import Flask, request, redirect, url_for, render_template_string, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
ensure_admin()

app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

USERS_FILE = "users.json"
ADMIN_USER = os.environ.get("ADMIN_USER")
ADMIN_PASS = os.environ.get("ADMIN_PASS")

def ensure_admin():
    if not ADMIN_USER or not ADMIN_PASS:
        return
    users = load_users()
    uname = ADMIN_USER.strip().lower()

    if uname not in users:
        users[uname] = {"pw": generate_password_hash(ADMIN_PASS), "role": "admin"}
        save_users(users)
    else:
        users[uname]["role"] = "admin"
        if "pw" not in users[uname]:
            users[uname]["pw"] = generate_password_hash(ADMIN_PASS)
        save_users(users)

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

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user():
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

# ----------------- LOGIN GUARD -----------------
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
  {"ing":"apple","tr":"elma","level":"A1","d":0,"y":0},
  {"ing":"water","tr":"su","level":"A1","d":0,"y":0},
  {"ing":"bread","tr":"ekmek","level":"A1","d":0,"y":0},
  {"ing":"milk","tr":"süt","level":"A1","d":0,"y":0},
  {"ing":"house","tr":"ev","level":"A1","d":0,"y":0},
  {"ing":"car","tr":"araba","level":"A1","d":0,"y":0},
  {"ing":"dog","tr":"köpek","level":"A1","d":0,"y":0},
  {"ing":"cat","tr":"kedi","level":"A1","d":0,"y":0},
  {"ing":"book","tr":"kitap","level":"A1","d":0,"y":0},
  {"ing":"pen","tr":"kalem","level":"A1","d":0,"y":1},

  {"ing":"table","tr":"masa","level":"A1","d":0,"y":0},
  {"ing":"chair","tr":"sandalye","level":"A1","d":0,"y":0},
  {"ing":"door","tr":"kapı","level":"A1","d":0,"y":0},
  {"ing":"window","tr":"pencere","level":"A1","d":0,"y":0},
  {"ing":"phone","tr":"telefon","level":"A1","d":0,"y":0},
  {"ing":"school","tr":"okul","level":"A1","d":0,"y":0},
  {"ing":"teacher","tr":"öğretmen","level":"A1","d":0,"y":0},
  {"ing":"student","tr":"öğrenci","level":"A1","d":0,"y":0},
  {"ing":"friend","tr":"arkadaş","level":"A1","d":0,"y":0},
  {"ing":"family","tr":"aile","level":"A1","d":0,"y":0},

  {"ing":"mother","tr":"anne","level":"A1","d":0,"y":0},
  {"ing":"father","tr":"baba","level":"A1","d":0,"y":0},
  {"ing":"brother","tr":"erkek kardeş","level":"A1","d":0,"y":0},
  {"ing":"sister","tr":"kız kardeş","level":"A1","d":0,"y":0},
  {"ing":"food","tr":"yemek","level":"A1","d":0,"y":0},
  {"ing":"drink","tr":"içecek","level":"A1","d":0,"y":0},
  {"ing":"city","tr":"şehir","level":"A1","d":0,"y":0},
  {"ing":"street","tr":"sokak","level":"A1","d":0,"y":0},
  {"ing":"shop","tr":"mağaza","level":"A1","d":0,"y":0},
  {"ing":"money","tr":"para","level":"A1","d":0,"y":0},

  {"ing":"time","tr":"zaman","level":"A1","d":0,"y":0},
  {"ing":"day","tr":"gün","level":"A1","d":0,"y":0},
  {"ing":"night","tr":"gece","level":"A1","d":0,"y":0},
  {"ing":"morning","tr":"sabah","level":"A1","d":0,"y":0},
  {"ing":"good","tr":"iyi","level":"A1","d":0,"y":0},
  {"ing":"bad","tr":"kötü","level":"A1","d":0,"y":0},
  {"ing":"big","tr":"büyük","level":"A1","d":0,"y":0},
  {"ing":"small","tr":"küçük","level":"A1","d":0,"y":0},
  {"ing":"new","tr":"yeni","level":"A1","d":0,"y":0},
  {"ing":"old","tr":"eski","level":"A1","d":0,"y":0},





  
{"ing":"answer","tr":"cevap","level":"A2","d":0,"y":0},
  {"ing":"question","tr":"soru","level":"A2","d":0,"y":0},
  {"ing":"problem","tr":"problem","level":"A2","d":0,"y":0},
  {"ing":"idea","tr":"fikir","level":"A2","d":0,"y":0},
  {"ing":"job","tr":"iş","level":"A2","d":0,"y":0},
  {"ing":"work","tr":"çalışmak / iş","level":"A2","d":0,"y":0},
  {"ing":"office","tr":"ofis","level":"A2","d":0,"y":0},
  {"ing":"company","tr":"şirket","level":"A2","d":0,"y":0},
  {"ing":"meeting","tr":"toplantı","level":"A2","d":0,"y":0},
  {"ing":"plan","tr":"plan","level":"A2","d":0,"y":0},

  {"ing":"travel","tr":"seyahat etmek","level":"A2","d":0,"y":0},
  {"ing":"holiday","tr":"tatil","level":"A2","d":0,"y":0},
  {"ing":"ticket","tr":"bilet","level":"A2","d":0,"y":0},
  {"ing":"hotel","tr":"otel","level":"A2","d":0,"y":0},
  {"ing":"airport","tr":"havaalanı","level":"A2","d":0,"y":0},
  {"ing":"weather","tr":"hava durumu","level":"A2","d":0,"y":0},
  {"ing":"season","tr":"mevsim","level":"A2","d":0,"y":0},
  {"ing":"temperature","tr":"sıcaklık","level":"A2","d":0,"y":0},
  {"ing":"rain","tr":"yağmur","level":"A2","d":0,"y":0},
  {"ing":"snow","tr":"kar","level":"A2","d":0,"y":0},

  {"ing":"health","tr":"sağlık","level":"A2","d":0,"y":0},
  {"ing":"doctor","tr":"doktor","level":"A2","d":0,"y":0},
  {"ing":"hospital","tr":"hastane","level":"A2","d":0,"y":0},
  {"ing":"medicine","tr":"ilaç","level":"A2","d":0,"y":0},
  {"ing":"problem","tr":"sorun","level":"A2","d":0,"y":0},
  {"ing":"help","tr":"yardım etmek","level":"A2","d":0,"y":0},
  {"ing":"learn","tr":"öğrenmek","level":"A2","d":0,"y":0},
  {"ing":"teach","tr":"öğretmek","level":"A2","d":0,"y":0},
  {"ing":"practice","tr":"pratik yapmak","level":"A2","d":0,"y":0},
  {"ing":"remember","tr":"hatırlamak","level":"A2","d":0,"y":0},

  {"ing":"buy","tr":"satın almak","level":"A2","d":0,"y":0},
  {"ing":"sell","tr":"satmak","level":"A2","d":0,"y":0},
  {"ing":"price","tr":"fiyat","level":"A2","d":0,"y":0},
  {"ing":"cheap","tr":"ucuz","level":"A2","d":0,"y":0},
  {"ing":"expensive","tr":"pahalı","level":"A2","d":0,"y":0},
  {"ing":"choose","tr":"seçmek","level":"A2","d":0,"y":0},
  {"ing":"decide","tr":"karar vermek","level":"A2","d":0,"y":0},
  {"ing":"wait","tr":"beklemek","level":"A2","d":0,"y":0},
  {"ing":"arrive","tr":"varmak","level":"A2","d":0,"y":0},
  {"ing":"leave","tr":"ayrılmak","level":"A2","d":0,"y":0},






  {"ing":"experience","tr":"deneyim","level":"B1","d":0,"y":0},
  {"ing":"improve","tr":"geliştirmek","level":"B1","d":0,"y":0},
  {"ing":"increase","tr":"artırmak","level":"B1","d":0,"y":0},
  {"ing":"reduce","tr":"azaltmak","level":"B1","d":0,"y":0},
  {"ing":"result","tr":"sonuç","level":"B1","d":0,"y":0},
  {"ing":"reason","tr":"sebep","level":"B1","d":0,"y":0},
  {"ing":"effect","tr":"etki","level":"B1","d":0,"y":0},
  {"ing":"success","tr":"başarı","level":"B1","d":0,"y":0},
  {"ing":"fail","tr":"başarısız olmak","level":"B1","d":0,"y":0},
  {"ing":"goal","tr":"hedef","level":"B1","d":0,"y":0},

  {"ing":"chance","tr":"şans / ihtimal","level":"B1","d":0,"y":0},
  {"ing":"risk","tr":"risk","level":"B1","d":0,"y":0},
  {"ing":"choice","tr":"seçim","level":"B1","d":0,"y":0},
  {"ing":"decision","tr":"karar","level":"B1","d":0,"y":0},
  {"ing":"opinion","tr":"fikir","level":"B1","d":0,"y":0},
  {"ing":"agree","tr":"katılmak","level":"B1","d":0,"y":0},
  {"ing":"disagree","tr":"katılmamak","level":"B1","d":0,"y":0},
  {"ing":"explain","tr":"açıklamak","level":"B1","d":0,"y":0},
  {"ing":"describe","tr":"tanımlamak","level":"B1","d":0,"y":0},
  {"ing":"suggest","tr":"önermek","level":"B1","d":0,"y":0},

  {"ing":"support","tr":"desteklemek","level":"B1","d":0,"y":0},
  {"ing":"manage","tr":"yönetmek","level":"B1","d":0,"y":0},
  {"ing":"control","tr":"kontrol etmek","level":"B1","d":0,"y":0},
  {"ing":"organize","tr":"düzenlemek","level":"B1","d":0,"y":0},
  {"ing":"prepare","tr":"hazırlamak","level":"B1","d":0,"y":0},
  {"ing":"develop","tr":"geliştirmek","level":"B1","d":0,"y":0},
  {"ing":"solve","tr":"çözmek","level":"B1","d":0,"y":0},
  {"ing":"discover","tr":"keşfetmek","level":"B1","d":0,"y":0},
  {"ing":"expect","tr":"ummak / beklemek","level":"B1","d":0,"y":0},
  {"ing":"avoid","tr":"kaçınmak","level":"B1","d":0,"y":0},

  {"ing":"compare","tr":"karşılaştırmak","level":"B1","d":0,"y":0},
  {"ing":"depend","tr":"bağlı olmak","level":"B1","d":0,"y":0},
  {"ing":"allow","tr":"izin vermek","level":"B1","d":0,"y":0},
  {"ing":"refuse","tr":"reddetmek","level":"B1","d":0,"y":0},
  {"ing":"protect","tr":"korumak","level":"B1","d":0,"y":0},
  {"ing":"accept","tr":"kabul etmek","level":"B1","d":0,"y":0},
  {"ing":"continue","tr":"devam etmek","level":"B1","d":0,"y":0},
  {"ing":"quit","tr":"bırakmak","level":"B1","d":0,"y":0},
  {"ing":"require","tr":"gerektirmek","level":"B1","d":0,"y":0},
  {"ing":"achieve","tr":"başarmak","level":"B1","d":0,"y":0},






  
  {"ing":"analyze","tr":"analiz etmek","level":"B2","d":0,"y":0},
  {"ing":"assume","tr":"varsaymak","level":"B2","d":0,"y":0},
  {"ing":"estimate","tr":"tahmin etmek","level":"B2","d":0,"y":0},
  {"ing":"evaluate","tr":"değerlendirmek","level":"B2","d":0,"y":0},
  {"ing":"interpret","tr":"yorumlamak","level":"B2","d":0,"y":0},
  {"ing":"conclude","tr":"sonuca varmak","level":"B2","d":0,"y":0},
  {"ing":"predict","tr":"öngörmek","level":"B2","d":0,"y":0},
  {"ing":"determine","tr":"belirlemek","level":"B2","d":0,"y":0},
  {"ing":"identify","tr":"tanımlamak / belirlemek","level":"B2","d":0,"y":0},
  {"ing":"recognize","tr":"fark etmek / tanımak","level":"B2","d":0,"y":0},

  {"ing":"approach","tr":"yaklaşım","level":"B2","d":0,"y":0},
  {"ing":"strategy","tr":"strateji","level":"B2","d":0,"y":0},
  {"ing":"process","tr":"süreç","level":"B2","d":0,"y":0},
  {"ing":"structure","tr":"yapı","level":"B2","d":0,"y":0},
  {"ing":"method","tr":"yöntem","level":"B2","d":0,"y":0},
  {"ing":"feature","tr":"özellik","level":"B2","d":0,"y":0},
  {"ing":"issue","tr":"sorun / konu","level":"B2","d":0,"y":0},
  {"ing":"challenge","tr":"zorluk","level":"B2","d":0,"y":0},
  {"ing":"solution","tr":"çözüm","level":"B2","d":0,"y":0},
  {"ing":"outcome","tr":"sonuç","level":"B2","d":0,"y":0},

  {"ing":"requirement","tr":"gereksinim","level":"B2","d":0,"y":0},
  {"ing":"resource","tr":"kaynak","level":"B2","d":0,"y":0},
  {"ing":"efficiency","tr":"verimlilik","level":"B2","d":0,"y":0},
  {"ing":"performance","tr":"performans","level":"B2","d":0,"y":0},
  {"ing":"capacity","tr":"kapasite","level":"B2","d":0,"y":0},
  {"ing":"impact","tr":"etki","level":"B2","d":0,"y":0},
  {"ing":"benefit","tr":"fayda","level":"B2","d":0,"y":0},
  {"ing":"drawback","tr":"dezavantaj","level":"B2","d":0,"y":0},
  {"ing":"alternative","tr":"alternatif","level":"B2","d":0,"y":0},
  {"ing":"priority","tr":"öncelik","level":"B2","d":0,"y":0},

  {"ing":"maintain","tr":"sürdürmek / korumak","level":"B2","d":0,"y":0},
  {"ing":"implement","tr":"uygulamak","level":"B2","d":0,"y":0},
  {"ing":"optimize","tr":"optimize etmek","level":"B2","d":0,"y":0},
  {"ing":"eliminate","tr":"ortadan kaldırmak","level":"B2","d":0,"y":0},
  {"ing":"adapt","tr":"uyum sağlamak","level":"B2","d":0,"y":0},
  {"ing":"monitor","tr":"izlemek","level":"B2","d":0,"y":0},
  {"ing":"resolve","tr":"çözümlemek","level":"B2","d":0,"y":0},
  {"ing":"justify","tr":"haklı çıkarmak","level":"B2","d":0,"y":0},
  {"ing":"negotiate","tr":"müzakere etmek","level":"B2","d":0,"y":0},
  {"ing":"emphasize","tr":"vurgulamak","level":"B2","d":0,"y":0},








  
  {"ing":"advocate","tr":"savunmak / desteklemek","level":"C1","d":0,"y":0},
  {"ing":"allocate","tr":"tahsis etmek","level":"C1","d":0,"y":0},
  {"ing":"anticipate","tr":"öngörmek","level":"C1","d":0,"y":0},
  {"ing":"articulate","tr":"net ifade etmek","level":"C1","d":0,"y":0},
  {"ing":"assess","tr":"değerlendirmek","level":"C1","d":0,"y":0},
  {"ing":"attribute","tr":"atfetmek","level":"C1","d":0,"y":0},
  {"ing":"coherent","tr":"tutarlı","level":"C1","d":0,"y":0},
  {"ing":"comprehensive","tr":"kapsamlı","level":"C1","d":0,"y":0},
  {"ing":"conceive","tr":"tasarlamak / düşünmek","level":"C1","d":0,"y":0},
  {"ing":"constrain","tr":"kısıtlamak","level":"C1","d":0,"y":0},

  {"ing":"derive","tr":"türetmek / elde etmek","level":"C1","d":0,"y":0},
  {"ing":"diminish","tr":"azalmak / azaltmak","level":"C1","d":0,"y":0},
  {"ing":"elaborate","tr":"detaylandırmak","level":"C1","d":0,"y":0},
  {"ing":"empirical","tr":"deneysel","level":"C1","d":0,"y":0},
  {"ing":"endeavor","tr":"çaba / girişim","level":"C1","d":0,"y":0},
  {"ing":"enhance","tr":"geliştirmek","level":"C1","d":0,"y":0},
  {"ing":"explicit","tr":"açık / net","level":"C1","d":0,"y":0},
  {"ing":"feasible","tr":"uygulanabilir","level":"C1","d":0,"y":0},
  {"ing":"fundamental","tr":"temel","level":"C1","d":0,"y":0},
  {"ing":"hypothesis","tr":"hipotez","level":"C1","d":0,"y":0},

  {"ing":"implicit","tr":"örtük","level":"C1","d":0,"y":0},
  {"ing":"inevitable","tr":"kaçınılmaz","level":"C1","d":0,"y":0},
  {"ing":"integrate","tr":"entegre etmek","level":"C1","d":0,"y":0},
  {"ing":"justify","tr":"gerekçelendirmek","level":"C1","d":0,"y":0},
  {"ing":"manifest","tr":"belirgin / ortaya koymak","level":"C1","d":0,"y":0},
  {"ing":"notion","tr":"kavram","level":"C1","d":0,"y":0},
  {"ing":"paradigm","tr":"paradigma","level":"C1","d":0,"y":0},
  {"ing":"predominant","tr":"baskın","level":"C1","d":0,"y":0},
  {"ing":"preliminary","tr":"ön","level":"C1","d":0,"y":0},
  {"ing":"profound","tr":"derin","level":"C1","d":0,"y":0},

  {"ing":"rationale","tr":"gerekçe","level":"C1","d":0,"y":0},
  {"ing":"refine","tr":"iyileştirmek","level":"C1","d":0,"y":0},
  {"ing":"reinforce","tr":"pekiştirmek","level":"C1","d":0,"y":0},
  {"ing":"subsequent","tr":"sonraki","level":"C1","d":0,"y":0},
  {"ing":"sufficient","tr":"yeterli","level":"C1","d":0,"y":0},
  {"ing":"synthesize","tr":"sentezlemek","level":"C1","d":0,"y":0},
  {"ing":"theoretical","tr":"teorik","level":"C1","d":0,"y":0},
  {"ing":"ultimately","tr":"nihayetinde","level":"C1","d":0,"y":0},
  {"ing":"validate","tr":"doğrulamak","level":"C1","d":0,"y":0},
  {"ing":"whereas","tr":"oysa / -iken","level":"C1","d":0,"y":0},








  
  {"ing":"abide","tr":"uymak","level":"C2","d":0,"y":0},
  {"ing":"acquiesce","tr":"sessizce kabul etmek","level":"C2","d":0,"y":0},
  {"ing":"ameliorate","tr":"iyileştirmek","level":"C2","d":0,"y":0},
  {"ing":"arbitrary","tr":"keyfi","level":"C2","d":0,"y":0},
  {"ing":"assertive","tr":"iddialı / kendinden emin","level":"C2","d":0,"y":0},
  {"ing":"belligerent","tr":"saldırgan","level":"C2","d":0,"y":0},
  {"ing":"candor","tr":"açıklık / dürüstlük","level":"C2","d":0,"y":0},
  {"ing":"circumvent","tr":"etrafından dolaşmak / aşmak","level":"C2","d":0,"y":0},
  {"ing":"coerce","tr":"zorlamak","level":"C2","d":0,"y":0},
  {"ing":"convoluted","tr":"karmaşık","level":"C2","d":0,"y":0},

  {"ing":"corroborate","tr":"doğrulamak","level":"C2","d":0,"y":0},
  {"ing":"cryptic","tr":"üstü kapalı / gizemli","level":"C2","d":0,"y":0},
  {"ing":"detrimental","tr":"zararlı","level":"C2","d":0,"y":0},
  {"ing":"disparity","tr":"eşitsizlik / fark","level":"C2","d":0,"y":0},
  {"ing":"elusive","tr":"zor yakalanan","level":"C2","d":0,"y":0},
  {"ing":"embezzle","tr":"zimmete geçirmek","level":"C2","d":0,"y":0},
  {"ing":"exacerbate","tr":"kötüleştirmek","level":"C2","d":0,"y":0},
  {"ing":"exemplify","tr":"örneklemek","level":"C2","d":0,"y":0},
  {"ing":"fastidious","tr":"aşırı titiz","level":"C2","d":0,"y":0},
  {"ing":"fortuitous","tr":"şans eseri","level":"C2","d":0,"y":0},

  {"ing":"hackneyed","tr":"basmakalıp","level":"C2","d":0,"y":0},
  {"ing":"idiosyncrasy","tr":"kendine özgü özellik","level":"C2","d":0,"y":0},
  {"ing":"impeccable","tr":"kusursuz","level":"C2","d":0,"y":0},
  {"ing":"incessant","tr":"aralıksız","level":"C2","d":0,"y":0},
  {"ing":"juxtapose","tr":"yan yana koymak","level":"C2","d":0,"y":0},
  {"ing":"lucid","tr":"açık / berrak","level":"C2","d":0,"y":0},
  {"ing":"meticulous","tr":"çok dikkatli","level":"C2","d":0,"y":0},
  {"ing":"nonchalant","tr":"umursamaz","level":"C2","d":0,"y":0},
  {"ing":"obfuscate","tr":"bilerek karmaşıklaştırmak","level":"C2","d":0,"y":0},
  {"ing":"ostentatious","tr":"gösterişli","level":"C2","d":0,"y":0},

  {"ing":"pervasive","tr":"yaygın","level":"C2","d":0,"y":0},
  {"ing":"pragmatic","tr":"pragmatik","level":"C2","d":0,"y":0},
  {"ing":"quintessential","tr":"en tipik","level":"C2","d":0,"y":0},
  {"ing":"resilient","tr":"dayanıklı","level":"C2","d":0,"y":0},
  {"ing":"scrutinize","tr":"didik didik incelemek","level":"C2","d":0,"y":0},
  {"ing":"spurious","tr":"asılsız","level":"C2","d":0,"y":0},
  {"ing":"tenuous","tr":"zayıf / belirsiz","level":"C2","d":0,"y":0},
  {"ing":"ubiquitous","tr":"her yerde bulunan","level":"C2","d":0,"y":0},
  {"ing":"unwarranted","tr":"yersiz","level":"C2","d":0,"y":0},
  {"ing":"vindicate","tr":"aklamak / haklı çıkarmak","level":"C2","d":0,"y":0}
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

REGISTER_HTML = LOGIN_HTML.replace("Giriş", "Kayıt Ol")\
    .replace("Kelime Quiz hesabınla giriş yap", "Yeni hesap oluştur")\
    .replace("Giriş</button>", "Kayıt Ol</button>")\
    .replace('Hesabın yok mu? <a href="/register">Kayıt ol</a>', 'Hesabın var mı? <a href="/login">Giriş</a>')


# ----------------- QUIZ HTML -----------------
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
      flex-wrap:wrap;
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
      display:inline-block;
      text-decoration:none;
    }
    .btn:active{transform: translateY(1px)}
    .btn.secondary{
      background: rgba(255,255,255,.08);
      color:var(--text);
      border:1px solid var(--line);
      box-shadow:none;
    }
    /* AKTİF SEVİYE BUTONU */
    .btn.active{
      background: linear-gradient(135deg, rgba(110,231,255,.95), rgba(167,139,250,.95));
      color:#07111f;
      box-shadow: 0 10px 20px rgba(110,231,255,.18);
      border:none;
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
        user=current_user()
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
        + btn("A1") + btn("A2") + btn("B1") + btn("B2") + btn("C1") + btn("C2")
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
      display:inline-block;
      text-decoration:none;
    }}
    .btn.secondary{{
      background: rgba(255,255,255,.08);
      color:var(--text);
      border:1px solid var(--line);
    }}
    .btn.active{{
      background: linear-gradient(135deg, rgba(110,231,255,.95), rgba(167,139,250,.95));
      color:#07111f;
      box-shadow: 0 10px 20px rgba(110,231,255,.18);
      border:none;
    }}

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
        <div class="sub">Kullanıcı: <b>{current_user()}</b> • Seçili seviye: <b>{level}</b></div>
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

  <div style="margin-top:14px"></div>
  <table>
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
        rows.append({
            "username": uname,
            "role": data.get("role", "user"),
            "data_file": data_file_for(uname),
        })
    return render_template_string(ADMIN_USERS_HTML, users=rows, admin=current_user())

from flask import Response

@app.route("/admin/export/users")
@admin_required
def admin_export_users():
    users = load_users()

    payload = json.dumps(users, ensure_ascii=False, indent=2)
    return Response(
        payload,
        mimetype="application/json; charset=utf-8",
        headers={
            "Content-Disposition": 'attachment; filename="users_export.json"'
        }
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


if __name__ == "__main__":
    ensure_admin()
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)

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
<title>Kelime Quiz</title>
<h2>{{question}}</h2>

<form method="post">
<input name="answer" autofocus>
<input type="hidden" name="ing" value="{{word.ing}}">
<button>Kontrol</button>
</form>

{% if wrong %}
<p style="color:red;">Yanlış ❌ Doğru: {{correct}}</p>
{% endif %}

<hr>
<h3>Yeni kelime ekle</h3>
<form action="/add" method="post">
<input name="ing" placeholder="İngilizce">
<input name="tr" placeholder="Türkçe">
<button>Ekle</button>
</form>

<a href="/stats">İstatistik</a>
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
    words = load_words()
    html = "<h2>İstatistik</h2><ul>"
    for w in words:
        total = w["d"] + w["y"]
        pct = int((w["d"] / total) * 100) if total else 0
        html += f"<li>{w['ing']} = {w['tr']} | {w['d']}D {w['y']}Y %{pct}</li>"
    html += "</ul><a href='/'>Geri</a>"
    return html

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)


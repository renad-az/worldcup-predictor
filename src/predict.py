import json
import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")

# ─────────────────────────────────────────
# تحميل البيانات من data/raw
# ─────────────────────────────────────────
def load_data():
    with open("data/raw/sa_matches.json", encoding="utf-8") as f:
        sa = json.load(f)
    with open("data/raw/ur_matches.json", encoding="utf-8") as f:
        ur = json.load(f)
    with open("data/raw/h2h.json", encoding="utf-8") as f:
        h2h = json.load(f)
    return sa, ur, h2h

# ─────────────────────────────────────────
# تنظيم نتائج المباريات
# ─────────────────────────────────────────
def extract_results(data, team_id):
    rows = []
    wins = draws = losses = goals_for = goals_against = 0

    for m in data.get("response", []):
        home      = m["teams"]["home"]
        away      = m["teams"]["away"]
        gh        = m["goals"]["home"] or 0
        ga        = m["goals"]["away"] or 0
        rows.append(f"  {home['name']} {gh} - {ga} {away['name']}")

        is_home = home["id"] == team_id
        my_g    = gh if is_home else ga
        op_g    = ga if is_home else gh
        won     = home["winner"] if is_home else away["winner"]

        goals_for     += my_g
        goals_against += op_g
        if won is True:    wins   += 1
        elif won is False: losses += 1
        else:              draws  += 1

    total   = wins + draws + losses or 1
    summary = (
        f"  فوز: {wins} | تعادل: {draws} | خسارة: {losses} | "
        f"أهداف سجّل: {goals_for} | أهداف استقبل: {goals_against} | "
        f"معدل: {goals_for/total:.1f} لكل مباراة"
    )
    return "\n".join(rows), summary, wins, draws, losses, goals_for, goals_against

# ─────────────────────────────────────────
# إرسال البيانات لكلود
# ─────────────────────────────────────────
def get_prediction(sa, ur, h2h):
    sa_results, sa_summary, *sa_stats = extract_results(sa,  523)
    ur_results, ur_summary, *ur_stats = extract_results(ur,  26)
    h2h_results, _, *_                = extract_results(h2h, 523)

    prompt = f"""أنت محلل كرة قدم خبير. حلل مباراة السعودية vs أوروغواي في كأس العالم 2026.

=== آخر 10 مباريات للسعودية ===
{sa_results}
الملخص: {sa_summary}

=== آخر 10 مباريات لأوروغواي ===
{ur_results}
الملخص: {ur_summary}

=== المواجهات المباشرة السابقة ===
{h2h_results}

=== معلومات إضافية ===
- أوروغواي تأخروا في الوصول 24 ساعة قبل المباراة
- المباراة في ميامي (جو حار)
- السعودية فازوا على الأرجنتين 2022

أجب فقط بـ JSON بدون أي نص خارجه:
{{
  "score_sa": رقم,
  "score_ur": رقم,
  "prob_sa": رقم بين 0-100,
  "prob_draw": رقم بين 0-100,
  "prob_ur": رقم بين 0-100,
  "winner": "sa" أو "draw" أو "ur",
  "analysis": "تحليل 3 جمل بالعربية",
  "key_factor": "أهم عامل يحسم المباراة"
}}
تأكد أن prob_sa + prob_draw + prob_ur = 100"""

    print("🤖 كلود يحلل البيانات...")
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    resp   = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    raw   = resp.content[0].text
    clean = raw.replace("```json", "").replace("```", "").strip()
    pred  = json.loads(clean)

    # احفظ النتيجة
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/prediction.json", "w", encoding="utf-8") as f:
        json.dump(pred, f, ensure_ascii=False, indent=2)
    print("💾 تم حفظ التوقع: outputs/prediction.json")

    return pred, sa_stats, ur_stats

# ─────────────────────────────────────────
# التشغيل الرئيسي
# ─────────────────────────────────────────
if __name__ == "__main__":
    sa, ur, h2h = load_data()
    pred, sa_stats, ur_stats = get_prediction(sa, ur, h2h)

    print("\n📊 التوقع:")
    print(f"  النتيجة : السعودية {pred['score_sa']} - {pred['score_ur']} أوروغواي")
    print(f"  🇸🇦 فوز السعودية : {pred['prob_sa']}%")
    print(f"  🤝 تعادل          : {pred['prob_draw']}%")
    print(f"  🇺🇾 فوز أوروغواي : {pred['prob_ur']}%")
    print(f"\n  التحليل    : {pred['analysis']}")
    print(f"  العامل الحاسم : {pred['key_factor']}")
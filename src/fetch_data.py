import requests
import json
import os
from dotenv import load_dotenv

# تحميل المفاتيح من ملف .env
load_dotenv()
API_KEY = os.getenv("API_FOOTBALL_KEY")

HEADERS = {"x-apisports-key": API_KEY}
BASE    = "https://v3.football.api-sports.io"

# ─────────────────────────────────────────
# IDs الفرق
# السعودية = 523
# أوروغواي = 26
# ─────────────────────────────────────────

def get_last_matches(team_id, n=10):
    """جيب آخر n مباراة للفريق"""
    url  = f"{BASE}/fixtures?team={team_id}&last={n}"
    resp = requests.get(url, headers=HEADERS)
    data = resp.json()
    print(f"✅ جلبت آخر {n} مباريات للفريق {team_id}")
    return data

def get_head_to_head(team1_id, team2_id, n=10):
    """جيب المواجهات المباشرة بين فريقين"""
    url  = f"{BASE}/fixtures/headtohead?h2h={team1_id}-{team2_id}&last={n}"
    resp = requests.get(url, headers=HEADERS)
    data = resp.json()
    print(f"✅ جلبت المواجهات المباشرة")
    return data

def get_team_statistics(team_id, season=2024):
    """جيب إحصائيات الفريق في الموسم"""
    url  = f"{BASE}/teams/statistics?team={team_id}&season={season}"
    resp = requests.get(url, headers=HEADERS)
    data = resp.json()
    print(f"✅ جلبت إحصائيات الفريق {team_id}")
    return data

def save_data(data, filename):
    """احفظ البيانات في مجلد data/raw"""
    os.makedirs("data/raw", exist_ok=True)
    path = f"data/raw/{filename}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"💾 تم الحفظ: {path}")

# ─────────────────────────────────────────
# التشغيل الرئيسي
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("📡 جاري جلب البيانات...\n")

    # السعودية
    sa_matches = get_last_matches(523)
    save_data(sa_matches, "sa_matches")

    # أوروغواي
    ur_matches = get_last_matches(26)
    save_data(ur_matches, "ur_matches")

    # المواجهات المباشرة
    h2h = get_head_to_head(523, 26)
    save_data(h2h, "h2h")

    # الإحصائيات
    sa_stats = get_team_statistics(523)
    save_data(sa_stats, "sa_stats")

    ur_stats = get_team_statistics(26)
    save_data(ur_stats, "ur_stats")

    print("\n✅ تم جلب وحفظ كل البيانات في data/raw/")
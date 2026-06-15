import json
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec

# ─────────────────────────────────────────
# تحميل البيانات
# ─────────────────────────────────────────
def load_prediction():
    with open("outputs/prediction.json", encoding="utf-8") as f:
        return json.load(f)

def load_stats():
    with open("data/raw/sa_matches.json", encoding="utf-8") as f:
        sa = json.load(f)
    with open("data/raw/ur_matches.json", encoding="utf-8") as f:
        ur = json.load(f)
    return sa, ur

# ─────────────────────────────────────────
# استخراج الإحصائيات
# ─────────────────────────────────────────
def extract_stats(data, team_id):
    wins = draws = losses = goals_for = goals_against = 0
    for m in data.get("response", []):
        home    = m["teams"]["home"]
        away    = m["teams"]["away"]
        gh      = m["goals"]["home"] or 0
        ga      = m["goals"]["away"] or 0
        is_home = home["id"] == team_id
        my_g    = gh if is_home else ga
        op_g    = ga if is_home else gh
        won     = home["winner"] if is_home else away["winner"]
        goals_for     += my_g
        goals_against += op_g
        if won is True:    wins   += 1
        elif won is False: losses += 1
        else:              draws  += 1
    return wins, draws, losses, goals_for, goals_against

# ─────────────────────────────────────────
# رسم الشارتات
# ─────────────────────────────────────────
def draw_chart(pred, sa_stats, ur_stats):
    wins_sa, draws_sa, losses_sa, gf_sa, ga_sa = sa_stats
    wins_ur, draws_ur, losses_ur, gf_ur, ga_ur = ur_stats

    # الألوان
    C_SA   = "#00A86B"
    C_UR   = "#5EB2FF"
    C_DRAW = "#6B7280"
    C_GOLD = "#C8A951"
    C_TEXT = "#E8EDF5"
    C_MID  = "#161D2E"
    C_BG   = "#0A0F1A"

    fig = plt.figure(figsize=(14, 10), facecolor=C_BG)
    gs  = GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

    # ── شارت 1: نسب الفوز (Donut) ──────────────────────
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_facecolor(C_MID)
    sizes  = [pred["prob_sa"], pred["prob_draw"], pred["prob_ur"]]
    colors = [C_SA, C_DRAW, C_UR]
    ax1.pie(
        sizes, colors=colors, startangle=90,
        wedgeprops=dict(width=0.55, edgecolor=C_BG, linewidth=2)
    )
    ax1.text(0, 0.12, f"{pred['prob_sa']}%", ha="center", va="center",
             fontsize=15, fontweight="bold", color=C_SA)
    ax1.text(0, -0.15, "KSA", ha="center", va="center",
             fontsize=9, color=C_TEXT)
    patches = [
        mpatches.Patch(color=C_SA,   label=f"Saudi Arabia {pred['prob_sa']}%"),
        mpatches.Patch(color=C_DRAW, label=f"Draw {pred['prob_draw']}%"),
        mpatches.Patch(color=C_UR,   label=f"Uruguay {pred['prob_ur']}%"),
    ]
    ax1.legend(handles=patches, loc="lower center", bbox_to_anchor=(0.5, -0.28),
               fontsize=8, facecolor=C_MID, labelcolor=C_TEXT, framealpha=0.8)
    ax1.set_title("Win Probability", color=C_GOLD, fontsize=11, pad=10)

    # ── شارت 2: النتيجة المتوقعة ───────────────────────
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_facecolor(C_MID)
    ax2.axis("off")
    ax2.text(0.5, 0.85, "Predicted Score", ha="center",
             fontsize=11, color=C_GOLD, transform=ax2.transAxes)
    ax2.text(0.5, 0.52, f"{pred['score_sa']}  -  {pred['score_ur']}",
             ha="center", fontsize=38, fontweight="bold",
             color=C_TEXT, transform=ax2.transAxes)
    ax2.text(0.25, 0.28, "🇸🇦 KSA", ha="center",
             fontsize=11, color=C_SA, transform=ax2.transAxes)
    ax2.text(0.75, 0.28, "URU 🇺🇾", ha="center",
             fontsize=11, color=C_UR, transform=ax2.transAxes)
    winner_map = {
        "sa":   ("Saudi Arabia Wins 🇸🇦", C_SA),
        "draw": ("Draw 🤝",               C_DRAW),
        "ur":   ("Uruguay Wins 🇺🇾",      C_UR),
    }
    wlabel, wcolor = winner_map[pred["winner"]]
    ax2.text(0.5, 0.10, wlabel, ha="center",
             fontsize=10, color=wcolor, fontweight="bold",
             transform=ax2.transAxes)
    ax2.set_title("Final Prediction", color=C_GOLD, fontsize=11, pad=10)

    # ── شارت 3: آخر 10 مباريات (Stacked Bar) ──────────
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.set_facecolor(C_MID)
    teams  = ["Saudi Arabia", "Uruguay"]
    wins   = [wins_sa,   wins_ur]
    draws  = [draws_sa,  draws_ur]
    losses = [losses_sa, losses_ur]
    x = range(len(teams))
    b1 = ax3.bar(x, wins,   color=C_SA,    label="Win",  width=0.5)
    b2 = ax3.bar(x, draws,  bottom=wins,   color=C_DRAW, label="Draw", width=0.5)
    b3 = ax3.bar(x, losses,
                 bottom=[w+d for w,d in zip(wins, draws)],
                 color="#DC2626", label="Loss", width=0.5)
    ax3.set_xticks(list(x))
    ax3.set_xticklabels(teams, color=C_TEXT, fontsize=9)
    ax3.tick_params(colors=C_TEXT)
    ax3.spines[:].set_color("#2D3748")
    ax3.set_title("Last 10 Matches", color=C_GOLD, fontsize=11, pad=10)
    ax3.legend(fontsize=8, facecolor=C_MID, labelcolor=C_TEXT, framealpha=0.8)
    for bar in [b1, b2, b3]:
        for rect in bar:
            h = rect.get_height()
            if h > 0:
                ax3.text(rect.get_x() + rect.get_width()/2,
                         rect.get_y() + h/2, str(int(h)),
                         ha="center", va="center",
                         color="white", fontsize=10, fontweight="bold")

    # ── شارت 4: مقارنة الأهداف ─────────────────────────
    ax4 = fig.add_subplot(gs[1, 0])
    ax4.set_facecolor(C_MID)
    cats = ["Goals Scored", "Goals Conceded"]
    sa_g = [gf_sa, ga_sa]
    ur_g = [gf_ur, ga_ur]
    x4   = range(len(cats))
    w    = 0.35
    ax4.bar([i - w/2 for i in x4], sa_g, width=w, color=C_SA,  label="Saudi Arabia")
    ax4.bar([i + w/2 for i in x4], ur_g, width=w, color=C_UR,  label="Uruguay")
    ax4.set_xticks(list(x4))
    ax4.set_xticklabels(cats, color=C_TEXT, fontsize=9)
    ax4.tick_params(colors=C_TEXT)
    ax4.spines[:].set_color("#2D3748")
    ax4.set_title("Goals Stats (Last 10)", color=C_GOLD, fontsize=11, pad=10)
    ax4.legend(fontsize=8, facecolor=C_MID, labelcolor=C_TEXT, framealpha=0.8)
    for bars in ax4.containers:
        ax4.bar_label(bars, color=C_TEXT, fontsize=9, padding=2)

    # ── شارت 5: التحليل النصي ──────────────────────────
    ax5 = fig.add_subplot(gs[1, 1:])
    ax5.set_facecolor(C_MID)
    ax5.axis("off")
    ax5.text(0.5, 0.95, "AI Analysis", ha="center",
             fontsize=11, color=C_GOLD, transform=ax5.transAxes, fontweight="bold")
    ax5.text(0.5, 0.70, pred["analysis"], ha="center", va="top",
             fontsize=9.5, color=C_TEXT, transform=ax5.transAxes,
             multialignment="center",
             bbox=dict(boxstyle="round,pad=0.5", facecolor="#1E293B", edgecolor="#2D3748"))
    ax5.text(0.5, 0.25, f"Key Factor: {pred['key_factor']}",
             ha="center", va="center", fontsize=9.5, color=C_GOLD,
             transform=ax5.transAxes,
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#1A1A00",
                       edgecolor=C_GOLD, alpha=0.8))

    # ── العنوان الرئيسي ────────────────────────────────
    fig.text(0.5, 0.97, "  FIFA World Cup 2026  |  🇸🇦 Saudi Arabia  vs  Uruguay 🇺🇾",
             ha="center", fontsize=14, fontweight="bold", color=C_GOLD)
    fig.text(0.5, 0.935, "AI-Powered Prediction — Real Data from API-Football",
             ha="center", fontsize=9, color="#7A8BAA")

    # ── حفظ الشارت ────────────────────────────────────
    os.makedirs("outputs", exist_ok=True)
    path = "outputs/prediction_chart.png"
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=C_BG)
    print(f" تم حفظ الشارت: {path}")
    plt.show()

# ─────────────────────────────────────────
# التشغيل الرئيسي
# ─────────────────────────────────────────
if __name__ == "__main__":
    print(" جاري رسم الشارتات...")
    pred     = load_prediction()
    sa, ur   = load_stats()
    sa_stats = extract_stats(sa, 523)
    ur_stats = extract_stats(ur, 26)
    draw_chart(pred, sa_stats, ur_stats)
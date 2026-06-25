import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from collections import defaultdict

# --- Configurazione file ---
FILES = {
    "gemma3":      "benchmark_lookup_gemma3.csv",
    "llama3.2":    "benchmark_lookup_llama3.2.csv",
    "qwen3":       "benchmark_lookup_qwen3.csv",
    "deepseek-r1": "benchmark_lookup_deepseek-r1-distill-llama.csv",
}

COLORI = {
    "gemma3":      "#378ADD",
    "llama3.2":    "#1D9E75",
    "qwen3":       "#F5A623",
    "deepseek-r1": "#E24B4A",
}

# --- Leggi tutti i CSV ---
dati = {}
for nome, filepath in FILES.items():
    righe = list(csv.DictReader(open(filepath)))
    dati[nome] = {
        "latenze":  [float(r["latenza_ms"])       for r in righe],
        "tok_sec":  [float(r["tok_sec"])           for r in righe],
        "cpu":      [float(r["cpu_media"])         for r in righe],
        "ram":      [float(r["ram_media_mb"])      for r in righe],
        "compl":    [float(r["completion_tokens"]) for r in righe],
        "load":     [r["load_level"]               for r in righe],
    }

modelli = list(dati.keys())
colori  = [COLORI[m] for m in modelli]
x       = np.arange(len(modelli))
w       = 0.4

def med(m, k): return round(np.mean(dati[m][k]), 1)
def mn(m, k):  return round(np.min(dati[m][k]),  1)
def mx(m, k):  return round(np.max(dati[m][k]),  1)
def std(m, k): return round(np.std(dati[m][k]),  1)

# --- Figura ---
fig = plt.figure(figsize=(16, 13))
fig.suptitle(
    "Confronto comparativo — 4 modelli LLM su Docker Model Runner\n"
    "27 combinazioni lookup table (load × capacity × legacy_risk) · Server Ubuntu x86-64",
    fontsize=13, fontweight="bold", y=0.99
)
gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.55, wspace=0.38)

# ── 1: Latenza media con barre errore ────────────────────────
ax1 = fig.add_subplot(gs[0, :])
lat_med = [med(m, "latenze") for m in modelli]
lat_std = [std(m, "latenze") for m in modelli]
bars = ax1.bar(modelli, lat_med, color=colori, zorder=3, width=0.5,
               yerr=lat_std, capsize=5, error_kw={"elinewidth": 1.5, "ecolor": "gray"})
for b, v in zip(bars, lat_med):
    ax1.text(b.get_x() + b.get_width()/2, v + max(lat_std)*0.1 + 200,
             f"{v:,.0f} ms", ha="center", fontsize=9, fontweight="bold")
ax1.set_title("Latenza media per combinazione (± std dev)", fontsize=12)
ax1.set_ylabel("ms")
ax1.set_yscale("log")
ax1.set_ylim(500, 100000)
ax1.set_yticks([1000, 2000, 5000, 10000, 20000, 50000])
ax1.get_yaxis().set_major_formatter(plt.ScalarFormatter())
ax1.grid(axis="y", alpha=0.3, zorder=0)
ax1.set_xlabel("")

# Annotazione scala logaritmica
ax1.text(0.98, 0.95, "Scala logaritmica", transform=ax1.transAxes,
         fontsize=8, ha="right", va="top", color="gray", style="italic")

# ── 2: Throughput (tok/s) ────────────────────────────────────
ax2 = fig.add_subplot(gs[1, 0])
tok_med = [med(m, "tok_sec") for m in modelli]
bars2 = ax2.bar(modelli, tok_med, color=colori, zorder=3, width=0.5)
for b, v in zip(bars2, tok_med):
    ax2.text(b.get_x() + b.get_width()/2, v + 0.3, f"{v}", ha="center", fontsize=8)
ax2.set_title("Throughput medio (tok/s)", fontsize=11)
ax2.set_ylabel("tok/s")
ax2.set_xticklabels(modelli, rotation=15, ha="right", fontsize=8)
ax2.grid(axis="y", alpha=0.3, zorder=0)

# ── 3: CPU media ─────────────────────────────────────────────
ax3 = fig.add_subplot(gs[1, 1])
cpu_med = [med(m, "cpu") for m in modelli]
cpu_mx  = [mx(m,  "cpu") for m in modelli]
xi = np.arange(len(modelli))
ax3.bar(xi - w/2, cpu_med, width=w, color=colori, label="CPU media %", zorder=3)
ax3.bar(xi + w/2, cpu_mx,  width=w, color=[c + "88" for c in colori],
        label="CPU max %", zorder=3, edgecolor=colori, linewidth=1)
for i, (m, mx_) in enumerate(zip(cpu_med, cpu_mx)):
    ax3.text(i - w/2, m + 0.3, f"{m}", ha="center", fontsize=7)
    ax3.text(i + w/2, mx_ + 0.3, f"{mx_}", ha="center", fontsize=7)
ax3.set_title("CPU media e max (%)", fontsize=11)
ax3.set_ylabel("%")
ax3.set_xticks(xi)
ax3.set_xticklabels(modelli, rotation=15, ha="right", fontsize=8)
ax3.legend(fontsize=8)
ax3.grid(axis="y", alpha=0.3, zorder=0)

# ── 4: RAM media ─────────────────────────────────────────────
ax4 = fig.add_subplot(gs[1, 2])
ram_med = [med(m, "ram") for m in modelli]
ram_mx  = [mx(m,  "ram") for m in modelli]
ax4.plot(modelli, ram_med, marker="o", color="#378ADD", linewidth=2,
         markersize=8, label="RAM media", zorder=3)
ax4.plot(modelli, ram_mx,  marker="s", color="#E24B4A", linewidth=1.5,
         linestyle="--", markersize=6, label="RAM max", zorder=3)
ax4.fill_between(range(len(modelli)), ram_med, ram_mx, alpha=0.1, color="#378ADD")
for i, (m, r) in enumerate(zip(modelli, ram_med)):
    ax4.annotate(f"{r:.0f}", xy=(i, r), xytext=(0, 8),
                 textcoords="offset points", ha="center", fontsize=8)
ax4.set_title("RAM media e max (MB)", fontsize=11)
ax4.set_ylabel("MB")
ax4.set_xticks(range(len(modelli)))
ax4.set_xticklabels(modelli, rotation=15, ha="right", fontsize=8)
ax4.legend(fontsize=8)
ax4.grid(alpha=0.3)

# ── 5: Completion tokens medi ────────────────────────────────
ax5 = fig.add_subplot(gs[2, 0])
compl_med = [med(m, "compl") for m in modelli]
compl_mx  = [mx(m,  "compl") for m in modelli]
bars5 = ax5.bar(modelli, compl_med, color=colori, zorder=3, width=0.5)
for b, v in zip(bars5, compl_med):
    ax5.text(b.get_x() + b.get_width()/2, v + 3, f"{v}", ha="center", fontsize=8)
ax5.set_title("Completion tokens medi\n(lunghezza risposta)", fontsize=11)
ax5.set_ylabel("token")
ax5.set_xticklabels(modelli, rotation=15, ha="right", fontsize=8)
ax5.grid(axis="y", alpha=0.3, zorder=0)

# ── 6: Scatter latenza vs tok/s ──────────────────────────────
ax6 = fig.add_subplot(gs[2, 1])
for m in modelli:
    ax6.scatter(med(m, "latenze"), med(m, "tok_sec"),
                color=COLORI[m], s=150, zorder=3,
                edgecolors="gray", linewidths=0.7, label=m)
    ax6.annotate(f"  {m}",
                 xy=(med(m, "latenze"), med(m, "tok_sec")),
                 fontsize=8)
ax6.set_xlabel("Latenza media (ms)", fontsize=10)
ax6.set_ylabel("Tok/s media", fontsize=10)
ax6.set_title("Latenza vs Throughput", fontsize=11)
ax6.set_xscale("log")
ax6.legend(fontsize=8)
ax6.grid(alpha=0.3)

# ── 7: Tabella riepilogo ─────────────────────────────────────
ax7 = fig.add_subplot(gs[2, 2])
ax7.axis("off")
intestazioni = ["Modello", "Lat.\nmed (ms)", "Tok/s", "CPU\n(%)", "RAM\n(MB)", "Compl.\ntok"]
righe_tab = []
for m in modelli:
    righe_tab.append([
        m,
        f"{med(m,'latenze'):,.0f}",
        str(med(m, "tok_sec")),
        str(med(m, "cpu")),
        f"{med(m,'ram'):.0f}",
        str(med(m, "compl")),
    ])
tab = ax7.table(cellText=righe_tab, colLabels=intestazioni,
                loc="center", cellLoc="center")
tab.auto_set_font_size(False)
tab.set_fontsize(8)
tab.scale(1, 1.9)
for (r, c), cell in tab.get_celld().items():
    if r == 0:
        cell.set_facecolor("#1A3A5C")
        cell.set_text_props(color="white", fontweight="bold")
    else:
        m = modelli[r - 1]
        cell.set_facecolor(COLORI[m] + "22")
    cell.set_edgecolor("#CCCCCC")
ax7.set_title("Riepilogo comparativo", fontsize=10, pad=12)

plt.savefig("confronto_4_modelli.png", dpi=150, bbox_inches="tight")
print("Grafico salvato: confronto_4_modelli.png")

# --- Stampa riepilogo testuale ---
print("\n" + "="*65)
print(f"{'Modello':<14} | {'Lat. med':>9} | {'Tok/s':>6} | {'CPU%':>6} | {'RAM MB':>7} | {'Compl.tok':>10}")
print("-"*65)
for m in modelli:
    print(f"{m:<14} | {med(m,'latenze'):>9,.0f} | {med(m,'tok_sec'):>6} | "
          f"{med(m,'cpu'):>6} | {med(m,'ram'):>7.0f} | {med(m,'compl'):>10}")

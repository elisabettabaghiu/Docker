import csv
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from collections import defaultdict

INPUT_CSV  = "benchmark_lookup_deepseek-r1-distill-llama.csv" # cambia nome LLM
INPUT_JSON = "lookup_table_deepseek-r1-distill-llama.json" # cambia nome LLM


# --- Leggi CSV ---
righe = []
with open(INPUT_CSV, newline="") as f:
    for r in csv.DictReader(f):
        righe.append(r)

latenze  = [float(r["latenza_ms"])    for r in righe]
tok_secs = [float(r["tok_sec"])       for r in righe]
cpu      = [float(r["cpu_media"])     for r in righe]
ram      = [float(r["ram_media_mb"])  for r in righe]
compl    = [float(r["completion_tokens"]) for r in righe]
labels   = [f"{r['load_level'][0].upper()}-{r['capacity_level'][0].upper()}-{r['legacy_risk'][0].upper()}"
            for r in righe]
idx      = list(range(1, len(righe)+1))

# Raggruppa per load_level
gruppi = defaultdict(list)
for r in righe:
    gruppi[r["load_level"]].append(float(r["latenza_ms"]))

c_blu   = "#378ADD"
c_verde = "#1D9E75"
c_rosso = "#E24B4A"
c_amber = "#F5A623"

fig = plt.figure(figsize=(16, 12))
fig.suptitle("Lookup Table — deepseek-r1-distill-llama:latest\n" # cambia nome LLM
             "27 combinazioni (load × capacity × legacy_risk) · Docker Model Runner",
             fontsize=13, fontweight="bold", y=0.99)
gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.55, wspace=0.38)

# ── 1: Latenza per ogni combinazione ─────────────────────────
ax1 = fig.add_subplot(gs[0, :])
colori_barre = []
for r in righe:
    if r["load_level"] == "low":      colori_barre.append(c_verde)
    elif r["load_level"] == "medium": colori_barre.append(c_amber)
    else:                             colori_barre.append(c_rosso)
ax1.bar(idx, latenze, color=colori_barre, zorder=3, width=0.7)
ax1.axhline(np.mean(latenze), color="gray", linestyle="--", linewidth=1,
            label=f"Media {round(np.mean(latenze),0):.0f} ms")
ax1.set_xlabel("Combinazione (#)")
ax1.set_ylabel("Latenza (ms)")
ax1.set_title("Latenza per combinazione  (verde=load:low · arancio=load:medium · rosso=load:high)")
ax1.set_xticks(idx)
ax1.set_xticklabels(labels, rotation=90, fontsize=6.5)
ax1.legend(fontsize=9)
ax1.grid(axis="y", alpha=0.3, zorder=0)

# ── 2: Latenza media per load_level ──────────────────────────
ax2 = fig.add_subplot(gs[1, 0])
livelli = ["low", "medium", "high"]
medie_load = [round(np.mean(gruppi[l]), 1) for l in livelli]
ax2.bar(livelli, medie_load, color=[c_verde, c_amber, c_rosso], zorder=3, width=0.5)
for i, v in enumerate(medie_load):
    ax2.text(i, v + 10, str(v), ha="center", fontsize=9)
ax2.set_title("Latenza media\nper load_level")
ax2.set_ylabel("ms")
ax2.grid(axis="y", alpha=0.3, zorder=0)

# ── 3: Token per secondo ──────────────────────────────────────
ax3 = fig.add_subplot(gs[1, 1])
ax3.plot(idx, tok_secs, color=c_blu, linewidth=1.5, marker="o", markersize=3, zorder=3)
ax3.axhline(np.mean(tok_secs), color="gray", linestyle="--", linewidth=1,
            label=f"Media {round(np.mean(tok_secs),1)} tok/s")
ax3.set_title("Throughput (tok/s)")
ax3.set_xlabel("Combinazione (#)")
ax3.set_ylabel("tok/s")
ax3.legend(fontsize=8)
ax3.grid(alpha=0.3, zorder=0)

# ── 4: CPU per combinazione ───────────────────────────────────
ax4 = fig.add_subplot(gs[1, 2])
colori_cpu = [c_rosso if c > 30 else c_amber if c > 10 else c_verde for c in cpu]
ax4.bar(idx, cpu, color=colori_cpu, zorder=3, width=0.7)
ax4.set_title("CPU media % per combinazione")
ax4.set_xlabel("Combinazione (#)")
ax4.set_ylabel("CPU %")
ax4.set_xticks(idx[::3])
ax4.grid(axis="y", alpha=0.3, zorder=0)

# ── 5: RAM ────────────────────────────────────────────────────
ax5 = fig.add_subplot(gs[2, 0])
ax5.plot(idx, ram, color=c_verde, linewidth=1.5, marker="s", markersize=3, zorder=3)
ax5.axhline(np.mean(ram), color="gray", linestyle="--", linewidth=1,
            label=f"Media {round(np.mean(ram),0):.0f} MB")
ax5.set_title("RAM media (MB)")
ax5.set_xlabel("Combinazione (#)")
ax5.set_ylabel("MB")
ax5.legend(fontsize=8)
ax5.grid(alpha=0.3, zorder=0)

# ── 6: Completion tokens per combinazione ────────────────────
ax6 = fig.add_subplot(gs[2, 1])
ax6.bar(idx, compl, color=c_blu, zorder=3, width=0.7, alpha=0.8)
ax6.axhline(np.mean(compl), color="gray", linestyle="--", linewidth=1,
            label=f"Media {round(np.mean(compl),1)}")
ax6.set_title("Completion tokens per combinazione")
ax6.set_xlabel("Combinazione (#)")
ax6.set_ylabel("token")
ax6.legend(fontsize=8)
ax6.grid(axis="y", alpha=0.3, zorder=0)

# ── 7: Tabella riepilogo statistiche ─────────────────────────
ax7 = fig.add_subplot(gs[2, 2])
ax7.axis("off")
dati_tab = [
    ["Metrica",           "Min",    "Media",  "Max"],
    ["Latenza (ms)",      str(round(np.min(latenze),0)),
                          str(round(np.mean(latenze),0)),
                          str(round(np.max(latenze),0))],
    ["Tok/s",             str(round(np.min(tok_secs),1)),
                          str(round(np.mean(tok_secs),1)),
                          str(round(np.max(tok_secs),1))],
    ["CPU media (%)",     str(round(np.min(cpu),1)),
                          str(round(np.mean(cpu),1)),
                          str(round(np.max(cpu),1))],
    ["RAM (MB)",          str(round(np.min(ram),0)),
                          str(round(np.mean(ram),0)),
                          str(round(np.max(ram),0))],
    ["Compl. tokens",     str(round(np.min(compl),0)),
                          str(round(np.mean(compl),1)),
                          str(round(np.max(compl),0))],
]
tab = ax7.table(cellText=dati_tab[1:], colLabels=dati_tab[0],
                loc="center", cellLoc="center")
tab.auto_set_font_size(False)
tab.set_fontsize(9)
tab.scale(1, 1.8)
for (r, c), cell in tab.get_celld().items():
    if r == 0:
        cell.set_facecolor("#1A3A5C")
        cell.set_text_props(color="white", fontweight="bold")
    elif r % 2 == 0:
        cell.set_facecolor("#F4F6F8")
    cell.set_edgecolor("#CCCCCC")
ax7.set_title("Statistiche globali", fontsize=10, pad=12)
 
plt.savefig("grafici_lookup_deepseek-r1-distill-llama.png", dpi=150, bbox_inches="tight") # cambia nome LLM
print("Grafico salvato: grafici_lookup_deepseek-r1-distill-llama.png") # cambia nome LLM

# --- Stampa riepilogo testo ---
print("\nStatistiche deepseek-r1-distill-llama — 27 combinazioni:")
print(f"  Latenza:   min {round(np.min(latenze),0):.0f} ms | "
      f"media {round(np.mean(latenze),0):.0f} ms | "
      f"max {round(np.max(latenze),0):.0f} ms")
print(f"  Tok/s:     min {round(np.min(tok_secs),1)} | "
      f"media {round(np.mean(tok_secs),1)} | "
      f"max {round(np.max(tok_secs),1)}")
print(f"  CPU:       min {round(np.min(cpu),1)}% | "
      f"media {round(np.mean(cpu),1)}% | "
      f"max {round(np.max(cpu),1)}%")
print(f"  RAM:       min {round(np.min(ram),0):.0f} MB | "
      f"media {round(np.mean(ram),0):.0f} MB | "
      f"max {round(np.max(ram),0):.0f} MB")
print(f"  Compl.tok: min {round(np.min(compl),0):.0f} | "
      f"media {round(np.mean(compl),1)} | "
      f"max {round(np.max(compl),0):.0f}")

import csv
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

# --- Leggi CSV ---
richieste = []
latenze = []
tok_sec = []
completion_tokens = []

with open("risultati.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        richieste.append(int(row["richiesta"]))
        latenze.append(float(row["latenza_totale_ms"]))
        tok_sec.append(float(row["token_per_secondo"]))
        completion_tokens.append(int(row["completion_tokens"]))

# --- Calcola statistiche (escludendo cold start) ---
latenze_warm = latenze[1:]
media = round(np.mean(latenze_warm), 1)
mediana = round(np.median(latenze_warm), 1)
minimo = round(np.min(latenze_warm), 1)
massimo = round(np.max(latenze_warm), 1)
tok_media = round(np.mean(tok_sec[1:]), 1)

# --- Figura con 3 grafici ---
fig = plt.figure(figsize=(12, 9))
fig.suptitle("Docker Model Runner — Benchmark ai/smollm2\nApple Silicon ARM64",
             fontsize=14, fontweight="bold", y=0.98)

gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)

colore_main = "#378ADD"
colore_cold = "#E24B4A"
colore_warm = "#1D9E75"

# ---- Grafico 1: Latenza per richiesta ----
ax1 = fig.add_subplot(gs[0, :])
colori_barre = [colore_cold] + [colore_main] * (len(richieste) - 1)
barre = ax1.bar(richieste, latenze, color=colori_barre, width=0.6, zorder=3)
ax1.axhline(media, color=colore_warm, linestyle="--", linewidth=1.2,
            label=f"Media warm ({media} ms)")
ax1.set_xlabel("Numero richiesta", fontsize=11)
ax1.set_ylabel("Latenza (ms)", fontsize=11)
ax1.set_title("Latenza per richiesta", fontsize=12)
ax1.set_xticks(richieste)
ax1.grid(axis="y", alpha=0.3, zorder=0)
ax1.legend(fontsize=10)

# Etichetta cold start
ax1.annotate("cold start",
             xy=(1, latenze[0]),
             xytext=(1.6, latenze[0] * 0.92),
             fontsize=9, color=colore_cold,
             arrowprops=dict(arrowstyle="->", color=colore_cold, lw=1))

# ---- Grafico 2: Token/secondo ----
ax2 = fig.add_subplot(gs[1, 0])
ax2.plot(richieste, tok_sec, marker="o", color=colore_main,
         linewidth=1.5, markersize=5, zorder=3)
ax2.plot(richieste[0], tok_sec[0], marker="o", color=colore_cold,
         markersize=7, zorder=4)
ax2.axhline(tok_media, color=colore_warm, linestyle="--", linewidth=1.2,
            label=f"Media warm ({tok_media} tok/s)")
ax2.set_xlabel("Numero richiesta", fontsize=11)
ax2.set_ylabel("Token / secondo", fontsize=11)
ax2.set_title("Throughput di inferenza", fontsize=12)
ax2.set_xticks(richieste)
ax2.grid(alpha=0.3, zorder=0)
ax2.legend(fontsize=10)

# ---- Grafico 3: Box plot latenza warm ----
ax3 = fig.add_subplot(gs[1, 1])
bp = ax3.boxplot(latenze_warm, patch_artist=True, widths=0.5,
                 medianprops=dict(color=colore_warm, linewidth=2))
bp["boxes"][0].set_facecolor(colore_main)
bp["boxes"][0].set_alpha(0.6)
ax3.set_ylabel("Latenza (ms)", fontsize=11)
ax3.set_title("Distribuzione latenza\n(warm, richieste 2–10)", fontsize=12)
ax3.set_xticks([1])
ax3.set_xticklabels(["ai/smollm2"])
ax3.grid(axis="y", alpha=0.3)

# Annotazioni statistiche
stats_text = f"min: {minimo} ms\nmax: {massimo} ms\nmediana: {mediana} ms\nmedia: {media} ms"
ax3.text(1.35, np.median(latenze_warm), stats_text,
         fontsize=9, va="center",
         color="#444441")

plt.savefig("benchmark_grafici.png", dpi=150, bbox_inches="tight")
print("Grafico salvato: benchmark_grafici.png")
print(f"\nStatistiche warm (richieste 2-10):")
print(f"  Media latenza:  {media} ms")
print(f"  Mediana:        {mediana} ms")
print(f"  Min:            {minimo} ms")
print(f"  Max:            {massimo} ms")
print(f"  Media tok/s:    {tok_media} tok/s")

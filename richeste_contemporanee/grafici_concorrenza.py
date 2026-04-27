import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# --- Leggi CSV ---
dati = {}
with open("risultati_concorrenza.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        n = int(row["concorrenza"])
        if n not in dati:
            dati[n] = {"lat_media": [], "lat_max": [], "tok": []}
        dati[n]["lat_media"].append(float(row["latenza_media_ms"]))
        dati[n]["lat_max"].append(float(row["latenza_max_ms"]))
        dati[n]["tok"].append(float(row["tok_sec_media"]))

livelli = sorted(dati.keys())
lat_medie = [round(np.mean(dati[n]["lat_media"]), 1) for n in livelli]
lat_max   = [round(np.mean(dati[n]["lat_max"]), 1) for n in livelli]
lat_std   = [round(np.std(dati[n]["lat_media"]), 1) for n in livelli]
tok_medie = [round(np.mean(dati[n]["tok"]), 1) for n in livelli]

colore_main  = "#378ADD"
colore_max   = "#E24B4A"
colore_tok   = "#1D9E75"

fig = plt.figure(figsize=(12, 8))
fig.suptitle("Docker Model Runner — Scalabilità al variare della concorrenza\nai/smollm2 · Apple Silicon ARM64",
             fontsize=13, fontweight="bold", y=0.98)

gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)

# ---- Grafico 1: Latenza media con barre errore ----
ax1 = fig.add_subplot(gs[0, :])
ax1.plot(livelli, lat_medie, marker="o", color=colore_main,
         linewidth=2, markersize=7, label="Latenza media", zorder=3)
ax1.fill_between(livelli,
                 [m - s for m, s in zip(lat_medie, lat_std)],
                 [m + s for m, s in zip(lat_medie, lat_std)],
                 alpha=0.15, color=colore_main, label="±1 std dev")
ax1.plot(livelli, lat_max, marker="s", color=colore_max,
         linewidth=1.5, linestyle="--", markersize=6,
         label="Latenza max (worst case)", zorder=3)
for x, y in zip(livelli, lat_medie):
    ax1.annotate(f"{y} ms", xy=(x, y), xytext=(0, 10),
                 textcoords="offset points", ha="center", fontsize=9)
ax1.set_xlabel("Richieste concorrenti", fontsize=11)
ax1.set_ylabel("Latenza (ms)", fontsize=11)
ax1.set_title("Latenza al variare della concorrenza", fontsize=12)
ax1.set_xticks(livelli)
ax1.legend(fontsize=10)
ax1.grid(alpha=0.3)

# ---- Grafico 2: Throughput tok/s ----
ax2 = fig.add_subplot(gs[1, 0])
ax2.bar(livelli, tok_medie, color=colore_tok, width=0.5, zorder=3)
for x, y in zip(livelli, tok_medie):
    ax2.text(x, y + 1, f"{y}", ha="center", fontsize=9)
ax2.set_xlabel("Richieste concorrenti", fontsize=11)
ax2.set_ylabel("Token / secondo", fontsize=11)
ax2.set_title("Throughput medio", fontsize=12)
ax2.set_xticks(livelli)
ax2.grid(axis="y", alpha=0.3, zorder=0)

# ---- Grafico 3: Degradazione relativa ----
ax3 = fig.add_subplot(gs[1, 1])
degradazione = [round(l / lat_medie[0], 2) for l in lat_medie]
colori = [colore_main if d < 1.5 else colore_max for d in degradazione]
ax3.bar(livelli, degradazione, color=colori, width=0.5, zorder=3)
ax3.axhline(1.0, color="gray", linestyle="--", linewidth=1)
for x, y in zip(livelli, degradazione):
    ax3.text(x, y + 0.02, f"{y}x", ha="center", fontsize=9)
ax3.set_xlabel("Richieste concorrenti", fontsize=11)
ax3.set_ylabel("Fattore di degradazione", fontsize=11)
ax3.set_title("Degradazione rispetto a 1 richiesta", fontsize=12)
ax3.set_xticks(livelli)
ax3.grid(axis="y", alpha=0.3, zorder=0)

plt.savefig("benchmark_concorrenza_grafici.png", dpi=150, bbox_inches="tight")
print("Grafico salvato: benchmark_concorrenza_grafici.png")

print("\nRiepilogo:")
print(f"{'Concorrenza':>12} | {'Lat. media':>10} | {'Lat. max':>10} | {'Tok/s':>8} | {'Degrado':>8}")
print("-" * 58)
for i, n in enumerate(livelli):
    print(f"{n:>12} | {lat_medie[i]:>10} | {lat_max[i]:>10} | "
          f"{tok_medie[i]:>8} | {degradazione[i]:>7}x")

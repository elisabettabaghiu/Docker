import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# Leggi CSV
dati = {}
with open("risultati_risorse.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        n = int(row["concorrenza"])
        if n not in dati:
            dati[n] = {"lat": [], "cpu": [], "cpu_max": [], "ram": [], "ram_max": []}
        dati[n]["lat"].append(float(row["latenza_media_ms"]))
        dati[n]["cpu"].append(float(row["cpu_media_percent"]))
        dati[n]["cpu_max"].append(float(row["cpu_max_percent"]))
        dati[n]["ram"].append(float(row["ram_media_mb"]))
        dati[n]["ram_max"].append(float(row["ram_max_mb"]))

livelli    = sorted(dati.keys())
lat_medie  = [round(np.mean(dati[n]["lat"]), 1) for n in livelli]
cpu_medie  = [round(np.mean(dati[n]["cpu"]), 1) for n in livelli]
cpu_max    = [round(np.mean(dati[n]["cpu_max"]), 1) for n in livelli]
ram_medie  = [round(np.mean(dati[n]["ram"]), 1) for n in livelli]
ram_max    = [round(np.mean(dati[n]["ram_max"]), 1) for n in livelli]

c_blue   = "#378ADD"
c_red    = "#E24B4A"
c_green  = "#1D9E75"
c_amber  = "#F5A623"

fig = plt.figure(figsize=(12, 9))
fig.suptitle("Docker Model Runner — CPU e RAM al variare della concorrenza\nai/smollm2 · Apple Silicon ARM64",
             fontsize=13, fontweight="bold", y=0.98)
gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)

# Grafico 1: CPU media e max
ax1 = fig.add_subplot(gs[0, 0])
x = np.arange(len(livelli))
w = 0.35
ax1.bar(x - w/2, cpu_medie, width=w, color=c_blue, label="CPU media %", zorder=3)
ax1.bar(x + w/2, cpu_max,   width=w, color=c_red,  label="CPU max %",   zorder=3)
for i, (m, mx) in enumerate(zip(cpu_medie, cpu_max)):
    ax1.text(i - w/2, m + 0.5, f"{m}%", ha="center", fontsize=8)
    ax1.text(i + w/2, mx + 0.5, f"{mx}%", ha="center", fontsize=8)
ax1.set_xticks(x)
ax1.set_xticklabels(livelli)
ax1.set_xlabel("Richieste concorrenti", fontsize=11)
ax1.set_ylabel("CPU %", fontsize=11)
ax1.set_title("Utilizzo CPU", fontsize=12)
ax1.legend(fontsize=9)
ax1.grid(axis="y", alpha=0.3, zorder=0)

# Grafico 2: RAM media e max
ax2 = fig.add_subplot(gs[0, 1])
ax2.plot(livelli, ram_medie, marker="o", color=c_green,
         linewidth=2, markersize=7, label="RAM media", zorder=3)
ax2.plot(livelli, ram_max, marker="s", color=c_amber,
         linewidth=1.5, linestyle="--", markersize=6, label="RAM max", zorder=3)
ax2.fill_between(livelli, ram_medie, ram_max, alpha=0.1, color=c_green)
for x_val, y_val in zip(livelli, ram_medie):
    ax2.annotate(f"{y_val}", xy=(x_val, y_val), xytext=(0, 8),
                 textcoords="offset points", ha="center", fontsize=8)
ax2.set_xlabel("Richieste concorrenti", fontsize=11)
ax2.set_ylabel("RAM (MB)", fontsize=11)
ax2.set_title("Utilizzo RAM", fontsize=12)
ax2.set_xticks(livelli)
ax2.legend(fontsize=9)
ax2.grid(alpha=0.3)

# Grafico 3: Latenza vs CPU (scatter)
ax3 = fig.add_subplot(gs[1, 0])
sc = ax3.scatter(cpu_medie, lat_medie, c=livelli, cmap="Blues",
                 s=120, zorder=3, edgecolors="gray", linewidths=0.5)
for i, n in enumerate(livelli):
    ax3.annotate(f"  n={n}", xy=(cpu_medie[i], lat_medie[i]), fontsize=9)
ax3.set_xlabel("CPU media %", fontsize=11)
ax3.set_ylabel("Latenza media (ms)", fontsize=11)
ax3.set_title("Latenza vs CPU", fontsize=12)
ax3.grid(alpha=0.3)

# Grafico 4: Latenza vs RAM (scatter)
ax4 = fig.add_subplot(gs[1, 1])
ax4.scatter(ram_medie, lat_medie, c=livelli, cmap="Greens",
            s=120, zorder=3, edgecolors="gray", linewidths=0.5)
for i, n in enumerate(livelli):
    ax4.annotate(f"  n={n}", xy=(ram_medie[i], lat_medie[i]), fontsize=9)
ax4.set_xlabel("RAM media (MB)", fontsize=11)
ax4.set_ylabel("Latenza media (ms)", fontsize=11)
ax4.set_title("Latenza vs RAM", fontsize=12)
ax4.grid(alpha=0.3)

plt.savefig("benchmark_risorse_grafici.png", dpi=150, bbox_inches="tight")
print("Grafico salvato: benchmark_risorse_grafici.png")

print("\nRiepilogo risorse:")
print(f"{'Conc.':>6} | {'Lat. ms':>8} | {'CPU %':>6} | {'CPU max':>8} | {'RAM MB':>8} | {'RAM max':>8}")
print("-" * 58)
for i, n in enumerate(livelli):
    print(f"{n:>6} | {lat_medie[i]:>8} | {cpu_medie[i]:>6} | "
          f"{cpu_max[i]:>8} | {ram_medie[i]:>8} | {ram_max[i]:>8}")

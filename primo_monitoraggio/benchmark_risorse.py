import requests
import csv
import time
import threading
import psutil
import numpy as np
from datetime import datetime

# --- Configurazione ---
URL = "http://localhost:12434/engines/llama.cpp/v1/chat/completions"
MODEL = "ai/smollm2"
DOMANDA = "What is Docker in one sentence?"
LIVELLI_CONCORRENZA = [1, 2, 4, 8]
RIPETIZIONI = 3
OUTPUT_CSV = "risultati_risorse.csv"
CAMPIONAMENTO_SEC = 0.5  # ogni quanti secondi campionare CPU/RAM

# --- Variabili condivise tra thread ---
monitoraggio_attivo = False
campioni_cpu = []
campioni_ram = []

# --- Thread di monitoraggio risorse ---
def monitor_risorse():
    """Campiona CPU e RAM finché monitoraggio_attivo è True."""
    while monitoraggio_attivo:
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory()
        campioni_cpu.append(cpu)
        campioni_ram.append(ram.used / (1024 ** 2))  # in MB
        time.sleep(CAMPIONAMENTO_SEC)

# --- Funzione singola richiesta ---
def fai_richiesta(risultati, indice):
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": DOMANDA}]
    }
    inizio = time.time()
    try:
        risposta = requests.post(URL, json=payload, timeout=60)
        fine = time.time()
        dati = risposta.json()
        latenza = round((fine - inizio) * 1000, 2)
        tok_sec = round(dati.get("timings", {}).get("predicted_per_second", 0), 2)
        completion_tokens = dati["usage"].get("completion_tokens", 0)
        risultati[indice] = (latenza, tok_sec, completion_tokens)
    except Exception as e:
        fine = time.time()
        risultati[indice] = (round((fine - inizio) * 1000, 2), 0, 0)
        print(f"  [errore]: {e}")

# --- CSV header ---
with open(OUTPUT_CSV, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "concorrenza",
        "ripetizione",
        "latenza_media_ms",
        "latenza_max_ms",
        "tok_sec_media",
        "cpu_media_percent",
        "cpu_max_percent",
        "ram_media_mb",
        "ram_max_mb",
        "n_campioni"
    ])

print(f"Benchmark risorse — modello: {MODEL}")
print(f"Livelli: {LIVELLI_CONCORRENZA} | Ripetizioni: {RIPETIZIONI}")
print(f"Campionamento risorse ogni {CAMPIONAMENTO_SEC}s")
print("=" * 70)

# RAM baseline (prima di qualsiasi richiesta)
ram_baseline = psutil.virtual_memory().used / (1024 ** 2)
print(f"RAM baseline sistema: {round(ram_baseline)} MB\n")

# --- Loop principale ---
for n in LIVELLI_CONCORRENZA:
    print(f"[ Concorrenza: {n} ]")

    for r in range(1, RIPETIZIONI + 1):
        # Reset campioni
        campioni_cpu.clear()
        campioni_ram.clear()

        # Avvia monitor in background
        monitoraggio_attivo = True
        monitor_thread = threading.Thread(target=monitor_risorse, daemon=True)
        monitor_thread.start()

        # Avvia richieste parallele
        risultati = [None] * n
        threads = [threading.Thread(target=fai_richiesta, args=(risultati, i))
                   for i in range(n)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Ferma monitor
        monitoraggio_attivo = False
        monitor_thread.join(timeout=2)

        # Calcola metriche latenza
        latenze = [res[0] for res in risultati if res]
        tok_secs = [res[1] for res in risultati if res and res[1] > 0]
        lat_media = round(np.mean(latenze), 1)
        lat_max = round(np.max(latenze), 1)
        tok_media = round(np.mean(tok_secs), 1) if tok_secs else 0

        # Calcola metriche risorse
        cpu_media = round(np.mean(campioni_cpu), 1) if campioni_cpu else 0
        cpu_max = round(np.max(campioni_cpu), 1) if campioni_cpu else 0
        ram_media = round(np.mean(campioni_ram), 1) if campioni_ram else 0
        ram_max = round(np.max(campioni_ram), 1) if campioni_ram else 0
        n_campioni = len(campioni_cpu)

        print(f"  rep {r}/{RIPETIZIONI} | "
              f"lat: {lat_media} ms | "
              f"CPU: {cpu_media}% (max {cpu_max}%) | "
              f"RAM: {ram_media} MB (max {ram_max} MB)")

        # Salva su CSV
        with open(OUTPUT_CSV, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([n, r, lat_media, lat_max, tok_media,
                             cpu_media, cpu_max, ram_media, ram_max, n_campioni])

        time.sleep(1.5)

print("\n" + "=" * 70)
print(f"Completato. Risultati in: {OUTPUT_CSV}")

# --- Riepilogo ---
print("\nRiepilogo per livello di concorrenza:")
print(f"{'Conc.':>6} | {'Lat. ms':>8} | {'CPU %':>6} | {'CPU max':>8} | {'RAM MB':>8} | {'RAM max':>8}")
print("-" * 58)

import csv as csv_mod
riepilogo = {}
with open(OUTPUT_CSV, newline="") as f:
    reader = csv_mod.DictReader(f)
    for row in reader:
        n = int(row["concorrenza"])
        if n not in riepilogo:
            riepilogo[n] = {"lat": [], "cpu": [], "cpu_max": [], "ram": [], "ram_max": []}
        riepilogo[n]["lat"].append(float(row["latenza_media_ms"]))
        riepilogo[n]["cpu"].append(float(row["cpu_media_percent"]))
        riepilogo[n]["cpu_max"].append(float(row["cpu_max_percent"]))
        riepilogo[n]["ram"].append(float(row["ram_media_mb"]))
        riepilogo[n]["ram_max"].append(float(row["ram_max_mb"]))

for n, d in sorted(riepilogo.items()):
    print(f"{n:>6} | {round(np.mean(d['lat']), 1):>8} | "
          f"{round(np.mean(d['cpu']), 1):>6} | "
          f"{round(np.mean(d['cpu_max']), 1):>8} | "
          f"{round(np.mean(d['ram']), 1):>8} | "
          f"{round(np.mean(d['ram_max']), 1):>8}")

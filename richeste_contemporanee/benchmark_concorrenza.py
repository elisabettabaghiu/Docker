import requests
import csv
import time
import threading
import numpy as np

# Configurazione
URL = "http://localhost:12434/engines/llama.cpp/v1/chat/completions"
MODEL = "ai/smollm2"
DOMANDA = "What is Docker in one sentence?"
LIVELLI_CONCORRENZA = [1, 2, 4, 8]   # N richieste simultanee per ogni test
RIPETIZIONI = 5                        # quante volte ripetiamo ogni livello
OUTPUT_CSV = "risultati_concorrenza.csv"

# Funzione singola richiesta 
# la funzione manda richiesta HTTP al modello, misura tempo di esecuzione e salva latenza e token
def fai_richiesta(risultati, indice):
    """Esegue una richiesta e salva latenza e tok/s nella lista risultati."""
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
        print(f"  [errore richiesta {indice}]: {e}")

# CSV header 
with open(OUTPUT_CSV, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "concorrenza",
        "ripetizione",
        "latenza_media_ms",
        "latenza_max_ms",
        "latenza_min_ms",
        "tok_sec_media",
        "completion_tokens_media"
    ])

print(f"Benchmark concorrenza — modello: {MODEL}")
print(f"Livelli testati: {LIVELLI_CONCORRENZA} richieste simultanee")
print(f"Ripetizioni per livello: {RIPETIZIONI}")
print("=" * 65)

#  Loop principale 
for n in LIVELLI_CONCORRENZA:
    print(f"\n[ Concorrenza: {n} richiesta/e simultanea/e ]")

    for r in range(1, RIPETIZIONI + 1):
        # Prepara strutture
        risultati = [None] * n
        threads = []

        # Avvia tutti i thread insieme
        for i in range(n):
            # ogmi richiesta è un thread, tutti partono insieme
            t = threading.Thread(target=fai_richiesta, args=(risultati, i))
            threads.append(t)

        inizio_batch = time.time()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        fine_batch = time.time()

        # Calcola statistiche del batch
        latenze = [r[0] for r in risultati if r]
        tok_secs = [r[1] for r in risultati if r and r[1] > 0]
        tokens = [r[2] for r in risultati if r]

        lat_media = round(np.mean(latenze), 1)
        lat_max = round(np.max(latenze), 1)
        lat_min = round(np.min(latenze), 1)
        tok_media = round(np.mean(tok_secs), 1) if tok_secs else 0
        tok_completion = round(np.mean(tokens), 1)

        print(f"  rep {r}/{RIPETIZIONI} | "
              f"lat media: {lat_media} ms | "
              f"lat max: {lat_max} ms | "
              f"{tok_media} tok/s")

        # Salva su CSV
        with open(OUTPUT_CSV, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([n, r, lat_media, lat_max, lat_min,
                             tok_media, tok_completion])

        time.sleep(1)  # pausa tra un batch e l'altro

print("\n" + "=" * 65)
print(f"Completato. Risultati in: {OUTPUT_CSV}")

# Riepilogo finale
print("\nRiepilogo per livello di concorrenza:")
print(f"{'Concorrenza':>12} | {'Lat. media ms':>14} | {'Tok/s media':>12}")
print("-" * 45)

import csv as csv_mod
riepilogo = {}
with open(OUTPUT_CSV, newline="") as f:
    reader = csv_mod.DictReader(f)
    for row in reader:
        n = int(row["concorrenza"])
        if n not in riepilogo:
            riepilogo[n] = {"latenze": [], "tok": []}
        riepilogo[n]["latenze"].append(float(row["latenza_media_ms"]))
        riepilogo[n]["tok"].append(float(row["tok_sec_media"]))

for n, dati in sorted(riepilogo.items()):
    print(f"{n:>12} | {round(np.mean(dati['latenze']), 1):>14} | "
          f"{round(np.mean(dati['tok']), 1):>12}")

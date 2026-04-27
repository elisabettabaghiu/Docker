import requests
import json
import csv
import time
from datetime import datetime

# Configurazione
URL = "http://localhost:12434/engines/llama.cpp/v1/chat/completions" # API locale (DMR)
MODEL = "ai/smollm2" # modello AI usato
DOMANDA = "What is Docker in one sentence?" # inpuut
N_RICHIESTE = 10 # numero test
OUTPUT_CSV = "risultati.csv" # file sove salvo i dati

# --- Intestazione CSV ---
with open(OUTPUT_CSV, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "richiesta",
        "latenza_totale_ms",
        "prompt_ms",
        "predicted_ms",
        "token_per_secondo",
        "prompt_tokens",
        "completion_tokens",
        "cached_tokens",
        "risposta"
    ])

print(f"Avvio benchmark: {N_RICHIESTE} richieste al modello {MODEL}")
print(f"Domanda: {DOMANDA}")
print("-" * 60)

# --- Loop benchmark ---
for i in range(1, N_RICHIESTE + 1):
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": DOMANDA}]
    }

    # misuro latenza
    inizio = time.time()
    risposta = requests.post(URL, json=payload) #chiamata API (ritorna JSON)
    fine = time.time()

    latenza_totale_ms = round((fine - inizio) * 1000, 2)

    dati = risposta.json()

    # Estrai campi
    content = dati["choices"][0]["message"]["content"] # prende sono il testo della risposta
    usage = dati["usage"]
    timings = dati.get("timings", {})

    prompt_ms = round(timings.get("prompt_ms", 0), 2)
    predicted_ms = round(timings.get("predicted_ms", 0), 2)
    tok_sec = round(timings.get("predicted_per_second", 0), 2)
    prompt_tokens = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)
    cached_tokens = usage.get("prompt_tokens_details", {}).get("cached_tokens", 0)

    # Stampa a schermo
    print(f"[{i}/{N_RICHIESTE}] latenza: {latenza_totale_ms} ms | "
          f"{tok_sec} tok/s | "
          f"completion: {completion_tokens} token")

    # Scrivi su CSV
    with open(OUTPUT_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            i,
            latenza_totale_ms,
            prompt_ms,
            predicted_ms,
            tok_sec,
            prompt_tokens,
            completion_tokens,
            cached_tokens,
            content.replace("\n", " ")
        ])

    time.sleep(0.5) # pausa tra le richeste

print("-" * 60)
print(f"Benchmark completato. Risultati salvati in: {OUTPUT_CSV}")

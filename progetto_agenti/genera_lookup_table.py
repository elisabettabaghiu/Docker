import requests
import json
import re
import csv
import time
import threading
import psutil
import numpy as np
from itertools import product
from datetime import datetime

# ── Configurazione ────────────────────────────────────────────
URL    = "http://localhost:12434/engines/llama.cpp/v1/chat/completions"
MODEL = "qwen3:latest"   # cambia qui per testare altri modelli
# testo: gemma3, llama 3.2 (oppure docker.io/ai/llama3.2), qwen3, deepseek-r1-distill-llama

OUTPUT_JSON    = f"lookup_table_{MODEL.split(':')[0].replace('/', '_')}.json"
OUTPUT_CSV     = f"metrics_{MODEL.split(':')[0].replace('/', '_')}.csv"

# ── Variabili simboliche ──────────────────────────────────────
VARIABILI = {
    "load_level":     ["low", "medium", "high"],
    "capacity_level": ["low", "medium", "high"],
    "latency_risk":    ["low", "medium", "high"],
}

# ── Prompt per il modello ─────────────────────────────────────
def costruisci_prompt(combo):
    return (
        f"You are an agent in a distributed system. "
        f"Your current state is: "
        f"load_level={combo['load_level']}, "
        f"capacity_level={combo['capacity_level']}, "
        f"latency_risk={combo['latency_risk']}. "
        f"Respond with a JSON object with exactly two fields: "
        f"\"advice\" (a single word summarizing your recommendation, "
        f"e.g. accept, offload, scale_up, stable, reduce, redistribute) "
        f"and \"message\" (a concise status message of max 2 sentences). "
        f"Output only the JSON object, no other text."
    )

def estrai_advice_e_messaggio(content):
    match = re.search(r'\{.*?\}', content, re.DOTALL)
    if match:
        try:
            dati = json.loads(match.group())
            return dati.get("advice", "unknown").strip(), dati.get("message", content).strip()
        except json.JSONDecodeError:
            pass
    return "unknown", content

# ── Monitor risorse ───────────────────────────────────────────
monitoraggio_attivo = False
campioni_cpu = []
campioni_ram = []

def monitor_risorse():
    while monitoraggio_attivo:
        campioni_cpu.append(psutil.cpu_percent(interval=None))
        campioni_ram.append(psutil.virtual_memory().used / (1024 ** 2))
        time.sleep(0.5)

# ── Singola chiamata API ──────────────────────────────────────
def chiama_modello(prompt):
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }
    inizio = time.time()
    risposta = requests.post(URL, json=payload, timeout=120)
    fine = time.time()
    dati = risposta.json()

    timings = dati.get("timings", {})
    usage   = dati.get("usage", {})
    content = dati["choices"][0]["message"]["content"].strip()

    return {
        "message":           content,
        "latenza_ms":        round((fine - inizio) * 1000, 2),
        "prompt_ms":         round(timings.get("prompt_ms", 0), 2),
        "predicted_ms":      round(timings.get("predicted_ms", 0), 2),
        "tok_sec":           round(timings.get("predicted_per_second", 0), 2),
        "prompt_tokens":     usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "cached_tokens":     usage.get("prompt_tokens_details", {}).get("cached_tokens", 0),
    }

# ── Genera tutte le combinazioni ──────────────────────────────
chiavi     = list(VARIABILI.keys())
valori     = list(VARIABILI.values())
combo_list = [dict(zip(chiavi, v)) for v in product(*valori)]
totale     = len(combo_list)

print(f"Docker Model Runner — Generazione lookup table")
print(f"Modello:      {MODEL}")
print(f"Variabili:    {chiavi}")
print(f"Combinazioni: {totale}  ({' x '.join(str(len(v)) for v in valori)})")
print(f"Output JSON:  {OUTPUT_JSON}")
print(f"Output CSV (metriche): {OUTPUT_CSV}")
print("=" * 65)

ram_baseline = round(psutil.virtual_memory().used / (1024 ** 2))
print(f"RAM baseline: {ram_baseline} MB\n")

# ── CSV header (metriche per grafici, non nella lookup table) ─
with open(OUTPUT_CSV, "w", newline="") as f:
    csv.writer(f).writerow([
        "idx", *chiavi, "advice",
        "latenza_ms", "prompt_ms", "predicted_ms", "tok_sec",
        "prompt_tokens", "completion_tokens", "cached_tokens",
        "cpu_media", "cpu_max", "ram_media_mb", "ram_max_mb"
    ])

lookup_table     = []
metriche_globali = []

# ── Loop principale ───────────────────────────────────────────
for idx, combo in enumerate(combo_list, 1):
    label = " | ".join(f"{k}={v}" for k, v in combo.items())
    print(f"[{idx:>2}/{totale}] {label}")

    prompt = costruisci_prompt(combo)

    campioni_cpu.clear()
    campioni_ram.clear()
    monitoraggio_attivo = True
    t_mon = threading.Thread(target=monitor_risorse, daemon=True)
    t_mon.start()

    try:
        res    = chiama_modello(prompt)
        errore = None
    except Exception as e:
        res = {
            "message": "", "latenza_ms": 0, "prompt_ms": 0,
            "predicted_ms": 0, "tok_sec": 0,
            "prompt_tokens": 0, "completion_tokens": 0, "cached_tokens": 0
        }
        errore = str(e)

    monitoraggio_attivo = False
    t_mon.join(timeout=2)

    cpu_media = round(np.mean(campioni_cpu), 1) if campioni_cpu else 0
    cpu_max   = round(np.max(campioni_cpu),  1) if campioni_cpu else 0
    ram_media = round(np.mean(campioni_ram), 1) if campioni_ram else 0
    ram_max   = round(np.max(campioni_ram),  1) if campioni_ram else 0

    advice, message = estrai_advice_e_messaggio(res["message"]) if not errore else ("unknown", "")

    if errore:
        print(f"         ERRORE: {errore}")
    else:
        print(f"         OK  advice={advice} | {res['latenza_ms']} ms | "
              f"{res['tok_sec']} tok/s | "
              f"CPU {cpu_media}% | RAM {ram_media} MB")
        metriche_globali.append(res)

    # lookup table: solo stato + consiglio, niente metriche
    entry = {
        **combo,
        "advice":  advice,
        "message": message,
    }
    lookup_table.append(entry)

    # CSV: metriche complete per analisi/grafici
    with open(OUTPUT_CSV, "a", newline="") as f:
        csv.writer(f).writerow([
            idx, *combo.values(), advice,
            res["latenza_ms"], res["prompt_ms"], res["predicted_ms"],
            res["tok_sec"], res["prompt_tokens"], res["completion_tokens"],
            res["cached_tokens"], cpu_media, cpu_max, ram_media, ram_max
        ])

    time.sleep(1)

# ── Salva JSON ────────────────────────────────────────────────
output = {
    "metadata": {
        "model":              MODEL,
        "generated":          datetime.now().isoformat(),
        "variables":          VARIABILI,
        "total_combinations": totale,
    },
    "lookup_table": lookup_table
}

with open(OUTPUT_JSON, "w") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

# ── Riepilogo ─────────────────────────────────────────────────
print("\n" + "=" * 65)
print("COMPLETATO")
print("=" * 65)
if metriche_globali:
    latenze  = [m["latenza_ms"] for m in metriche_globali]
    tok_secs = [m["tok_sec"]    for m in metriche_globali if m["tok_sec"] > 0]
    print(f"Combinazioni generate:  {len(metriche_globali)}/{totale}")
    print(f"Latenza media:          {round(np.mean(latenze), 1)} ms")
    print(f"Latenza min/max:        {round(np.min(latenze), 1)} / {round(np.max(latenze), 1)} ms")
    print(f"Throughput medio:       {round(np.mean(tok_secs), 1) if tok_secs else 'N/A'} tok/s")
print(f"\nLookup table JSON:  {OUTPUT_JSON}")
print(f"Metriche CSV:       {OUTPUT_CSV}")

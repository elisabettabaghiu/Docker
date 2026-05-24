# Docker Model Runner — Benchmark e Lookup Table Sperimentale

Repository della tesi di laurea triennale:
**"Docker Model Runner: esecuzione e gestione di modelli AI in ambienti containerizzati"**

> Elisabetta Baghiu — Università degli Studi di Ferrara, Corso di Laurea in Informatica, A.A. 2024/2025

---

## Descrizione

Questo repository contiene il codice e i dati relativi all'analisi sperimentale
condotta nella tesi. L'esperimento prevede la generazione automatica di una
**lookup table** di messaggi per un sistema multi-agente distribuito, utilizzando
Docker Model Runner come backend di inferenza locale.

Per ogni combinazione delle tre variabili simboliche (`load_level`,
`capacity_level`, `legacy_risk`), ciascuna con tre livelli (`low`, `medium`,
`high`), viene generato automaticamente un messaggio che un agente invierebbe
al coordinatore centrale per descrivere il proprio stato. Le 27 combinazioni
risultanti (3 × 3 × 3) vengono testate su quattro modelli LLM diversi,
misurando latenza, throughput, utilizzo di CPU e RAM per ciascuna chiamata.

---

## Struttura del repository

```
progetto_agenti/
│
├── genera_lookup_table.py          # Genera la lookup table per un modello
├── grafici_lookup.py               # Grafici per un singolo modello
├── confronto_modelli.py            # Grafico comparativo tra i 4 modelli
│
├── benchmark_lookup_gemma3.csv
├── benchmark_lookup_llama3_2.csv
├── benchmark_lookup_qwen3.csv
├── benchmark_lookup_deepseek-r1-distill-llama.csv
│
├── lookup_table_gemma3.json
├── lookup_table_llama3_2.json
├── lookup_table_qwen3.json
├── lookup_table_deepseek-r1-distill-llama.json
│
└── README.md
```

---

## Requisiti

### Software

- Python 3.10 o superiore
- Docker Desktop 4.40+ con Docker Model Runner abilitato
  (`Settings → Features in development → Enable Docker Model Runner`)
- Librerie Python:

```bash
pip install requests numpy matplotlib psutil
```

### Modelli

I modelli devono essere disponibili localmente tramite Docker Model Runner:

```bash
docker model pull gemma3:latest
docker model pull llama3.2:latest
docker model pull qwen3:latest
docker model pull deepseek-r1-distill-llama:latest
```

Verifica con:

```bash
docker model list
```

---

## Configurazione della connessione

### Caso 1 — Docker Model Runner in locale

L'API è raggiungibile direttamente su `http://localhost:12434`.
Nessuna configurazione aggiuntiva necessaria.

### Caso 2 — Docker Model Runner su server remoto (via SSH tunnel)

Se Docker Model Runner gira su un server remoto, è necessario aprire un
tunnel SSH perché il servizio ascolta esclusivamente su `localhost` del server.

Apri il tunnel in un terminale dedicato e **tienilo aperto** per tutta la
durata dell'esperimento:

```bash
ssh -L 12434:localhost:12434 \
    -o ServerAliveInterval=30 \
    -o ServerAliveCountMax=10 \
    utente@indirizzo_server
```

Verifica che il tunnel funzioni con:

```bash
curl http://localhost:12434/engines/llama.cpp/v1/models
```

Se la risposta è un JSON con la lista dei modelli, il tunnel è attivo
e gli script funzioneranno senza modifiche.

---

## Riproduzione dell'esperimento

### Step 1 — Generare la lookup table per un modello

Apri `genera_lookup_table.py` e imposta il modello desiderato:

```python
MODEL = "gemma3:latest"   # oppure llama3.2, qwen3, deepseek-r1-distill-llama
```

Esegui:

```bash
python3 genera_lookup_table.py
```

Output prodotto:
- `lookup_table_<modello>.json` — lookup table completa con messaggi e metriche
- `benchmark_lookup_<modello>.csv` — dati di benchmark riga per riga

**Tempi di esecuzione stimati:**

| Modello | Tempo per 27 combinazioni |
|---|---|
| gemma3 | ~1 minuto |
| llama3.2 | ~1 minuto |
| qwen3 | ~12 minuti |
| deepseek-r1 | ~13 minuti |

### Step 2 — Generare i grafici per un singolo modello

Imposta il nome del modello nelle prime righe di `grafici_lookup.py`:

```python
INPUT_CSV  = "benchmark_lookup_gemma3.csv"
INPUT_JSON = "lookup_table_gemma3.json"
```

Esegui:

```bash
python3 grafici_lookup.py
```

Output: `grafici_lookup_gemma3.png` con sei grafici (latenza, throughput,
CPU, RAM, completion tokens, statistiche globali).

### Step 3 — Grafico comparativo tra i 4 modelli

Assicurati di aver eseguito lo Step 1 per tutti e quattro i modelli, poi:

```bash
python3 confronto_modelli.py
```

Output: `confronto_4_modelli.png` con il confronto completo tra i modelli.

---

## Struttura della lookup table (formato JSON)

```json
{
  "metadata": {
    "model": "gemma3:latest",
    "generated": "2026-05-24T14:18:32",
    "variables": {
      "load_level":     ["low", "medium", "high"],
      "capacity_level": ["low", "medium", "high"],
      "legacy_risk":    ["low", "medium", "high"]
    },
    "total_combinations": 27
  },
  "lookup_table": [
    {
      "load_level": "low",
      "capacity_level": "low",
      "legacy_risk": "low",
      "message": "Status: Operating at low load and capacity, with minimal legacy risk. I am currently able to handle additional tasks.",
      "metrics": {
        "latenza_ms": 1302.27,
        "tok_sec": 27.35,
        "prompt_tokens": 73,
        "completion_tokens": 24,
        "cpu_media_pct": 14.8,
        "ram_media_mb": 2974.6
      }
    }
  ]
}
```

Per consultare la tabella in un sistema multi-agente:

```python
import json

with open("lookup_table_gemma3.json") as f:
    tabella = json.load(f)["lookup_table"]

def cerca_messaggio(load, capacity, legacy):
    for entry in tabella:
        if (entry["load_level"]     == load and
            entry["capacity_level"] == capacity and
            entry["legacy_risk"]    == legacy):
            return entry["message"]
    return None

# Esempio
msg = cerca_messaggio("high", "low", "medium")
print(msg)
```

---

## Risultati principali

| Modello | Latenza media | Tok/s | CPU % | RAM (MB) | Token risposta |
|---|---|---|---|---|---|
| gemma3 | 1.718 ms | 27,4 | 16,4% | 2.909 | 30,6 |
| llama3.2 | 2.019 ms | 35,1 | 18,2% | 3.072 | 42,3 |
| qwen3 | 27.253 ms | 15,0 | 12,7% | 2.867 | 390,1 |
| deepseek-r1 | 28.399 ms | 15,2 | 15,7% | 2.972 | 410,9 |

gemma3 e llama3.2 completano ogni combinazione in circa 2 secondi con risposte
concise (30–42 token). qwen3 e deepseek-r1 impiegano 27–28 secondi producendo
risposte molto più elaborate (390–411 token) per via del meccanismo di
ragionamento esplicito interno (chain-of-thought).

---

## Riferimenti

- [Docker Model Runner — Documentazione ufficiale](https://docs.docker.com/model-runner/)
- [llama.cpp](https://github.com/ggerganov/llama.cpp)
- [Repository tesi](https://github.com/elisabettabaghiu/Docker/tree/main/progetto_agenti)

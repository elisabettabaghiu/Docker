Terminale 1 — avvia il modello e lascialo lì:
docker model run ai/smollm2

Terminale 2 — richiesta HTTP
curl http://localhost:12434/engines/llama.cpp/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ai/smollm2",
    "messages": [{"role": "user", "content": "What is Docker in one sentence?"}]
  }’
{"choices":[{"finish_reason":"stop","index":0,"message":{"role":"assistant","content":"Docker is an open-source containerization platform that enables developers to create and deploy applications in isolated environments, reducing the need for traditional operating system installation and configuration."}}],"created":1777122897,"model":"bf6f20a603055433b4b998119e17928fc4a89b35c42855dd7eada105058cae0a","system_fingerprint":"b1-e365e65","object":"chat.completion","usage":{"completion_tokens":34,"prompt_tokens":37,"total_tokens":71,"prompt_tokens_details":{"cached_tokens":23}},"id":"chatcmpl-nQ1ZcTd1q0xfpC7wDUeKts36zmYUieM2","timings":{"cache_n":23,"prompt_n":14,"prompt_ms":118.309,"prompt_per_token_ms":8.450642857142856,"prompt_per_second":118.33419266497053,"predicted_n":34,"predicted_ms":231.446,"predicted_per_token_ms":6.807235294117647,"predicted_per_second":146.90251721783918}} 


- curl è il programma che invia richeste al server
- chiamo un server locale su localhost:12434 (nul mio PC sulla porta usata dal DMR
- /engines/llama.cpp/v1/chat/completions è il motore AI usato
- "content": "What is Docker in one sentence?" è l’imput 
[in risposta ottengo "content":"Docker is an open-source containerization platform that enables developers to create and deploy applications in isolated environments, reducing the need for traditional operating system installation and configuration."]

Struttura sistema: TU → CURL → API Docker → MODELLO → RISPOSTA
 TU (utente) →  scrivo il comando curl con una domanda dentro (JSON) (“What is Docker?”)
 curl invia la richiesta dal terminale al server (su internet o in locale
 API Docker (server locale) http://localhost:12434/engines/llama.cpp/v1/chat/completions → un server che gira sul Mac dentro Docker. Il server riceve la richiesta, capisce che deve usare un modello AI, prepara il modello e gli passa il messaggio
 Il modello (SmolLM2) legge la domanda, usa i suoi parametri e genera una risposta

- In choices trovo message → struttura della conversazione (role = chi parla, assistant = modello AI, content = risposta generata)
- usage → consumo di token (prompt_tokens = input che hai dato, completion_tokens = risposta generata, total_tokens = somma totale)
- prompt_tokens_details → "cached_tokens" = numero di token già in cache quindi non sono stati ricalcolati
- timings → performance 
completion_tokens: 34 = quanti token ha generato il modello per risponderti
prompt_tokens: 37 = quanti token aveva la tua domanda in ingresso.
prompt_ms = tempo per leggere la domanda
predicted_ms = tempo per generare risposta
predicted_per_second: 146.9 — token generati al secondo (+ alto=+veloce a rispondere)
prompt_per_second: 118.3 — token della domanda elaborati al secondo




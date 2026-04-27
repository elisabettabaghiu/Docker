Per misurare CPU e RAM useremo docker stats, che è il comando nativo di Docker per monitorare le risorse in tempo reale. Mentre il benchmark gira, in parallelo campioneremo le risorse del container ogni secondo e le salveremo su file.
Il problema è che docker stats mostra le statistiche del container Docker, ma Docker Model Runner non gira come un container classico — gira come un processo gestito dal Docker Desktop engine. Quindi useremo un approccio diverso: misureremo le risorse di sistema (CPU e RAM del processo Python + del motore di inferenza) direttamente con la libreria psutil di Python, che legge i dati dal sistema operativo.

python3 benchmark_risorse.py
Benchmark risorse — modello: ai/smollm2
Livelli: [1, 2, 4, 8] | Ripetizioni: 3
Campionamento risorse ogni 0.5s
======================================================================
RAM baseline sistema: 3213 MB

[ Concorrenza: 1 ]
  rep 1/3 | lat: 1294.1 ms | CPU: 23.5% (max 54.5%) | RAM: 3299.8 MB (max 3473.8 MB)
  rep 2/3 | lat: 266.2 ms | CPU: 15.5% (max 15.5%) | RAM: 3031.8 MB (max 3031.8 MB)
  rep 3/3 | lat: 192.9 ms | CPU: 11.8% (max 11.8%) | RAM: 3390.9 MB (max 3390.9 MB)
[ Concorrenza: 2 ]
  rep 1/3 | lat: 452.4 ms | CPU: 19.4% (max 20.4%) | RAM: 3216.1 MB (max 3400.8 MB)
  rep 2/3 | lat: 320.0 ms | CPU: 12.9% (max 12.9%) | RAM: 3332.2 MB (max 3332.2 MB)
  rep 3/3 | lat: 420.0 ms | CPU: 14.0% (max 16.2%) | RAM: 3382.2 MB (max 3389.7 MB)
[ Concorrenza: 4 ]
  rep 1/3 | lat: 773.5 ms | CPU: 12.8% (max 13.8%) | RAM: 3403.2 MB (max 3407.1 MB)
  rep 2/3 | lat: 808.3 ms | CPU: 15.3% (max 16.9%) | RAM: 3359.2 MB (max 3374.2 MB)
  rep 3/3 | lat: 655.0 ms | CPU: 13.6% (max 15.0%) | RAM: 3380.8 MB (max 3393.2 MB)
[ Concorrenza: 8 ]
  rep 1/3 | lat: 1378.9 ms | CPU: 15.0% (max 18.8%) | RAM: 3418.3 MB (max 3441.9 MB)
  rep 2/3 | lat: 1411.1 ms | CPU: 15.1% (max 21.2%) | RAM: 3332.3 MB (max 3361.1 MB)
  rep 3/3 | lat: 1639.2 ms | CPU: 13.0% (max 17.5%) | RAM: 3331.5 MB (max 3391.6 MB)
======================================================================
Completato. Risultati in: risultati_risorse.csv

Riepilogo per livello di concorrenza:
 Conc. |  Lat. ms |  CPU % |  CPU max |   RAM MB |  RAM max
----------------------------------------------------------
     1 |    584.4 |   16.9 |     27.3 |   3240.8 |   3298.8
     2 |    397.5 |   15.4 |     16.5 |   3310.2 |   3374.2
     4 |    745.6 |   13.9 |     15.2 |   3381.1 |   3391.5
     8 |   1476.4 |   14.4 |     19.2 |   3360.7 |   3398.2


L’analisi delle risorse evidenzia che l’utilizzo della CPU rimane pressoché 
costante al variare del numero di richieste concorrenti, oscillando tra il 
14% e il 17%. Questo comportamento indica che il motore di inferenza 
non sfrutta il parallelismo per gestire più richieste simultaneamente, 
ma le elabora in modo sequenziale o pseudo-sequenziale.
Analogamente, l’utilizzo della memoria RAM risulta stabile, suggerendo 
che il modello viene caricato una sola volta e condiviso tra tutte le 
richieste, senza duplicazione delle risorse.
L’incremento della latenza osservato all’aumentare della concorrenza 
non è quindi imputabile a un aumento del carico computazionale, bensì 
alla presenza di una coda di richieste gestita dal sistema.
Per applicazioni ad alto carico concorrente servirebbe un'architettura 
diversa (es. ai/smollm2-vllm)

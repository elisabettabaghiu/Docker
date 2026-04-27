Terminale 1: docker model run ai/smollm2
Terminale 2: 
python3 benchmark_concorrenza.py

Risultato: 
Benchmark concorrenza — modello: ai/smollm2
Livelli testati: [1, 2, 4, 8] richieste simultanee
Ripetizioni per livello: 5
=================================================================
[ Concorrenza: 1 richiesta/e simultanea/e ]
  rep 1/5 | lat media: 1297.6 ms | lat max: 1297.6 ms | 138.8 tok/s
  rep 2/5 | lat media: 388.5 ms | lat max: 388.5 ms | 83.0 tok/s
  rep 3/5 | lat media: 418.5 ms | lat max: 418.5 ms | 82.1 tok/s
  rep 4/5 | lat media: 453.3 ms | lat max: 453.3 ms | 81.5 tok/s
  rep 5/5 | lat media: 519.6 ms | lat max: 519.6 ms | 80.0 tok/s

[ Concorrenza: 2 richiesta/e simultanea/e ]
  rep 1/5 | lat media: 439.8 ms | lat max: 558.2 ms | 107.0 tok/s
  rep 2/5 | lat media: 521.0 ms | lat max: 734.5 ms | 75.9 tok/s
  rep 3/5 | lat media: 473.5 ms | lat max: 634.9 ms | 85.1 tok/s
  rep 4/5 | lat media: 748.5 ms | lat max: 946.7 ms | 71.3 tok/s
  rep 5/5 | lat media: 520.4 ms | lat max: 691.9 ms | 95.6 tok/s

[ Concorrenza: 4 richiesta/e simultanea/e ]
  rep 1/5 | lat media: 912.1 ms | lat max: 1318.7 ms | 100.1 tok/s
  rep 2/5 | lat media: 1092.5 ms | lat max: 1716.0 ms | 66.3 tok/s
  rep 3/5 | lat media: 1026.8 ms | lat max: 1825.4 ms | 69.6 tok/s
  rep 4/5 | lat media: 859.2 ms | lat max: 1381.2 ms | 85.3 tok/s
  rep 5/5 | lat media: 1085.4 ms | lat max: 1755.1 ms | 68.4 tok/s

[ Concorrenza: 8 richiesta/e simultanea/e ]
  rep 1/5 | lat media: 2177.7 ms | lat max: 3888.4 ms | 66.1 tok/s
  rep 2/5 | lat media: 1980.7 ms | lat max: 3319.2 ms | 74.2 tok/s
  rep 3/5 | lat media: 1806.2 ms | lat max: 3296.0 ms | 81.5 tok/s
  rep 4/5 | lat media: 1204.9 ms | lat max: 2502.4 ms | 92.2 tok/s
  rep 5/5 | lat media: 1706.6 ms | lat max: 3271.7 ms | 79.8 tok/s
=================================================================
Completato. Risultati in: risultati_concorrenza.csv

Riepilogo per livello di concorrenza:
 Concorrenza |  Lat. media ms |  Tok/s media
---------------------------------------------
           1 |          615.5 |         93.1
           2 |          540.6 |         87.0
           4 |          995.2 |         77.9
           8 |         1775.2 |         78.8

L’esperimento di concorrenza ha simulato l’interazione simultanea di più client attraverso l’utilizzo di thread paralleli. 
I risultati evidenziano che l’aumento del  numero di richieste concorrenti comporta un incremento significativo della 
latenza media, passando da circa 615 ms con una singola richiesta a oltre 1700 ms con otto richieste simultanee.
Questo comportamento indica che il sistema non esegue vera parallelizzazione  delle inferenze, ma gestisce le richieste in modo 
sequenziale o semi-sequenziale attraverso una coda interna. Di conseguenza, all’aumentare del carico, le richieste subiscono un ritardo crescente.
Tuttavia, il throughput in token al secondo rimane relativamente stabile, suggerendo che la velocità di generazione del modello non varia 
significativamente, mentre la degradazione delle prestazioni è principalmente dovuta alla gestione della concorrenza.
Il modello non diventa più lento, ma i clienti aspettano di più.



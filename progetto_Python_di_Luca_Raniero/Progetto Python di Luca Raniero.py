#importo tutte le librerie necessarie
import requests
import json
from datetime import datetime, timedelta, date
import os

#creo la variale url dal quale ricavare i dati
url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

#creo la variabile params per la quantità di dati da ricavare
params = {
    'start': '1',
    'limit': '100',
    'convert': 'USD'
}

#creo la variabile headers per avere accesso alla API
headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': '8871c96e-cce7-40d7-91b3-de5e03e24137'
}

#creo la variabile di richiesta che scaricherà i dati desiderati in formato json
r = requests.get(url=url, headers = headers, params = params).json()

#creo una serie di liste utili per risolvere i task richiesti dal progetto
volume_24h = ['nothing', 0]
percent_change_24h = []
cmc_rank = []
volume_over_76 = []

#creo le variabili di limite a parte in modo da essere facilmente individuabili in futuro se dovessero essere modificate
top_cmc = 20
min_volume_in_USD = 76000000

#inizio un loop per ricavare i dati delle task di mio interesse
for index, _ in enumerate(r['data']):

    #aggiungo alla lista 'percent_change_24h' l'acronimo della criptovaluta e
    #il rispettivo incremento percentuale delle ultime 24 ore
    percent_change_24h.append(
        [r['data'][index]['symbol'], float(r['data'][index]['quote']['USD']['percent_change_24h'])])

    #ricerco il volume maggiore (in dollari) delle ultime 24 ore sfruttando un if statement
    if float(r['data'][index]['quote']['USD']['volume_24h']) > volume_24h[1]:
        #ogni volta trovo un valore massimo nuovo, sovrascrivo la variabile 'volume_24h'
        volume_24h = [r['data'][index]['symbol'], float(r['data'][index]['quote']['USD']['volume_24h'])]

    #ricerco tutte quelle criptovalute che ricadono nella top 20 secondo la classifica di CoinMarketCap
    if r['data'][index]['cmc_rank'] <= top_cmc:
        #aggiungo tali valori nella rispettiva lista creata in precedenza
        cmc_rank.append(
            [r['data'][index]['cmc_rank'], r['data'][index]['symbol'], r['data'][index]['quote']['USD']['price']])

    #ricerco tutte quelle criptovalute che superano il volume minimo richiesto dalla task
    if float(r['data'][index]['quote']['USD']['volume_24h']) > min_volume_in_USD:
        #aggiungo tali valori nella rispettiva lista creata in precedenza
        volume_over_76.append([r['data'][index]['symbol'], r['data'][index]['quote']['USD']['price']])


#riordino i valori sulla base del secondo valore all'interno della lista di lista (dal più grande al più piccolo)
percent_change_24h = sorted(percent_change_24h, key=lambda x: x[1], reverse=True)
#creo due dizionari che accoglieranno le rispettive prime 10 e ultime 10 criptovalute
dict_percent_change_24h_best = {}
dict_percent_change_24h_worst = {}
#creo un ciclo for per ogni dizionario creato prima che va ad aggiungere i dati desiderati
for i in percent_change_24h[:10]:
    dict_percent_change_24h_best[i[0]] = i[1]
for i in percent_change_24h[-10:]:
    dict_percent_change_24h_worst[i[0]] = i[1]


#creo il dizionario per accogliere il valore della criptovaluta con volume maggiore nelle ultime 24 ore
dict_volume_24h = {volume_24h[0]: volume_24h[1]}


#sfrutto la stessa logica per entrambi i dizionatri creati successivi, il primo per le prime 20 criptovlaute secondo cmc
#e il secondo per tutte lelcriptovalute che superano i 76.000.000$ di volume
# (il riordinarle è un passaggio in più ma per chiarezza di dati)
dict_cmc_rank = {}
for i in sorted(cmc_rank, key=lambda x: x[0]):
    dict_cmc_rank[i[1]] = i[2]

dict_volume_over_76 = {}
for i in sorted(volume_over_76, key=lambda x: x[0]):
    dict_volume_over_76[i[0]] = i[1]


#creo il dizionario definitivo che andrà a scrivere il file json di nostro interesse, completato con tutti
#i dizionari creati in precedenza
data = {'volume_24h': dict_volume_24h,
        'best_percent_change_24h': dict_percent_change_24h_best,
        'worst_percent_change_24h': dict_percent_change_24h_worst,
        'cmc_rank': dict_cmc_rank,
        'volume_over_76': dict_volume_over_76
       }

#creo la variabile che conterrà il nome del file del giorno precedente (per come, se esiste, dovrebbe essere strutturato
yesterday = (datetime.now() - timedelta(days=1)).strftime('%d_%m_%y%y')
filename_yest = 'data_' + yesterday + '.json'

#eseguo un if statement per verificare se il suddetto file esiste (ovviamente se il monitoraggio inizia oggi,
#sicuramente non ho file di confronto)
if os.path.exists(filename_yest):
    #se la condizione di dovesse verificare, carico il file del giorno precedente
    dati_ieri = json.load(open(filename_yest))

    #creo la varibile che conterrà il profitto (per profitto intendo sia che esso sia positivo che negativo)
    profit = []
    #creo un for loop che vada a calcolare il profitto (vedi task)
    for i, u in dati_ieri['cmc_rank'].items():
        profit.append(round(((data['cmc_rank'][i] - dati_ieri['cmc_rank'][i]) / dati_ieri['cmc_rank'][i]) * 100, 2))

    #aggiungo la voce profit e relativa somma ai dati da mettere nel file json
    data['profit'] = sum(profit)


#creo la variabile che conterrà il nome del file json che verrà creato sulla base di 'data'
date_object = datetime.now().strftime('%d_%m_%y%y')
filename = 'data_' + str(date_object) + '.json'

#creo il nuovo file con tutti i dati organizzati
with open(filename, "w") as json_file:
    json.dump(data, json_file, indent=4)


''' 
Ovviamente questo script funziona solo se 'cmc_rank' del giorno precedente è la stessa e identica del giorno 
attuale, altrimenti verrà un errore (ma anche questo era specificato come possibile problema nei vari task del progetto
quindi non sono andato a fixare questo possibile bug.

Mentre per rendere automatico questo script ogni giorno, basterebbe utilizzare 'Task Scheduler' di Windows (o affini per
altri sistemi operativi) oppure creare un ciclo While infinito che si attiva ogni 24h esatte.
'''

import os
import json
import csv
import requests
import statistics
import pandas as pd
import anthropic
import ast
import re
from pathlib import Path
from pprint import pprint
from collections import defaultdict, Counter

dossier_script = os.path.dirname(os.path.abspath(__file__))
fichier_events = os.path.join(dossier_script, "events.csv")
fichier_markets = os.path.join(dossier_script, "markets.csv")

# Clés API PushOver
api_global_pushover = "XXX"
api_appli_pushover = "XXX"

# Fait appel à l'API Anthropic - clef API à rentrer
client = anthropic.Anthropic(api_key="XXX")

# Liste des actifs à associer aux Events
liste_actifs = [
        "US Equities (S&P 500 / Nasdaq)", "European Equities (EuroStoxx)",
        "US Treasury Bonds", "Crude Oil", "Gold", "Natural Gas",
        "Copper", "US Dollar (USD)", "Euro (EUR)"
    ]

# Envoie de notification PushOver
def NOTIF_PUSHOVER(message):

    requests.post("https://api.pushover.net/1/messages.json", data={
        "token": api_global_pushover,
        "user": api_appli_pushover,
        "message": message,
        "title": "🚨 Délit d'initié détecté"
    })

# Extraction de l'asset et l'action à partir de la réponse générée par le LLM
def parseReponse(reponse):
    json_str = re.search(r'```json\n(.*?)\n```', reponse, re.DOTALL).group(1)
    data = json.loads(json_str)
    return data["asset"], data["action"]

# Appel au LLM pour association marché - asset : prend comme paramètres la liste des actifs définit arbitrairement, les tags associés à l'event du marché et la question/titre du marché
def result_LLM(liste_actifs, tag, question_marche):

    prompt = (f"""
    You are a Quantitative Global Macro Analyst.
    An abnormal buying flow (insider trading) has just been detected in favor of 'YES' on a Polymarket contract.

    Your task: Determine the best financial trade to execute immediately assuming the 'YES' outcome is now highly probable.

    Constraints:
    1. Respond ONLY in JSON format.
    2. "asset": Choose ONE asset strictly from this list: {liste_actifs}.If no asset is significantly impacted, use "NONE".
    3. "action": "buy" or "sell".
    4. "reasoning": Brief technical explanation in English explaining why the 'YES' outcome affects this asset.
    5. "reco": MUST follow this structure: "Following the analysis of the insider trading flow for 'YES', I suggest you [buy/sell] [asset]. If no reco is significantly identified, use "NONE""

    DATA:
    Category: {tag}
    Question: "{question_marche}"
    Insider Signal Direction: "YES"
    """)

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        temperature=0.1,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text

# Modification du fichier markets.csv pour inclure l'association marché - asset/action
def ASSET_TO_MARKET():

    tag = []
    question = ""
    markets = []
    events = []

    # On ouvre le fichier markets.csv et on récupère dans une liste l'ID du marché et la question
    with open(fichier_markets, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for ligne in reader:
            if ligne["acceptingOrders"] == "True":
                markets.append([ligne["marketId"], ligne["question"]])

    # On ouvre le fichier events.csv et on récupère dans une liste le titre de l'Event, les tags et les ID des marchés associés
    with open(fichier_events, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for ligne in reader:
            events.append([ligne["titre"], ligne["tags"], ligne["markets_id"]])

    # On consolide dans une liste les dictionnaire par marché associant l'ID du marché, la question du marché et les tags associés
    resultat = []
    for event in events:
        tags = ast.literal_eval(event[1])
        ids_event = ast.literal_eval(event[2])

        for market in markets:
            if market[0] in ids_event:
                resultat.append({
                    "market_id": market[0],
                    "question": market[1],
                    "tags": tags
                })

    # On génère les asset/action pour chaque market via le LLM et retourne un couple (asset, action). Ex : US Treasury Bond, sell
    nouvelles_valeurs = {}
    for market in resultat:
        reponse = result_LLM(liste_actifs, market["tags"], market["question"])
        asset, action = parseReponse(reponse)
        nouvelles_valeurs[market["market_id"]] = (asset, action)

    with open(fichier_markets, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        lignes = list(reader)
        colonnes = reader.fieldnames

    # On met à jour chaque ligne dans le CSV avec les valeurs asset et action (correspondant aux headers asset et orders dans le CSV)
    for ligne in lignes:
        if ligne["marketId"] in nouvelles_valeurs:
            asset, action = nouvelles_valeurs[ligne["marketId"]]
            ligne["asset"] = asset
            ligne["order"] = action
    
    # On réécrit le fichier
    with open(fichier_markets, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=colonnes)
        writer.writeheader()
        writer.writerows(lignes)

# Demande à l'utilisateur les Events qu'il veut surveiller et les stock dans events.csv
def choixEvents():

    # Limit arbitraire pour limiter le nombre de requêtes
    limit_events = 50

    url_events = "https://gamma-api.polymarket.com/events"

    # On applique des conditions à la requête : Events actifs et toujours ouverts, trie par volume et issue pas encore déterminée
    params_events = {
            "active": "true",
            "closed": "false",
            "order": "volume",
            "ascending": "false",
            "is_determined": "false",
            "limit": limit_events
        }

    events = requests.get(url_events, params=params_events).json()

    liste_Events = []

    # Permet de récupérer tous les tags pour chaque Event
    # Dans liste_Events, on a pour chaque Event : ID Event / Titre / Label / ID Markets
    liste_Events = [[e["id"], e["title"], [t["label"] for t in e["tags"]], [i["id"] for i in e["markets"]]] for e in events]

    # Catégorie que l'on souhaite exclure (arbitrairement)
    liste_Exclusion = ["Sports", "Culture", "Crypto", "Elections"]

    # On filtre en retirant les catégories pour lesquelles il n'est pas susceptible d'y avoir de délit d'initié (liste non exhaustive)
    liste_Events = [e for e in liste_Events if not any(tag in liste_Exclusion for tag in e[2])]

    # On affiche les Events et on demande à l'utilisateur quel Event il souhaite analyser
    for x in range(0, len(liste_Events)):
        print(str(x+1) + " - " + liste_Events[x][1])

    while True:
        try:
            eventsToAnalyze = input("\nEvent(s) to analyze : (format: x, y, z, ...): ")

            eventsToAnalyze = [int(x.strip()) for x in eventsToAnalyze.split(',')]
            break

        except ValueError:
            return("Wrong input format")
        
    eventsToAnalyze = [x - 1 for x in eventsToAnalyze]

    liste_Events = [liste_Events[i] for i in eventsToAnalyze]

    # Récupérer les Events déjà présents dans le CSV
    events_existants = set()
    fichier_existe_events = os.path.exists(fichier_events)

    if fichier_existe_events:
        with open(fichier_events, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            events_existants = {ligne["event_id"] for ligne in reader}

    liste_Events_a_ajouter = [e for e in liste_Events if str(e[0]) not in events_existants]

    # On stock dans un fichier CSV les Events sélectionnés

    with open(fichier_events, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not fichier_existe_events:
            writer.writerow(["event_id", "titre", "tags", "markets_id"])
        for ligne in liste_Events_a_ajouter:
            writer.writerow(ligne)

    # On stock dans une liste les marchés associés aux Events sélectionnés (pour avoir la totalité des marchés concernant dans le fichier CSV)
    liste_markets = []

    for i in liste_Events:
        for x in i[3]:
            liste_markets.append(x)

    # Récupérer les Markets déjà présents dans le CSV
    markets_existants = set()
    fichier_existe_markets = os.path.exists(fichier_markets)

    if fichier_existe_markets:
        with open(fichier_markets, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            markets_existants = {ligne["marketId"] for ligne in reader}

    # On stock dans un fichier CSV les Markets correspondant aux Events sélectionnés
    # On veut récupérer : marketId, acceptingOrders (True/False), conditionId, question
    data_markets = []
    for i in liste_markets:

        if str(i) in markets_existants:
            continue

        url_markets = "https://gamma-api.polymarket.com/markets/" + str(i)
        markets = requests.get(url_markets).json()
        if markets["acceptingOrders"] == True:
            data_markets.append([markets["id"],markets["question"],markets["acceptingOrders"],markets["conditionId"]])

    with open(fichier_markets, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not fichier_existe_markets:
            writer.writerow(["marketId", "question", "acceptingOrders", "conditionId", "asset", "order"])
        for ligne in data_markets:
            writer.writerow(ligne)

# Obtenir les X derniers trades sur un Market et les stocker
def getTrades(market_ID):

    liste_trades = []

    url_trades = "https://data-api.polymarket.com/trades"
    
    params_trades = {
        "market": market_ID,
        "limit": 500
    }
    
    trades = requests.get(url_trades, params=params_trades).json()

    # Pour chaque trade, on va récupérer l'adresse du wallet / username, le volume, le prix, le side, l'outcome, calcul du montant total
    for i in trades:
        liste_trades.append([i["proxyWallet"], i["name"], i["size"], i["price"], i["side"], i["outcome"], float(i["price"]) * float(i["size"]), i["title"]])
    
    return liste_trades

# Récupère les trades passés par un utilisateur
def getTradesUser(adress_user):

    url_trades = "https://data-api.polymarket.com/trades"
    
    params_trades = {
        "user": adress_user,
        "limit": 500
    }
    
    trades_users = requests.get(url_trades, params=params_trades).json()

    return trades_users

# Agréger les wallets d'un trade et calcul Z-Score du marché
def ConsoWallet_ZScore(listeDeTrades, market_ConditionID):
    
    # defaultdict permet de créer automatiquement une valeur par défaut quand une clé n'existe pas encore, pour éviter erreur KeyError
    volumeByWallet = defaultdict(float)
    amountByWallet = defaultdict(float)
    outcomeByWallet = defaultdict(Counter)
    titleByWallet = {}
    nameByWallet = {}

    for trade in listeDeTrades:
        if trade[4] == "BUY":
            wallet = trade[0] #trade[0] = proxyWallet
            volumeByWallet[wallet] += float(trade[2]) #trade[2] = size
            amountByWallet[wallet] += float(trade[2]) * float(trade[3]) #trade[3] = price
            titleByWallet[wallet] = trade[7]
            outcomeByWallet[wallet][trade[5]] += 1
            nameByWallet[wallet] = trade[1]

    volumes = list(volumeByWallet.values())
    amounts = list(amountByWallet.values())

    mean_v = statistics.mean(volumes)
    std_v = statistics.stdev(volumes)
    mean_a = statistics.mean(amounts)
    std_a = statistics.stdev(amounts)

    # Identification wallet suspects
    suspects_level1 = []
    for wallet in volumeByWallet:
        z_volume = (volumeByWallet[wallet] - mean_v) / std_v
        z_amount = (amountByWallet[wallet] - mean_a) / std_a

        if abs(z_volume) > 2.5 and abs(z_amount) > 2.5:
            outcome = outcomeByWallet[wallet].most_common(1)[0][0]
            suspects_level1.append({
                "wallet": wallet,
                "market_id": market_ConditionID,
                "name": nameByWallet[wallet],
                "outcome": outcome,
                "title": titleByWallet[wallet],
                "total_volume": round(volumeByWallet[wallet], 2),
                "total_amount": round(amountByWallet[wallet], 2),
                "z_volume": round(z_volume, 2),
                "z_amount": round(z_amount, 2),
            })

    suspects_level1.sort(key=lambda x: max(abs(x["z_volume"]), abs(x["z_amount"])), reverse=True)
    return suspects_level1

# Calcul du Z-Score au sein de l'historique de trade de l'utilisateur
def zScore_Users(listeSuspects):

    historique = []
    flag_level2 = []

    for i in listeSuspects:
        wallet = i["wallet"]
        historique = getTradesUser(wallet)

        if len(historique) < 2:
            print("Nombre de trades inférieur à 2")
            continue

        volumes_historique = [float(t["size"]) for t in historique]
        montants_historique = [float(t["size"]) * float(t["price"]) for t in historique]
        
        mean_v = statistics.mean(volumes_historique)
        std_v = statistics.stdev(volumes_historique)
        mean_a = statistics.mean(montants_historique)
        std_a = statistics.stdev(montants_historique)

        if std_v == 0 or std_a == 0:
            continue

        z_vol_user = (i["total_volume"] - mean_v) / std_v
        z_amt_user = (i["total_amount"] - mean_a) / std_a

        if z_vol_user > 2.5 and z_amt_user > 2.5:
            flag_level2.append({
                "wallet": wallet,
                "name": i["name"],
                "title": i["title"],
                "market_id": i["market_id"],
                "outcome": i["outcome"],
                "z_volume_market": i["z_volume"],
                "z_amount_market": i["z_amount"],
                "z_volume_user": round(z_vol_user, 2),
                "z_amount_user": round(z_amt_user, 2),
                "volume_sur_market": i["total_volume"],
                "montant_sur_market": i["total_amount"],
            })
        
        flag_level2.sort(key=lambda x: max(x["z_volume_user"], x["z_amount_user"]), reverse=True)
    return flag_level2

# Envoie de la notification pour le suspect de niveau 2 détecté
def traiterSuspects(suspects_level2):
    
    # Charge les markets du CSV dans un dictionnaire
    markets_data = {}
    with open(fichier_markets, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for ligne in reader:
            markets_data[ligne["conditionId"]] = {
                "question": ligne["question"],
                "asset": ligne["asset"],
                "order": ligne["order"]
            }

    # Pour chaque suspect niveau 2, on envoie une notification
    for suspect in suspects_level2:
        
        market_id = suspect["market_id"]

        if market_id not in markets_data:
            print(f"Market {market_id} non trouvé dans le CSV")
            continue

        market_info = markets_data[market_id]

        # Inverse l'ordre si le suspect a parié NO (car LLM a généré pour YES)
        if suspect["outcome"] == "Yes":
            action = market_info["order"]
        else:
            action = "buy" if market_info["order"] == "sell" else "sell"

        message = (
            f"Marché : {market_info['question']}\n"
            f"Pari initié sur : {suspect['outcome']}\n"
            f"Actif concerné : {market_info['asset']}\n"
            f"Position recommandée : {action.upper()}\n\n"
            f"Wallet : {suspect['wallet'][:10]}...\n"
            f"Name : {suspect['name']}\n"
            f"Z-volume market : {suspect['z_volume_market']}\n"
            f"Z-volume historique : {suspect['z_volume_user']}"
        )

        NOTIF_PUSHOVER(message)
        print(f"✅ Notification envoyée pour {suspect['wallet'][:10]}...")

# On fait appel à toutes les fonctions précédemments déclarées pour retourner une liste de potentiels délits d'initiés
def analyzeMarkets():
    result_analyze = []
    with open(fichier_markets, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for ligne in reader:
            if ligne["conditionId"] is not None and ligne["conditionId"] != "":
                resultat = zScore_Users(ConsoWallet_ZScore(getTrades(ligne["conditionId"]), ligne["conditionId"]))
                if resultat != []:
                    result_analyze.extend(resultat)
    return result_analyze

# On demande à l'utilisateur s'il veut analyser de nouveaux Events. Si non --> on analyse les Events choisis précedemment et enregistrés sur le fichier "events.csv"
while True:
    choix_Analyse = input("Analyze new events ? (Y/N) : ").upper()
    if choix_Analyse in ["Y", "N"]:
        break
    print("Error: wrong input")

# Si l'utilisateur décide d'analyser de nouveaux marchés : 
if choix_Analyse == "Y":
    # On lui affiche les Events et on lui demande de choisir ceux qu'il veut analyser
    choixEvents()
    # On inscrit dans le fichier markets.csv les actifs associés à chaque event
    ASSET_TO_MARKET()
    traiterSuspects(analyzeMarkets())
elif choix_Analyse == "N":
    if not os.path.exists(fichier_markets):
        print("Aucun fichier markets.csv trouvé. Lance d'abord une analyse avec 'Y' pour sélectionner des marchés.")
    else:
        traiterSuspects(analyzeMarkets())
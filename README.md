# ai_in_finance_project
Polymarket insider detection system
# Polymarket : la fin de l'information privilégiée ? 🔍

---

## 1. Project Information

| | |
|---|---|
| **Project Title** | Polymarket : la fin de l'information privilégiée ? |
| **Group Name** | Robin Wood |
| **Group Members** | Broudic Goldman Erwan <br> Levelleux Antoine <br> Piat Quentin |
| **Course Name** | AI in Finance |
| **Instructor** | Nicolas De Roux & Mohamed EL FAKIR |
| **Submission Date** | 20/04/2026 |

---

## 2. Project Description 📌

Est-il possible de scraper l'API de Polymarket afin de détecter d'éventuels délits d'initiés, et en tirer des recommandations d'investissement sur des actifs financiers via une notification mobile ?

Polymarket, c'est jusqu'à 400 000 dollars pour un seul compte en pariant sur la chute de Maduro au Venezuela quelques heures avant l'intervention militaire américaine. Jusqu'à 1,2 million de dollars gagné après l'attaque des USA sur l'Iran début Avril sur une dizaine de comptes. Ça fait rêver, ça nous a fait rêver. Alors bien évidemment interdit en France, on a adapté notre projet.

Pour rappel, Polymarket est une plateforme de « marché de prédiction » basée sur la blockchain. Pour faire simple, c'est un site où les gens parient de l'argent sur l'issue d'événements réels (politique, sport, économie, pop culture).

- Au lieu de parier contre un bookmaker, vous échangez avec d'autres utilisateurs.
- Chaque événement est représenté par des actions (OUI ou NON).
- Le prix d'une action varie entre 0 $ et 1 $.
- Si le prix de l'action "OUI" est à 0,60 $, cela signifie que le marché estime qu'il y a 60 % de chances que l'événement se produise.
- Si vous avez raison, votre action passe à 1 $.
- Si vous avez tort, elle tombe à 0 $.

Ainsi, on considère souvent Polymarket comme une source d'information plus fiable que les sondages ou les experts. Pourquoi ? Parce que les gens mettent leur propre argent en jeu, ce qui les incite à être le plus objectifs possible. Surtout que la plateforme utilise la crypto-monnaie (le stablecoin USDC sur le réseau Polygon) : toutes les transactions sont visibles, rapides et ne dépendent pas d'une banque centrale.

Deux idées nous sont venues en tête. Premièrement, est-ce que Polymarket pourrait devenir un outil de nowcasting, notamment pour la prévision économique ? Par humilité, et pour ne pas concurrencer votre propre business, nous nous sommes plutôt demandé s'il serait possible de scraper les données de Polymarket afin de détecter d'éventuels délits d'initiés, pour ensuite en tirer des recommandations d'investissement sur des actifs financiers via une notification mobile.

---

## 3. Project Goal 🎯

Concrètement, le système surveille en temps réel les flux de transactions sur Polymarket. Lorsqu'un comportement statistiquement anormal est détecté sur un wallet, le système considère qu'il existe un signal potentiel de délit d'initié. Ce signal est ensuite transmis à un LLM (Claude), qui analyse le contexte du pari pour identifier quel actif financier serait le plus impacté par la résolution de l'événement, et dans quel sens il faudrait se positionner. La recommandation est finalement envoyée directement sur le téléphone de l'utilisateur via une notification **Pushover**.

**Qu'est-ce qu'un comportement anormal ?** Nous avons retenu trois critères systématiques :
- Un montant inhabituellement élevé (vis-à-vis de la moyenne de marché et de son propre wallet)
- Un timing suspect (WIP)
- Un compte nouvellement actif (WIP)

**Une solution réussie**, pour nous, c'est un système qui parvient à enchaîner correctement ces trois étapes :
1. Détecter un signal suspect de manière autonome
2. L'associer intelligemment à un actif financier pertinent (par exemple relier "opération militaire en Iran" au pétrole brut)
3. Formuler une recommandation directionnelle cohérente, le tout **avant que l'information ne soit publiquement connue**

L'ambition de ce projet est de mettre en lumière une réalité souvent ignorée du grand public : les marchés de prédiction, et Polymarket en particulier, peuvent constituer un vecteur de délits d'initiés tout aussi préoccupant que les marchés financiers traditionnels. Lorsqu'un insider place plusieurs centaines de milliers de dollars sur la chute d'un régime politique quelques heures avant une intervention militaire, il laisse une trace on-chain visible par tous, et c'est précisément cette trace que notre système cherche à exploiter.

Pour cela, nous avons loué un serveur **OVH en Allemagne** pour exécuter le code en continu et recevoir les alertes 24h/24. (Le serveur est effectivement loué, mais la fonctionnalité n'est pas encore implémentée).

---

## 4. Task Definition ⚙️

Ce projet mêle deux tâches distinctes mais complémentaires.

**Tâche 1 - Association d'un actif à un marché :** le modèle reçoit le titre et la catégorie du pari et produit une recommandation structurée en JSON indiquant quel actif acheter ou vendre parmi une liste prédéfinie de neuf instruments (S&P 500, EuroStoxx, Treasuries, Crude Oil, Gold, Natural Gas, Copper, USD, EUR).

**Tâche 2 - Détection de transactions anormales :** à partir des données de positions sur un marché Polymarket, le système cherche à identifier des comportements déviants (classification binaire : délit d'initié détecté ou non). Cette détection repose sur un score composite construit à partir de règles statistiques : principalement un Z-score sur les montants investis, croisé avec le timing de la transaction et le profil du wallet.

**Tâche 3 - Envoie d'une notification :** une fois le signal détecté, une notification est envoyée via PushOver afin de prévenir l'utilisateur de la présence d'un potentiel délit d'initié. Le message inclut les informations nécéssaires à la prise de décision (pari, Z-score, nom du parieur, actif concerné, action conseillée : Sell / Buy / Hold)

En termes d'évaluation, la performance est mesurée par l'**accuracy** de la recommandation LLM : on compare la direction suggérée par le modèle avec ce qui s'est effectivement passé sur le marché financier dans les heures ou jours suivant la résolution du pari. Une matrice de confusion complète a également été calculée sur notre jeu de données synthétique.

---

## 5. Dataset Description 📊

Ce projet présente une particularité notable : il n'existe pas de dataset préconstitué sur lequel s'appuyer. Les délits d'initiés avérés sont par nature rares, difficiles à identifier a posteriori, et ne font l'objet d'aucun label officiel. Nous avons donc dû construire notre base de données de toutes pièces.

Notre dataset final se compose de deux parties : une vingtaine de délits avérés identifiés grâce à des sources journalistiques, et un ensemble synthétique d'environ 100 titres Polymarket labellisés manuellement sur Google Sheets.

| Champ | Valeur |
|---|---|
| Nombre d'échantillons (réels) | 25 délits d'initiés avérés |
| Nombre d'échantillons (synthétiques) | 100 titres Polymarket labellisés manuellement |
| Nombre de features | 6 variables principales |
| Variable cible | action (buy/sell) + asset (parmi 9 instruments) |
| Source données brutes | API Polymarket (gamma-api, data-api, clob) |
| Source labels | Labellisation manuelle sur Google Sheets |

### Feature Description

| Feature | Description | Type | Rôle dans le système |
|---|---|---|---|
| `title` | Titre de l'événement Polymarket (ex: "US strikes Iran by June?") | Texte | Input principal du LLM pour le raisonnement macro |
| `tags` | Catégories associées à l'événement (ex: Middle East, Politics, Economy) | Catégoriel | Filtrage des événements non pertinents + contextualisation pour LLM |
| `totalBought` | Montant total investi par un wallet sur un outcome donné (en USDC) | Numérique continu | Variable centrale pour le calcul du Z-score et la détection d'anomalie |
| `outcome` | Sens de la position du wallet sur le marché (YES ou NO) | Catégoriel binaire | Détermine la direction du signal transmis au LLM |
| `liquidity` | Liquidité totale du marché en dollars | Numérique continu | Sert à contextualiser la taille du marché et normaliser les montants |

### Target Variable

| Attribut | Détail |
|---|---|
| **Nom** | action + asset (couple retourné par le LLM en JSON) |
| **Signification** | Recommandation d'investissement générée suite à la détection d'un signal anormal |
| **Valeurs possibles : action** | `buy` ou `sell` ou `hold` |
| **Valeurs possibles : asset** | US Equities (S&P 500 / Nasdaq), European Equities (EuroStoxx), US Treasury Bonds, Crude Oil, Gold, Natural Gas, Copper, US Dollar (USD), Euro (EUR), ou `NONE` si aucun actif n'est significativement impacté |

### Data Types

| Type de variable | Features concernées | Remarque |
|---|---|---|
| Texte libre | title, question | Traités directement par le LLM, pas d'encodage nécessaire |
| Catégoriel | tags, outcome | outcome est trinaire (YES/NO/Hold) ; tags sert au filtrage |
| Numérique continu | totalBought, liquidity | Utilisés pour le Z-score ; distribution très asymétrique |
| Temporel (implicite) | Timing des transactions | Non stocké directement, mais inféré pour la détection d'anomalie |

### Data Distribution

| Caractéristique | Observation |
|---|---|
| Déséquilibre des classes | Très fort : les délits avérés sont ultra-minoritaires face au volume total de transactions Polymarket |
| Distribution de `totalBought` | Fortement asymétrique (heavy-tailed) : quelques gros wallets concentrent l'essentiel des volumes |
| Distribution de `liquidity` | Hétérogène selon les marchés ; certains marchés récents ont une liquidité nulle |
| Équilibre YES/NO (dataset synthétique) | Équilibré manuellement lors de la labellisation pour éviter un biais de classification |

### Data Quality

| Problème identifié | Impact | Solution appliquée |
|---|---|---|
| Faible volumétrie des délits réels (25 cas) | Instabilité statistique : 1 cas = >2% de variation sur l'accuracy | Construction d'un dataset synthétique de 100 lignes |
| Biais de mémorisation du LLM | Accuracy artificiellement gonflée sur les données réelles | Évaluation distincte sur dataset synthétique |
| Biais de labellisation humaine | Les labels du dataset synthétique reflètent notre interprétation | À garder en tête dans l'interprétation des résultats |
| Marchés sans `acceptingOrders` | Données inutilisables pour la détection en temps réel | Filtrage explicite dans le preprocessing |

---

## 6. Data Preprocessing 🔧

Le preprocessing de ce projet est relativement léger comparé à un projet de ML classique, dans la mesure où une grande partie du traitement sémantique est déléguée au LLM. Néanmoins, plusieurs étapes sont indispensables.

**Filtrage par catégorie :** nous retirons systématiquement les événements tagués `Sports`, `Culture`, `Crypto` et `Elections`. Ces catégories présentent peu de surface d'attaque pour un délit d'initié ayant un impact mesurable sur des actifs financiers traditionnels.

**Filtrage des marchés clôturés :** les marchés dont le champ `acceptingOrders` est à `False` sont exclus. Parallèlement, les valeurs de `liquidity` manquantes sont remplacées par zéro.

**Calcul du Z-score :** l'étape de preprocessing la plus importante pour la détection. Il permet de normaliser les montants indépendamment de la taille du marché — un investissement de 10 000 $ peut être parfaitement banal sur un marché à 5 millions de dollars de volume, et extrêmement suspect sur un marché à 50 000 $.

**Construction du dataset synthétique :** pour le backtesting, nous avons construit manuellement un dataset à partir d'une centaine de titres Polymarket encore ouverts, en y associant à la main le sens du délit fictif et l'actif attendu. Cette étape était nécessaire pour contourner deux biais majeurs : la mémorisation des événements passés par le LLM, et l'instabilité statistique liée au trop faible nombre d'exemples.

> 💡 Nous aurions pu utiliser FinBERT, mais l'entraînement aurait nécessité un accès payant à des plateformes journalistiques (Financial Times, TechCrunch, Les Échos). Nous avons donc privilégié la simplicité et la robustesse d'une approche par scoring.

---

## 7. Modeling Approach 🤖

### Chosen Models

Notre approche se décompose en **deux blocs distincts** :

**Bloc 1 - Moteur de détection statistique (Z-score composite)**

Nous avons délibérément écarté un classifieur ML supervisé : la rareté des labels positifs et l'impossibilité d'obtenir un historique exhaustif des transactions rendaient l'entraînement peu crédible. Nous nous sommes appuyés sur une définition opérationnelle du délit d'initié, inspirée du Code monétaire et financier : montant anormalement élevé, timing suspect, et profil de compte inhabituel.

**Bloc 2 - LLM Claude (raisonnement & recommandation)**

C'est lui qui reçoit le titre du pari, sa catégorie et le sens du signal détecté, et qui produit en retour une recommandation structurée en JSON. Le choix de Claude s'explique par la qualité de ses capacités de raisonnement macro.

### Modeling Strategy

La stratégie repose sur une **séparation claire des responsabilités** :
- Les règles statistiques gèrent ce que le LLM fait mal (détecter une anomalie numérique)
- Le LLM gère ce que les règles ne peuvent pas faire (comprendre le sens géopolitique d'un pari)

Deux garde-fous contre les hallucinations :
- La liste des actifs éligibles est fournie explicitement dans le prompt, avec instruction de répondre `NONE` si aucun actif n'est impacté
- La température est fixée à **0.1** pour maximiser la cohérence et la reproductibilité

### Evaluation Metrics

Le backtesting a été conduit en deux phases :

| Phase | Dataset | Accuracy | Remarque |
|---|---|---|---|
| Phase 1 | Délits avérés réels | > 99% | Biaisé par la mémorisation du LLM |
| Phase 2 | Dataset synthétique (100 titres) | Voir matrice de confusion | Évaluation la plus fiable |

La métrique principale est l'**accuracy** : proportion de cas où la recommandation du LLM correspond à ce qui s'est réellement passé sur le marché. La matrice de confusion permet de distinguer les faux positifs (recommandation erronée → perte) des faux négatifs (signal manqué).

| Métrique de suivi | Précision | Rappel | F1-Score |
|-------------------|-----------|--------|----------|
| BUY               | 100,00%   | 97,73% | 98,85%   |
| SELL              | 100,00%   | 100,00%| 100,00%  |
| HOLD              | 97,92%    | 100,00%| 98,95%   |

> ⚠️ Ces métriques restent à interpréter avec prudence. L'accuracy élevée sur les données réelles est probablement gonflée par la mémorisation du LLM.

---

## 8. Project Structure 📁
├── data/
│   ├── delits_averes.csv          # 25 délits d'initiés réels documentés
│   └── dataset_synthetique.csv    # 100 titres Polymarket labellisés manuellement
├── notebooks/
│   └── Polybot_Officiel.ipynb     # Notebook principal (scraping + détection + LLM + push)
├── src/
│   ├── scraper.py                 # Appels API Polymarket (gamma-api, data-api, clob)
│   ├── detector.py                # Calcul Z-score et score composite de détection
│   └── llm_advisor.py             # Intégration Claude + envoi Pushover
├── docs/
│   └── rapport.pdf                # Rapport final du projet
├── selected_approach/             # Approche retenue et justification méthodologique
└── README.md

---

## 9. Installation ⚡

```bash
pip install -r requirements.txt
```

Les principales librairies utilisées sont `requests` pour les appels API Polymarket, `pandas` pour la manipulation des données, et `anthropic` pour l'intégration avec Claude.

Le projet nécessite quatre clés d'API à configurer dans votre environnement. Dans Google Colab, ces clés sont gérées via `userdata` ; en local, elles peuvent être stockées dans un fichier `.env` :

```env
CLAUDE_API_KEY=...
PUSHOVER_API_TOKEN=...
PUSHOVER_USER_KEY=...
OVH_SERVER_API=...
```

> Sans ces clés, la partie détection et scraping reste fonctionnelle, mais les recommandations LLM et les notifications mobiles seront désactivées.

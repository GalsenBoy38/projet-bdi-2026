# FestiBed – Groupe 3 – Étude technique du chargement des données

*Référence : MLD GLOBAL FINAL et UML technique ORM du 22/10/2026. Gabarits : `Gabarits_chargement_FestiBed_Groupe_3.xlsx`.*

## 1. Objectif

Le cahier des charges (« Intégration des données sources disponibles ») demande :

- d'utiliser les **données publiques** pour initier le jeu d'essai, après **nettoyage** et import ;
- de les **compléter par des données synthétiques** : quotas de Pass, hébergements, périodes de disponibilité, réservations ;
- d'atteindre un volume permettant des **tests de montée en charge et de concurrence** :
  - au moins **100 000 réservations** ;
  - au moins **la moitié du quota de Pass** réservée pour chaque festival ;
  - **chaque festival propose au moins 30 Pass** ;
  - des **périodes de festivals qui se chevauchent**.

Cette étude décrit, pour chaque table du MLD, d'où viennent les données, comment les transformer, dans quel ordre les charger, et ce qui manque dans les sources.

## 2. Sources disponibles (dossier `data/`)

| Fichier | Lignes | Format | Utilisé pour |
|---|---|---|---|
| `panorama-des-festivals.csv` | 3 136 | UTF-8 **avec BOM**, séparateur `;`, fins de ligne CRLF | REGION, DEPARTEMENT, COMMUNE, FESTIVAL |
| `hebergements_classes.csv` | 21 435 | UTF-8 sans BOM, séparateur `;` | ETABLISSEMENT et ses 6 sous-types |
| `panorama-des-festivals.json` / `.geojson` | – | Même contenu que le CSV | Non utilisés : le CSV suffit |

## 3. Architecture du chargement (ETL)

```
 CSV publics ──► 1. Extraction ──► 2. Nettoyage ──► 3. Géocodage ──► 4. Génération ──► 5. Chargement ──► 6. Contrôles
                  (lecture CSV)     (normalisation)   (API Adresse)    synthétique       Oracle / H2        (requêtes SQL)
                                                                       (graine fixe)
                                          └───────────── 1 fichier CSV par table (mêmes en-têtes que les gabarits Excel) ─────────────┘
```

**Choix technique recommandé**

- **Étapes 1 à 4 : un script Python.** Il utilise les modules `csv` et `datetime`, plus `Faker` pour les données synthétiques. Il produit un fichier `NN_TABLE.csv` (UTF-8, séparateur `;`) par onglet du gabarit. Avec une **graine aléatoire fixe**, le jeu est reproductible : même script, mêmes données. Cela facilite les tests et l'audit.
- **Étape 5 : deux cibles.**
  - **Oracle** : SQL*Loader (`sqlldr`) en *direct path*. C'est le plus rapide pour les gros volumes, comme les millions de nuitées et les 100 000 réservations.
  - **H2** (tests) : `INSERT INTO … SELECT * FROM CSVREAD(…)`.

  Dans les deux cas, le chargement se fait **hors de l'application**, sans passer par JPA. Insérer des millions de lignes une par une avec Hibernate serait trop lent.
- **Les gabarits Excel servent à documenter la structure**, et éventuellement à saisir à la main les données des scénarios (Jeff, Samantha, Ronald). **N'ouvrez pas et ne ré-enregistrez pas les CSV de chargement avec Excel** : Excel supprime les zéros initiaux (`01024` devient `1024`) et peut casser l'UTF-8.

## 4. Ordre de chargement

L'ordre est imposé par les clés étrangères. Ce sont les onglets `01` à `27` du classeur.

| # | Table | Origine | Volume visé |
|---|---|---|---|
| 1–3 | REGION → DEPARTEMENT → COMMUNE | Public | 20 / 102 / ≈ 1 568 |
| 4–8 | UTILISATEUR → UTILISATEUR_BACKOFFICE → ORGANISATEUR, HEBERGEUR → FESTIVALIER | Synthétique | ≈ 50 000 comptes |
| 9 | FESTIVAL | Mixte | 3 136 |
| 10–16 | ETABLISSEMENT puis HOTEL_DE_TOURISME, AUBERGE_COLLECTIVE, CAMPING, PARC_RESIDENTIEL_DE_LOISIRS, VILLAGE_DE_VACANCES, RESIDENCE_DE_TOURISME | Mixte | 21 430 |
| 17–20 | OPTION_HEBERGEMENT → HEBERGEMENT → PHOTO_HEBERGEMENT → EQUIPEMENT | Synthétique | ≈ 60 000 hébergements |
| 21–24 | RESERVATION → PAIEMENT → SELECTION → PASS | Synthétique | ≥ 100 000 réservations |
| 25 | NUITEE (après SELECTION, à cause de `idSelection`) | Synthétique | 1 à 3 millions |
| 26–27 | NOTATION_FESTIVAL, NOTATION_ETABLISSEMENT | Synthétique | ≈ 30 000 chacune |

Après le chargement, **recalez les séquences et les colonnes IDENTITY** sur `MAX(id) + 1`. Sinon, la première insertion faite par l'application provoquera une violation de clé primaire.

## 5. Chargement des données existantes : règles de nettoyage

Le détail colonne par colonne se trouve dans l'onglet `99_Correspondances` du classeur. Les points importants, mesurés sur les fichiers réels, sont les suivants.

### 5.1 Festivals (`panorama-des-festivals.csv`)

| Problème constaté | Effectif | Règle de transformation |
|---|---|---|
| Code INSEE sans zéro initial (`1024`) | 183 | `zfill(5)` → `01024` (la Corse `2A…`/`2B…` est déjà correcte) |
| Code postal et département sans zéro initial (`1340`, `1`) | idem | `zfill(5)` pour le code postal, `zfill(2)` pour le département |
| Coordonnées dans une seule colonne `"49.81, 2.80"` | 3 134 (2 vides) | Découper sur la virgule → `latitude`, `longitude` de COMMUNE |
| Même code INSEE avec plusieurs libellés de commune | 69 codes | Garder le libellé le plus fréquent |
| Domaine : casse incohérente (`Musiques Actuelles`, `Divers spectacle vivant`) | 16 libellés → 13 | Majuscules, sans accents, espaces remplacés par `_`, puis correspondance avec l'enum `Domaine` |
| Complément domaine : 139 valeurs distinctes, alors que l'enum `SousDomaine` en compte 6 | 1 092 vides | Valeur de l'enum si elle existe, sinon NULL (voir la décision à prendre en §7) |
| Périodicité : `Annuelle`/`annuelle`/`ANNUELLE`, `Bi-annuelle`/`Bi-Annuelle`, `Biennale` sans précision | 510 vides | Correspondance avec les 5 valeurs de l'enum ; vide → NULL ; `Biennale` seule → `IRREGULIERE` ou NULL |
| Mois de début `"07 (juillet)"` | 3 136 | `int(valeur[:2])` |
| N° d'identification vide ou générique (`AD999`, `CE999`…) | 38 vides, 21 doublons | Charger tel quel : **pas de contrainte UNIQUE** sur `numIdentification` |
| N° d'édition au format décimal (`"17.0"`) | – | Colonne absente du MLD : ignorée |
| Dates « anciennes » (2017 à 2020) | 339 vides | Conservées dans `dateDebutAncien` et `dateFinAncien`, et servent à calculer les dates 2027 (§6) |
| Colonnes absentes du modèle (autres communes, soutiens, commentaires, enquête DRAC) | – | Ignorées : choix de rétro-conception à justifier dans le rapport |

Une région, un département ou une commune n'est inséré **qu'une fois**. On garde un dictionnaire `libellé → id` pour retrouver les clés étrangères.

### 5.2 Établissements (`hebergements_classes.csv`)

| Problème constaté | Effectif | Règle |
|---|---|---|
| Valeur `-` utilisée pour « non renseigné » | toutes les colonnes optionnelles | `-` → NULL |
| Dates au format `jj/mm/aaaa` | 21 435 | `datetime.strptime(v, "%d/%m/%Y")` |
| `classement prorogé` = `oui`/`non` | 21 435 | → 1 / 0 |
| Classement `3 étoiles` | 21 286 | → `TROIS_ETOILES`, etc. |
| Classement `Auberge collective` / `Aire naturelle` | 116 / 33 | **Absents de l'enum `Classement`** : il faut décider (voir §7) |
| Typologie → sous-type (héritage JOINED) | 6 valeurs | HÔTEL → HOTEL_DE_TOURISME ; CAMPING → CAMPING ; etc. Une ligne dans ETABLISSEMENT **plus** une ligne dans le sous-type, avec le même id |
| Colonnes de nombre selon le type (chambres, emplacements, unités, logements) | – | Seule la colonne qui correspond au sous-type est utilisée |
| Doublons (nom + adresse + code postal) | 5 | Garder la ligne la plus récente (date de classement) |
| Code postal vide / commune vide | 1 / 2 | Compléter à la main, ou les retrouver par géocodage |
| **Pas de latitude/longitude, pas de code INSEE, pas de téléphone** | 21 435 | Voir §5.3 et §7 |

### 5.3 Géocodage des établissements (obligatoire)

Le cahier des charges impose : « les informations géographiques et géoréférencées doivent être utilisées pour la recherche des établissements et des hébergements par localisation ». Or le CSV des hébergements **ne contient aucune coordonnée**. Seules 553 des 6 468 communes d'établissements figurent aussi dans le fichier des festivals : on ne peut donc pas récupérer les coordonnées par la commune.

Solution : le **géocodage par lot** de la Base Adresse Nationale (API Adresse, gratuite, service d'État).

- Envoyez un CSV `id;adresse;code_postal;commune` au service de géocodage par lot. Il s'agit de l'endpoint `/search/csv/` de l'API Adresse, aujourd'hui hébergée par la Géoplateforme IGN. Paramètres : `columns=adresse`, `columns=commune`, `postcode=code_postal`.
- La réponse ajoute les colonnes `latitude`, `longitude`, `result_score` et `result_citycode` (code INSEE).
- Si `result_score < 0.5`, prenez le **centre de la commune** fourni par l'API Géo (`geo.api.gouv.fr/communes`).
- Envoyez des lots de quelques milliers de lignes et **gardez le résultat en cache** (fichier CSV versionné) : le géocodage ne se fait qu'une fois.

## 6. Données synthétiques : règles de génération

| Donnée | Règle | Justification |
|---|---|---|
| `dateDebutFestival` / `dateFinFestival` | Date ancienne transposée en **2027** (même mois et même jour). Sinon, un jour tiré dans `moisDebut` 2027, pour une durée de 2 à 4 jours | La source ne contient que des dates passées, ou seulement un mois |
| Chevauchements | Plusieurs festivals proches (même département) sur des dates qui se recouvrent, notamment en juillet et en août | Exigé pour tester la disponibilité et la concurrence |
| `quotaPass` | 30 à 60 pour 75 % des festivals, 100 à 500 pour les gros. **Total ≈ 250 000** | Au moins 30 Pass ; au moins 100 000 réservations, d'au moins 1 Pass chacune, et ≤ quota |
| Pass réservés | Pour chaque festival, entre 50 % et 90 % du quota | Au moins la moitié réservée, et des Pass restent disponibles pour les tests |
| `prixPass` | Selon le domaine (ex. 25 à 250 €) | – |
| Comptes | ≈ 47 000 festivaliers de test (`fournisseurAuth` NULL ou TEST, e-mail `testNNNNN@festibed.test`), 500 organisateurs, 2 500 hébergeurs | Les comptes de peuplement ne s'authentifient pas par un réseau social |
| `motDePasseHache` | Hash **BCrypt** d'un mot de passe de test, calculé une fois et réutilisé | Ne jamais stocker un mot de passe en clair |
| HEBERGEMENT | 1 à 5 offres par établissement. Le type dépend de la typologie : hôtel/auberge → chambre simple/double ; camping/parc → emplacement ; village/résidence → bungalow. La capacité ne dépasse pas la capacité d'accueil | Le cahier des charges demande des hébergements créés sans lien avec un festival |
| NUITEE | Une ligne par nuit disponible, **autour des périodes de festivals** (pas toute l'année). `idSelection` est NULL si la nuit est libre, renseigné si elle est réservée | Le volume reste maîtrisé (1 à 3 millions de lignes), et la clé primaire (hébergement, date) empêche toute double réservation |
| RESERVATION / SELECTION / PASS | Une réservation = 1 à 3 sélections ; une sélection = 1 festival, 1 à 4 Pass, et des nuitées dont la **capacité totale est ≥ nombre de Pass** | Respecte la règle de cohérence Pass / capacité du modèle de tâches et du BPMN |
| PAIEMENT | Statut `ACCEPTE`, montant = Pass + nuitées | Le paiement n'est pas développé, mais la table existe |
| Données des scénarios | Musilac / camping du Sierroz (scénario 1), festivals autour d'Autun fin juillet, Jazz à Couches, Saint Rock, hôtel Les Arcades (scénarios 2 et 3) | Ces données doivent **exister** pour la démonstration |

## 7. Ce qui manque : données absentes et décisions à prendre

### 7.1 Données absentes des sources

1. **Latitude et longitude des établissements** : à obtenir par géocodage (§5.3). C'est indispensable pour la recherche par localisation.
2. **Téléphone des établissements** (`telephoneEtablissement`) : absent. La colonne doit rester **NULL autorisé**, ou être remplie avec des données synthétiques.
3. **Dates 2027 des festivals, quotas, prix, statut actif, organisateur** : à générer (§6).
4. **Toutes les offres d'hébergement** (HEBERGEMENT, NUITEE, PHOTO, OPTION, EQUIPEMENT) : rien dans les sources.
5. **Utilisateurs, réservations, sélections, Pass, paiements, notations** : entièrement synthétiques.
6. **Code INSEE des établissements** : absent, mais `result_citycode` du géocodage le fournit si vous en avez besoin.

### 7.2 Écarts entre les données et le modèle (à trancher dans l'équipe)

| Écart | Option recommandée |
|---|---|
| L'enum `Classement` n'a que 1 à 5 étoiles, alors que 149 établissements sont classés « Auberge collective » ou « Aire naturelle », et que `classement` est NOT NULL | Ajouter `AUBERGE_COLLECTIVE` et `AIRE_NATURELLE` à l'enum |
| L'enum `SousDomaine` compte 6 valeurs pour 139 compléments distincts (Humour, Cirque, Documentaire…) | Garder les 6 valeurs et mettre NULL pour les autres, en le justifiant ; ou transformer le sous-domaine en texte libre |
| `numIdentification` n'est pas unique dans la source (doublons `XX999`, valeurs vides) | Pas de contrainte UNIQUE ; la clé reste `idFestival` |
| Festivals sur deux mois (« 7.5 », etc.) | Seul `moisDebut` est conservé : perte acceptée |
| Commune : le MLD prévoit `VARCHAR(40)`, et le libellé le plus long fait 28 caractères dans les festivals et 38 dans les hébergements | OK |
| ETABLISSEMENT n'a pas de clé étrangère vers COMMUNE (la commune y est stockée en texte) | OK, puisque la recherche se fait par latitude/longitude. À justifier |

## 8. Contrôles après chargement

À exécuter et à présenter lors de l'audit :

```sql
-- Volumes
SELECT COUNT(*) FROM RESERVATION;                    -- >= 100 000
SELECT MIN(quotaPass) FROM FESTIVAL;                 -- >= 30

-- Au moins la moitié du quota réservée, jamais plus que le quota
SELECT f.idFestival, f.quotaPass, COUNT(p.idPass) AS reserves
FROM FESTIVAL f LEFT JOIN PASS p ON p.idFestival = f.idFestival
GROUP BY f.idFestival, f.quotaPass
HAVING COUNT(p.idPass) < f.quotaPass / 2 OR COUNT(p.idPass) > f.quotaPass;   -- 0 ligne attendue

-- Établissements non géocodés
SELECT COUNT(*) FROM ETABLISSEMENT WHERE latitudeEtablissement IS NULL;      -- 0 attendu

-- Chaque établissement a exactement un sous-type
SELECT COUNT(*) FROM ETABLISSEMENT e
WHERE (SELECT COUNT(*) FROM HOTEL_DE_TOURISME h WHERE h.idEtablissement = e.idEtablissement)
    + (SELECT COUNT(*) FROM CAMPING c WHERE c.idEtablissement = e.idEtablissement)
    + (SELECT COUNT(*) FROM AUBERGE_COLLECTIVE a WHERE a.idEtablissement = e.idEtablissement)
    + (SELECT COUNT(*) FROM PARC_RESIDENTIEL_DE_LOISIRS p WHERE p.idEtablissement = e.idEtablissement)
    + (SELECT COUNT(*) FROM VILLAGE_DE_VACANCES v WHERE v.idEtablissement = e.idEtablissement)
    + (SELECT COUNT(*) FROM RESIDENCE_DE_TOURISME r WHERE r.idEtablissement = e.idEtablissement) <> 1;  -- 0

-- Festivals qui se chevauchent (doit être > 0)
SELECT COUNT(*) FROM FESTIVAL a JOIN FESTIVAL b
  ON a.idFestival < b.idFestival
 AND a.dateDebutFestival <= b.dateFinFestival AND b.dateDebutFestival <= a.dateFinFestival;
```

Mettez ensuite à jour les statistiques de l'optimiseur Oracle (`DBMS_STATS.GATHER_SCHEMA_STATS`) avant les tests de performance.

## 9. Exemple de chargement Oracle (SQL*Loader)

```
-- commune.ctl
OPTIONS (DIRECT=TRUE, SKIP=1)
LOAD DATA CHARACTERSET UTF8
INFILE '03_COMMUNE.csv'
APPEND INTO TABLE COMMUNE
FIELDS TERMINATED BY ';' OPTIONALLY ENCLOSED BY '"' TRAILING NULLCOLS
(codeInsee, nomCommune, latitude DECIMAL EXTERNAL, longitude DECIMAL EXTERNAL, codeDepartement)
```

Commande : `sqlldr userid=festibed/***@//hote:1521/service control=commune.ctl log=commune.log`

Équivalent H2 (tests) :

```sql
INSERT INTO COMMUNE SELECT * FROM CSVREAD('03_COMMUNE.csv', NULL, 'charset=UTF-8 fieldSeparator=;');
```

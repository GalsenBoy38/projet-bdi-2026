# FestiBed – Groupe 3 – Étude technique du chargement des données

*Référence : schéma `docs/JPA_modelisation/3_peuplement_donnees/schema_festibed.py` (source unique), MLD `docs/Output_Diagramme/MLD_GLOBAL_FINAL.puml` et UML technique ORM `UML_technique_ORM.puml`, mis à jour le 03/11/2026 avec l'intégration d'OpenStreetMap. Gabarits : `docs/JPA_modelisation/2_insertion_excel/Gabarits_insertion_vides.xlsx`.*

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
| `hebergements_classes.csv` | 21 435 | UTF-8 sans BOM, séparateur `;` | ETABLISSEMENT et ses 6 sous-types classés |
| `osm-france-tourism-accommodation.csv` | 60 203 | UTF-8 **avec BOM**, séparateur `;`, CRLF, 2 champs entre guillemets sur plusieurs lignes | Complément des établissements classés (téléphone, e-mail, position) ; ETABLISSEMENT_NON_CLASSE ; COMMUNE |
| `panorama-des-festivals.json` / `.geojson` | – | Même contenu que le CSV | Non utilisés : le CSV suffit |

Le fichier OSM est un extrait **OpenStreetMap** (balise `tourism=*` : hôtels, chambres d'hôtes, gîtes, campings…) publié sous licence **ODbL** : toute réutilisation publique doit mentionner « © les contributeurs d'OpenStreetMap ».

Services publics utilisés (résultats mis en cache dans `3_peuplement_donnees/cache/`, versionnés) :

| Service | Usage | Cache |
|---|---|---|
| API Adresse (BAN) `/search/csv/` | Géocodage des adresses des établissements classés | `geocodage_etablissements.csv` |
| API Adresse (BAN) `/reverse/csv/` | Adresse et code postal des lieux OSM non classés | `geocodage_inverse_osm.csv` |
| API Géo `geo.api.gouv.fr/communes` | Code postal et centre de chaque commune (repli) | `communes_api_geo.csv` |

## 3. Architecture du chargement (ETL)

```
 CSV publics ──► 1. Extraction ──► 2. Nettoyage ──► 3. Géocodage + ──► 4. Génération ──► 5. Chargement ──► 6. Contrôles
                  (lecture CSV)     (normalisation)   rapprochement OSM   synthétique       Oracle / H2        (requêtes SQL)
                                                      (BAN, API Géo)      (graine fixe)
                                          └───────────── 1 fichier CSV par table (mêmes en-têtes que les gabarits Excel) ─────────────┘
```

**Choix technique**

- **Étapes 1 à 4 : un script Python** (`generer_peuplement.py`, bibliothèque standard uniquement). Il produit un fichier `NN_TABLE.csv` (UTF-8, séparateur `;`) par table. Avec une **graine aléatoire fixe** et les caches de géocodage, le jeu est reproductible à l'octet près.
- **Étape 5 : deux cibles.**
  - **Oracle** : SQL*Loader (`sqlldr`). C'est le plus rapide pour les gros volumes (≈ 680 000 nuitées, 220 000 Pass).
  - **H2** (tests) : `INSERT INTO … SELECT … FROM CSVREAD(…)`.

  Dans les deux cas, le chargement se fait **hors de l'application**, sans passer par JPA. Insérer des millions de lignes une par une avec Hibernate serait trop lent.
- **Les gabarits Excel servent à documenter la structure** et à saisir à la main les données des scénarios. **N'ouvrez pas et ne ré-enregistrez pas les CSV de chargement avec Excel** : Excel supprime les zéros initiaux (`01024` devient `1024`) et peut casser l'UTF-8.

## 4. Ordre de chargement

L'ordre est imposé par les clés étrangères (fichiers `01` à `28`).

| # | Table | Origine | Volume |
|---|---|---|---|
| 1–3 | REGION → DEPARTEMENT → COMMUNE | Public (festivals + OSM + API Géo) | 20 / 104 / 13 633 |
| 4–8 | UTILISATEUR → FESTIVALIER, UTILISATEUR_BACKOFFICE → ORGANISATEUR, HEBERGEUR | Synthétique | 50 000 comptes |
| 9 | FESTIVAL | Mixte | 3 136 |
| 10–17 | ETABLISSEMENT puis HOTEL_DE_TOURISME, AUBERGE_COLLECTIVE, CAMPING, PARC_RESIDENTIEL_DE_LOISIRS, VILLAGE_DE_VACANCES, RESIDENCE_DE_TOURISME, **ETABLISSEMENT_NON_CLASSE** | Mixte | 56 724 (21 430 classés + 35 294 non classés) |
| 18–21 | OPTION_HEBERGEMENT → HEBERGEMENT → PHOTO_HEBERGEMENT → EQUIPEMENT | Synthétique | 111 584 hébergements |
| 22–25 | RESERVATION → PAIEMENT → SELECTION → PASS | Synthétique | 113 168 réservations, 220 247 Pass |
| 26 | NUITEE (après SELECTION, à cause de `idSelection`) | Synthétique | 682 643 |
| 27–28 | NOTATION_FESTIVAL, NOTATION_ETABLISSEMENT | Synthétique | 30 000 chacune |

COMMUNE contient désormais toutes les communes **des festivals et des établissements** (clé étrangère `ETABLISSEMENT.codeInsee`). Après le chargement, **recalez les séquences** (`03_sequences_*.sql`), sinon la première insertion de l'application violera une clé primaire.

## 5. Chargement des données existantes : règles de nettoyage

### 5.1 Festivals (`panorama-des-festivals.csv`)

| Problème constaté | Effectif | Règle de transformation |
|---|---|---|
| Code INSEE sans zéro initial (`1024`) | 183 | `zfill(5)` → `01024` (la Corse `2A…`/`2B…` est déjà correcte) |
| Code postal et département sans zéro initial (`1340`, `1`) | idem | `zfill(5)` pour le code postal, `zfill(2)` pour le département |
| Coordonnées dans une seule colonne `"49.81, 2.80"` | 3 134 (2 vides) | Découper sur la virgule → `latitude`, `longitude` de COMMUNE |
| Même code INSEE avec plusieurs libellés de commune | 69 codes | Garder le libellé le plus fréquent |
| Domaine : casse incohérente (`Musiques Actuelles`, `Divers spectacle vivant`) | 16 libellés → 13 | Majuscules, sans accents, espaces remplacés par `_`, puis correspondance avec l'enum `Domaine` |
| Complément domaine : 139 valeurs distinctes pour 6 valeurs dans l'enum `SousDomaine` | 1 665 NULL | Valeur de l'enum si elle existe, sinon NULL (choix justifié en §7.2) |
| Périodicité : `Annuelle`/`annuelle`/`ANNUELLE`, `Bi-annuelle`/`Bi-Annuelle`, `Biennale` sans précision | 513 NULL | Correspondance avec les 5 valeurs de l'enum ; vide ou `Biennale` seule → NULL |
| Mois de début `"07 (juillet)"` | 3 136 | `int(valeur[:2])` |
| N° d'identification vide ou générique (`AD999`, `CE999`…) | 38 vides, 21 doublons | Chargé tel quel : **pas de contrainte UNIQUE** sur `numIdentification` |
| Dates « anciennes » (2017 à 2020) | 339 vides | Conservées dans `dateDebutAncien` et `dateFinAncien`, et servent à calculer les dates 2027 (§6) |
| Colonnes absentes du modèle (autres communes, soutiens, commentaires, enquête DRAC, n° d'édition) | – | Ignorées : choix de rétro-conception |

### 5.2 Établissements classés (`hebergements_classes.csv`)

| Problème constaté | Effectif | Règle |
|---|---|---|
| Valeur `-` utilisée pour « non renseigné » | toutes les colonnes optionnelles | `-` → NULL |
| Dates au format `jj/mm/aaaa` | 21 435 | `datetime.strptime(v, "%d/%m/%Y")` |
| `classement prorogé` = `oui`/`non` | 21 435 | → 1 / 0 |
| Classement `3 étoiles`, `Auberge collective`, `Aire naturelle` | 21 286 / 116 / 33 | → `TROIS_ETOILES`, …, `AUBERGE_COLLECTIVE`, `AIRE_NATURELLE` |
| Typologie → sous-type (héritage JOINED) | 6 valeurs | HÔTEL → HOTEL_DE_TOURISME ; CAMPING → CAMPING ; etc. Une ligne dans ETABLISSEMENT **plus** une ligne dans le sous-type, avec le même id |
| Colonnes de nombre selon le type (chambres, emplacements, unités, logements) | – | Seule la colonne qui correspond au sous-type est utilisée |
| Doublons (nom + adresse + code postal) | 5 | Garder la ligne la plus récente (date de classement) |
| **Pas de coordonnées, pas de code INSEE, pas de téléphone ni d'e-mail** | 21 435 | Géocodage BAN (§5.3) puis rapprochement OSM (§5.4) |

### 5.3 Géocodage des établissements classés (BAN)

Le cahier des charges impose : « les informations géographiques et géoréférencées doivent être utilisées pour la recherche des établissements et des hébergements par localisation ». Le CSV des établissements classés **ne contient aucune coordonnée**.

- Le script envoie un CSV `cle;adresse;code_postal;commune` à l'endpoint `/search/csv/` de l'API Adresse (paramètres `columns=adresse`, `columns=commune`, `postcode=code_postal`), par lots de 4 000.
- La réponse fournit `latitude`, `longitude`, `result_score` et `result_citycode` (code INSEE → `ETABLISSEMENT.codeInsee`).
- Résultat retenu si `result_score ≥ 0,4` : **20 731 sur 21 430** (97 %).

### 5.4 OpenStreetMap (`osm-france-tourism-accommodation.csv`)

**Nettoyage**

| Problème constaté | Effectif | Règle |
|---|---|---|
| `wilderness_hut` (refuge non gardé, gratuit, non réservable) | 1 143 | Écarté |
| Lieu sans nom (chalets, appartements…) | 7 018 | Écarté : impossible à présenter à un festivalier |
| Identifiant OSM non unique entre types d'objets (`node/…` et `relation/…`) | 418 relations | Clé `osmRef` = `type/id` (« node/11773691645 »), UNIQUE |
| Coordonnées dans une seule colonne `"45.44, -0.43"` | 60 203 | Découpées → `latitudeEtablissement`, `longitudeEtablissement` |
| Plusieurs valeurs séparées par `;` (téléphone, e-mail) | 425 | Première valeur seulement, tronquée (30 / 150 caractères) ; e-mail sans `@` → NULL |
| `Nombre étoiles` = 0, 6 ou 7 (saisies erronées) | 35 | → NULL ; étoiles **déclaratives**, rangées dans `nbEtoilesDeclarees`, jamais dans `classement` |
| `Nombre chambres` négatif (`-4`) ou nul | 1 | → NULL |
| `Capacité` d'un camping = nombre d'emplacements (convention OSM) | – | Capacité d'accueil = emplacements × 3 |
| Pas d'adresse ni de code postal | 60 203 | Géocodage **inverse** BAN : adresse retenue si à ≤ 200 m et dans la même commune ; code postal de la BAN, sinon celui de l'API Géo |
| Même lieu en double (même nom, même commune, à < 200 m) | 562 | On garde le plus renseigné |
| Type OSM → `TypeNonClasse` | 9 valeurs | hotel → HOTEL, motel → MOTEL, guest_house → CHAMBRE_D_HOTES, chalet → GITE_CHALET, apartment → APPARTEMENT, hostel → AUBERGE_DE_JEUNESSE, camp_site → CAMPING, caravan_site → AIRE_DE_CAMPING_CAR, alpine_hut → REFUGE_GARDE |
| Capacité, lits et chambres tous absents | ≈ 41 000 lieux | Estimée : capacité OSM, sinon nombre de lits, sinon chambres × 2, sinon valeur par type (gîte 6, appartement 4, chambre d'hôtes 8, hôtel 40, camping 150…) |

**Rapprochement avec les établissements classés**

Il n'existe aucune clé commune entre les deux sources : le rapprochement est heuristique.

1. Candidats : lieux OSM de la même commune (code INSEE de la BAN ; à défaut, même nom de commune), ou à moins de 2 km du point BAN.
2. Comparaison des noms sur les **mots significatifs** : sans accents ni articles, sans mots génériques (« hôtel », « camping »…) et **sans les mots du nom de la commune** (sinon « B&B Hôtel Cholet Sud » serait apparié à « B&B Hôtel Cholet Centre »). Similarité = mots communs / mots du nom le plus court, **≥ 0,5 exigé**.
3. Bonus de proximité (< 150 m) et de type compatible (un camping classé ne peut être rapproché d'un hôtel OSM qu'à moins de 150 m).
4. Affectation un pour un, par score décroissant puis distance croissante.

Résultat : **16 186 établissements classés sur 21 430 (76 %)** retrouvés dans OSM. Pour eux : téléphone (7 041), e-mail (3 673), site web manquant (48), position du bâtiment OSM à la place du point d'adresse BAN, et coordonnées pour **406 établissements que la BAN n'avait pas trouvés**. Un échantillon de 40 paires contrôlées à la main donne ≈ 95 % de paires justes ; les erreurs restantes concernent des sous-marques d'une même chaîne (Ibis / Ibis Budget).

**Établissements non classés**

Les **35 294** lieux OSM restants deviennent des établissements non classés : une ligne dans ETABLISSEMENT (avec `classement`, `dateClassement` et `classementProroge` à NULL) et une ligne dans ETABLISSEMENT_NON_CLASSE. Répartition : chambres d'hôtes 8 141, hôtels non classés 7 752, gîtes/chalets 5 893, appartements 4 333, campings 3 944, aires de camping-car 3 439, auberges de jeunesse 1 064, refuges gardés 639, motels 89. 2 319 n'ont pas d'adresse à moins de 200 m (refuges, campings isolés) : `adresse` est NULL, la position GPS suffit pour la recherche.

## 6. Données synthétiques : règles de génération

| Donnée | Règle | Justification |
|---|---|---|
| `dateDebutFestival` / `dateFinFestival` | Date ancienne transposée en **2027** (même mois et même jour). Sinon, un jour tiré dans `moisDebut` 2027, pour une durée de 2 à 4 jours | La source ne contient que des dates passées, ou seulement un mois |
| Chevauchements | Nombreux festivals d'un même département aux dates qui se recouvrent (5 539 paires), surtout en juillet-août | Exigé pour tester la disponibilité et la concurrence |
| `quotaPass` | 30 à 80 pour 70 % des festivals, 100 à 300 pour les gros | Au moins 30 Pass ; au moins 100 000 réservations |
| Pass réservés | Pour chaque festival, entre 50 % et 90 % du quota | Au moins la moitié réservée, et des Pass restent disponibles pour les tests |
| `prixPass` | Selon le domaine (ex. 35 à 180 € pour les musiques actuelles) | – |
| Comptes | 47 000 festivaliers de test (`fournisseurAuth` NULL, e-mail `@festibed.test`), 500 organisateurs, 2 500 hébergeurs | Les comptes de peuplement ne s'authentifient pas par un réseau social |
| `motDePasseHache` | Hash **BCrypt** d'un mot de passe de test, calculé une fois et réutilisé | Ne jamais stocker un mot de passe en clair |
| HEBERGEMENT | 1 à 4 offres par établissement, selon le type : hôtel → chambre simple/double ; camping/parc/aire → emplacement ; village/résidence → bungalow ; gîte/appartement → **logement entier** ; auberge de jeunesse/refuge → **lit en dortoir**. Capacité ≤ capacité d'accueil. Prix selon les étoiles (classement officiel, sinon étoiles déclarées dans OSM, sinon 2) | Le cahier des charges demande des hébergements créés sans lien avec un festival |
| NUITEE | Une ligne par nuit disponible, **autour des périodes de festivals** (pas toute l'année). `idSelection` est NULL si la nuit est libre | Volume maîtrisé ; la clé primaire (hébergement, date) empêche toute double réservation |
| RESERVATION / SELECTION / PASS | Une réservation = 1 à 3 sélections ; une sélection = 1 festival, 1 à 4 Pass, et des nuitées dont la **capacité totale est ≥ nombre de Pass** | Règle de cohérence Pass / capacité du modèle de tâches et du BPMN |
| PAIEMENT | Statut `NON_GERE`, montant = Pass + nuitées | Le paiement n'est pas développé, mais la table existe |
| Données des scénarios | Musilac / camping du Sierroz (scénario 1), festivals autour d'Autun fin juillet, Jazz à Couches, Saint Rock, hôtel des Arcades (scénarios 2 et 3), compte de Ronald (scénario 4) | Ces données doivent **exister** pour la démonstration |

## 7. Ce qui manque : données absentes et décisions prises

### 7.1 Données absentes des sources

1. **Coordonnées** : 293 établissements classés (0,5 %) n'ont de position ni dans la BAN ni dans OSM ; ils n'apparaissent pas dans une recherche par distance.
2. **Téléphone et e-mail** : fournis par OSM pour 18 339 et 8 889 établissements ; NULL pour les autres (colonnes facultatives).
3. **Adresse** des lieux OSM : reconstituée par géocodage inverse, NULL pour 2 319 lieux isolés.
4. **Dates 2027 des festivals, quotas, prix, organisateur** : générés (§6).
5. **Toutes les offres d'hébergement** (HEBERGEMENT, NUITEE, PHOTO, OPTION, EQUIPEMENT) et **utilisateurs, réservations, sélections, Pass, paiements, notations** : entièrement synthétiques.

### 7.2 Écarts entre les données et le modèle : décisions

| Écart | Décision |
|---|---|
| L'enum `Classement` n'avait que 1 à 5 étoiles, alors que 149 établissements sont classés « Auberge collective » ou « Aire naturelle » | `AUBERGE_COLLECTIVE` et `AIRE_NATURELLE` ajoutés à l'enum |
| OSM recense des hébergements **non classés**, qui n'ont ni classement ni date de classement | `classement`, `dateClassement`, `classementProroge` deviennent facultatifs, avec un CHECK « tous NULL ou tous renseignés » ; nouveau sous-type ETABLISSEMENT_NON_CLASSE (héritage JOINED). Les 6 sous-classes classées exigent toujours le classement dans leur constructeur JPA |
| Les étoiles OSM sont déclaratives | Rangées dans `nbEtoilesDeclarees` (non classés), jamais confondues avec le classement officiel |
| Gîtes, appartements, dortoirs n'entraient dans aucun `TypeHebergement` | Ajout de `LOGEMENT_ENTIER` et `LIT_EN_DORTOIR` |
| ETABLISSEMENT n'avait pas de clé étrangère vers COMMUNE | `codeInsee` (FK vers COMMUNE, facultatif) ajouté : OSM et la BAN fournissent le code INSEE. `nomCommuneEtablissement` reste le libellé postal (« PARIS 9E ARRONDISSEMENT ») |
| Noms OSM jusqu'à 99 caractères | `nomCommercial` passe de 80 à 100 caractères |
| L'enum `SousDomaine` compte 6 valeurs pour 139 compléments distincts | Les 6 valeurs sont gardées, NULL pour les autres (1 665 festivals) : choix de modélisation assumé |
| `numIdentification` n'est pas unique dans la source | Pas de contrainte UNIQUE ; la clé reste `idFestival` |
| Festivals sur deux mois (« 7.5 ») | Seul `moisDebut` est conservé : perte acceptée |

**À reporter dans le MCD Looping** (`docs/Input_Diagramme/MCD_GLOBAL_FINAL-20-10-2026.loo`, fichier binaire non modifiable par script) : entité ETABLISSEMENT (attributs `codeInsee` via une association « Situer » 0,n – 0,1 vers COMMUNE, `emailEtablissement`, `osmRef` ; classement facultatif) ; nouvelle sous-entité ETABLISSEMENT_NON_CLASSE (`typeNonClasse`, `nbEtoilesDeclarees`, `nbChambres`, `nbLits`) dans l'héritage d'ETABLISSEMENT ; valeurs `LOGEMENT_ENTIER` et `LIT_EN_DORTOIR` pour le type d'hébergement. Le MCD de rétro-conception reçoit l'entité LIEU_OSM (voir `docs/Output_Diagramme/MLD_retro_conception.puml`).

## 8. Contrôles après chargement

`04_controles.sql` : toutes les lignes « anomalies » doivent valoir 0 (vérifié sur H2 avec le peuplement complet).

```sql
-- Volumes
SELECT COUNT(*) FROM RESERVATION;                    -- >= 100 000
SELECT MIN(quotaPass) FROM FESTIVAL;                 -- >= 30

-- Au moins la moitié du quota réservée, jamais plus que le quota
SELECT COUNT(*) FROM FESTIVAL WHERE nbPassVendus * 2 < quotaPass OR nbPassVendus > quotaPass;   -- 0

-- Chaque établissement a exactement un sous-type parmi les 7 (6 classés + non classé)
-- Classement renseigné si et seulement si l'établissement n'est pas dans ETABLISSEMENT_NON_CLASSE
SELECT COUNT(*) FROM ETABLISSEMENT e
WHERE (e.classement IS NULL
       AND NOT EXISTS (SELECT 1 FROM ETABLISSEMENT_NON_CLASSE x WHERE x.idEtablissement = e.idEtablissement))
   OR (e.classement IS NOT NULL
       AND EXISTS (SELECT 1 FROM ETABLISSEMENT_NON_CLASSE x WHERE x.idEtablissement = e.idEtablissement));  -- 0

-- Festivals qui se chevauchent (doit être > 0)
SELECT COUNT(*) FROM FESTIVAL a JOIN FESTIVAL b
  ON a.idFestival < b.idFestival
 AND a.dateDebutFestival <= b.dateFinFestival AND b.dateDebutFestival <= a.dateFinFestival;
```

Mettez ensuite à jour les statistiques de l'optimiseur Oracle (`DBMS_STATS.GATHER_SCHEMA_STATS`) avant les tests de performance.

## 9. Exemple de chargement Oracle (SQL*Loader)

Les fichiers de contrôle sont générés dans `3_peuplement_donnees/sqlldr/` ; exemple :

```
-- 03_COMMUNE.ctl
OPTIONS (SKIP=1, ROWS=5000, BINDSIZE=20000000, READSIZE=20000000, ERRORS=0)
LOAD DATA
CHARACTERSET AL32UTF8
INFILE 'csv/03_COMMUNE.csv'
APPEND INTO TABLE COMMUNE
FIELDS TERMINATED BY ';' OPTIONALLY ENCLOSED BY '"' TRAILING NULLCOLS
(codeInsee CHAR(20), nomCommune CHAR(160), latitude, longitude, codeDepartement CHAR(12))
```

Commande : `02_charger_oracle.bat festibed/***@//hote:1521/service` (charge les 28 tables dans l'ordre).

Équivalent H2 (tests) :

```sql
INSERT INTO COMMUNE (codeInsee, nomCommune, latitude, longitude, codeDepartement)
SELECT codeInsee, nomCommune, latitude, longitude, codeDepartement
FROM CSVREAD('csv/03_COMMUNE.csv', NULL, 'charset=UTF-8 fieldSeparator=;');
```

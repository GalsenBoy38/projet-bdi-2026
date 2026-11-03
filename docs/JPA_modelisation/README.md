# FestiBed – Groupe 3 – Modélisation JPA

Ce dossier part du MLD GLOBAL FINAL et de l'UML technique ORM du 22/10/2026. Il y ajoute les corrections nécessaires pour JPA, pour la stratégie de concurrence du 23/10/2026 et pour l'intégration du jeu OpenStreetMap `data/osm-france-tourism-accommodation.csv` (03/11/2026).

```
JPA_modelisation/
├── 1_entites_jpa/            Entités Kotlin (JPA / Hibernate), repositories Spring Data, application.yml
│   └── verification_h2/      Programme qui vérifie tout le dossier sur H2 (mapping, données, concurrence)
├── 2_insertion_excel/        Gabarits Excel vides, jeu d'essai Excel des scénarios, conversion Excel → INSERT
└── 3_peuplement_donnees/     Schéma SQL Oracle/H2, génération du peuplement (≥ 100 000 réservations),
                              chargement SQL*Loader / H2, contrôles
```

Le schéma est décrit **une seule fois**, dans `3_peuplement_donnees/schema_festibed.py`. Le DDL Oracle et H2, les en-têtes CSV, les fichiers SQL*Loader, les gabarits Excel et le MLD PlantUML (`docs/Output_Diagramme/MLD_GLOBAL_FINAL.puml`, par `generer_mld.py`) en sont tous générés : il ne peut donc pas y avoir d'écart entre eux. Les entités Kotlin, elles, sont validées contre ce schéma par Hibernate (`hbm2ddl.auto=validate`).

## Changements par rapport à l'UML technique du 22/10

| Changement | Raison |
|---|---|
| `Festival.nbPassVendus` (+ CHECK `nbPassVendus BETWEEN 0 AND quotaPass`) | Utilisé par l'UPDATE conditionnel de la stratégie de concurrence, mais absent du modèle. En **lecture seule** pour JPA, pour que la sauvegarde d'un festival n'écrase pas les ventes |
| `Selection.festival` (FK `idFestival`, UNIQUE `numeroReservation + idFestival`) | Une sélection correspond à un festival ; avant, on ne le retrouvait qu'à travers les Pass |
| `Pass.festival` supprimé | Dépendance transitive (le festival se retrouve par la sélection) : respect de la 3e forme normale |
| `StatutSelection`, `StatutPaiement` en enums | Ce n'étaient que des `String` libres |
| `Classement` + `AUBERGE_COLLECTIVE`, `AIRE_NATURELLE` | 149 établissements du jeu public ont ces classements |
| `Etablissement.noteMoyenne`, `nbNotes` | Filtre « note de l'établissement » sans recalculer une moyenne à chaque recherche |
| `Paiement` : clé technique `idPaiement`, `numTransaction` nullable | Le paiement n'est pas développé, donc il n'y a pas encore de numéro de transaction |
| `Reservation.numeroReservation` aléatoire (`FB` + 10 caractères base 32) | La validation anonyme donne accès à la réservation avec email + numéro : un numéro séquentiel se devinerait |
| Pas de collections inverses (`Festivalier.reservations`, `Selection.nuitees`, `Hebergement.nuitees`, `Reservation.paiement`…) : relations unidirectionnelles | Chargements massifs ou `@OneToOne` inverse toujours chargé ; même principe que MarketHub |
| Séquences `allocationSize = 50` (au lieu de IDENTITY) | Permet les INSERT groupés (création de plusieurs Pass) |
| `Etablissement` : `classement`, `dateClassement`, `classementProroge` facultatifs (CHECK tous NULL ou tous renseignés) + sous-classe `EtablissementNonClasse` (`typeNonClasse`, `nbEtoilesDeclarees`, `nbChambres`, `nbLits`) | 35 294 hébergements non classés recensés par OpenStreetMap (chambres d'hôtes, gîtes, appartements…) |
| `Etablissement.commune` (FK `codeInsee` vers COMMUNE), `emailEtablissement`, `osmRef` (UNIQUE) ; `adresse` facultative ; `nomCommercial` 100 caractères | Code INSEE fourni par OSM et la BAN ; e-mail et téléphone d'OSM ; lieux OSM sans adresse proche |
| `TypeHebergement` + `LOGEMENT_ENTIER`, `LIT_EN_DORTOIR` | Offres des gîtes, appartements, auberges de jeunesse et refuges |
| `VARCHAR2(n CHAR)` dans Oracle | Un nom accentué de 80 caractères dépasse 80 **octets** en UTF-8 |
| Index sur toutes les clés étrangères et les critères de recherche | Oracle n'indexe pas automatiquement les clés étrangères |

## 1. `1_entites_jpa` – entités Kotlin

Les entités suivent les conventions du projet MarketHub (`backend/server/.../data/entities`) :

- un fichier par entité, suffixe `Entity` ;
- package `data.entities`, enums dans `enums` (un fichier par enum), repositories dans `data.repositories` (un fichier par repository) ;
- les colonnes sont déclarées dans le constructeur, et chaque `@Table` / `@Column` porte un nom explicite ;
- l'identifiant technique s'appelle `id` (`val id: Long? = null`) ; les clés naturelles gardent leur nom (`codeInsee`, `codeDepartement`, `numeroReservation`) ;
- les relations « un vers plusieurs » sont **unidirectionnelles**, avec `@OneToMany(cascade = ALL, orphanRemoval = true)` + `@JoinColumn(nullable = false)` côté parent, comme `CommandeEntity.lignes`. Il n'y a ni `mappedBy` ni référence retour ;
- les requêtes simples sont des méthodes dérivées (`findAllByFestivalierId`, `findByEmail`…).

```
src/main/kotlin/fr/uga/miage/m1/festibed/
├── enums/              Domaine, SousDomaine, Periodicite, Classement, CategorieCamping, MentionVillage,
│                       TypeSejour, TypeNonClasse, TypeHebergement, StatutSelection, StatutPaiement
└── data/
    ├── entities/       27 entités + 4 clés composées (@Embeddable)
    └── repositories/   13 repositories + la projection HebergementDisponible
```

| Entités | Remarque |
|---|---|
| `UtilisateurEntity` ← `FestivalierEntity`, `UtilisateurBackofficeEntity` ← `OrganisateurEntity`, `HebergeurEntity` | Héritage JOINED |
| `RegionEntity`, `DepartementEntity`, `CommuneEntity` | |
| `FestivalEntity`, `NotationFestivalEntity` (+ `NotationFestivalId`) | `nbPassVendus` en lecture seule ; `@MapsId` |
| `EtablissementEntity` + 7 sous-classes (`HotelDeTourismeEntity`, `CampingEntity`…, `EtablissementNonClasseEntity`), `NotationEtablissementEntity` (+ Id) | Héritage JOINED ; `estClasse` |
| `HebergementEntity` (+ `HebergementId`), `OptionHebergementEntity`, `PhotoHebergementEntity`, `NuiteeEntity` (+ `NuiteeId`) | Clés composées, `ManyToMany` via EQUIPEMENT |
| `ReservationEntity` ◆ `SelectionEntity` ◆ `PassEntity`, `PaiementEntity` | Composition en cascade, unidirectionnelle |

| Repository | Méthodes principales |
|---|---|
| `FestivalRepository` | `reserverPass`, `libererPass`, `modifierQuota` (**UPDATE conditionnels**), `rechercher`, `findAllByOrganisateurId` |
| `NuiteeRepository` | `occuper`, `liberer`, `retirerSiLibre` (**UPDATE conditionnels**), `nuitsLibres`, `findAllBySelectionId` |
| `HebergementRepository` | `rechercherDisponibles` (projection DTO `HebergementDisponible`), `findAllByEtablissementId` |
| `EtablissementRepository` | `ajouterNote` (UPDATE atomique), `findAllByHebergeurId` |
| `ReservationRepository` | `trouverAnonyme` (email + numéro), `findAllByFestivalierId` |
| `SelectionRepository`, `PaiementRepository`, `FestivalierRepository`, `OrganisateurRepository`, `HebergeurRepository`, `CommuneRepository`, `NotationFestivalRepository`, `NotationEtablissementRepository` | Méthodes dérivées |

**Écarts volontaires par rapport à MarketHub**

| MarketHub | FestiBed | Pourquoi |
|---|---|---|
| Toutes les entités en `data class` | `data class` sauf les deux hiérarchies (`UtilisateurEntity`, `EtablissementEntity` et leurs sous-classes) | Kotlin interdit d'hériter d'une `data class` ; les sous-classes passent les champs communs au constructeur parent |
| `equals`/`hashCode`/`toString` générés | Redéfinis sur l'identifiant dans les entités qui ont des relations | Avec des relations `LAZY`, ceux générés par la `data class` chargeraient les relations (ou lèveraient `LazyInitializationException` hors transaction) et l'`id` change au `persist` |
| `@ManyToOne` par défaut (EAGER) | `@ManyToOne(fetch = LAZY)` | Volume : 660 000 nuitées → hébergement → établissement (7 tables) → hébergeur |
| `GenerationType.UUID` | Séquences Oracle `allocationSize = 50` | Clés numériques du MLD, INSERT groupés |
| Noms de colonnes `snake_case` | Noms du MLD (`nomFestival`) | Le schéma, les CSV, SQL*Loader et les gabarits Excel utilisent les noms du MLD |
| Plugins `spring` + `jpa` | + `all-open` sur `@Entity`/`@Embeddable` | Sans classe ouverte, Hibernate ne peut pas créer de proxy `LAZY` |

Les entités ne sortent pas de la couche `data` : comme dans MarketHub, un mapper les convertit en objets du domaine **dans la transaction** de l'adapter.

**Configuration Maven** (à ajouter au `kotlin-maven-plugin`, comme dans le `pom.xml` de MarketHub) :

```xml
<configuration>
    <compilerPlugins>
        <plugin>spring</plugin>
        <plugin>jpa</plugin>        <!-- constructeur sans argument pour @Entity/@Embeddable -->
        <plugin>all-open</plugin>   <!-- classes ouvertes => proxys LAZY possibles -->
    </compilerPlugins>
    <pluginOptions>
        <option>all-open:annotation=jakarta.persistence.Entity</option>
        <option>all-open:annotation=jakarta.persistence.MappedSuperclass</option>
        <option>all-open:annotation=jakarta.persistence.Embeddable</option>
    </pluginOptions>
</configuration>
```

Dépendances : `spring-boot-starter-data-jpa`, `kotlin-reflect` (requis par Spring Data avec Kotlin), `ojdbc11` (runtime), `h2` (test).

> ⚠️ **Obligatoire** : `physical-strategy: PhysicalNamingStrategyStandardImpl`, comme dans `application.yml`. La stratégie par défaut de Spring Boot renommerait `nomFestival` en `nom_festival` (même avec un `@Column(name = ...)` explicite), et la validation du schéma échouerait.

## 2. `2_insertion_excel` – fichiers Excel d'insertion

| Fichier | Rôle |
|---|---|
| `Gabarits_insertion_vides.xlsx` | Un onglet par table (ordre d'insertion), en-têtes seuls. Le commentaire de chaque en-tête donne le type, s'il est obligatoire, la clé référencée et les valeurs d'enum |
| `Jeu_essai_scenarios.xlsx` | ≈ 5 000 lignes cohérentes (dont 133 établissements non classés OSM) (toutes les clés étrangères sont présentes), autour des scénarios : Musilac + camping du Sierroz (1), Jazz à Couches / Saint Rock + hôtel des Arcades à Autun (2 et 3), compte de Ronald (4) |
| `excel_vers_sql.py` | Convertit un classeur au format des gabarits en `*_oracle.sql` et `*_h2.sql`. Il contrôle les en-têtes, les colonnes obligatoires, les longueurs et les valeurs d'enum, puis recale les séquences |
| `insert_jeu_essai_scenarios_oracle.sql` / `_h2.sql` | Le jeu d'essai déjà converti |
| `generer_excel.py` | Régénère les deux classeurs depuis le peuplement complet |

**Comptes de démonstration** (mot de passe `festibed`, haché en BCrypt) :
- `ronald.organisateur@festibed.test` (organisateur) ;
- `hebergeur.demo@festibed.test` (hébergeur du Sierroz et des Arcades).

```bash
python excel_vers_sql.py Mon_classeur.xlsx         # -> Mon_classeur_oracle.sql, Mon_classeur_h2.sql
```

## 3. `3_peuplement_donnees` – peuplement de la base

```bash
pip install openpyxl
python generer_peuplement.py               # ≈ 50 s ; données identiques à chaque exécution (graine fixe + caches)
python generer_peuplement.py --geocoder    # uniquement si des adresses manquent dans cache/ (BAN, API Géo)
python generer_mld.py                      # régénère docs/Output_Diagramme/MLD_GLOBAL_FINAL.puml
```

| Étape | Détail |
|---|---|
| Nettoyage festivals | Codes INSEE et postaux complétés (`1024` → `01024`), Corse en 2A/2B, 16 libellés de domaine → 13 enums, périodicités normalisées, coordonnées découpées |
| Nettoyage établissements | 5 doublons supprimés, `-` → NULL, classements → enum, sous-type selon la typologie |
| Géocodage | API Adresse (BAN) : **20 731 établissements classés sur 21 430 (97 %)** ont des coordonnées fiables (score ≥ 0,4). Résultat dans `cache/geocodage_etablissements.csv` |
| OpenStreetMap | **16 186 classés (76 %) rapprochés** d'un lieu OSM (nom + commune + distance) : téléphone, e-mail, position du bâtiment. **35 294 lieux non classés ajoutés** (sans nom et refuges non gardés écartés, 562 doublons) ; adresse et code postal par géocodage inverse BAN (`cache/geocodage_inverse_osm.csv`) et API Géo (`cache/communes_api_geo.csv`). Détail : `docs/etude_chargement/` §5.4 |
| Données synthétiques | Dates 2027 (transposées des éditions passées), quotas 30–300, 111 584 hébergements, nuitées autour des festivals, 113 168 réservations, 220 247 Pass, notations |

**Volumes**

| Table | Lignes | Table | Lignes |
|---|---|---|---|
| FESTIVAL | 3 136 | RESERVATION | 113 168 |
| ETABLISSEMENT | 56 724 (21 430 classés + 35 294 non classés) | SELECTION | 126 687 |
| HEBERGEMENT | 111 584 | PASS | 220 247 |
| NUITEE | 682 643 (452 626 libres) | UTILISATEUR | 50 000 |
| COMMUNE | 13 633 | | |

**Contrôles intégrés** (dans `rapport_peuplement.txt` et `04_controles.sql`), tous OK :
- au moins 100 000 réservations ;
- au moins 30 Pass par festival ;
- au moins la moitié du quota réservée, jamais plus que le quota ;
- `nbPassVendus` égal au nombre réel de Pass ;
- capacité des nuitées ≥ nombre de Pass de chaque sélection ;
- nuitées réservées comprises dans les nuits du festival ;
- festivals qui se chevauchent ;
- les festivals des scénarios ont encore des Pass et des hébergements libres.

**Chargement Oracle**
1. `01_schema_oracle.sql` (SQL*Plus ou SQL Developer).
2. `02_charger_oracle.bat utilisateur/motdepasse@//hote:1521/service` (SQL*Loader, tables dans l'ordre des clés étrangères, journaux dans `logs/`).
3. `03_sequences_oracle.sql` (recale les séquences après les identifiants chargés).
4. `04_controles.sql` : toutes les lignes « anomalies » doivent valoir 0.

Ensuite : `EXEC DBMS_STATS.GATHER_SCHEMA_STATS(USER)` avant les tests de performance.

**Chargement H2** (tests) : `01_schema_h2.sql`, puis `02_charger_h2.sql` (exécuté depuis ce dossier), puis `03_sequences_h2.sql`.

## Ce qui a été vérifié

Avec `1_entites_jpa/verification_h2` (Kotlin 2.2.21, Hibernate 6.6.29, Spring Data JPA 3.5.5, H2 2.3.232), sur le jeu d'essai **et** sur le peuplement complet (chargé en ≈ 80 s), le 03/11/2026 :

- `hbm2ddl.auto=validate` accepte toutes les entités face au schéma ;
- les 11 contrôles « anomalies » de `04_controles.sql` renvoient 0 ;
- les lectures fonctionnent : héritage JOINED (dont un établissement non classé OSM et la commune d'un établissement), clés composées et `@MapsId`, projection de recherche d'hébergements autour de Musilac (le Sierroz est trouvé) ;
- l'écriture d'une réservation complète fonctionne : cascade Reservation → Selection → Pass, séquences, paiement ;
- `reserverPass` vend les derniers Pass puis refuse le suivant, `modifierQuota` refuse un quota inférieur aux ventes, `occuper` refuse une nuit déjà prise, `retirerSiLibre` refuse une nuit réservée ;
- la sauvegarde d'un festival par l'organisateur n'écrase pas `nbPassVendus` ;
- **concurrence** : sur 8 transactions simultanées sur la même nuitée, une seule l'obtient.

```bash
cd 1_entites_jpa/verification_h2
mvn -q compile dependency:build-classpath -Dmdep.outputFile=cp.txt
java -cp "target/classes;$(cat cp.txt)" VerifKt essai      # ou : complet
```

**Non vérifié ici** : l'exécution sur un vrai serveur Oracle (aucun disponible sur ce poste). Il reste à tester `01_schema_oracle.sql`, SQL*Loader et `ddl-auto=validate` sur Oracle. Le DDL vise Oracle 19c/21c. Sur Oracle 23ai, Hibernate attend le type `BOOLEAN` natif à la place de `NUMBER(1)`.

## Limites connues
- 293 établissements classés (0,5 %) n'ont de coordonnées ni dans la BAN ni dans OSM : ils n'apparaîtront pas dans une recherche par distance.
- Le rapprochement classés ↔ OSM est heuristique (≈ 95 % de paires justes sur un échantillon) : quelques sous-marques d'une même chaîne peuvent être confondues, et un hôtel classé non reconnu peut figurer aussi parmi les non classés.
- La capacité d'accueil des non classés est souvent estimée (pas renseignée dans OSM).
- 1 665 festivals ont un sous-domaine à NULL : leur complément n'appartient pas aux 6 valeurs de l'enum `SousDomaine`. C'est un choix de modélisation à justifier.
- `telephoneEtablissement` et `emailEtablissement` ne sont connus que pour les établissements présents dans OSM avec ces informations (18 339 et 8 889).
- Données OpenStreetMap sous licence ODbL : mentionner « © les contributeurs d'OpenStreetMap » dans l'application.

# FestiBed – Groupe 3 – Entités JPA Kotlin (Spring Boot)

Module Spring Boot 4 / Spring Data JPA / Kotlin, écrit sur le modèle du projet MarketHub
(`backend/server/.../data/entities`). Il implémente l'UML technique ORM du groupe
(`docs/Output_Diagramme/UML_technique_ORM.puml`).

Aucun script SQL ni accès JDBC direct : **Hibernate crée le schéma à partir des entités**
(`ddl-auto`), les données de démonstration sont insérées par `config/DataInitializer` à travers
les repositories, et toutes les requêtes sont des méthodes dérivées ou du JPQL.

```
src/main/kotlin/fr/uga/miage/m1/festibed/
├── FestiBedApplication.kt
├── enums/                 11 enums (un fichier par enum)
├── data/entities/         27 entités XxxEntity
├── data/repositories/     17 repositories XxxRepository
└── config/DataInitializer.kt   données des scénarios (Musilac, Jazz à Couches, Saint Rock, Ronald…)
src/test/kotlin/...        25 tests @DataJpaTest (H2 en mémoire)
```

## Lancer

```bash
mvn test                      # 25 tests sur H2 en mémoire
mvn spring-boot:run           # crée target/h2/festibed.mv.db et y insère les données de démonstration
mvn spring-boot:run -Dspring-boot.run.profiles=oracle   # FESTIBED_DB_URL / _USER / _PASSWORD
```

Comptes de démonstration (mot de passe `festibed`, haché en BCrypt) :
`ronald.organisateur@festibed.test` (organisateur de Musilac et Jazz à Couches),
`hebergeur.demo@festibed.test` (Sierroz et Arcades).

## Conventions reprises de MarketHub

- Une entité par fichier, suffixe `Entity`, `data class` avec les colonnes dans le constructeur.
- Identifiant technique `val id: UUID? = null` + `@GeneratedValue(strategy = GenerationType.UUID)`.
- Noms de tables et de colonnes en `snake_case`, contraintes nommées (`uk_…`, `idx_…`).
- Unicité métier par `UniqueConstraint` sur une clé technique, comme `StockEntity`
  (`uk_stock_produit_entrepot`) : pas de clé composée.
- `@ManyToOne(optional = false)` + `@JoinColumn(name = "…_id", nullable = false)`.
- Compositions en `@OneToMany(cascade = [ALL], orphanRemoval = true)` + `@JoinColumn`,
  **unidirectionnelles** comme `CommandeEntity.lignes`.
- Requêtes dérivées (`findAllByOrganisateurId`, `findByNumeroAndFestivalierEmail`…).
- Tests `@DataJpaTest` + `@ActiveProfiles("test")`, `application-test.yml` en `create-drop`.

## Associations

| Association | Mapping |
|---|---|
| Departement → Region, Commune → Departement, Festival → Commune | `@ManyToOne(optional = false)` |
| Festival → Organisateur, Etablissement → Hebergeur / Commune | `@ManyToOne` facultatif |
| Hebergement → Etablissement, Nuitee → Hebergement | `@ManyToOne(optional = false)` + unicité (`etablissement_id, numero`), (`hebergement_id, date_nuitee`) |
| Nuitee → Selection | `@ManyToOne` facultatif : `null` = nuit libre |
| Hebergement ↔ OptionHebergement | **`@ManyToMany`** + `@JoinTable(name = "equipement")` |
| Hebergement ◆ PhotoHebergement, Reservation ◆ Selection ◆ Pass | `@OneToMany(cascade = ALL, orphanRemoval = true)` + `@JoinColumn` |
| Paiement → Reservation | `@OneToOne(optional = false)`, `reservation_id` unique |
| NotationFestival / NotationEtablissement → Festival / Etablissement, Festivalier | 2 × `@ManyToOne` + unicité du couple |
| Utilisateur ← Festivalier, UtilisateurBackoffice ← Organisateur, Hebergeur | `@Inheritance(JOINED)` |
| Etablissement ← 6 typologies classées + EtablissementNonClasse | `@Inheritance(JOINED)` |

## Écarts par rapport à MarketHub / à l'UML

- **Héritage** : `UtilisateurEntity`, `UtilisateurBackofficeEntity` et `EtablissementEntity` sont des
  classes abstraites, et leurs sous-classes des classes simples : Kotlin interdit d'hériter d'une
  `data class`. Leur `equals`/`hashCode` porte sur l'`id`.
- **Clés composées de l'UML** (`HebergementId`, `NuiteeId`, `Notation…Id`) remplacées par un `id` UUID
  + une contrainte d'unicité, comme `StockEntity` dans MarketHub.
- **Concurrence** : `Festival.nbPassVendus` et `Etablissement.noteMoyenne` / `nbNotes` sont en lecture
  seule pour JPA (`insertable = false, updatable = false`, `@ColumnDefault("0")`). Ils ne changent que
  par les UPDATE conditionnels JPQL `FestivalRepository.reserverPass`, `NuiteeRepository.occuper`,
  `EtablissementRepository.ajouterNote`, appliquant la stratégie de concurrence du 23/10.
- Plugin `all-open` ajouté sur `@Entity` (en plus de `spring` et `jpa`) pour que Hibernate puisse créer des proxys.
- Les `@ManyToOne` sont chargés immédiatement (EAGER par défaut, comme MarketHub) : suffisant pour le
  prototype. Avec le peuplement complet (660 000 nuitées), passer les relations en `LAZY`.

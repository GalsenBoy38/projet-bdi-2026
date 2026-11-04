# Rapport de vérification du modèle de tâches – FestiBed Groupe 3

- **Fichier vérifié** : `Modéles_de_taches.kxml` (version du 04/11/2026, 11h46). Il compte 40 tâches et 5 objets abstraits.
- **Référentiel** : IHM, chapitre 4, « Validation du modèle de tâches », et le sujet `projet_IGD_2026_FestiBed`, scénarios 1 à 4.
- **Méthode** : lecture de l'arbre complet (exécutants, opérateurs, décorations, préconditions et objets), puis déroulement manuel de chaque scénario dans l'arbre, tâche par tâche. Le simulateur K-MADe n'a pas été lancé.

## Synthèse

| Niveau de validation | Résultat |
|---|---|
| Syntaxe (6 règles du cours) | **Conforme : 6/6** |
| Sémantique : scénario 1 (Jeff, Musilac) | **Passe**, avec 2 remarques |
| Sémantique : scénario 2 (expiration du panier) | **Ne passe pas** |
| Sémantique : scénario 3 (indisponibilité à la validation) | **Ne passe pas** |
| Scénario 4 (Ronald, organisateur) | Hors périmètre : ce modèle traite l'objectif « Passer une réservation » |
| Questions d'analyse (but de l'utilisateur, dernière sous-tâche) | Globalement oui, 2 réserves |

**Verdict** : le modèle est **syntaxiquement valide mais pas encore sémantiquement valide**. Il ne généralise que le scénario nominal. Les scénarios 2 et 3 n'aboutissent pas, pour trois raisons :
- il n'y a aucune itération ;
- il n'y a aucune branche d'échec ;
- les objets ne sont jamais modifiés (aucun effet de bord).

---

## 1. Validation syntaxique

| # | Règle du chapitre 4 | Résultat | Détail |
|---|---|---|---|
| 1 | Chaque tâche décomposée se lit « pour faire T, il faut faire T.1, T.2… » | OK | Exemples : « Pour valider le panier il faut s'identifier, consulter le récapitulatif, confirmer la réservation » ; « Pour rechercher un festival il faut saisir les critères, afficher les festivals, choisir un festival ». |
| 2 | Toute tâche feuille a un exécutant non abstrait | OK | 29 feuilles : 23 interactives et 6 système. Aucune n'est abstraite. |
| 3 | Une tâche décomposée est abstraite, ou du même exécutant que toutes ses sous-tâches | OK | 10 tâches décomposées sont abstraites. La 11e, « 2 Ajuster le panier », est interactive et ses 2 sous-tâches le sont aussi. |
| 4 | Aucune feuille n'a d'opérateur | OK | Toutes les feuilles sont en `ELEM`. |
| 5 | Toute tâche décomposée a un opérateur | OK | 8 en SEQ et 3 en ALT. |
| 6 | Aucune tâche décomposée n'a une seule sous-tâche | OK | Le minimum est de 2 sous-tâches (1.3.3, 2 et 3.1). |

## 2. Déroulement des scénarios

Notation utilisée dans les tableaux : ✔ = la tâche est exécutable et correspond au scénario ; ⚠ = exécutable mais écart avec le scénario ; ✘ = blocage.

### Scénario 1 : Jeff réserve 2 Pass Musilac et un emplacement au camping du Sierroz → **PASSE**

| Étape du scénario | Tâches K-MADe | |
|---|---|---|
| Il recherche Musilac | 1.1.1 (ALT) → 1.1.1.1 Saisir un nom de festival ; 1.1.2 Afficher ; 1.1.3 Choisir (`card($FestivalsAffiches) > 0` vaut 1 > 0) | ✔ |
| Il demande deux Pass | 1.2 Saisir le nombre de Pass | ✔ |
| Il consulte les hébergements disponibles, **puis** filtre sur le type camping | 1.3.1 Choisir les critères (**obligatoire, avant** l'affichage) → 1.3.1.1 type ; 1.3.2 Afficher | ⚠ |
| Il sélectionne un emplacement pour 2 personnes | 1.3.3, avec la précondition `isExist(... disponible == true)` vraie ; puis 1.3.3.1 et 1.3.3.2 | ✔ |
| Il ajoute la sélection au panier | 1.4 ; on saute la tâche 2, qui est optionnelle | ✔ |
| Il s'authentifie avec un réseau social | 3 (`card($Panier) > 0`) → 3.1 (ALT) → 3.1.1 ; puis 3.2 | ✔ |
| La validation réussit : réservation, 2 Pass et 1 bon | 3.3.1 → 3.3.2 Payer → 3.3.3 (`ressourcesDisponibles == true`) → 3.3.3.1 à 3.3.3.4 | ✔ |

Deux remarques sur ce scénario :
- Dans le modèle, le festivalier doit choisir un critère d'hébergement **avant** de voir la liste. Dans le scénario, Jeff consulte d'abord la liste, puis filtre. Le filtre devrait donc être **optionnel et placé après** 1.3.2.
- La tâche « Payer » arrive **avant** la vérification des disponibilités, qui correspond à la précondition de 3.3.3. Si la vérification échoue, le festivalier a déjà payé.

### Scénario 2 : Samantha laisse expirer son panier → **NE PASSE PAS**

| Étape du scénario | Tâches K-MADe | |
|---|---|---|
| Elle cherche autour d'Autun fin juillet (localisation **et** période) | 1.1.1 est en **ALT** : un seul critère est possible | ⚠ |
| Elle trouve des festivals et des hébergements, puis ajoute une sélection | 1.1 → 1.4 | ✔ |
| Après 15 min, FestiBed indique que la sélection a expiré | **Aucune tâche** ne correspond. L'attribut `minutesDepuisAjout` existe mais n'est utilisé dans aucune précondition. | ✘ |
| Elle doit recommencer la réservation | Toutes les itérations valent `[1]` : impossible de revenir à la tâche 1 | ✘ |

De plus, aucune tâche ne vide `$Panier` (tous les effets de bord sont à `void`). En simulation, la tâche 3 reste donc exécutable alors que le panier devrait être vide.

### Scénario 3 : indisponibilité détectée à la validation, puis nouvelle réservation → **NE PASSE PAS**

| Étape du scénario | Tâches K-MADe | |
|---|---|---|
| Elle choisit Jazz à Couches et une chambre à l'hôtel des Arcades | 1.1 → 1.4 | ✔ |
| À la validation, une ressource est devenue indisponible | La précondition de 3.3.3 est fausse (`ressourcesDisponibles == false`). Mais il n'y a **aucune alternative** : ni tâche système « Signaler l'indisponibilité », ni retour possible. La racine est en SEQ et reste bloquée. | ✘ |
| La réservation n'est pas créée | Rien ne le représente dans le modèle | ✘ |
| Elle choisit Saint Rock et valide | Il faudrait recommencer 1 → 3, mais la racine et la tâche 1 sont à `[1]` | ✘ |

### Scénario 4 : Ronald ajoute son festival et fixe le quota de Pass

Ce scénario concerne l'Organisateur et le back-office. Le sujet demande un modèle de tâches pour un seul objectif : **« Passer une réservation à FestiBed »**. Le scénario 4 est donc hors périmètre de ce modèle.

Il apporte une seule chose utile ici : les hébergements apparaissent sans être liés au festival. C'est cohérent avec la tâche 1.3.2 « Afficher les hébergements disponibles ».

## 3. Questions d'analyse du chapitre 4

1. **La décomposition suit-elle le but de l'utilisateur ?** Oui : constituer le panier, l'ajuster, puis le valider. Les tâches système (afficher, générer, envoyer) sont des retours d'information, pas des étapes propres au logiciel.
2. **La dernière sous-tâche de chaque tâche accomplit-elle la tâche mère ?** Oui pour la racine (3), la tâche 1 (1.4), 1.1 (1.1.3), 1.3 (1.3.3), 3 (3.3) et 3.3 (3.3.3). Deux réserves :
   - **2 Ajuster le panier** : avec un ALT, on peut consulter **ou** modifier, mais pas consulter **puis** modifier. Il vaudrait mieux un SEQ : 2.1 Consulter, puis 2.2 Modifier en optionnel.
   - **3.3.3.4 Télécharger** : la réservation est déjà obtenue (affichée et envoyée par mail). Cette dernière tâche devrait être **optionnelle**.

## 4. Autres constats

- **Préconditions manquantes** sur les règles métier du sujet. L'objet `Selection` est défini mais aucune tâche ne l'utilise.
  - 1.2 : le nombre de Pass doit être disponible. Proposition : `getValue($SelectionEnCours, $nbPass) <= getValue($SelectionEnCours, $passDisponibles)`.
  - 1.4 : la réservation groupée doit respecter la capacité. Proposition : `getValue($SelectionEnCours, $capaciteTotale) >= getValue($SelectionEnCours, $nbPass)`.
- **Panier multi-festivals** : le sujet permet de « supprimer du panier l'ensemble correspondant à un festival ». Le panier peut donc contenir plusieurs festivals, mais la tâche 1 n'est exécutée qu'une fois.
- **Libellés à corriger** :
  - « Afficher reservation confirmer » → « Afficher la réservation confirmée » ;
  - « Envoyer reservation par mail » → « Envoyer la réservation par e-mail » ;
  - « Sélectionner hébergement » → « Sélectionner un hébergement » ;
  - « Choisir nuitée » → « Choisir les nuitées » ;
  - « Générer les pass » → « Générer les Pass ».

## 5. Corrections proposées, par priorité

1. **Itérations**. Mettre la tâche 1 « Constituer le panier » en itération *n* (« tant que le festivalier ajoute un festival »). Mettre la racine (ou un regroupement de 1, 2 et 3) en itération « tant que la réservation n'est pas créée ». Cela permet de dérouler le scénario 2 (recommencer) et le scénario 3 (choisir Saint Rock).
2. **Branche d'échec de la validation**. Restructurer 3.3 :
   - 3.3.1 Confirmer la validation (INT) ;
   - 3.3.2 Vérifier les disponibilités (SYS) ;
   - 3.3.3 Traiter le résultat (ALT), avec deux branches :
     - **Réservation créée** (précondition `ressourcesDisponibles == true`) : Payer, puis Recevoir la réservation ;
     - **Signaler l'indisponibilité** (SYS, précondition `ressourcesDisponibles == false`).

   Cela corrige aussi l'ordre entre le paiement et la vérification.
3. **Expiration**. Ajouter dans la tâche 2 une tâche système « Signaler l'expiration et retirer la sélection ». Sa précondition serait `isExist($Panier, $minutesDepuisAjout >= 15)`.
4. **Critères de recherche**.
   - 1.1.1 : passer l'ALT en **sans ordre**, avec des feuilles optionnelles, pour permettre « Autun + fin juillet ».
   - 1.3 : mettre les critères en sans ordre et optionnels, **après** l'affichage.
5. **Préconditions** : ajouter celles de 1.2 et 1.4 (section 4).
6. **Analyse** : passer 2 en SEQ et rendre 3.3.3.4 optionnelle (section 3).
7. **Libellés** : corriger ceux de la section 4.

Pour vérifier après correction, il faudra relancer la simulation dans K-MADe sur les scénarios 1 à 3, puis régénérer le SVG et le PDF avec `python kxml_vers_svg.py`.

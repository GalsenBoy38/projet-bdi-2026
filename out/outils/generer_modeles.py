"""FestiBed - génération cohérente des modèles de données (méthode Merise du cours AFMP).

Une SEULE spécification (ci-dessous) produit :
  - out/plantuml/01_mld_sources_publiques.puml   MLD rétro-conçu des sources (3FN)
  - out/plantuml/02_mcd_sources_publiques.puml   MCD rétro-conçu des sources (Merise)
  - out/plantuml/03a/03b_mcd_global_*.puml       MCD global (Merise / Merise 2)
  - out/plantuml/05a/05b_mld_global_*.puml       MLD global (3FN)
  - out/sql/mpd_oracle.sql                        MPD (création des tables Oracle)
  - out/outils/build/*.html                       formalisme textuel (dictionnaire, MLD textuel)
et vérifie les règles de qualité du cours (noms distincts, identifiants, associations <-> clés étrangères).

Usage : python generer_modeles.py
"""
import html, os, re, sys
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))      # .../out
PUML, SQL, BUILD = (os.path.join(ROOT, d) for d in ("plantuml", "sql", os.path.join("outils", "build")))
for d in (PUML, SQL, BUILD):
    os.makedirs(d, exist_ok=True)

# =============================================================================
# 1. SPÉCIFICATION
# -----------------------------------------------------------------------------
# Colonne : (nom, type Oracle, obligatoire, clé, drapeaux, sémantique)
#   clé      : "PK", "UK", "FK:TABLE[.colonne]", "PK,FK:TABLE[.colonne]" ou ""
#   drapeaux : g = ajouté par FestiBed (absent des sources publiques)
#              t = technique (MLD/MPD seulement, absent du MCD)
#              c = attribut calculé (redondance maîtrisée)
#              b = booléen
# Genre de relation :
#   ent   = entité -> relation          asso = association n-aire -> relation
#   sub1  = sous-entité transformée T1  tech = relation technique (pas dans le MCD)
# =============================================================================
ID = "NUMBER(10)"
R = OrderedDict()


def rel(name, kind, group, sem, cols, checks=(), src=False, view="a"):
    R[name] = dict(kind=kind, group=group, sem=sem, cols=list(cols), checks=list(checks), src=src, view=view)


# ---------------------------------------------------------------- géographie
rel("REGION", "ent", "Référentiel géographique", "Région administrative française (dont outre-mer).", [
    ("id_region", ID, 1, "PK", "", "Identifiant de la région"),
    ("nom_region", "VARCHAR2(60)", 1, "UK", "", "Nom officiel de la région")], src=True)
rel("DEPARTEMENT", "ent", "Référentiel géographique", "Département français identifié par son code officiel (01…95, 2A, 2B, 971…).", [
    ("code_departement", "VARCHAR2(3)", 1, "PK", "", "Code officiel du département"),
    ("nom_departement", "VARCHAR2(60)", 1, "", "", "Nom du département"),
    ("id_region", ID, 1, "FK:REGION", "", "Région d'appartenance")], src=True)
rel("COMMUNE", "ent", "Référentiel géographique", "Commune française identifiée par son code INSEE, avec son centroïde géographique.", [
    ("code_insee", "CHAR(5)", 1, "PK", "", "Code officiel géographique INSEE"),
    ("nom_commune", "VARCHAR2(100)", 1, "", "", "Libellé officiel de la commune"),
    ("latitude_commune", "NUMBER(9,6)", 0, "", "", "Latitude WGS84 du centroïde (degrés)"),
    ("longitude_commune", "NUMBER(9,6)", 0, "", "", "Longitude WGS84 du centroïde (degrés)"),
    ("code_departement", "VARCHAR2(3)", 1, "FK:DEPARTEMENT", "", "Département de la commune")],
    ["CHECK (latitude_commune BETWEEN -90 AND 90)", "CHECK (longitude_commune BETWEEN -180 AND 180)"], src=True)

# ---------------------------------------------------------------- festivals
rel("DOMAINE", "ent", "Festivals", "Grand domaine artistique d'une manifestation (type de festival).", [
    ("id_domaine", ID, 1, "PK", "", "Identifiant du domaine"),
    ("libelle_domaine", "VARCHAR2(80)", 1, "UK", "", "Libellé normalisé (ex. Musiques actuelles)")], src=True)
rel("SOUS_DOMAINE", "ent", "Festivals", "Style précisant le domaine (ex. Jazz, blues et musiques improvisées) ; indépendant du domaine dans la source.", [
    ("id_sous_domaine", ID, 1, "PK", "", "Identifiant du sous-domaine"),
    ("libelle_sous_domaine", "VARCHAR2(80)", 1, "UK", "", "Libellé normalisé du style")], src=True)
rel("PERIODICITE", "ent", "Festivals", "Rythme de tenue d'une manifestation.", [
    ("id_periodicite", ID, 1, "PK", "", "Identifiant de la périodicité"),
    ("libelle_periodicite", "VARCHAR2(40)", 1, "UK", "", "Annuelle, biennale paire, biennale impaire…")], src=True)
rel("ORGANISME_SOUTIEN", "ent", "Festivals", "Organisme public pouvant soutenir un festival (Ministère de la culture, CNC, CNL, CNV).", [
    ("id_organisme", ID, 1, "PK", "", "Identifiant de l'organisme"),
    ("sigle_organisme", "VARCHAR2(10)", 1, "UK", "", "Sigle (MC, CNC, CNL, CNV)"),
    ("libelle_organisme", "VARCHAR2(80)", 1, "", "", "Nom complet de l'organisme")], src=True)
rel("FESTIVAL", "ent", "Festivals", "Manifestation proposée dans FestiBed, issue du jeu public ou créée/complétée par un Organisateur.", [
    ("id_festival", ID, 1, "PK", "", "Identifiant technique du festival"),
    ("code_identification", "VARCHAR2(10)", 0, "UK", "", "N° d'identification de la source (codes génériques mis à NULL)"),
    ("nom_festival", "VARCHAR2(200)", 1, "", "", "Nom de la manifestation"),
    ("site_web_festival", "VARCHAR2(300)", 0, "", "", "Adresse du site web"),
    ("date_creation_festival", "DATE", 0, "", "", "Date de création de la manifestation"),
    ("mois_habituel_debut", "NUMBER(2)", 1, "", "", "Mois habituel de début (1 à 12)"),
    ("date_debut_source", "DATE", 0, "", "", "Date de début de l'édition décrite par la source"),
    ("date_fin_source", "DATE", 0, "", "", "Date de fin de l'édition décrite par la source"),
    ("num_edition_2018", "NUMBER(4)", 0, "", "", "Numéro de l'édition 2018"),
    ("num_edition_2019", "NUMBER(4)", 0, "", "", "Numéro de l'édition 2019"),
    ("montant_soutien_2017", "NUMBER(10)", 0, "", "", "Soutien 2017 du ministère à la structure (euros)"),
    ("commentaire_festival", "VARCHAR2(4000)", 0, "", "", "Commentaire libre de la source"),
    ("code_postal_festival", "VARCHAR2(5)", 1, "", "", "Code postal de la commune principale"),
    ("code_insee", "CHAR(5)", 1, "FK:COMMUNE", "", "Commune principale"),
    ("id_domaine", ID, 1, "FK:DOMAINE", "", "Domaine du festival"),
    ("id_sous_domaine", ID, 0, "FK:SOUS_DOMAINE", "", "Sous-domaine (style)"),
    ("id_periodicite", ID, 0, "FK:PERIODICITE", "", "Périodicité"),
    ("id_organisateur", ID, 0, "FK:ORGANISATEUR.id_compte", "g", "Organisateur responsable"),
    ("date_debut_festival", "DATE", 0, "", "g", "Premier jour de l'édition commercialisée"),
    ("date_fin_festival", "DATE", 0, "", "g", "Dernier jour de l'édition commercialisée"),
    ("prix_pass", "NUMBER(8,2)", 0, "", "g", "Prix d'un Pass (euros TTC)"),
    ("quota_pass", "NUMBER(6)", 1, "", "g", "Nombre maximal de Pass alloués à FestiBed"),
    ("nb_pass_reserves", "NUMBER(6)", 1, "", "gc", "Nombre de Pass des réservations confirmées (calculé)"),
    ("statut_festival", "VARCHAR2(10)", 1, "", "g", "BROUILLON, ACTIF ou DESACTIVE"),
    ("description_festival", "VARCHAR2(4000)", 0, "", "g", "Présentation rédigée par l'organisateur"),
    ("version_festival", ID, 1, "", "gt", "Version pour le verrouillage optimiste (@Version)")],
    ["CHECK (mois_habituel_debut BETWEEN 1 AND 12)", "CHECK (date_fin_festival >= date_debut_festival)",
     "CHECK (quota_pass >= 0)", "CHECK (nb_pass_reserves BETWEEN 0 AND quota_pass)", "CHECK (prix_pass >= 0)",
     "CHECK (statut_festival IN ('BROUILLON','ACTIF','DESACTIVE'))",
     "CHECK (statut_festival <> 'ACTIF' OR (date_debut_festival IS NOT NULL AND date_fin_festival IS NOT NULL AND prix_pass IS NOT NULL))"],
    src=True)
rel("FESTIVAL_COMMUNE", "asso", "Festivals", "Fait qu'un festival se déroule aussi dans d'autres communes que sa commune principale.", [
    ("id_festival", ID, 1, "PK,FK:FESTIVAL", "", ""),
    ("code_insee", "CHAR(5)", 1, "PK,FK:COMMUNE", "", "")], src=True)
rel("SOUTIEN", "asso", "Festivals", "Fait qu'un organisme a soutenu un festival une année donnée.", [
    ("id_festival", ID, 1, "PK,FK:FESTIVAL", "", ""),
    ("id_organisme", ID, 1, "PK,FK:ORGANISME_SOUTIEN", "", ""),
    ("annee_soutien", "NUMBER(4)", 1, "PK", "", "")], ["CHECK (annee_soutien BETWEEN 1990 AND 2100)"], src=True)

# ---------------------------------------------------------------- établissements
rel("TYPOLOGIE_ETABLISSEMENT", "ent", "Établissements et hébergements",
    "Catégorie réglementaire d'établissement ; détermine la nature de ses unités d'accueil.", [
    ("code_typologie", "VARCHAR2(20)", 1, "PK", "", "HOTEL, CAMPING, RESIDENCE, VILLAGE_VACANCES, PRL, AUBERGE"),
    ("libelle_typologie", "VARCHAR2(60)", 1, "UK", "", "Libellé de la source (ex. HÔTEL DE TOURISME)"),
    ("unite_accueil", "VARCHAR2(30)", 1, "", "", "Nature des unités comptées (chambre, emplacement, logement…)")], src=True)
rel("CLASSEMENT", "ent", "Établissements et hébergements", "Niveau de classement officiel d'un établissement.", [
    ("id_classement", ID, 1, "PK", "", "Identifiant du classement"),
    ("libelle_classement", "VARCHAR2(40)", 1, "UK", "", "1 à 5 étoiles, Aire naturelle, Auberge collective"),
    ("nb_etoiles", "NUMBER(1)", 0, "", "", "Nombre d'étoiles (vide si non étoilé)")],
    ["CHECK (nb_etoiles BETWEEN 1 AND 5)"], src=True)
rel("ETABLISSEMENT", "ent", "Établissements et hébergements",
    "Lieu physique d'hébergement collectif classé, répertorié dans le jeu de données public.", [
    ("id_etablissement", ID, 1, "PK", "", "Identifiant technique de l'établissement"),
    ("nom_commercial", "VARCHAR2(200)", 1, "", "", "Nom commercial"),
    ("adresse_etablissement", "VARCHAR2(300)", 1, "", "", "Numéro et voie"),
    ("code_postal_etablissement", "VARCHAR2(5)", 1, "", "", "Code postal"),
    ("site_internet", "VARCHAR2(300)", 0, "", "", "Adresse du site web"),
    ("date_classement", "DATE", 1, "", "", "Date de la décision de classement"),
    ("classement_proroge", "NUMBER(1)", 1, "", "b", "Classement prorogé (oui/non)"),
    ("capacite_accueil", "NUMBER(6)", 1, "", "", "Capacité d'accueil totale (personnes)"),
    ("nb_unites", "NUMBER(5)", 1, "", "", "Nombre d'unités d'accueil (nature : typologie)"),
    ("categorie_camping", "VARCHAR2(10)", 0, "", "", "TOURISME ou LOISIRS (campings seulement)"),
    ("mention_village", "VARCHAR2(30)", 0, "", "", "Mention des villages de vacances"),
    ("type_sejour", "VARCHAR2(30)", 0, "", "", "Formule de séjour des villages de vacances"),
    ("code_insee", "CHAR(5)", 1, "FK:COMMUNE", "", "Commune de l'établissement"),
    ("code_typologie", "VARCHAR2(20)", 1, "FK:TYPOLOGIE_ETABLISSEMENT", "", "Typologie (discriminant des sous-entités)"),
    ("id_classement", ID, 1, "FK:CLASSEMENT", "", "Classement"),
    ("id_hebergeur", ID, 0, "FK:HEBERGEUR.id_compte", "g", "Hébergeur responsable"),
    ("latitude_etablissement", "NUMBER(9,6)", 0, "", "g", "Latitude WGS84 (géocodage de l'adresse)"),
    ("longitude_etablissement", "NUMBER(9,6)", 0, "", "g", "Longitude WGS84 (géocodage de l'adresse)"),
    ("note_moyenne_etablissement", "NUMBER(3,2)", 0, "", "gc", "Moyenne des notes (calculée)"),
    ("nb_notes_etablissement", "NUMBER(8)", 1, "", "gc", "Nombre de notes (calculé)")],
    ["CHECK (classement_proroge IN (0,1))", "CHECK (capacite_accueil > 0)", "CHECK (nb_unites >= 0)",
     "CHECK (categorie_camping IS NULL OR (code_typologie = 'CAMPING' AND categorie_camping IN ('TOURISME','LOISIRS')))",
     "CHECK (mention_village IS NULL OR (code_typologie = 'VILLAGE_VACANCES' AND mention_village IN ('NON','HEBERGEMENT_DISPERSE','HEBERGEMENT_LEGER','HEBERGEMENT_LEGER_ET_DISPERSE')))",
     "CHECK (type_sejour IS NULL OR (code_typologie = 'VILLAGE_VACANCES' AND type_sejour IN ('FORMULE_PENSION','FORMULE_LOCATION','FORMULE_LOCATION_PENSION')))",
     "CHECK (note_moyenne_etablissement BETWEEN 1 AND 5)", "CHECK (nb_notes_etablissement >= 0)",
     "UNIQUE (nom_commercial, adresse_etablissement, code_postal_etablissement)"], src=True)

# ---------------------------------------------------------------- comptes
rel("COMPTE_INTERNE", "ent", "Comptes", "Compte d'authentification interne au Back-Office FestiBed.", [
    ("id_compte", ID, 1, "PK", "g", "Identifiant du compte"),
    ("email_compte", "VARCHAR2(254)", 1, "UK", "g", "Adresse électronique de connexion"),
    ("mot_de_passe_hash", "VARCHAR2(100)", 1, "", "g", "Empreinte du mot de passe (bcrypt)"),
    ("nom_compte", "VARCHAR2(80)", 1, "", "g", "Nom du titulaire"),
    ("prenom_compte", "VARCHAR2(80)", 1, "", "g", "Prénom du titulaire"),
    ("telephone_compte", "VARCHAR2(20)", 0, "", "g", "Téléphone"),
    ("date_creation_compte", "TIMESTAMP", 1, "", "g", "Date de création du compte")])
rel("ORGANISATEUR", "sub1", "Comptes", "Compte interne responsable d'un ou plusieurs festivals.", [
    ("id_compte", ID, 1, "PK,FK:COMPTE_INTERNE", "g", ""),
    ("nom_structure", "VARCHAR2(150)", 0, "", "g", "Structure organisatrice (association, société…)")])
rel("HEBERGEUR", "sub1", "Comptes", "Compte interne responsable d'un ou plusieurs établissements d'hébergement.", [
    ("id_compte", ID, 1, "PK,FK:COMPTE_INTERNE", "g", ""),
    ("raison_sociale", "VARCHAR2(150)", 0, "", "g", "Raison sociale de l'exploitant")])
rel("FESTIVALIER", "ent", "Comptes", "Utilisateur du FrontOffice, authentifié par un réseau social ou compte de test du peuplement.", [
    ("id_festivalier", ID, 1, "PK", "g", "Identifiant du festivalier"),
    ("email_festivalier", "VARCHAR2(254)", 1, "UK", "g", "Adresse électronique"),
    ("nom_festivalier", "VARCHAR2(80)", 1, "", "g", "Nom"),
    ("prenom_festivalier", "VARCHAR2(80)", 1, "", "g", "Prénom"),
    ("fournisseur_auth", "VARCHAR2(10)", 1, "", "g", "GOOGLE, FACEBOOK, GITHUB ou TEST"),
    ("id_externe", "VARCHAR2(128)", 1, "", "g", "Identifiant chez le fournisseur (uid Firebase) ou identifiant généré test-NNNNNN"),
    ("compte_test", "NUMBER(1)", 1, "", "gb", "Compte généré pour les tests (non authentifiable)"),
    ("date_inscription", "TIMESTAMP", 1, "", "g", "Date de première connexion")],
    ["CHECK (fournisseur_auth IN ('GOOGLE','FACEBOOK','GITHUB','TEST'))", "CHECK (compte_test IN (0,1))",
     "UNIQUE (fournisseur_auth, id_externe)",
     "CHECK ((compte_test = 1 AND fournisseur_auth = 'TEST') OR (compte_test = 0 AND fournisseur_auth <> 'TEST'))"],
    view="b")

# ---------------------------------------------------------------- hébergements
rel("TYPE_HEBERGEMENT", "ent", "Établissements et hébergements", "Nature d'une offre réservable (chambre simple, chambre double, emplacement, bungalow…).", [
    ("id_type_hebergement", ID, 1, "PK", "g", "Identifiant du type"),
    ("libelle_type_hebergement", "VARCHAR2(60)", 1, "UK", "g", "Libellé du type")])
rel("OPTION_HEBERGEMENT", "ent", "Établissements et hébergements", "Prestation complémentaire (petit-déjeuner, parking, wifi, accès PMR…).", [
    ("id_option", ID, 1, "PK", "g", "Identifiant de l'option"),
    ("libelle_option", "VARCHAR2(60)", 1, "UK", "g", "Libellé de l'option")])
rel("HEBERGEMENT", "ent", "Établissements et hébergements",
    "Unité réservable proposée par un établissement à FestiBed, indépendamment de tout festival.", [
    ("id_hebergement", ID, 1, "PK", "g", "Identifiant de l'hébergement"),
    ("libelle_hebergement", "VARCHAR2(120)", 1, "", "g", "Intitulé (ex. Chambre 12, Emplacement B4)"),
    ("capacite_hebergement", "NUMBER(3)", 1, "", "g", "Nombre maximal de personnes"),
    ("prix_nuit", "NUMBER(8,2)", 1, "", "g", "Prix d'une nuit (euros TTC)"),
    ("description_hebergement", "VARCHAR2(2000)", 0, "", "g", "Description libre"),
    ("statut_hebergement", "VARCHAR2(10)", 1, "", "g", "PUBLIE ou RETIRE"),
    ("id_etablissement", ID, 1, "FK:ETABLISSEMENT", "g", "Établissement qui le propose"),
    ("id_type_hebergement", ID, 1, "FK:TYPE_HEBERGEMENT", "g", "Type d'hébergement"),
    ("version_hebergement", ID, 1, "", "gt", "Version pour le verrouillage optimiste (@Version)")],
    ["CHECK (capacite_hebergement > 0)", "CHECK (prix_nuit >= 0)", "CHECK (statut_hebergement IN ('PUBLIE','RETIRE'))"])
rel("HEBERGEMENT_OPTION", "asso", "Établissements et hébergements", "Fait qu'un hébergement inclut une option.", [
    ("id_hebergement", ID, 1, "PK,FK:HEBERGEMENT", "g", ""),
    ("id_option", ID, 1, "PK,FK:OPTION_HEBERGEMENT", "g", "")])
rel("PHOTO", "ent", "Établissements et hébergements", "Photographie illustrant un hébergement (composant de l'hébergement).", [
    ("id_photo", ID, 1, "PK", "g", "Identifiant de la photo"),
    ("url_photo", "VARCHAR2(500)", 1, "", "g", "Emplacement du fichier image"),
    ("legende_photo", "VARCHAR2(200)", 0, "", "g", "Légende"),
    ("ordre_photo", "NUMBER(3)", 1, "", "g", "Rang d'affichage"),
    ("id_hebergement", ID, 1, "FK:HEBERGEMENT", "g", "Hébergement illustré")],
    ["UNIQUE (id_hebergement, ordre_photo)"])
rel("PERIODE_DISPONIBILITE", "ent", "Établissements et hébergements",
    "Intervalle de nuits [début, fin[ pendant lequel l'hébergeur ouvre un hébergement à FestiBed (composant de l'hébergement).", [
    ("id_periode", ID, 1, "PK", "g", "Identifiant de la période"),
    ("date_debut_dispo", "DATE", 1, "", "g", "Première nuit disponible"),
    ("date_fin_dispo", "DATE", 1, "", "g", "Jour de départ (nuit exclue)"),
    ("id_hebergement", ID, 1, "FK:HEBERGEMENT", "g", "Hébergement concerné")],
    ["CHECK (date_fin_dispo > date_debut_dispo)"])

# ---------------------------------------------------------------- panier
rel("PANIER", "ent", "Panier", "Sélection temporaire d'un festivalier, éventuellement anonyme.", [
    ("id_panier", ID, 1, "PK", "g", "Identifiant du panier"),
    ("jeton_session", "VARCHAR2(36)", 1, "UK", "g", "Jeton (UUID) du navigateur pour un panier anonyme"),
    ("date_creation_panier", "TIMESTAMP", 1, "", "g", "Date de création"),
    ("date_maj_panier", "TIMESTAMP", 1, "", "g", "Date de dernière modification"),
    ("id_festivalier", ID, 0, "FK:FESTIVALIER", "g", "Propriétaire une fois authentifié")], view="b")
rel("SELECTION", "ent", "Panier",
    "Élément du panier : pour un festival, le nombre de Pass demandés et les hébergements choisis (composant du panier).", [
    ("id_selection", ID, 1, "PK", "g", "Identifiant de la sélection"),
    ("nb_pass_selection", "NUMBER(3)", 1, "", "g", "Nombre de Pass demandés"),
    ("date_ajout", "TIMESTAMP", 1, "", "g", "Date d'ajout au panier"),
    ("date_expiration", "TIMESTAMP", 1, "", "g", "Date de retrait automatique (ajout + 15 min, paramétrable)"),
    ("id_panier", ID, 1, "FK:PANIER", "g", "Panier"),
    ("id_festival", ID, 1, "FK:FESTIVAL", "g", "Festival ciblé")],
    ["CHECK (nb_pass_selection > 0)", "CHECK (date_expiration > date_ajout)", "UNIQUE (id_panier, id_festival)"], view="b")
rel("SELECTION_HEBERGEMENT", "asso", "Panier", "Fait qu'une sélection inclut un hébergement.", [
    ("id_selection", ID, 1, "PK,FK:SELECTION", "g", ""),
    ("id_hebergement", ID, 1, "PK,FK:HEBERGEMENT", "g", "")], view="b")

# ---------------------------------------------------------------- réservation
rel("COMMANDE", "ent", "Réservation", "Résultat de la validation d'un panier ; regroupe une réservation par festival et porte le paiement.", [
    ("id_commande", ID, 1, "PK", "g", "Identifiant de la commande"),
    ("numero_commande", "VARCHAR2(20)", 1, "UK", "g", "Numéro communiqué au festivalier"),
    ("date_commande", "TIMESTAMP", 1, "", "g", "Date de validation du panier"),
    ("montant_commande", "NUMBER(10,2)", 1, "", "g", "Montant total (euros TTC)"),
    ("statut_commande", "VARCHAR2(10)", 1, "", "g", "VALIDEE, PAYEE ou ANNULEE"),
    ("id_festivalier", ID, 1, "FK:FESTIVALIER", "g", "Festivalier")],
    ["CHECK (montant_commande >= 0)", "CHECK (statut_commande IN ('VALIDEE','PAYEE','ANNULEE'))"], view="b")
rel("PAIEMENT", "ent", "Réservation", "Règlement (ou tentative) d'une commande ; non développé dans le prototype.", [
    ("id_paiement", ID, 1, "PK", "g", "Identifiant du paiement"),
    ("montant_paiement", "NUMBER(10,2)", 1, "", "g", "Montant réglé"),
    ("moyen_paiement", "VARCHAR2(10)", 0, "", "g", "CARTE, VIREMENT ou AUTRE"),
    ("statut_paiement", "VARCHAR2(10)", 1, "", "g", "NON_GERE, EN_ATTENTE, ACCEPTE, REFUSE, REMBOURSE"),
    ("date_paiement", "TIMESTAMP", 0, "", "g", "Date du règlement"),
    ("reference_paiement", "VARCHAR2(100)", 0, "", "g", "Référence du prestataire de paiement"),
    ("id_commande", ID, 1, "FK:COMMANDE", "g", "Commande réglée")],
    ["CHECK (montant_paiement >= 0)", "CHECK (moyen_paiement IN ('CARTE','VIREMENT','AUTRE'))",
     "CHECK (statut_paiement IN ('NON_GERE','EN_ATTENTE','ACCEPTE','REFUSE','REMBOURSE'))"], view="b")
rel("RESERVATION", "ent", "Réservation", "Réservation définitive de Pass et d'hébergements pour un même festival.", [
    ("id_reservation", ID, 1, "PK", "g", "Identifiant de la réservation"),
    ("numero_reservation", "VARCHAR2(20)", 1, "UK", "g", "Numéro de réservation"),
    ("statut_reservation", "VARCHAR2(10)", 1, "", "g", "CONFIRMEE ou ANNULEE"),
    ("date_annulation", "TIMESTAMP", 0, "", "g", "Date d'annulation"),
    ("motif_annulation", "VARCHAR2(300)", 0, "", "g", "Motif (ex. festival désactivé)"),
    ("id_commande", ID, 1, "FK:COMMANDE", "g", "Commande d'origine"),
    ("id_festival", ID, 1, "FK:FESTIVAL", "g", "Festival concerné")],
    ["CHECK (statut_reservation IN ('CONFIRMEE','ANNULEE'))",
     "CHECK ((statut_reservation = 'CONFIRMEE' AND date_annulation IS NULL) OR (statut_reservation = 'ANNULEE' AND date_annulation IS NOT NULL))",
     "UNIQUE (id_commande, id_festival)"], view="b")
rel("PASS", "ent", "Réservation", "Droit d'accès individuel à un festival pour toute sa durée, édité en PDF (composant de la réservation).", [
    ("id_pass", ID, 1, "PK", "g", "Identifiant du Pass"),
    ("numero_pass", "VARCHAR2(20)", 1, "UK", "g", "Numéro imprimé sur le Pass"),
    ("prix_paye", "NUMBER(8,2)", 1, "", "g", "Prix du Pass au moment de la réservation"),
    ("date_emission_pass", "TIMESTAMP", 1, "", "g", "Date d'émission"),
    ("id_reservation", ID, 1, "FK:RESERVATION", "g", "Réservation")],
    ["CHECK (prix_paye >= 0)"], view="b")
rel("BON_HEBERGEMENT", "ent", "Réservation", "Document PDF attestant la réservation d'un hébergement pour les nuits d'un festival (composant de la réservation).", [
    ("id_bon", ID, 1, "PK", "g", "Identifiant du bon"),
    ("numero_bon", "VARCHAR2(20)", 1, "UK", "g", "Numéro imprimé sur le bon"),
    ("date_arrivee", "DATE", 1, "", "g", "Première nuit réservée"),
    ("date_depart", "DATE", 1, "", "g", "Jour de départ"),
    ("prix_sejour", "NUMBER(10,2)", 1, "", "g", "Prix du séjour au moment de la réservation"),
    ("date_emission_bon", "TIMESTAMP", 1, "", "g", "Date d'émission"),
    ("id_reservation", ID, 1, "FK:RESERVATION", "g", "Réservation"),
    ("id_hebergement", ID, 1, "FK:HEBERGEMENT", "g", "Hébergement occupé")],
    ["CHECK (date_depart > date_arrivee)", "CHECK (prix_sejour >= 0)",
     "UNIQUE (id_reservation, id_hebergement)", "UNIQUE (id_bon, id_hebergement)"], view="b")
rel("NUITEE", "tech", "Réservation", "Nuit occupée d'un hébergement : traduction physique de la contrainte de non-chevauchement.", [
    ("id_hebergement", ID, 1, "PK,FK:HEBERGEMENT", "gt", "Hébergement occupé"),
    ("date_nuit", "DATE", 1, "PK", "gt", "Nuit occupée"),
    ("id_bon", ID, 1, "FK:BON_HEBERGEMENT", "gt", "Bon qui occupe la nuit")],
    ["FOREIGN KEY (id_bon, id_hebergement) REFERENCES BON_HEBERGEMENT (id_bon, id_hebergement) ON DELETE CASCADE"], view="b")
rel("NOTE_FESTIVAL", "asso", "Notation", "Note attribuée par un festivalier à un festival après son séjour.", [
    ("id_festivalier", ID, 1, "PK,FK:FESTIVALIER", "g", ""),
    ("id_festival", ID, 1, "PK,FK:FESTIVAL", "g", ""),
    ("valeur_note_festival", "NUMBER(1)", 1, "", "g", "Note de 1 à 5"),
    ("commentaire_note_festival", "VARCHAR2(1000)", 0, "", "g", "Commentaire"),
    ("date_note_festival", "TIMESTAMP", 1, "", "g", "Date de la note")],
    ["CHECK (valeur_note_festival BETWEEN 1 AND 5)"], view="b")
rel("NOTE_ETABLISSEMENT", "asso", "Notation", "Note attribuée par un festivalier à un établissement après son séjour.", [
    ("id_festivalier", ID, 1, "PK,FK:FESTIVALIER", "g", ""),
    ("id_etablissement", ID, 1, "PK,FK:ETABLISSEMENT", "g", ""),
    ("valeur_note_etab", "NUMBER(1)", 1, "", "g", "Note de 1 à 5"),
    ("commentaire_note_etab", "VARCHAR2(1000)", 0, "", "g", "Commentaire"),
    ("date_note_etab", "TIMESTAMP", 1, "", "g", "Date de la note")],
    ["CHECK (valeur_note_etab BETWEEN 1 AND 5)"], view="b")
rel("NOTIFICATION", "ent", "Notation", "Message adressé à un festivalier (annulation, chevauchement, expiration).", [
    ("id_notification", ID, 1, "PK", "g", "Identifiant"),
    ("type_notification", "VARCHAR2(30)", 1, "", "g", "ANNULATION_FESTIVAL, CHEVAUCHEMENT_RESERVATIONS, EXPIRATION_SELECTION"),
    ("message_notification", "VARCHAR2(1000)", 1, "", "g", "Texte affiché"),
    ("date_notification", "TIMESTAMP", 1, "", "g", "Date d'émission"),
    ("lue", "NUMBER(1)", 1, "", "gb", "Notification lue"),
    ("id_festivalier", ID, 1, "FK:FESTIVALIER", "g", "Destinataire"),
    ("id_reservation", ID, 0, "FK:RESERVATION", "g", "Réservation concernée")],
    ["CHECK (type_notification IN ('ANNULATION_FESTIVAL','CHEVAUCHEMENT_RESERVATIONS','EXPIRATION_SELECTION'))",
     "CHECK (lue IN (0,1))"], view="b")

# Entités du MCD sans relation propre
MCD_ONLY = OrderedDict([
    ("ANNEE", dict(sem="Année civile (dimension temporelle du soutien).", src=True, view="a",
                   attrs=[("annee_soutien", "Entier", "Année civile", True)])),
    ("CAMPING", dict(sem="Établissement de typologie camping.", src=True, view="a",
                     attrs=[("categorie_camping", "Texte", "TOURISME ou LOISIRS", False)])),
    ("VILLAGE_VACANCES", dict(sem="Établissement de typologie village de vacances.", src=True, view="a",
                              attrs=[("mention_village", "Texte", "Mention", False), ("type_sejour", "Texte", "Formule de séjour", False)])),
])
# Attributs de relations portés graphiquement par une sous-entité (transformation T3)
SUB_ATTR = {"categorie_camping": "CAMPING", "mention_village": "VILLAGE_VACANCES", "type_sejour": "VILLAGE_VACANCES"}

# Spécialisations : (sur-entité, sous-entités, contrainte, transformation, justification)
SPECS = [
    ("ETABLISSEMENT", ["CAMPING", "VILLAGE_VACANCES"], "X", "T3", True,
     "Spécialisation exclusive non totale définie par un attribut (code_typologie) : T3 recommandé par le cours "
     "(une seule relation ETABLISSEMENT, attributs spécifiques nullables, discriminant = code_typologie, CHECK de cohérence). "
     "Priorité au temps de calcul : la recherche d'hébergements ne fait aucune jointure supplémentaire."),
    ("COMPTE_INTERNE", ["ORGANISATEUR", "HEBERGEUR"], "T", "T1", False,
     "Spécialisation totale mais non exclusive (une même personne peut être organisateur et hébergeur) : T1 "
     "(une relation par entité, dépendances d'inclusion ORGANISATEUR[id_compte] ⊆ COMPTE_INTERNE[id_compte]). "
     "Priorité à la qualité des données : les associations ORGANISER et GERER référencent exactement le bon rôle."),
]

# Associations binaires x,1 (traduites par une clé étrangère) :
# (nom, sémantique, [(entité, cardinalité)], (relation, colonne FK), vue, sources?)
# "(1,1)" = composition (identification relative au composé)
ASSOS = [
    ("APPARTENIR", "Rattachement d'un département à sa région.", [("DEPARTEMENT", "1,1"), ("REGION", "0,n")], ("DEPARTEMENT", "id_region"), "a", True),
    ("SITUER", "Rattachement d'une commune à son département.", [("COMMUNE", "1,1"), ("DEPARTEMENT", "0,n")], ("COMMUNE", "code_departement"), "a", True),
    ("SE_DEROULER", "Commune principale où se tient un festival.", [("FESTIVAL", "1,1"), ("COMMUNE", "0,n")], ("FESTIVAL", "code_insee"), "a", True),
    ("RELEVER_DE", "Domaine artistique d'un festival.", [("FESTIVAL", "1,1"), ("DOMAINE", "0,n")], ("FESTIVAL", "id_domaine"), "a", True),
    ("PRECISER", "Style précisant un festival.", [("FESTIVAL", "0,1"), ("SOUS_DOMAINE", "0,n")], ("FESTIVAL", "id_sous_domaine"), "a", True),
    ("AVOIR_POUR_RYTHME", "Périodicité d'un festival.", [("FESTIVAL", "0,1"), ("PERIODICITE", "0,n")], ("FESTIVAL", "id_periodicite"), "a", True),
    ("LOCALISER", "Commune où se trouve un établissement.", [("ETABLISSEMENT", "1,1"), ("COMMUNE", "0,n")], ("ETABLISSEMENT", "code_insee"), "a", True),
    ("AVOIR_POUR_TYPOLOGIE", "Typologie réglementaire d'un établissement.", [("ETABLISSEMENT", "1,1"), ("TYPOLOGIE_ETABLISSEMENT", "0,n")], ("ETABLISSEMENT", "code_typologie"), "a", True),
    ("ETRE_CLASSE", "Classement officiel d'un établissement.", [("ETABLISSEMENT", "1,1"), ("CLASSEMENT", "0,n")], ("ETABLISSEMENT", "id_classement"), "a", True),
    ("ORGANISER", "Responsabilité d'un organisateur sur un festival.", [("FESTIVAL", "0,1"), ("ORGANISATEUR", "0,n")], ("FESTIVAL", "id_organisateur"), "a", False),
    ("GERER", "Responsabilité d'un hébergeur sur un établissement.", [("ETABLISSEMENT", "0,1"), ("HEBERGEUR", "0,n")], ("ETABLISSEMENT", "id_hebergeur"), "a", False),
    ("PROPOSER", "Offre d'un hébergement par un établissement.", [("HEBERGEMENT", "1,1"), ("ETABLISSEMENT", "0,n")], ("HEBERGEMENT", "id_etablissement"), "a", False),
    ("CATEGORISER", "Type d'un hébergement.", [("HEBERGEMENT", "1,1"), ("TYPE_HEBERGEMENT", "0,n")], ("HEBERGEMENT", "id_type_hebergement"), "a", False),
    ("ILLUSTRER", "Photo d'un hébergement (composition).", [("PHOTO", "(1,1)"), ("HEBERGEMENT", "0,n")], ("PHOTO", "id_hebergement"), "a", False),
    ("OUVRIR", "Période d'ouverture d'un hébergement (composition).", [("PERIODE_DISPONIBILITE", "(1,1)"), ("HEBERGEMENT", "0,n")], ("PERIODE_DISPONIBILITE", "id_hebergement"), "a", False),
    ("POSSEDER", "Panier d'un festivalier authentifié.", [("PANIER", "0,1"), ("FESTIVALIER", "0,n")], ("PANIER", "id_festivalier"), "b", False),
    ("CONTENIR", "Sélection d'un panier (composition).", [("SELECTION", "(1,1)"), ("PANIER", "0,n")], ("SELECTION", "id_panier"), "b", False),
    ("CIBLER", "Festival visé par une sélection.", [("SELECTION", "1,1"), ("FESTIVAL", "0,n")], ("SELECTION", "id_festival"), "b", False),
    ("PASSER", "Commande passée par un festivalier.", [("COMMANDE", "1,1"), ("FESTIVALIER", "0,n")], ("COMMANDE", "id_festivalier"), "b", False),
    ("REGLER", "Paiement d'une commande.", [("PAIEMENT", "1,1"), ("COMMANDE", "0,n")], ("PAIEMENT", "id_commande"), "b", False),
    ("REGROUPER", "Réservations issues d'une même commande.", [("RESERVATION", "1,1"), ("COMMANDE", "1,n")], ("RESERVATION", "id_commande"), "b", False),
    ("CONCERNER", "Festival d'une réservation.", [("RESERVATION", "1,1"), ("FESTIVAL", "0,n")], ("RESERVATION", "id_festival"), "b", False),
    ("DONNER_ACCES", "Pass d'une réservation (composition).", [("PASS", "(1,1)"), ("RESERVATION", "1,n")], ("PASS", "id_reservation"), "b", False),
    ("COMPRENDRE", "Bon d'hébergement d'une réservation (composition).", [("BON_HEBERGEMENT", "(1,1)"), ("RESERVATION", "1,n")], ("BON_HEBERGEMENT", "id_reservation"), "b", False),
    ("OCCUPER", "Hébergement occupé par un bon.", [("BON_HEBERGEMENT", "1,1"), ("HEBERGEMENT", "0,n")], ("BON_HEBERGEMENT", "id_hebergement"), "b", False),
    ("RECEVOIR", "Destinataire d'une notification.", [("NOTIFICATION", "1,1"), ("FESTIVALIER", "0,n")], ("NOTIFICATION", "id_festivalier"), "b", False),
    ("SIGNALER", "Réservation à l'origine d'une notification.", [("NOTIFICATION", "0,1"), ("RESERVATION", "0,n")], ("NOTIFICATION", "id_reservation"), "b", False),
]
# Cardinalités des associations n-aires devenues relations
ASSO_CARDS = {
    "FESTIVAL_COMMUNE": [("FESTIVAL", "0,n"), ("COMMUNE", "0,n")],
    "SOUTIEN": [("FESTIVAL", "0,n"), ("ORGANISME_SOUTIEN", "0,n"), ("ANNEE", "0,n")],
    "HEBERGEMENT_OPTION": [("HEBERGEMENT", "0,n"), ("OPTION_HEBERGEMENT", "0,n")],
    "SELECTION_HEBERGEMENT": [("SELECTION", "1,n"), ("HEBERGEMENT", "0,n")],
    "NOTE_FESTIVAL": [("FESTIVALIER", "0,n"), ("FESTIVAL", "0,n")],
    "NOTE_ETABLISSEMENT": [("FESTIVALIER", "0,n"), ("ETABLISSEMENT", "0,n")],
}
# Contraintes Merise/2 entre associations : (code, type, association contrainte, association de référence, texte)
CI_MERISE2 = [
    ("CI-I1", "I", "NOTE_FESTIVAL", "CONCERNER",
     "Inclusion : un festivalier ne note un festival que s'il existe une réservation CONFIRMEE de ce festivalier "
     "(PASSER ∘ REGROUPER) concernant ce festival (CONCERNER), terminée à la date de la note."),
    ("CI-I2", "I", "NOTE_ETABLISSEMENT", "OCCUPER",
     "Inclusion : un festivalier ne note un établissement que s'il y a occupé un hébergement (OCCUPER ∘ PROPOSER) "
     "par une réservation CONFIRMEE terminée."),
]

COMPOSITION_TABLES = {a[3][0] for a in ASSOS if any(c.startswith("(") for _, c in a[2])} | {"SELECTION_HEBERGEMENT", "HEBERGEMENT_OPTION"}

# =============================================================================
# 2. OUTILS
# =============================================================================
def cols(n): return R[n]["cols"]
def pk(n): return [c[0] for c in cols(n) if "PK" in c[3]]
def is_fk(c): return "FK:" in c[3]
def fk_target(c):
    t = c[3].split("FK:")[1]
    tab, _, col = t.partition(".")
    return tab, (col or pk(tab)[0])
def fks(n): return [(c[0],) + fk_target(c) + (c[2],) for c in cols(n) if is_fk(c)]


def domaine(c):
    name, ty, nn, key, fl, _ = c
    if "b" in fl: return "Booléen"
    if ty.startswith(("VARCHAR2", "CHAR")):
        return "Texte(%s)" % re.search(r"\((\d+)", ty).group(1)
    if ty == "DATE": return "Date"
    if ty == "TIMESTAMP": return "DateHeure"
    m = re.match(r"NUMBER\((\d+)(?:,(\d+))?\)", ty)
    if m and m.group(2): return "Décimal(%s,%s)" % (m.group(1), m.group(2))
    return "Entier"


def mcd_attrs(n, sources_only=False):
    """Attributs conceptuels d'une entité : ni clés étrangères, ni colonnes techniques, ni attributs de sous-entités."""
    out = []
    for c in cols(n):
        name, ty, nn, key, fl, desc = c
        if is_fk(c) and R[n]["kind"] != "asso": continue
        if is_fk(c): continue
        if "t" in fl or name in SUB_ATTR: continue
        if sources_only and "g" in fl: continue
        out.append(c)
    return out


# =============================================================================
# 3. VÉRIFICATIONS (règles de qualité du cours)
# =============================================================================
errors = []
# a) chaque FK d'une relation 'ent' est la traduction d'exactement une association x,1 (ou d'une spécialisation T1)
fk_from_assos = {(a[3][0], a[3][1]) for a in ASSOS}
for n, r in R.items():
    for col, tab, tcol, nn in fks(n):
        if r["kind"] in ("ent",) and (n, col) not in fk_from_assos:
            errors.append(f"FK {n}.{col} sans association dans le MCD")
        if tab not in R: errors.append(f"FK {n}.{col} -> {tab} inconnue")
for a in ASSOS:
    t, c = a[3]
    if c not in [x[0] for x in cols(t)]: errors.append(f"association {a[0]} : colonne {t}.{c} absente")
    side = [card for e, card in a[2] if e == t][0]
    nn = [x[2] for x in cols(t) if x[0] == c][0]
    if side.strip("()").startswith("1") != bool(nn):
        errors.append(f"association {a[0]} : cardinalité {side} incohérente avec NOT NULL={nn} sur {t}.{c}")
# b) règle 1 du cours : noms d'entités, d'associations et d'attributs du MCD tous distincts
names = {}
def reg(nm, what):
    if nm in names and names[nm] != what: errors.append(f"nom non distinct : {nm} ({names[nm]} / {what})")
    names[nm] = what
for n, r in R.items():
    if r["kind"] != "tech": reg(n, "relation " + n)
    for c in mcd_attrs(n):
        if r["kind"] == "asso" and "PK" in c[3] and n != "SOUTIEN": continue
        if n == "SOUTIEN" and c[0] == "annee_soutien": continue
        reg(c[0], "attribut de " + n)
for n, e in MCD_ONLY.items():
    reg(n, "entité " + n)
    for a in e["attrs"]:
        if a[0] not in SUB_ATTR: reg(a[0], "attribut de " + n)
for a in ASSOS: reg(a[0], "association " + a[0])
# c) règle 2 : chaque entité a un identifiant
for n, r in R.items():
    if not pk(n): errors.append(f"{n} sans identifiant")
if errors:
    print("\n".join(errors)); sys.exit(1)

# =============================================================================
# 4. PLANTUML
# =============================================================================
MERISE_STYLE = """!pragma layout smetana
allowmixing
hide circle
hide empty members
hide stereotype
skinparam shadowing false
skinparam defaultFontName Arial
skinparam defaultFontSize 12
<style>
classDiagram {
  class {
    BackgroundColor #E0F7FA
    LineColor #00838F
  }
  .ajout {
    BackgroundColor #FFF8E1
    LineColor #EF6C00
  }
  .ref {
    BackgroundColor #EEEEEE
    LineColor #9E9E9E
  }
  .asso {
    BackgroundColor #E8F5E9
    LineColor #2E7D32
    RoundCorner 40
  }
}
usecase {
  BackgroundColor #FFF59D
  LineColor #F9A825
}
</style>
"""


def merise_entity(n, sources_only, ref=False):
    if n in MCD_ONLY:
        e = MCD_ONLY[n]
        lines = [(f"<u>{a}</u>" if ident else a) + f" : {d}" for a, d, _, ident in e["attrs"]]
        st = "" if e["src"] else " <<ajout>>"
        return f'class "{n}" as {n}{st} {{\n  ' + "\n  ".join("{field} " + l for l in lines) + "\n}"
    r = R[n]
    st = " <<ref>>" if ref else ("" if r["src"] else " <<ajout>>")
    lines = []
    for c in mcd_attrs(n, sources_only):
        if ref and "PK" not in c[3]: continue
        if r["kind"] == "sub1" and "PK" in c[3]: continue   # identifiant hérité de la sur-entité
        nm = f"<u>{c[0]}</u>" if "PK" in c[3] else c[0]
        if "g" in c[4] and r["src"]: nm = f"<b>{nm}</b>"
        if "c" in c[4]: nm += " (calc.)"
        lines.append("{field} " + nm + " : " + domaine(c))
    if ref: lines.append("{field} … (cf. vue 1)")
    return f'class "{n}" as {n}{st} {{\n  ' + "\n  ".join(lines) + "\n}"


def merise_asso_box(name, attrs=()):
    if attrs:
        body = "\n  ".join("{field} " + f"{c[0]} : {domaine(c)}" for c in attrs)
        return f'class "{name}" as A_{name} <<asso>> {{\n  {body}\n}}'
    return f'class "{name}" as A_{name} <<asso>>'


def leg_links(a, legs):
    """Première patte entité -> association, les autres association -> entité :
    l'association se place entre les entités qu'elle relie (lecture Merise)."""
    (e0, c0), rest = legs[0], legs[1:]
    return [f'{e0} "{c0}" -- A_{a}'] + [f'A_{a} -- "{c}" {e}' for e, c in rest]


def gen_mcd(fname, title, entities, refs, sources_only, view_filter, notes=()):
    out = [f"@startuml {fname}", "' Généré par out/outils/generer_modeles.py - ne pas modifier à la main", MERISE_STYLE, f"title {title}", ""]
    shown = set(entities) | set(refs)
    for n in entities: out.append(merise_entity(n, sources_only))
    for n in refs: out.append(merise_entity(n, sources_only, ref=True))
    links = []
    for a in ASSOS:
        if sources_only and not a[5]: continue
        legs = a[2]
        if not all(e in shown for e, _ in legs): continue
        if not any(e in entities for e, _ in legs): continue
        out.append(merise_asso_box(a[0]))
        links += leg_links(a[0], legs)
    for n, legs in ASSO_CARDS.items():
        if sources_only and not R[n]["src"]: continue
        if not all(e in shown for e, _ in legs) or not any(e in entities for e, _ in legs): continue
        attrs = [c for c in cols(n) if not is_fk(c) and not (n == "SOUTIEN" and c[0] == "annee_soutien")]
        out.append(merise_asso_box(n, attrs))
        links += leg_links(n, legs)
    for i, (sup, subs, cstr, tr, src, _) in enumerate(SPECS):
        if sources_only and not src: continue
        if sup not in entities: continue
        out.append(f"<> SP{i}")
        for s in subs: links.append(f"{s} -- SP{i}")
        links.append(f"SP{i} --|> {sup} : {cstr}")
    for code, typ, a1, a2, _ in CI_MERISE2:
        if f"A_{a1}" in "\n".join(out) and f"A_{a2}" in "\n".join(out):
            out.append(f'usecase "{typ}" as {code.replace("-", "_")}')
            links.append(f"A_{a1} .. {code.replace('-', '_')}")
            links.append(f"{code.replace('-', '_')} ..> A_{a2}")
    out += [""] + links + list(notes) + ["@enduml"]
    open(os.path.join(PUML, fname + ".puml"), "w", encoding="utf-8").write("\n".join(out) + "\n")


src_entities = [n for n, r in R.items() if r["src"] and r["kind"] == "ent"] + [n for n, e in MCD_ONLY.items() if e["src"]]
gen_mcd("02_mcd_sources_publiques", "MCD rétro-conçu des sources publiques (Merise)", src_entities, [], True, None)
view_a = [n for n, r in R.items() if r["view"] == "a" and r["kind"] in ("ent", "sub1")] + list(MCD_ONLY)
view_b = [n for n, r in R.items() if r["view"] == "b" and r["kind"] in ("ent", "sub1")]
gen_mcd("03a_mcd_global_offre", "MCD global FestiBed - vue 1/2 : référentiels, offre, comptes (Merise)", view_a, [], False, "a")
gen_mcd("03b_mcd_global_reservation", "MCD global FestiBed - vue 2/2 : panier, réservation, notation (Merise / Merise 2)",
        view_b, ["FESTIVAL", "HEBERGEMENT", "ETABLISSEMENT"], False, "b")

MLD_STYLE = """!pragma layout smetana
hide circle
hide empty members
hide stereotype
skinparam shadowing false
skinparam defaultFontName Arial
skinparam defaultFontSize 12
skinparam ArrowColor #455A64
<style>
classDiagram {
  class {
    BackgroundColor #FFFFFF
    LineColor #37474F
    HeaderBackgroundColor #ECEFF1
  }
  .ref {
    BackgroundColor #EEEEEE
    LineColor #9E9E9E
  }
}
</style>
"""


def mld_table(n, sources_only, ref=False):
    lines = []
    for c in cols(n):
        name, ty, nn, key, fl, _ = c
        if sources_only and "g" in fl: continue
        if ref and "PK" not in key: continue
        tags = [t for t in ("PK", "FK") if t in key] + (["UK"] if key == "UK" else [])
        nm = f"<u>{name}</u>" if "PK" in key else name
        lines.append("{field} " + f"{nm} : {ty}" + (" NOT NULL" if nn and "PK" not in key else "") + (f"  <{','.join(tags)}>" if tags else ""))
    if ref: lines.append("{field} … (cf. vue 1)")
    st = " <<ref>>" if ref else ""
    return f'class "{n}" as {n}{st} {{\n  ' + "\n  ".join(lines) + "\n}"


def gen_mld(fname, title, tables, refs, sources_only):
    out = [f"@startuml {fname}", "' Généré par out/outils/generer_modeles.py - ne pas modifier à la main", MLD_STYLE, f"title {title}", ""]
    shown = set(tables) | set(refs)
    out += [mld_table(n, sources_only) for n in tables] + [mld_table(n, sources_only, True) for n in refs]
    seen = set()
    for n in tables:
        for col, tab, tcol, nn in fks(n):
            if sources_only and "g" in [c for c in cols(n) if c[0] == col][0][4]: continue
            if tab in shown and (n, tab, col) not in seen:
                seen.add((n, tab, col))
                out.append(f'{n} --> {tab} : "{col} = {tcol}"')
    out.append("@enduml")
    open(os.path.join(PUML, fname + ".puml"), "w", encoding="utf-8").write("\n".join(out) + "\n")


src_tables = [n for n, r in R.items() if r["src"]]
gen_mld("01_mld_sources_publiques", "MLD rétro-conçu des sources publiques (3FN)", src_tables, [], True)
gen_mld("05a_mld_global_offre", "MLD global - vue 1/2 : référentiels, offre, comptes (3FN)",
        [n for n, r in R.items() if r["view"] == "a"], [], False)
gen_mld("05b_mld_global_reservation", "MLD global - vue 2/2 : panier, réservation, notation (3FN)",
        [n for n, r in R.items() if r["view"] == "b"], ["FESTIVAL", "HEBERGEMENT", "ETABLISSEMENT"], False)

# =============================================================================
# 5. MPD (SQL Oracle)
# =============================================================================
DEFAULT0 = {"nb_pass_reserves", "quota_pass", "nb_notes_etablissement", "lue", "compte_test", "classement_proroge",
            "version_festival", "version_hebergement"}
INDEXES = [
    ("IX_FESTIVAL_RECHERCHE", "FESTIVAL (statut_festival, date_debut_festival, date_fin_festival)", "Recherche de festivals par période"),
    ("IX_FESTIVAL_DISPO", "FESTIVAL (statut_festival, pass_disponibles)", "Festivals ayant encore des Pass (colonne virtuelle)"),
    ("IX_FESTIVAL_STYLE", "FESTIVAL (id_domaine, id_sous_domaine)", "Recherche par type / style"),
    ("IX_COMMUNE_GEO", "COMMUNE (latitude_commune, longitude_commune)", "Pré-filtre géographique (boîte englobante)"),
    ("IX_ETAB_GEO", "ETABLISSEMENT (latitude_etablissement, longitude_etablissement)", "Hébergements proches d'un festival"),
    ("IX_ETAB_TYPO_CLASS", "ETABLISSEMENT (code_typologie, id_classement)", "Filtres typologie / classement"),
    ("IX_HEB_RECHERCHE", "HEBERGEMENT (id_etablissement, statut_hebergement, capacite_hebergement)", "Hébergements publiés d'un établissement"),
    ("IX_PERIODE_DATES", "PERIODE_DISPONIBILITE (id_hebergement, date_debut_dispo, date_fin_dispo)", "Disponibilité sur la période du festival"),
    ("IX_BON_HEB_DATES", "BON_HEBERGEMENT (id_hebergement, date_arrivee)", "Retrait d'hébergement, statistiques hébergeur"),
    ("IX_RESA_FESTIVAL", "RESERVATION (id_festival, statut_reservation)", "Désactivation d'un festival, statistiques organisateur"),
    ("IX_COMMANDE_FESTIVALIER", "COMMANDE (id_festivalier, date_commande)", "Historique et chevauchements d'un festivalier"),
    ("IX_COMMANDE_DATE", "COMMANDE (date_commande)", "Statistiques hebdomadaires"),
    ("IX_SELECTION_EXPIRATION", "SELECTION (date_expiration)", "Purge des sélections expirées"),
]


def ordre_creation():
    """Tri topologique : une relation est créée après toutes celles qu'elle référence."""
    ordre, vus = [], set()
    def visite(n):
        if n in vus: return
        vus.add(n)
        for _, tab, _, _ in fks(n):
            if tab != n: visite(tab)
        ordre.append(n)
    for n in R: visite(n)
    return ordre


def mpd():
    L = ["-- =============================================================================",
         "-- FestiBed - MPD : schéma physique Oracle (traduction du MLD global en 3FN)",
         "-- Généré par out/outils/generer_modeles.py à partir de la même spécification",
         "-- que les MCD/MLD PlantUML : ne pas modifier à la main.",
         "-- Périodes en intervalle semi-ouvert [début, fin[ (fin = jour de départ).",
         "-- =============================================================================", ""]
    for n in ordre_creation():
        r = R[n]
        defs = []
        for name, ty, nn, key, fl, desc in cols(n):
            s = f"  {name:<30} {ty}"
            if key == "PK" and ty == ID: s += " GENERATED BY DEFAULT AS IDENTITY"
            if name in DEFAULT0: s += " DEFAULT 0"
            if nn: s += " NOT NULL"
            defs.append(s)
        if n == "FESTIVAL":
            defs.append(f"  {'pass_disponibles':<30} GENERATED ALWAYS AS (quota_pass - nb_pass_reserves) VIRTUAL")
        defs.append(f"  CONSTRAINT PK_{n} PRIMARY KEY ({', '.join(pk(n))})")
        for c in cols(n):
            if c[3] == "UK": defs.append(f"  CONSTRAINT UK_{n}_{c[0]} UNIQUE ({c[0]})".upper().replace("UNIQUE (" + c[0].upper(), "UNIQUE (" + c[0]))
        for col, tab, tcol, nn in fks(n):
            if (n, col) == ("NUITEE", "id_bon"): continue   # couverte par la FK composée
            cascade = " ON DELETE CASCADE" if (n in COMPOSITION_TABLES or R[n]["kind"] in ("asso", "sub1")) and nn else ""
            defs.append(f"  CONSTRAINT FK_{n}_{col.upper()} FOREIGN KEY ({col}) REFERENCES {tab} ({tcol}){cascade}")
        for i, chk in enumerate(r["checks"], 1):
            kind = "CK" if chk.startswith("CHECK") else ("UK" if chk.startswith("UNIQUE") else "FK")
            defs.append(f"  CONSTRAINT {kind}_{n}_{i} {chk}")
        L.append(f"-- {r['sem']}")
        L.append(f"CREATE TABLE {n} (\n" + ",\n".join(defs) + "\n);\n")
    L += ["-- -----------------------------------------------------------------------------",
          "-- Index sur les clés étrangères (Oracle ne les crée pas : sans eux, modifier ou",
          "-- supprimer une ligne parente verrouille toute la table fille).",
          "-- -----------------------------------------------------------------------------"]
    done = set()
    for n in R:
        for col, tab, tcol, nn in fks(n):
            if pk(n) and pk(n)[0] == col: continue
            ix = f"IX_{n}_{col}".upper()
            if ix not in done:
                done.add(ix); L.append(f"CREATE INDEX {ix} ON {n} ({col});")
    L.append("\n-- Index des requêtes critiques")
    for ix, spec, why in INDEXES:
        L.append(f"CREATE INDEX {ix} ON {spec};  -- {why}")
    return "\n".join(L) + "\n"


open(os.path.join(SQL, "mpd_oracle.sql"), "w", encoding="utf-8").write(mpd())

# =============================================================================
# 6. FORMALISME TEXTUEL (HTML pour le document)
# =============================================================================
e = html.escape


def mld_text(tables, sources_only):
    out = ["<ul class='mld'>"]
    incl = []
    for n in tables:
        parts = []
        for c in cols(n):
            if sources_only and "g" in c[4]: continue
            t = e(c[0])
            if "PK" in c[3]: t = f"<u>{t}</u>"
            if not c[2]: t += "<sup>?</sup>"
            parts.append(t)
        out.append(f"<li><b>{n}</b>({', '.join(parts)})</li>")
        for col, tab, tcol, nn in fks(n):
            if sources_only and "g" in [c for c in cols(n) if c[0] == col][0][4]: continue
            incl.append(f"{n}[{col}] ⊆ {tab}[{tcol}]")
    out.append("</ul><p class='incl-title'><b>Dépendances d'inclusion (clés étrangères)</b></p><ul class='mld incl'>")
    out += [f"<li>{e(i)}</li>" for i in incl]
    out.append("</ul>")
    return "\n".join(out)


open(os.path.join(BUILD, "mld_sources.html"), "w", encoding="utf-8").write(mld_text(src_tables, True))
open(os.path.join(BUILD, "mld_global.html"), "w", encoding="utf-8").write(mld_text(list(R), False))


def dictionnaire():
    h = ["<h4>Entités</h4><table class='dico'><tr><th style='width:19%'>Entité</th><th>Sémantique</th><th style='width:46%'>Attributs (domaine) — identifiant souligné</th></tr>"]
    for n, r in R.items():
        if r["kind"] not in ("ent", "sub1"): continue
        attrs = []
        for c in mcd_attrs(n):
            if r["kind"] == "sub1" and "PK" in c[3]: continue
            a = f"<u>{e(c[0])}</u>" if "PK" in c[3] else e(c[0])
            extra = " — calculé" if "c" in c[4] else ""
            attrs.append(f"{a} : {domaine(c)}{'' if c[2] else ' (facultatif)'}{extra} — {e(c[5])}")
        ident = "hérité de COMPTE_INTERNE (id_compte)" if r["kind"] == "sub1" else ""
        tag = "" if r["src"] else " <span class='tag bo'>ajout</span>"
        h.append(f"<tr><td><b>{n}</b>{tag}</td><td>{e(r['sem'])}{('<br><i>Identifiant ' + ident + '</i>') if ident else ''}</td><td>{'<br>'.join(attrs)}</td></tr>")
    for n, x in MCD_ONLY.items():
        attrs = [(f"<u>{a}</u>" if idt else a) + f" : {d} — {e(s)}" for a, d, s, idt in x["attrs"]]
        sub = next((f"<br><i>Sous-entité de {s[0]} ({s[2]})</i>" for s in SPECS if n in s[1]), "")
        h.append(f"<tr><td><b>{n}</b></td><td>{e(x['sem'])}{sub}</td><td>{'<br>'.join(attrs)}</td></tr>")
    h.append("</table>")
    h.append("<h4>Associations</h4><table class='dico'><tr><th style='width:22%'>Association</th><th>Sémantique</th><th style='width:30%'>Entités liées (dimension)</th><th style='width:20%'>Attributs / traduction</th></tr>")
    for a in ASSOS:
        legs = ", ".join(f"{x}({c.replace(',', '-')})" for x, c in a[2])
        h.append(f"<tr><td><b>{a[0]}</b></td><td>{e(a[1])}</td><td>{legs}</td><td>clé étrangère {a[3][0]}.{a[3][1]}</td></tr>")
    for n, legs in ASSO_CARDS.items():
        attrs = [c for c in cols(n) if not is_fk(c) and not (n == "SOUTIEN" and c[0] == "annee_soutien")]
        at = "<br>".join(f"{c[0]} : {domaine(c)}" for c in attrs) or "—"
        h.append(f"<tr><td><b>{n}</b></td><td>{e(R[n]['sem'])}</td><td>{', '.join(f'{x}({c.replace(chr(44), chr(45))})' for x, c in legs)}</td><td>{at}<br><i>relation {n}</i></td></tr>")
    h.append("</table>")
    h.append("<h4>Spécialisations et transformation retenue</h4><table class='dico'><tr><th style='width:22%'>Sur-entité</th><th style='width:24%'>Sous-entités</th><th style='width:9%'>Contrainte</th><th style='width:7%'>Transf.</th><th>Motivation (à documenter selon le cours)</th></tr>")
    for sup, subs, cstr, tr, _, why in SPECS:
        h.append(f"<tr><td>{sup}</td><td>{', '.join(subs)}</td><td>{cstr}</td><td>{tr}</td><td>{e(why)}</td></tr>")
    h.append("</table>")
    return "\n".join(h)


open(os.path.join(BUILD, "dictionnaire.html"), "w", encoding="utf-8").write(dictionnaire())
ci = "".join(f"<li><b>{c}</b> ({t}) — {e(txt)}</li>" for c, t, _, _, txt in CI_MERISE2)
open(os.path.join(BUILD, "ci_merise2.html"), "w", encoding="utf-8").write(ci)
idx = "".join(f"<tr><td><code>{e(spec)}</code></td><td>{e(why)}</td></tr>" for _, spec, why in INDEXES)
open(os.path.join(BUILD, "index.html"), "w", encoding="utf-8").write(idx)

n_ent = sum(1 for r in R.values() if r["kind"] in ("ent", "sub1")) + len(MCD_ONLY)
print(f"OK : {len(R)} relations, {n_ent} entités MCD, {len(ASSOS) + len(ASSO_CARDS)} associations, règles du cours vérifiées.")

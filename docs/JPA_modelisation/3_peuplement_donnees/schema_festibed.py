"""FestiBed - Groupe 3 - Schéma relationnel (source unique).

Ce module décrit une seule fois les tables du modèle JPA (MLD GLOBAL FINAL du 22/10/2026
+ améliorations JPA + intégration OpenStreetMap du 03/11/2026). Tout le reste en est généré,
ce qui évite les incohérences :
  - le DDL Oracle et le DDL H2 (01_schema_oracle.sql / 01_schema_h2.sql),
  - les en-têtes des CSV de peuplement et les fichiers de contrôle SQL*Loader,
  - les gabarits Excel et la conversion Excel -> INSERT,
  - le MLD PlantUML (docs/Output_Diagramme/MLD_GLOBAL_FINAL.puml, voir generer_mld.py).

Types abstraits :
  id        identifiant technique   UUID        Oracle RAW(16)          H2 UUID
  int       entier                  Int         Oracle NUMBER(10)       H2 INTEGER
  num(n)    petit entier            Int         Oracle NUMBER(n)        H2 INTEGER
  bool      booléen                 Boolean     Oracle NUMBER(1) 0/1    H2 BOOLEAN
  dec(p,s)  décimal                 BigDecimal  Oracle NUMBER(p,s)      H2 NUMERIC(p,s)
  str(n)    texte                   String      Oracle VARCHAR2(n CHAR) H2 VARCHAR(n)
  date      date                    LocalDate   DATE
  ts        horodatage              LocalDateTime TIMESTAMP

Identifiants : genere=True marque une table dont la clé primaire est un UUID généré par Hibernate
(@GeneratedValue(strategy = GenerationType.UUID)). Les autres colonnes « id » (sous-classes JOINED,
clés étrangères) reprennent l'UUID de la table racine. Le peuplement numérote les lignes en interne
puis écrit des UUID déterministes (uuid5) : même graine, mêmes identifiants. Aucune séquence.
"""
import re
import uuid

# ---------------------------------------------------------------- énumérations
# (doivent rester identiques aux enums Kotlin de 1_entites_jpa)
ENUMS = {
    "Domaine": ["MUSIQUES_ACTUELLES", "CINEMA_ET_AUDIOVISUEL", "MUSIQUES_CLASSIQUES",
                "CIRQUE_ET_ARTS_DE_LA_RUE", "LIVRE_ET_LITTERATURE", "DANSE", "THEATRE",
                "ARTS_PLASTIQUES_ET_VISUELS", "PLURIDISCIPLINAIRE_SPECTACLE_VIVANT",
                "PLURIDISCIPLINAIRE_MUSIQUE", "DIVERS_SPECTACLE_VIVANT", "TRANSDISCIPLINAIRE",
                "DOMAINES_DIVERS"],
    "SousDomaine": ["AMPLIFIEES_OU_ELECTRONIQUES", "JAZZ_BLUES_ET_IMPROVISEES", "CHANSON",
                    "TRADITIONNELLES_ET_DU_MONDE", "BAROQUE_ET_ANCIEN", "ARTS_DE_LA_RUE"],
    "Periodicite": ["ANNUELLE", "BIENNALE_ANNEES_PAIRES", "BIENNALE_ANNEES_IMPAIRES",
                    "BIANNUELLE", "IRREGULIERE"],
    "Classement": ["UNE_ETOILE", "DEUX_ETOILES", "TROIS_ETOILES", "QUATRE_ETOILES",
                   "CINQ_ETOILES", "AUBERGE_COLLECTIVE", "AIRE_NATURELLE"],
    "CategorieCamping": ["TOURISME", "LOISIRS"],
    "MentionVillage": ["NON", "HEBERGEMENT_DISPERSE", "HEBERGEMENT_LEGER",
                       "HEBERGEMENT_LEGER_ET_DISPERSE"],
    "TypeSejour": ["FORMULE_PENSION", "FORMULE_LOCATION", "FORMULE_LOCATION_PENSION"],
    "TypeNonClasse": ["HOTEL", "MOTEL", "CHAMBRE_D_HOTES", "GITE_CHALET", "APPARTEMENT",
                      "AUBERGE_DE_JEUNESSE", "CAMPING", "AIRE_DE_CAMPING_CAR", "REFUGE_GARDE"],
    "TypeHebergement": ["CHAMBRE_SIMPLE", "CHAMBRE_DOUBLE", "EMPLACEMENT_DE_CAMPING", "BUNGALOW",
                        "LOGEMENT_ENTIER", "LIT_EN_DORTOIR"],
    "StatutSelection": ["CONFIRMEE", "ANNULEE"],
    "StatutPaiement": ["NON_GERE", "EN_ATTENTE", "ACCEPTE", "REFUSE", "REMBOURSE"],
}


class Col:
    def __init__(self, nom, typ, null=False, defaut=None, enum=None, desc=""):
        self.nom, self.typ, self.null, self.defaut, self.enum, self.desc = nom, typ, null, defaut, enum, desc


class Table:
    def __init__(self, nom, origine, cols, pk, uk=(), fk=(), checks=(), index=(), genere=False, desc=""):
        self.nom, self.origine, self.cols, self.pk = nom, origine, cols, pk
        self.uk, self.fk, self.checks, self.index, self.genere, self.desc = uk, fk, checks, index, genere, desc

    @property
    def noms(self):
        return [c.nom for c in self.cols]


C = Col
PUB, SYN, MIX = "PUBLIC", "SYNTHÉTIQUE", "MIXTE"

# Ordre = ordre de création et de chargement (clés étrangères)
TABLES = [
    Table("REGION", PUB, [C("idRegion", "id"), C("nomRegion", "str(30)", desc="CSV festivals « Région »")],
          pk=["idRegion"], uk=[["nomRegion"]], genere=True),
    Table("DEPARTEMENT", PUB, [C("codeDepartement", "str(3)", desc="2 premiers caractères du code INSEE (3 en outre-mer)"),
                               C("nomDepartement", "str(50)"), C("idRegion", "id")],
          pk=["codeDepartement"], fk=[(["idRegion"], "REGION", ["idRegion"])],
          index=[["idRegion"]]),
    Table("COMMUNE", PUB, [C("codeInsee", "str(5)", desc="« Code INSEE » complété sur 5 caractères"),
                           C("nomCommune", "str(40)"), C("latitude", "dec(12,9)", True),
                           C("longitude", "dec(12,9)", True), C("codeDepartement", "str(3)")],
          pk=["codeInsee"], fk=[(["codeDepartement"], "DEPARTEMENT", ["codeDepartement"])],
          checks=["latitude BETWEEN -90 AND 90", "longitude BETWEEN -180 AND 180"],
          index=[["codeDepartement"]]),
    Table("UTILISATEUR", SYN, [C("idUtilisateur", "id"), C("nom", "str(100)"), C("email", "str(150)")],
          pk=["idUtilisateur"], uk=[["email"]], genere=True),
    Table("FESTIVALIER", SYN, [C("idUtilisateur", "id"), C("fournisseurAuth", "str(30)", True),
                               C("identifiantExterneFestivalier", "str(100)", True)],
          pk=["idUtilisateur"], uk=[["fournisseurAuth", "identifiantExterneFestivalier"]],
          fk=[(["idUtilisateur"], "UTILISATEUR", ["idUtilisateur"])]),
    Table("UTILISATEUR_BACKOFFICE", SYN, [C("idUtilisateur", "id"), C("motDePasseHache", "str(100)")],
          pk=["idUtilisateur"], fk=[(["idUtilisateur"], "UTILISATEUR", ["idUtilisateur"])]),
    Table("ORGANISATEUR", SYN, [C("idUtilisateur", "id")], pk=["idUtilisateur"],
          fk=[(["idUtilisateur"], "UTILISATEUR_BACKOFFICE", ["idUtilisateur"])]),
    Table("HEBERGEUR", SYN, [C("idUtilisateur", "id")], pk=["idUtilisateur"],
          fk=[(["idUtilisateur"], "UTILISATEUR_BACKOFFICE", ["idUtilisateur"])]),
    Table("FESTIVAL", MIX, [
        C("idFestival", "id"), C("nomFestival", "str(100)"),
        C("domaine", "str(40)", enum="Domaine"), C("sousDomaine", "str(70)", True, enum="SousDomaine"),
        C("periodicite", "str(30)", True, enum="Periodicite"), C("moisDebut", "num(2)"),
        C("siteWebFestival", "str(150)", True), C("numIdentification", "str(50)", True),
        C("dateCreation", "date", True), C("codePostalFestival", "str(5)"),
        C("dateDebutAncien", "date", True), C("dateFinAncien", "date", True),
        C("dateDebutFestival", "date", desc="SYNTHÉTIQUE : date ancienne transposée dans l'année du jeu"),
        C("dateFinFestival", "date", desc="SYNTHÉTIQUE"),
        C("quotaPass", "int", desc="SYNTHÉTIQUE, >= 30"),
        C("nbPassVendus", "int", defaut="0", desc="Compteur modifié uniquement par UPDATE conditionnel"),
        C("prixPass", "dec(8,2)", desc="SYNTHÉTIQUE"), C("actifFestival", "bool", defaut="1"),
        C("codeInsee", "str(5)"), C("idOrganisateur", "id", True)],
        pk=["idFestival"],
        fk=[(["codeInsee"], "COMMUNE", ["codeInsee"]), (["idOrganisateur"], "ORGANISATEUR", ["idUtilisateur"])],
        checks=["moisDebut BETWEEN 1 AND 12", "dateFinFestival >= dateDebutFestival",
                "quotaPass >= 0", "nbPassVendus BETWEEN 0 AND quotaPass", "prixPass >= 0"],
        index=[["dateDebutFestival", "dateFinFestival"], ["codeInsee"], ["domaine"], ["idOrganisateur"]],
        genere=True),
    Table("ETABLISSEMENT", MIX, [
        C("idEtablissement", "id"), C("nomCommercial", "str(100)"),
        C("adresse", "str(80)", True, desc="Classés : CSV ; OSM : géocodage inverse BAN (NULL si aucune adresse proche)"),
        C("codePostalEtablissement", "str(5)"), C("nomCommuneEtablissement", "str(50)"),
        C("codeInsee", "str(5)", True, desc="OSM « Code Commune » ou code INSEE renvoyé par la BAN"),
        C("telephoneEtablissement", "str(30)", True, desc="OSM (premier numéro)"),
        C("emailEtablissement", "str(150)", True, desc="OSM (premier e-mail)"),
        C("siteWebEtablissement", "str(350)", True), C("capaciteAccueil", "int",
                                                        desc="Non classés sans capacité OSM : estimation (voir l'étude)"),
        C("classement", "str(50)", True, enum="Classement", desc="NULL = établissement non classé (OSM)"),
        C("dateClassement", "date", True), C("classementProroge", "bool", True),
        C("latitudeEtablissement", "dec(12,9)", True, desc="Point OSM, sinon géocodage BAN"),
        C("longitudeEtablissement", "dec(12,9)", True, desc="Point OSM, sinon géocodage BAN"),
        C("osmRef", "str(25)", True, desc="Objet OpenStreetMap rapproché (« node/123 », « relation/456 »)"),
        C("noteMoyenne", "dec(3,2)", True, desc="Dénormalisé : moyenne des notations"),
        C("nbNotes", "int", defaut="0"), C("idUtilisateur", "id", True)],
        pk=["idEtablissement"], uk=[["osmRef"]],
        fk=[(["codeInsee"], "COMMUNE", ["codeInsee"]), (["idUtilisateur"], "HEBERGEUR", ["idUtilisateur"])],
        checks=["capaciteAccueil > 0", "noteMoyenne BETWEEN 1 AND 5", "nbNotes >= 0",
                "(classement IS NULL AND dateClassement IS NULL AND classementProroge IS NULL) OR "
                "(classement IS NOT NULL AND dateClassement IS NOT NULL AND classementProroge IS NOT NULL)"],
        index=[["latitudeEtablissement", "longitudeEtablissement"], ["codePostalEtablissement"], ["idUtilisateur"],
               ["codeInsee"]],
        genere=True),
    Table("HOTEL_DE_TOURISME", PUB, [C("idEtablissement", "id"), C("nbChambresHotel", "int")],
          pk=["idEtablissement"], fk=[(["idEtablissement"], "ETABLISSEMENT", ["idEtablissement"])]),
    Table("AUBERGE_COLLECTIVE", PUB, [C("idEtablissement", "id"), C("nbChambresAuberge", "int")],
          pk=["idEtablissement"], fk=[(["idEtablissement"], "ETABLISSEMENT", ["idEtablissement"])]),
    Table("CAMPING", PUB, [C("idEtablissement", "id"), C("categorie", "str(10)", True, enum="CategorieCamping"),
                           C("nbEmplacementsCamping", "int")],
          pk=["idEtablissement"], fk=[(["idEtablissement"], "ETABLISSEMENT", ["idEtablissement"])]),
    Table("PARC_RESIDENTIEL_DE_LOISIRS", PUB, [C("idEtablissement", "id"), C("nbEmplacementsParc", "int")],
          pk=["idEtablissement"], fk=[(["idEtablissement"], "ETABLISSEMENT", ["idEtablissement"])]),
    Table("VILLAGE_DE_VACANCES", PUB, [C("idEtablissement", "id"), C("mention", "str(30)", True, enum="MentionVillage"),
                                       C("typeSejour", "str(30)", True, enum="TypeSejour"), C("nbLogements", "int")],
          pk=["idEtablissement"], fk=[(["idEtablissement"], "ETABLISSEMENT", ["idEtablissement"])]),
    Table("RESIDENCE_DE_TOURISME", PUB, [C("idEtablissement", "id"), C("nbUnitesHabitation", "int")],
          pk=["idEtablissement"], fk=[(["idEtablissement"], "ETABLISSEMENT", ["idEtablissement"])]),
    Table("ETABLISSEMENT_NON_CLASSE", PUB, [
        C("idEtablissement", "id"), C("typeNonClasse", "str(30)", enum="TypeNonClasse", desc="OSM « Type »"),
        C("nbEtoilesDeclarees", "num(1)", True, desc="OSM « Nombre étoiles » : déclaratif, pas un classement officiel"),
        C("nbChambres", "int", True), C("nbLits", "int", True)],
        pk=["idEtablissement"], fk=[(["idEtablissement"], "ETABLISSEMENT", ["idEtablissement"])],
        checks=["nbEtoilesDeclarees BETWEEN 1 AND 5", "nbChambres > 0", "nbLits > 0"],
        index=[["typeNonClasse"]],
        desc="Hébergement touristique recensé par OpenStreetMap mais absent de la liste des établissements classés"),
    Table("OPTION_HEBERGEMENT", SYN, [C("idOptionHebergement", "id"), C("libelleOptionHebergement", "str(50)")],
          pk=["idOptionHebergement"], uk=[["libelleOptionHebergement"]], genere=True),
    Table("HEBERGEMENT", SYN, [
        C("idEtablissement", "id"), C("numeroHebergement", "str(10)"),
        C("typeHebergement", "str(30)", enum="TypeHebergement"), C("capaciteHebergement", "int"),
        C("prixNuitHebergement", "dec(8,2)"), C("descriptionHebergement", "str(500)", True),
        C("actifHebergement", "bool", defaut="1")],
        pk=["idEtablissement", "numeroHebergement"],
        fk=[(["idEtablissement"], "ETABLISSEMENT", ["idEtablissement"])],
        checks=["capaciteHebergement > 0", "prixNuitHebergement >= 0"]),
    Table("PHOTO_HEBERGEMENT", SYN, [C("idPhotoHebergement", "id"), C("urlPhotoHebergement", "str(300)"),
                                     C("idEtablissement", "id"), C("numeroHebergement", "str(10)")],
          pk=["idPhotoHebergement"],
          fk=[(["idEtablissement", "numeroHebergement"], "HEBERGEMENT", ["idEtablissement", "numeroHebergement"])],
          index=[["idEtablissement", "numeroHebergement"]], genere=True),
    Table("EQUIPEMENT", SYN, [C("idEtablissement", "id"), C("numeroHebergement", "str(10)"),
                              C("idOptionHebergement", "id")],
          pk=["idEtablissement", "numeroHebergement", "idOptionHebergement"],
          fk=[(["idEtablissement", "numeroHebergement"], "HEBERGEMENT", ["idEtablissement", "numeroHebergement"]),
              (["idOptionHebergement"], "OPTION_HEBERGEMENT", ["idOptionHebergement"])],
          index=[["idOptionHebergement"]]),
    Table("RESERVATION", SYN, [C("numeroReservation", "str(20)", desc="Aléatoire et opaque (validation anonyme)"),
                               C("dateReservation", "ts"), C("idUtilisateur", "id")],
          pk=["numeroReservation"], fk=[(["idUtilisateur"], "FESTIVALIER", ["idUtilisateur"])],
          index=[["idUtilisateur"]]),
    Table("PAIEMENT", SYN, [C("idPaiement", "id"), C("numTransaction", "str(30)", True),
                            C("montantPaiement", "dec(10,2)"), C("datePaiement", "ts", True),
                            C("statutPaiement", "str(20)", enum="StatutPaiement"),
                            C("numeroReservation", "str(20)")],
          pk=["idPaiement"], uk=[["numTransaction"], ["numeroReservation"]],
          fk=[(["numeroReservation"], "RESERVATION", ["numeroReservation"])],
          checks=["montantPaiement >= 0"], genere=True),
    Table("SELECTION", SYN, [C("idSelection", "id"), C("prixPassSelection", "dec(8,2)"),
                             C("statutSelection", "str(20)", enum="StatutSelection"),
                             C("numeroReservation", "str(20)"), C("idFestival", "id")],
          pk=["idSelection"], uk=[["numeroReservation", "idFestival"]],
          fk=[(["numeroReservation"], "RESERVATION", ["numeroReservation"]),
              (["idFestival"], "FESTIVAL", ["idFestival"])],
          checks=["prixPassSelection >= 0"], index=[["idFestival"]], genere=True),
    Table("PASS", SYN, [C("idPass", "id"), C("codePass", "str(40)"), C("idSelection", "id")],
          pk=["idPass"], uk=[["codePass"]], fk=[(["idSelection"], "SELECTION", ["idSelection"])],
          index=[["idSelection"]], genere=True),
    Table("NUITEE", SYN, [C("idEtablissement", "id"), C("numeroHebergement", "str(10)"), C("dateNuitee", "date"),
                          C("prixNuitee", "dec(8,2)"), C("idSelection", "id", True, desc="NULL = nuit libre")],
          pk=["idEtablissement", "numeroHebergement", "dateNuitee"],
          fk=[(["idEtablissement", "numeroHebergement"], "HEBERGEMENT", ["idEtablissement", "numeroHebergement"]),
              (["idSelection"], "SELECTION", ["idSelection"])],
          checks=["prixNuitee >= 0"], index=[["dateNuitee", "idSelection"], ["idSelection"]]),
    Table("NOTATION_FESTIVAL", SYN, [C("idFestival", "id"), C("idUtilisateur", "id"),
                                     C("noteFestival", "num(1)"), C("dateNoteFestival", "date")],
          pk=["idFestival", "idUtilisateur"],
          fk=[(["idFestival"], "FESTIVAL", ["idFestival"]), (["idUtilisateur"], "FESTIVALIER", ["idUtilisateur"])],
          checks=["noteFestival BETWEEN 1 AND 5"], index=[["idUtilisateur"]]),
    Table("NOTATION_ETABLISSEMENT", SYN, [C("idEtablissement", "id"), C("idUtilisateur", "id"),
                                          C("noteEtablissement", "num(1)"), C("dateNoteEtablissement", "date")],
          pk=["idEtablissement", "idUtilisateur"],
          fk=[(["idEtablissement"], "ETABLISSEMENT", ["idEtablissement"]),
              (["idUtilisateur"], "FESTIVALIER", ["idUtilisateur"])],
          checks=["noteEtablissement BETWEEN 1 AND 5"], index=[["idUtilisateur"]]),
]
PAR_NOM = {t.nom: t for t in TABLES}
ESPACE_UUID = uuid.uuid5(uuid.NAMESPACE_URL, "https://festibed.fr/groupe3")


def racine(t, col):
    """Table dont la clé UUID générée alimente la colonne col de t (en suivant les clés étrangères)."""
    if t.genere and col in t.pk:
        return t.nom
    for cols, ref, rcols in t.fk:
        if col in cols:
            return racine(PAR_NOM[ref], rcols[cols.index(col)])
    raise ValueError(f"{t.nom}.{col} : identifiant sans table racine")


def uuid_de(table_racine, n):
    """UUID déterministe de la n-ième ligne d'une table racine (peuplement reproductible)."""
    return str(uuid.uuid5(ESPACE_UUID, f"{table_racine}:{n}"))


def type_sql(typ, dialecte):
    m = re.fullmatch(r"(\w+)(?:\((\d+)(?:,(\d+))?\))?", typ)
    base, a, b = m.groups()
    ora = dialecte == "oracle"
    if base == "id":
        return "RAW(16)" if ora else "UUID"
    if base == "int":
        return "NUMBER(10)" if ora else "INTEGER"
    if base == "num":
        return f"NUMBER({a})" if ora else "INTEGER"
    if base == "bool":
        return "NUMBER(1)" if ora else "BOOLEAN"
    if base == "dec":
        return f"NUMBER({a},{b})" if ora else f"NUMERIC({a},{b})"
    if base == "str":
        return f"VARCHAR2({a} CHAR)" if ora else f"VARCHAR({a})"
    if base == "date":
        return "DATE"
    if base == "ts":
        return "TIMESTAMP"
    raise ValueError(typ)


def court(nom, n=30):
    """Les noms de contraintes Oracle < 12.2 sont limités à 30 caractères."""
    if len(nom) <= n:
        return nom
    base, _, suffixe = nom.rpartition("_")
    if suffixe.isdigit():
        return base[:n - len(suffixe) - 1] + "_" + suffixe
    return nom[:n]


def ddl(dialecte):
    ora = dialecte == "oracle"
    out = [f"-- FestiBed - Groupe 3 - Schéma {'Oracle' if ora else 'H2 (tests)'}",
           "-- Généré par schema_festibed.py : ne pas modifier à la main.", ""]
    for t in TABLES:
        lignes = []
        for c in t.cols:
            d = f"  {c.nom:<32} {type_sql(c.typ, dialecte)}"
            if c.defaut is not None:
                v = c.defaut
                if c.typ == "bool" and not ora:
                    v = "TRUE" if v == "1" else "FALSE"
                d += f" DEFAULT {v}"
            if not c.null:
                d += " NOT NULL"
            lignes.append(d)
        lignes.append(f"  CONSTRAINT {court('PK_' + t.nom)} PRIMARY KEY ({', '.join(t.pk)})")
        for i, u in enumerate(t.uk, 1):
            lignes.append(f"  CONSTRAINT {court(f'UK_{t.nom}_{i}')} UNIQUE ({', '.join(u)})")
        for i, (cols, ref, rcols) in enumerate(t.fk, 1):
            lignes.append(f"  CONSTRAINT {court(f'FK_{t.nom}_{i}')} FOREIGN KEY ({', '.join(cols)}) "
                          f"REFERENCES {ref} ({', '.join(rcols)})")
        checks = list(t.checks)
        for c in t.cols:
            if c.enum:
                checks.append(f"{c.nom} IN ({', '.join(repr(v) for v in ENUMS[c.enum])})".replace('"', "'"))
            if c.typ == "bool" and ora:
                checks.append(f"{c.nom} IN (0, 1)")
        for i, ck in enumerate(checks, 1):
            lignes.append(f"  CONSTRAINT {court(f'CK_{t.nom}_{i}')} CHECK ({ck})")
        out.append(f"CREATE TABLE {t.nom} (\n" + ",\n".join(lignes) + "\n);\n")
    out.append("-- Index : Oracle n'indexe pas automatiquement les clés étrangères.")
    for t in TABLES:
        for i, cols in enumerate(t.index, 1):
            out.append(f"CREATE INDEX {court(f'IX_{t.nom}_{i}')} ON {t.nom} ({', '.join(cols)});")
    return "\n".join(out) + "\n"


def numero(t):
    return TABLES.index(t) + 1


def fichier_csv(t):
    return f"{numero(t):02d}_{t.nom}.csv"

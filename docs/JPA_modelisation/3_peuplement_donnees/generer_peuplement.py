"""FestiBed - Groupe 3 - Génération du peuplement de la base.

Étapes :
  1. Lecture et nettoyage des CSV publics (data/panorama-des-festivals.csv, data/hebergements_classes.csv,
     data/osm-france-tourism-accommodation.csv)
  2. Géocodage des établissements classés par la Base Adresse Nationale, rapprochement avec OpenStreetMap
     (téléphone, e-mail, position), géocodage inverse des lieux OSM non classés (résultats mis en cache dans cache/)
  3. Génération des données synthétiques (graine fixe : le jeu est reproductible)
  4. Écriture d'un CSV par table (csv/NN_TABLE.csv), des scripts SQL et SQL*Loader ; les identifiants,
     numérotés en interne, sont écrits en UUID déterministes (schema_festibed.uuid_de)
  5. Contrôles des règles du cahier des charges

Usage :
  python generer_peuplement.py                 # utilise les caches de géocodage s'ils existent
  python generer_peuplement.py --geocoder      # interroge la BAN et l'API Géo pour ce qui manque dans cache/
"""
import argparse
import collections
import csv
import datetime as dt
import io
import json
import math
import random
import string
import sys
import time
import unicodedata
import urllib.request
import uuid
from decimal import Decimal
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
from schema_festibed import TABLES, PAR_NOM, ENUMS, ddl, fichier_csv, numero, racine, uuid_de  # noqa: E402

RACINE = ICI.parents[2]
DATA = RACINE / "data"
SORTIE = ICI / "csv"
CACHE = ICI / "cache" / "geocodage_etablissements.csv"
CACHE_INVERSE = ICI / "cache" / "geocodage_inverse_osm.csv"
CACHE_COMMUNES = ICI / "cache" / "communes_api_geo.csv"
URL_BAN = "https://api-adresse.data.gouv.fr/search/csv/"
URL_BAN_INVERSE = "https://api-adresse.data.gouv.fr/reverse/csv/"
URL_GEO = "https://geo.api.gouv.fr/communes?fields=nom,code,codesPostaux,centre,codeDepartement&format=json"

ANNEE = 2027                      # année des festivals du jeu de données
AUJOURD_HUI = dt.date(2026, 11, 1)
GRAINE = 2026
NB_ORGANISATEURS, NB_HEBERGEURS, NB_FESTIVALIERS = 500, 2500, 47000
# Hash BCrypt du mot de passe de test « festibed » (comptes back-office de démonstration)
HASH_TEST = "$2b$10$JB2cWzXA3tTdKo7X63.kduGcMWfHUas5Zv8VPyJ55m1jjK0Qnv1Ze"

rnd = random.Random(GRAINE)
log = []


def note(msg):
    log.append(msg)
    print(msg)


# ================================================================== utilitaires
def sans_accent(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def code_enum(s):
    s = sans_accent(s).upper()
    return "_".join("".join(c if c.isalnum() else " " for c in s).split())


def vide(v):
    v = (v or "").strip()
    return None if v in ("", "-") else v


def date_fr(v):
    v = vide(v)
    if not v:
        return None
    for f in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return dt.datetime.strptime(v[:10], f).date()
        except ValueError:
            pass
    return None


def transposer(d, annee):
    try:
        return d.replace(year=annee)
    except ValueError:            # 29 février
        return d.replace(year=annee, day=28)


def lire_csv(nom):
    with open(DATA / nom, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def plus_frequent(valeurs):
    return collections.Counter(valeurs).most_common(1)[0][0]


def prix(a, b):
    return Decimal(rnd.randint(a * 2, b * 2) * 50) / 100     # pas de 0,50 €


# ============================================================ 1. festivals publics
SOUS_DOMAINE = {
    "MUSIQUES_AMPLIFIEES_OU_ELECTRONIQUES": "AMPLIFIEES_OU_ELECTRONIQUES",
    "JAZZ_BLUES_ET_MUSIQUES_IMPROVISEES": "JAZZ_BLUES_ET_IMPROVISEES",
    "CHANSON": "CHANSON",
    "MUSIQUES_TRADITIONNELLES_ET_DU_MONDE": "TRADITIONNELLES_ET_DU_MONDE",
    "BAROQUE_ET_ANCIEN": "BAROQUE_ET_ANCIEN",
    "ARTS_DE_LA_RUE": "ARTS_DE_LA_RUE",
}
PERIODICITE = {"ANNUELLE": "ANNUELLE", "BIENNALE_ANNEES_PAIRES": "BIENNALE_ANNEES_PAIRES",
               "BIENNALE_ANNEES_IMPAIRES": "BIENNALE_ANNEES_IMPAIRES", "BI_ANNUELLE": "BIANNUELLE",
               "IRREGULIERE": "IRREGULIERE", "BIENNALE": None}
PRIX_DOMAINE = {"MUSIQUES_ACTUELLES": (35, 180), "MUSIQUES_CLASSIQUES": (30, 150),
                "CINEMA_ET_AUDIOVISUEL": (20, 80), "LIVRE_ET_LITTERATURE": (10, 40)}


def dept_de_insee(insee):
    return insee[:3] if insee[:2] in ("97", "98") else insee[:2]


def charger_festivals():
    F = lire_csv("panorama-des-festivals.csv")
    regions, depts, communes, festivals = {}, {}, {}, []
    noms_dept = collections.defaultdict(list)
    region_dept = collections.defaultdict(list)
    noms_commune = collections.defaultdict(list)
    coords = {}
    for r in F:
        insee = r["Code INSEE"].strip().zfill(5)
        d = dept_de_insee(insee)
        noms_dept[d].append(r["Nom Département"].strip())
        region_dept[d].append(r["Région"].strip())
        noms_commune[insee].append(r["Libellé commune pour calcul CP, INSEE"].strip())
        c = vide(r["coordonnees_insee"])
        if c and insee not in coords:
            lat, lon = (x.strip() for x in c.split(","))
            coords[insee] = (Decimal(lat).quantize(Decimal("0.000000001")), Decimal(lon).quantize(Decimal("0.000000001")))
    for i, nom in enumerate(sorted({plus_frequent(v) for v in region_dept.values()}), 1):
        regions[nom] = {"idRegion": i, "nomRegion": nom}
    for d in sorted(noms_dept):
        depts[d] = {"codeDepartement": d, "nomDepartement": plus_frequent(noms_dept[d])[:50],
                    "idRegion": regions[plus_frequent(region_dept[d])]["idRegion"]}
    multi = 0
    for insee in sorted(noms_commune):
        multi += len(set(noms_commune[insee])) > 1
        lat, lon = coords.get(insee, (None, None))
        communes[insee] = {"codeInsee": insee, "nomCommune": plus_frequent(noms_commune[insee])[:40],
                           "latitude": lat, "longitude": lon, "codeDepartement": dept_de_insee(insee)}
    note(f"Festivals : {len(regions)} régions, {len(depts)} départements, {len(communes)} communes "
         f"({multi} codes INSEE à plusieurs libellés -> libellé le plus fréquent)")

    domaines_inconnus, sd_null, per_null, sans_date = collections.Counter(), 0, 0, 0
    for i, r in enumerate(F, 1):
        dom = code_enum(r["Domaine"])
        if dom not in ENUMS["Domaine"]:
            domaines_inconnus[dom] += 1
            dom = "DOMAINES_DIVERS"
        sd = SOUS_DOMAINE.get(code_enum(r["Complément domaine"])) if vide(r["Complément domaine"]) else None
        sd_null += sd is None
        per = PERIODICITE.get(code_enum(r["Périodicité"])) if vide(r["Périodicité"]) else None
        per_null += per is None
        mois = int(r["Mois habituel de début"][:2])
        a_deb, a_fin = date_fr(r["Date début ancien"]), date_fr(r["Date de fin ancien"])
        if a_deb:
            debut = transposer(a_deb, ANNEE)
            duree = (a_fin - a_deb).days if a_fin and a_fin >= a_deb else 0
        else:
            sans_date += 1
            debut = dt.date(ANNEE, mois, rnd.randint(1, 25))
            duree = rnd.randint(1, 3)
        gros = rnd.random() < 0.30
        quota = rnd.randint(100, 300) if gros else rnd.randint(30, 80)
        pa, pb = PRIX_DOMAINE.get(dom, (15, 90))
        insee = r["Code INSEE"].strip().zfill(5)
        festivals.append({
            "idFestival": i, "nomFestival": r["Nom de la manifestation"].strip()[:100], "domaine": dom,
            "sousDomaine": sd, "periodicite": per, "moisDebut": mois,
            "siteWebFestival": (vide(r["Site web"]) or "")[:150] or None,
            "numIdentification": vide(r["N° Identification"]), "dateCreation": date_fr(r["Date de création"]),
            "codePostalFestival": r["Code postal"].strip().zfill(5),
            "dateDebutAncien": a_deb, "dateFinAncien": a_fin,
            "dateDebutFestival": debut, "dateFinFestival": debut + dt.timedelta(days=duree),
            "quotaPass": quota, "nbPassVendus": 0, "prixPass": prix(pa, pb), "actifFestival": True,
            "codeInsee": insee, "idOrganisateur": None, "_dept": dept_de_insee(insee)})
    note(f"Festivals : {len(festivals)} ; sous-domaine hors enum -> NULL : {sd_null} ; périodicité NULL : {per_null} ; "
         f"sans date ancienne (date tirée dans le mois habituel) : {sans_date} ; domaines inconnus : {dict(domaines_inconnus)}")
    return regions, depts, communes, festivals


# ======================================================= 2. établissements publics
TYPOLOGIE = {"HÔTEL DE TOURISME": ("HOTEL_DE_TOURISME", "NOMBRE DE CHAMBRES", "nbChambresHotel"),
             "AUBERGE COLLECTIVE": ("AUBERGE_COLLECTIVE", "NOMBRE DE CHAMBRES", "nbChambresAuberge"),
             "CAMPING": ("CAMPING", "NOMBRE D'EMPLACEMENTS", "nbEmplacementsCamping"),
             "PARC RÉSIDENTIEL DE LOISIRS": ("PARC_RESIDENTIEL_DE_LOISIRS", "NOMBRE D'EMPLACEMENTS", "nbEmplacementsParc"),
             "VILLAGE DE VACANCES": ("VILLAGE_DE_VACANCES", "NOMBRE DE LOGEMENTS (villages de vacances)", "nbLogements"),
             "RÉSIDENCE DE TOURISME": ("RESIDENCE_DE_TOURISME", "NOMBRE D'UNITES D'HABITATION (résidences de tourisme)", "nbUnitesHabitation")}
CLASSEMENT = {"1 étoile": "UNE_ETOILE", "2 étoiles": "DEUX_ETOILES", "3 étoiles": "TROIS_ETOILES",
              "4 étoiles": "QUATRE_ETOILES", "5 étoiles": "CINQ_ETOILES",
              "Auberge collective": "AUBERGE_COLLECTIVE", "Aire naturelle": "AIRE_NATURELLE"}


# OSM « Type » -> TypeNonClasse (wilderness_hut = refuge non gardé, non réservable : écarté)
TYPE_OSM = {"hotel": "HOTEL", "motel": "MOTEL", "guest_house": "CHAMBRE_D_HOTES", "chalet": "GITE_CHALET",
            "apartment": "APPARTEMENT", "hostel": "AUBERGE_DE_JEUNESSE", "camp_site": "CAMPING",
            "caravan_site": "AIRE_DE_CAMPING_CAR", "alpine_hut": "REFUGE_GARDE"}
# TypeNonClasse -> (unités, capacité d'accueil) par défaut, quand OSM ne les donne pas
DEFAUT_NC = {"HOTEL": (20, 40), "MOTEL": (20, 40), "CHAMBRE_D_HOTES": (4, 8), "GITE_CHALET": (1, 6),
             "APPARTEMENT": (1, 4), "AUBERGE_DE_JEUNESSE": (10, 40), "CAMPING": (50, 150),
             "AIRE_DE_CAMPING_CAR": (15, 40), "REFUGE_GARDE": (4, 30)}
# Typologie officielle -> types OSM compatibles (rapprochement)
FAMILLE = {"HOTEL_DE_TOURISME": {"hotel", "motel", "guest_house"},
           "AUBERGE_COLLECTIVE": {"hostel", "alpine_hut", "guest_house"},
           "CAMPING": {"camp_site", "caravan_site"},
           "PARC_RESIDENTIEL_DE_LOISIRS": {"camp_site", "caravan_site", "chalet"},
           "VILLAGE_DE_VACANCES": {"chalet", "hotel", "apartment", "camp_site"},
           "RESIDENCE_DE_TOURISME": {"apartment", "hotel", "chalet"}}
ARTICLES = set("LE LA LES DE DU DES AU AUX ET EN SUR THE OF".split())
GENERIQUES = set("HOTEL HOSTELLERIE CAMPING RESIDENCE VILLAGE VACANCES PARC CHAMBRES CHAMBRE HOTES GITE GITES "
                 "MUNICIPAL CAMP SITE RESTAURANT".split())
CHAMPS_CACHE = ["cle", "latitude", "longitude", "score", "citycode", "postcode", "city"]
CHAMPS_INVERSE = ["osmRef", "adresse", "postcode", "citycode", "distance"]
CHAMPS_COMMUNES = ["code", "nom", "codePostal", "latitude", "longitude"]


def cle_adresse(r):
    return f"{r['NOM COMMERCIAL'].strip().upper()}|{r['ADRESSE'].strip().upper()}|{r['CODE POSTAL'].strip()}"


def jetons(nom, commune):
    """Mots significatifs d'un nom d'établissement : sans accents, sans articles, sans les mots du nom de la
    commune (« Ibis Cholet Sud » ≠ « Ibis Cholet Centre ») ni les mots génériques (« hôtel », « camping »),
    sauf s'il ne reste rien (« Hôtel du Parc »)."""
    mots = {m for m in code_enum(nom).split("_") if len(m) > 1 and m not in ARTICLES}
    ville = set(code_enum(commune).split("_"))
    return (mots - GENERIQUES - ville) or (mots - ville) or mots


def distance(lat1, lon1, lat2, lon2):
    """Distance en mètres (approximation équirectangulaire, suffisante à quelques kilomètres)."""
    x = math.radians(float(lon2) - float(lon1)) * math.cos(math.radians((float(lat1) + float(lat2)) / 2))
    return 6371000 * math.hypot(x, math.radians(float(lat2) - float(lat1)))


def coord(v):
    return Decimal(str(v).strip()).quantize(Decimal("0.000000001"))


def lire_cache(fichier, cle):
    if not fichier.exists():
        return {}
    with open(fichier, encoding="utf-8", newline="") as f:
        return {r[cle]: r for r in csv.DictReader(f, delimiter=";")}


def ecrire_cache(fichier, cache, champs):
    fichier.parent.mkdir(exist_ok=True)
    with open(fichier, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=champs, delimiter=";", extrasaction="ignore")
        w.writeheader()
        w.writerows(sorted(cache.values(), key=lambda x: x[champs[0]]))


def envoyer_lot(url, params, entetes, lignes):
    """Envoie un lot CSV à un service par lot de l'API Adresse (BAN) et renvoie les lignes de la réponse."""
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";")
    w.writerow(entetes)
    w.writerows(lignes)
    borne = uuid.uuid4().hex
    corps = io.BytesIO()
    for nom, val in params:
        corps.write(f"--{borne}\r\nContent-Disposition: form-data; name=\"{nom}\"\r\n\r\n{val}\r\n".encode())
    corps.write(f"--{borne}\r\nContent-Disposition: form-data; name=\"data\"; filename=\"lot.csv\"\r\n"
                f"Content-Type: text/csv\r\n\r\n".encode() + buf.getvalue().encode("utf-8") + f"\r\n--{borne}--\r\n".encode())
    req = urllib.request.Request(url, data=corps.getvalue(),
                                 headers={"Content-Type": f"multipart/form-data; boundary={borne}"})
    for essai in range(3):
        try:
            with urllib.request.urlopen(req, timeout=300) as rep:
                return list(csv.DictReader(io.StringIO(rep.read().decode("utf-8-sig")), delimiter=";"))
        except Exception as e:  # noqa: BLE001
            note(f"  erreur {e}, nouvel essai")
            time.sleep(5 * (essai + 1))
    note("  lot abandonné")
    return []


def geocoder(lignes, cache):
    """Géocodage par lots via l'API Adresse (BAN, data.gouv.fr). Seules les adresses publiques sont envoyées."""
    a_faire = [r for r in lignes if cle_adresse(r) not in cache]
    note(f"Géocodage : {len(lignes) - len(a_faire)} adresses en cache, {len(a_faire)} à géocoder")
    for k in range(0, len(a_faire), 4000):
        lot = a_faire[k:k + 4000]
        rep = envoyer_lot(URL_BAN, (("columns", "adresse"), ("columns", "commune"), ("postcode", "code_postal")),
                          ["cle", "adresse", "code_postal", "commune"],
                          [[cle_adresse(r), r["ADRESSE"].strip(), vide(r["CODE POSTAL"]) or "", vide(r["COMMUNE"]) or ""]
                           for r in lot])
        for r in rep:
            cache[r["cle"]] = {"cle": r["cle"], "latitude": r.get("latitude", ""), "longitude": r.get("longitude", ""),
                               "score": r.get("result_score", ""), "citycode": r.get("result_citycode", ""),
                               "postcode": r.get("result_postcode", ""), "city": r.get("result_city", "")}
        note(f"  lot {k // 4000 + 1} : {min(k + 4000, len(a_faire))}/{len(a_faire)}")
        ecrire_cache(CACHE, cache, CHAMPS_CACHE)
    return cache


def geocoder_inverse(lieux, cache):
    """Adresse la plus proche de chaque lieu OSM (API Adresse /reverse/csv/). Seules des coordonnées publiques
    (OpenStreetMap) sont envoyées."""
    a_faire = [o for o in lieux if o["osmRef"] not in cache]
    note(f"Géocodage inverse OSM : {len(lieux) - len(a_faire)} lieux en cache, {len(a_faire)} à géocoder")
    for k in range(0, len(a_faire), 5000):
        lot = a_faire[k:k + 5000]
        rep = envoyer_lot(URL_BAN_INVERSE, (("lat", "lat"), ("lon", "lon")), ["osmRef", "lat", "lon"],
                          [[o["osmRef"], o["lat"], o["lon"]] for o in lot])
        for r in rep:
            cache[r["osmRef"]] = {"osmRef": r["osmRef"], "adresse": r.get("result_name", ""),
                                  "postcode": r.get("result_postcode", ""), "citycode": r.get("result_citycode", ""),
                                  "distance": r.get("result_distance", "")}
        note(f"  lot {k // 5000 + 1} : {min(k + 5000, len(a_faire))}/{len(a_faire)}")
        ecrire_cache(CACHE_INVERSE, cache, CHAMPS_INVERSE)
    return cache


def lire_communes_api(telecharger):
    """Référentiel des communes et arrondissements (API Géo) : code postal et centre de chaque code INSEE."""
    if telecharger and not CACHE_COMMUNES.exists():
        lignes = {}
        for url in (URL_GEO, URL_GEO + "&type=arrondissement-municipal"):
            with urllib.request.urlopen(url, timeout=300) as rep:
                for c in json.loads(rep.read().decode("utf-8")):
                    lon, lat = (c.get("centre") or {}).get("coordinates", ("", ""))
                    lignes[c["code"]] = {"code": c["code"], "nom": c["nom"],
                                         "codePostal": min(c.get("codesPostaux") or [""]), "latitude": lat, "longitude": lon}
        ecrire_cache(CACHE_COMMUNES, lignes, CHAMPS_COMMUNES)
        note(f"API Géo : {len(lignes)} communes et arrondissements mis en cache")
    return lire_cache(CACHE_COMMUNES, "code")


def charger_etablissements(faire_geocodage):
    H = lire_csv("hebergements_classes.csv")
    garde = {}
    for r in H:          # doublons nom + adresse + CP : on garde le classement le plus récent
        k = cle_adresse(r)
        if k not in garde or date_fr(r["DATE DE CLASSEMENT"]) > date_fr(garde[k]["DATE DE CLASSEMENT"]):
            garde[k] = r
    note(f"Établissements classés : {len(H)} lignes, {len(H) - len(garde)} doublons supprimés")
    lignes = list(garde.values())
    cache = lire_cache(CACHE, "cle")
    if faire_geocodage:
        cache = geocoder(lignes, cache)
    etabs, sous = [], collections.defaultdict(list)
    sans_geo, rejet = 0, 0
    for r in lignes:
        g = cache.get(cle_adresse(r), {})
        ok = g.get("latitude") and float(g.get("score") or 0) >= 0.4
        cp = vide(r["CODE POSTAL"]) or (g.get("postcode") or None)
        commune = vide(r["COMMUNE"]) or (g.get("city") or None)
        if not cp or not commune:
            rejet += 1
            continue
        if not ok:
            sans_geo += 1
        citycode = g.get("citycode") or ""
        dept = dept_de_insee(citycode) if citycode else (cp[:3] if cp[:2] in ("97", "98") else cp[:2])
        typ = TYPOLOGIE[r["TYPOLOGIE ÉTABLISSEMENT"]]
        e = {"idEtablissement": len(etabs) + 1, "nomCommercial": r["NOM COMMERCIAL"].strip()[:100],
             "adresse": r["ADRESSE"].strip()[:80], "codePostalEtablissement": cp.zfill(5),
             "nomCommuneEtablissement": commune[:50], "codeInsee": citycode if ok else None,
             "telephoneEtablissement": None, "emailEtablissement": None,
             "siteWebEtablissement": vide(r["SITE INTERNET"]),
             "capaciteAccueil": int(r["CAPACITÉ D'ACCUEIL (PERSONNES)"]),
             "classement": CLASSEMENT[r["CLASSEMENT"]], "dateClassement": date_fr(r["DATE DE CLASSEMENT"]),
             "classementProroge": r["classement prorogé"].strip().lower() == "oui",
             "latitudeEtablissement": coord(g["latitude"]) if ok else None,
             "longitudeEtablissement": coord(g["longitude"]) if ok else None, "osmRef": None,
             "noteMoyenne": None, "nbNotes": 0, "idUtilisateur": None,
             "_type": typ[0], "_unites": int(r[typ[1]]), "_dept": dept, "_jetons": jetons(r["NOM COMMERCIAL"], commune)}
        etabs.append(e)
        s = {"idEtablissement": e["idEtablissement"], typ[2]: int(r[typ[1]])}
        if typ[0] == "CAMPING":
            s["categorie"] = vide(r["CATÉGORIE"])
        if typ[0] == "VILLAGE_DE_VACANCES":
            s["mention"], s["typeSejour"] = vide(r["MENTION (villages de vacances)"]), vide(r["TYPE DE SÉJOUR"])
        sous[typ[0]].append(s)
    note(f"Établissements classés : {len(etabs)} chargés, {rejet} rejetés (CP/commune introuvables), "
         f"{sans_geo} sans coordonnées BAN fiables (score < 0,4 ou non géocodés)")
    return etabs, sous


# ------------------------------------------------------------ OpenStreetMap
def premier(v, n):
    """Premier élément d'une valeur OSM multiple (« a;b »), tronqué à n caractères."""
    v = (vide(v) or "").split(";")[0].strip()
    return v[:n] or None


def entier(v):
    v = vide(v)
    return int(v) if v and v.isdigit() and int(v) > 0 else None


def lire_osm():
    lieux, ecartes = [], collections.Counter()
    for r in lire_csv("osm-france-tourism-accommodation.csv"):
        typ = r["Type"].strip()
        if typ not in TYPE_OSM:
            ecartes["refuges non gardés (non réservables)" if typ == "wilderness_hut" else f"type {typ}"] += 1
            continue
        if not vide(r["Nom"]):
            ecartes["sans nom"] += 1
            continue
        lat, lon = (coord(x) for x in r["OSM Point"].split(","))
        etoiles, email = entier(r["Nombre étoiles"]), premier(r["Email"], 150)
        lieux.append({
            "_rang": len(lieux), "osmRef": "/".join(r["OSM URL"].rstrip("/").split("/")[-2:]), "type": typ,
            "nom": r["Nom"].strip(), "insee": r["Code Commune"].strip().zfill(5), "commune": r["Commune"].strip(),
            "dept": r["Code Département"].strip(), "nomDept": r["Département"].strip(), "region": r["Région"].strip(),
            "lat": lat, "lon": lon, "telephone": premier(r["Téléphone"], 30),
            "email": email if email and "@" in email else None, "site": premier(r["Site Internet"], 350),
            "etoiles": etoiles if etoiles and etoiles <= 5 else None, "chambres": entier(r["Nombre chambres"]),
            "lits": entier(r["Nombre de lits"]), "capacite": entier(r["Capacité"]), "_jetons": jetons(r["Nom"], r["Commune"])})
    note(f"OSM : {len(lieux)} lieux retenus, écartés : {dict(ecartes)}")
    return lieux


def rapprocher(etabs, lieux):
    """Associe à chaque établissement classé au plus un lieu OSM, et inversement.

    Candidats : même code INSEE (même nom de commune si la BAN n'a pas trouvé l'adresse), ou à moins de
    2 km du point BAN. Score = mots communs / mots du nom le plus court (>= 0,5 exigé) + 0,3 si à moins
    de 150 m + 0,1 si le type OSM est compatible avec la typologie. Un type incompatible n'est accepté
    qu'à moins de 150 m. Affectation gloutonne par score décroissant puis distance croissante."""
    par_insee, par_nom, grille = (collections.defaultdict(list) for _ in range(3))
    for i, o in enumerate(lieux):
        par_insee[o["insee"]].append(i)
        par_nom[code_enum(o["commune"])].append(i)
        grille[(int(o["lat"] * 50), int(o["lon"] * 50))].append(i)
    paires = []
    for j, e in enumerate(etabs):
        a, lat, lon = e["_jetons"], e["latitudeEtablissement"], e["longitudeEtablissement"]
        if not a:
            continue
        if e["codeInsee"]:
            cands, meme = set(par_insee.get(e["codeInsee"], ())), set()
        else:
            cands = meme = set(par_nom.get(code_enum(e["nomCommuneEtablissement"]), ()))
        if lat is not None:
            gx, gy = int(lat * 50), int(lon * 50)
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    cands.update(grille.get((gx + dx, gy + dy), ()))
        for i in cands:
            o = lieux[i]
            b = o["_jetons"]
            if not b:
                continue
            sim = len(a & b) / min(len(a), len(b))
            if sim < 0.5:
                continue
            meme_commune = o["insee"] == e["codeInsee"] or i in meme
            d = distance(lat, lon, o["lat"], o["lon"]) if lat is not None else None
            if (d is None and not meme_commune) or (d is not None and d > (3000 if meme_commune else 2000)):
                continue
            compatible = o["type"] in FAMILLE[e["_type"]]
            proche = d is not None and d <= 150
            if not compatible and not proche:
                continue
            paires.append((-(sim + 0.3 * proche + 0.1 * compatible), d if d is not None else 1e9, j, i))
    paires.sort()
    assoc, pris = {}, set()
    for _, _, j, i in paires:
        if j not in assoc and i not in pris:
            assoc[j] = i
            pris.add(i)
    return assoc


def integrer_osm(etabs, sous, lieux, api_geo, faire_geocodage):
    """Complète les établissements classés retrouvés dans OSM, puis ajoute les lieux OSM non classés."""
    assoc = rapprocher(etabs, lieux)
    complete = collections.Counter()
    for j, i in assoc.items():
        e, o = etabs[j], lieux[i]
        complete["coordonnées absentes de la BAN"] += e["latitudeEtablissement"] is None
        complete["téléphone"] += bool(o["telephone"])
        complete["e-mail"] += bool(o["email"])
        complete["site web"] += bool(o["site"] and not e["siteWebEtablissement"])
        e["osmRef"], e["telephoneEtablissement"], e["emailEtablissement"] = o["osmRef"], o["telephone"], o["email"]
        e["siteWebEtablissement"] = e["siteWebEtablissement"] or o["site"]
        e["latitudeEtablissement"], e["longitudeEtablissement"] = o["lat"], o["lon"]   # point OSM = bâtiment
        e["codeInsee"] = e["codeInsee"] or o["insee"]
    note(f"OSM : {len(assoc)} établissements classés sur {len(etabs)} retrouvés dans OSM ; complétés : {dict(complete)}")

    utilises = set(assoc.values())
    restants, vus, doublons = [], collections.defaultdict(list), 0
    # le plus renseigné d'abord : en cas de doublon (nœud + relation), c'est lui qui est gardé
    for o in sorted((o for i, o in enumerate(lieux) if i not in utilises),
                    key=lambda o: (-sum(o[k] is not None for k in ("telephone", "email", "site", "chambres", "capacite")),
                                   o["_rang"])):
        k = (code_enum(o["nom"]), o["insee"])
        if any(distance(o["lat"], o["lon"], p["lat"], p["lon"]) < 200 for p in vus[k]):
            doublons += 1
            continue
        vus[k].append(o)
        restants.append(o)
    restants.sort(key=lambda o: o["_rang"])
    inverse = lire_cache(CACHE_INVERSE, "osmRef")
    if faire_geocodage:
        inverse = geocoder_inverse(restants, inverse)
    sans_adresse, sans_cp, par_type = 0, 0, collections.Counter()
    for o in restants:
        g = inverse.get(o["osmRef"], {})
        meme_commune = g.get("citycode") == o["insee"]
        cp = (g.get("postcode") if meme_commune else None) or api_geo.get(o["insee"], {}).get("codePostal")
        if not cp:
            sans_cp += 1
            continue
        proche = bool(meme_commune and g.get("adresse") and float(g.get("distance") or 1e9) <= 200)
        nc = TYPE_OSM[o["type"]]
        unites, capacite = DEFAUT_NC[nc]
        if nc in ("CAMPING", "AIRE_DE_CAMPING_CAR"):        # OSM « capacity » = nombre d'emplacements
            unites = o["capacite"] or unites
            capacite = o["capacite"] * 3 if o["capacite"] else capacite
        else:
            unites = o["chambres"] or unites
            capacite = o["capacite"] or o["lits"] or (o["chambres"] * 2 if o["chambres"] else capacite)
        e = {"idEtablissement": len(etabs) + 1, "nomCommercial": o["nom"][:100],
             "adresse": g["adresse"][:80] if proche else None, "codePostalEtablissement": cp,
             "nomCommuneEtablissement": o["commune"][:50], "codeInsee": o["insee"],
             "telephoneEtablissement": o["telephone"], "emailEtablissement": o["email"],
             "siteWebEtablissement": o["site"], "capaciteAccueil": capacite,
             "classement": None, "dateClassement": None, "classementProroge": None,
             "latitudeEtablissement": o["lat"], "longitudeEtablissement": o["lon"], "osmRef": o["osmRef"],
             "noteMoyenne": None, "nbNotes": 0, "idUtilisateur": None,
             "_type": "ETABLISSEMENT_NON_CLASSE", "_nc": nc, "_etoiles": o["etoiles"], "_unites": unites,
             "_dept": dept_de_insee(o["insee"])}
        sans_adresse += e["adresse"] is None
        par_type[nc] += 1
        etabs.append(e)
        sous["ETABLISSEMENT_NON_CLASSE"].append({
            "idEtablissement": e["idEtablissement"], "typeNonClasse": nc, "nbEtoilesDeclarees": o["etoiles"],
            "nbChambres": o["chambres"], "nbLits": o["lits"]})
    note(f"OSM : {sum(par_type.values())} établissements non classés ajoutés ({len(utilises)} déjà classés, "
         f"{doublons} doublons, {sans_cp} sans code postal), dont {sans_adresse} sans adresse à moins de 200 m ; "
         f"{dict(par_type.most_common())}")


def completer_geographie(regions, depts, communes, etabs, lieux, api_geo):
    """Ajoute les communes des établissements (clé étrangère ETABLISSEMENT.codeInsee -> COMMUNE)."""
    noms_osm, dept_osm = collections.defaultdict(list), {}
    for o in lieux:
        noms_osm[o["insee"]].append(o["commune"])
        dept_osm.setdefault(o["dept"], (o["nomDept"], o["region"]))
    ajout, perdu = collections.Counter(), 0
    for e in etabs:
        insee = e["codeInsee"]
        if not insee or insee in communes:
            continue
        d = dept_de_insee(insee)
        if d not in depts:
            if d not in dept_osm:
                e["codeInsee"], perdu = None, perdu + 1
                continue
            nom_dept, region = dept_osm[d]
            if region not in regions:
                regions[region] = {"idRegion": len(regions) + 1, "nomRegion": region}
                ajout["régions"] += 1
            depts[d] = {"codeDepartement": d, "nomDepartement": nom_dept[:50], "idRegion": regions[region]["idRegion"]}
            ajout["départements"] += 1
        a = api_geo.get(insee, {})
        nom = plus_frequent(noms_osm[insee]) if noms_osm.get(insee) else (a.get("nom") or e["nomCommuneEtablissement"])
        communes[insee] = {"codeInsee": insee, "nomCommune": nom[:40],
                           "latitude": coord(a["latitude"]) if a.get("latitude") else None,
                           "longitude": coord(a["longitude"]) if a.get("longitude") else None,
                           "codeDepartement": d}
        ajout["communes"] += 1
    note(f"Géographie complétée pour les établissements : {dict(ajout)}, code INSEE inconnu : {perdu}")


# ============================================================ 3. données synthétiques
PRENOMS = ("Camille Léa Manon Chloé Emma Inès Jade Louise Alice Lina Sarah Julie Clara Zoé Anna Lucie "
           "Lucas Hugo Louis Gabriel Arthur Jules Adam Raphaël Nathan Tom Théo Paul Léo Maël Noah Ethan "
           "Samir Fatou Moussa Aïcha Yanis Ibrahima Mamadou Awa Karim Sofia").split()
NOMS = ("Martin Bernard Dubois Thomas Robert Richard Petit Durand Leroy Moreau Simon Laurent Lefebvre "
        "Michel Garcia David Bertrand Roux Vincent Fournier Morel Girard André Mercier Dupont Lambert "
        "Bonnet François Martinez Diallo Ndiaye Diop Traoré Benali Nguyen Fontaine Chevalier Robin Gauthier").split()
OPTIONS = ["Wi-Fi", "Parking", "Accès PMR", "Petit-déjeuner inclus", "Climatisation", "Animaux acceptés",
           "Piscine", "Linge fourni", "Cuisine équipée", "Borne de recharge"]
ETOILES = {"UNE_ETOILE": 1, "DEUX_ETOILES": 2, "TROIS_ETOILES": 3, "QUATRE_ETOILES": 4, "CINQ_ETOILES": 5,
           "AUBERGE_COLLECTIVE": 1, "AIRE_NATURELLE": 1}
OFFRES = {  # typologie (ou TypeNonClasse) -> [(type, capacité min, capacité max, prix de base)]
    "HOTEL_DE_TOURISME": [("CHAMBRE_SIMPLE", 1, 1, 45), ("CHAMBRE_DOUBLE", 2, 3, 60)],
    "AUBERGE_COLLECTIVE": [("CHAMBRE_SIMPLE", 1, 1, 25), ("CHAMBRE_DOUBLE", 2, 6, 35)],
    "CAMPING": [("EMPLACEMENT_DE_CAMPING", 2, 6, 15), ("BUNGALOW", 2, 6, 45)],
    "PARC_RESIDENTIEL_DE_LOISIRS": [("EMPLACEMENT_DE_CAMPING", 2, 6, 18), ("BUNGALOW", 4, 6, 55)],
    "VILLAGE_DE_VACANCES": [("BUNGALOW", 2, 6, 50), ("CHAMBRE_DOUBLE", 2, 3, 55)],
    "RESIDENCE_DE_TOURISME": [("BUNGALOW", 2, 6, 60), ("CHAMBRE_DOUBLE", 2, 4, 55)],
    # établissements non classés (OSM) ; CAMPING est commun aux deux
    "HOTEL": [("CHAMBRE_SIMPLE", 1, 1, 40), ("CHAMBRE_DOUBLE", 2, 3, 55)],
    "MOTEL": [("CHAMBRE_SIMPLE", 1, 1, 35), ("CHAMBRE_DOUBLE", 2, 3, 45)],
    "CHAMBRE_D_HOTES": [("CHAMBRE_SIMPLE", 1, 1, 45), ("CHAMBRE_DOUBLE", 2, 4, 65)],
    "GITE_CHALET": [("LOGEMENT_ENTIER", 2, 8, 70)],
    "APPARTEMENT": [("LOGEMENT_ENTIER", 2, 6, 65)],
    "AUBERGE_DE_JEUNESSE": [("LIT_EN_DORTOIR", 1, 1, 22), ("CHAMBRE_DOUBLE", 2, 4, 50)],
    "AIRE_DE_CAMPING_CAR": [("EMPLACEMENT_DE_CAMPING", 2, 4, 12)],
    "REFUGE_GARDE": [("LIT_EN_DORTOIR", 1, 1, 30)],
}
ALPHABET = string.ascii_uppercase + "234567"   # base 32 sans 0/1/O/I ambigus


def generer_utilisateurs():
    users, backo, orga, heb, festivaliers = [], [], [], [], []
    emails = set()

    def creer(nom, email):
        assert email not in emails
        emails.add(email)
        users.append({"idUtilisateur": len(users) + 1, "nom": nom, "email": email})
        return len(users)

    for k in range(NB_ORGANISATEURS + NB_HEBERGEURS + NB_FESTIVALIERS):
        if k == 0:
            i = creer("Ronald Organisateur", "ronald.organisateur@festibed.test")
        elif k == NB_ORGANISATEURS:
            i = creer("Hébergeur Démonstration", "hebergeur.demo@festibed.test")
        else:
            p, n = rnd.choice(PRENOMS), rnd.choice(NOMS)
            i = creer(f"{p} {n}", sans_accent(f"{p}.{n}.{k + 1:05d}@festibed.test").lower())
        if k < NB_ORGANISATEURS + NB_HEBERGEURS:
            backo.append({"idUtilisateur": i, "motDePasseHache": HASH_TEST})
            (orga if k < NB_ORGANISATEURS else heb).append({"idUtilisateur": i})
        else:   # comptes de test : pas de réseau social
            festivaliers.append({"idUtilisateur": i, "fournisseurAuth": None, "identifiantExterneFestivalier": None})
    return users, backo, orga, heb, festivaliers


def nuits_festival(f):
    """Nuits proposées pour un festival : nuits du festival, 7 au maximum (au moins la nuit du 1er jour)."""
    n = max(1, min(7, (f["dateFinFestival"] - f["dateDebutFestival"]).days))
    return [f["dateDebutFestival"] + dt.timedelta(days=i) for i in range(n)]


def generer(festivals, etabs, orga, heb, festivaliers):
    # -------- organisateurs / hébergeurs (Ronald n'a pas de festival : scénario 4)
    for f in festivals:
        if rnd.random() < 0.7:
            f["idOrganisateur"] = rnd.choice(orga[1:])["idUtilisateur"]
    demo_heb = heb[0]["idUtilisateur"]
    for e in etabs:
        if rnd.random() < 0.65:
            e["idUtilisateur"] = rnd.choice(heb[1:])["idUtilisateur"]

    # -------- établissements et festivals des scénarios
    def etab(nom, cp):
        return next(e for e in etabs if e["nomCommercial"] == nom and e["codePostalEtablissement"] == cp)

    def fest(nom):
        return next(f for f in festivals if f["nomFestival"] == nom)

    sierroz, arcades = etab("CAMPING INTERNATIONAL DU SIERROZ", "73100"), etab("HÔTEL DES ARCADES", "71400")
    musilac, couches, saintrock = fest("Musilac"), fest("JAZZ A COUCHES"), fest("SAINT ROCK")
    for e in (sierroz, arcades):
        e["idUtilisateur"] = demo_heb

    # -------- options, hébergements, photos, équipements
    options = [{"idOptionHebergement": i, "libelleOptionHebergement": o} for i, o in enumerate(OPTIONS, 1)]
    hebergements, photos, equipements = [], [], []
    par_dept = collections.defaultdict(list)
    for e in etabs:
        n = min(e["_unites"], rnd.choices([1, 2, 3, 4], [30, 35, 25, 10])[0]) or 1
        etoiles = ETOILES[e["classement"]] if e["classement"] else (e["_etoiles"] or 2)
        for k in range(1, n + 1):
            if e is sierroz and k == 1:
                typ, cap, base = "EMPLACEMENT_DE_CAMPING", 2, 15
            elif e is arcades and k == 1:
                typ, cap, base = "CHAMBRE_SIMPLE", 1, 45
            else:
                typ, cmin, cmax, base = rnd.choice(OFFRES[e.get("_nc") or e["_type"]])
                cap = min(rnd.randint(cmin, cmax), e["capaciteAccueil"])
            prix_nuit = Decimal(round(base * (1 + 0.25 * (etoiles - 1)) * (1 + 0.1 * (cap - 1))
                                      * rnd.uniform(0.85, 1.2), 0)).quantize(Decimal("0.01"))
            h = {"idEtablissement": e["idEtablissement"], "numeroHebergement": f"H{k:03d}", "typeHebergement": typ,
                 "capaciteHebergement": cap, "prixNuitHebergement": prix_nuit,
                 "descriptionHebergement": f"{typ.replace('_', ' ').capitalize()} pour {cap} personne{'s' if cap > 1 else ''}"
                                           f" - {e['nomCommercial'].title()}",
                 "actifHebergement": True, "_dept": e["_dept"]}
            hebergements.append(h)
            cle = (h["idEtablissement"], h["numeroHebergement"])
            if (e is sierroz or e is arcades) and k == 1:
                pass          # hébergements des scénarios : jamais réservés par le peuplement
            else:
                par_dept[e["_dept"]].append(h)
            for p in range(1, rnd.choice([1, 1, 2]) + 1):
                photos.append({"idPhotoHebergement": len(photos) + 1,
                               "urlPhotoHebergement": f"https://img.festibed.test/h/{cle[0]}/{cle[1]}/{p}.webp",
                               "idEtablissement": cle[0], "numeroHebergement": cle[1]})
            for o in rnd.sample(options, rnd.randint(0, 4)):
                equipements.append({"idEtablissement": cle[0], "numeroHebergement": cle[1],
                                    "idOptionHebergement": o["idOptionHebergement"]})
    tous = [h for v in par_dept.values() for h in v]

    # -------- nuitées + sélections + Pass
    occupation = {}                 # (idEtab, numHeb, date) -> idSelection ou None
    prix_nuitee = {}

    def ouvrir(h, nuits):
        for d in nuits:
            k = (h["idEtablissement"], h["numeroHebergement"], d)
            if k not in occupation:
                occupation[k] = None
                ete = d.month in (7, 8)
                prix_nuitee[k] = (h["prixNuitHebergement"] * Decimal("1.20" if ete else "1.00")).quantize(Decimal("0.01"))

    def libre(h, nuits):
        return all(occupation.get((h["idEtablissement"], h["numeroHebergement"], d), 1) is None for d in nuits)

    selections, passes = [], []
    echecs = 0
    for f in sorted(festivals, key=lambda x: x["dateDebutFestival"]):
        nuits = nuits_festival(f)
        cible = round(f["quotaPass"] * rnd.uniform(0.5, 0.9))
        tailles = []
        while sum(tailles) < cible:
            tailles.append(min(rnd.choices([1, 2, 3, 4], [45, 40, 10, 5])[0], cible - sum(tailles)))
        local = par_dept.get(f["_dept"], [])
        candidats = rnd.sample(local, min(len(local), int(len(tailles) * 1.3) + 10))
        if len(candidats) < len(tailles) + 10:      # département peu équipé : hébergements d'ailleurs
            candidats += rnd.sample(tous, len(tailles) + 10 - len(candidats))
            candidats = list({(h["idEtablissement"], h["numeroHebergement"]): h for h in candidats}.values())
        for h in candidats:
            ouvrir(h, nuits)
        vendus = 0
        for n in tailles:
            debut = rnd.randrange(len(nuits))
            sejour = nuits[debut:debut + rnd.randint(1, 3)]
            rnd.shuffle(candidats)
            choisis, cap = [], 0
            for h in candidats:
                if libre(h, sejour):
                    choisis.append(h)
                    cap += h["capaciteHebergement"]
                    if cap >= n:
                        break
            if cap < n:                                   # tout est pris : un hébergement de plus
                h = next(h for h in rnd.sample(tous, 500) if h["capaciteHebergement"] >= n and all(
                    occupation.get((h["idEtablissement"], h["numeroHebergement"], d)) is None for d in sejour))
                ouvrir(h, nuits)
                candidats.append(h)
                choisis, echecs = [h], echecs + 1
            sid = len(selections) + 1
            selections.append({"idSelection": sid, "prixPassSelection": f["prixPass"], "statutSelection": "CONFIRMEE",
                               "numeroReservation": None, "idFestival": f["idFestival"],
                               "_debut": f["dateDebutFestival"], "_nb": n})
            for h in choisis:
                for d in sejour:
                    occupation[(h["idEtablissement"], h["numeroHebergement"], d)] = sid
            for _ in range(n):
                passes.append({"idPass": len(passes) + 1, "codePass": None, "idSelection": sid})
            vendus += n
        f["nbPassVendus"] = vendus

    # hébergements des scénarios : libres pendant leurs festivals
    hs = {(h["idEtablissement"], h["numeroHebergement"]): h for h in hebergements}
    ouvrir(hs[(sierroz["idEtablissement"], "H001")], nuits_festival(musilac))
    for f in (couches, saintrock):
        ouvrir(hs[(arcades["idEtablissement"], "H001")], nuits_festival(f))
    note(f"Sélections : {len(selections)}, Pass : {len(passes)}, nuitées : {len(occupation)} "
         f"(hébergement supplémentaire ouvert {echecs} fois)")

    # -------- réservations (1 à 3 sélections de festivals différents)
    rnd.shuffle(selections)
    reservations, numeros, k = [], set(), 0
    while k < len(selections):
        groupe = [selections[k]]
        k += 1
        voulu = rnd.choices([1, 2, 3], [90, 8, 2])[0]
        while len(groupe) < voulu and k < len(selections) and \
                selections[k]["idFestival"] not in {s["idFestival"] for s in groupe}:
            groupe.append(selections[k])
            k += 1
        while True:
            num = "FB" + "".join(rnd.choice(ALPHABET) for _ in range(10))
            if num not in numeros:
                numeros.add(num)
                break
        haut = min(s["_debut"] for s in groupe) - dt.timedelta(days=1)
        bas = min(dt.date(ANNEE - 1, 11, 2), haut)
        jour = bas + dt.timedelta(days=rnd.randint(0, max(0, (haut - bas).days)))
        quand = dt.datetime.combine(jour, dt.time(rnd.randint(7, 23), rnd.randint(0, 59), rnd.randint(0, 59)))
        for s in groupe:
            s["numeroReservation"] = num
        reservations.append({"numeroReservation": num, "dateReservation": quand,
                             "idUtilisateur": rnd.choice(festivaliers)["idUtilisateur"], "_sel": groupe})
    selections.sort(key=lambda s: s["idSelection"])
    for p in passes:
        p["codePass"] = f"PASS-{p['idPass']:07d}-{rnd.getrandbits(32):08X}"

    # -------- paiements (non développé dans le prototype : statut NON_GERE)
    nuitees_sel = collections.defaultdict(Decimal)
    for k2, sid in occupation.items():
        if sid is not None:
            nuitees_sel[sid] += prix_nuitee[k2]
    paiements = []
    for r in reservations:
        montant = sum(s["prixPassSelection"] * s["_nb"] + nuitees_sel[s["idSelection"]] for s in r["_sel"])
        paiements.append({"idPaiement": len(paiements) + 1, "numTransaction": None, "montantPaiement": montant,
                          "datePaiement": None, "statutPaiement": "NON_GERE",
                          "numeroReservation": r["numeroReservation"]})
    nuitees = [{"idEtablissement": k2[0], "numeroHebergement": k2[1], "dateNuitee": k2[2],
                "prixNuitee": prix_nuitee[k2], "idSelection": sid} for k2, sid in sorted(occupation.items())]

    # -------- notations (éditions et séjours passés)
    notes_f, vus = [], set()
    while len(notes_f) < 30000:
        f, u = rnd.choice(festivals), rnd.choice(festivaliers)["idUtilisateur"]
        if (f["idFestival"], u) in vus:
            continue
        vus.add((f["idFestival"], u))
        d = min(transposer(f["dateDebutFestival"], ANNEE - 1) + dt.timedelta(days=rnd.randint(1, 20)), AUJOURD_HUI)
        notes_f.append({"idFestival": f["idFestival"], "idUtilisateur": u,
                        "noteFestival": rnd.choices([1, 2, 3, 4, 5], [3, 7, 20, 40, 30])[0], "dateNoteFestival": d})
    notes_e, vus = [], set()
    while len(notes_e) < 30000:
        e, u = rnd.choice(etabs), rnd.choice(festivaliers)["idUtilisateur"]
        if (e["idEtablissement"], u) in vus:
            continue
        vus.add((e["idEtablissement"], u))
        notes_e.append({"idEtablissement": e["idEtablissement"], "idUtilisateur": u,
                        "noteEtablissement": rnd.choices([1, 2, 3, 4, 5], [4, 8, 25, 38, 25])[0],
                        "dateNoteEtablissement": dt.date(2025, 6, 1) + dt.timedelta(days=rnd.randint(0, 517))})
    recalculer_notes(etabs, notes_e)
    scenarios = {"sierroz": sierroz, "arcades": arcades, "musilac": musilac, "couches": couches,
                 "saintrock": saintrock}
    return (options, hebergements, photos, equipements, reservations, paiements, selections, passes, nuitees,
            notes_f, notes_e, scenarios)


def recalculer_notes(etabs, notes_e):
    somme, nb = collections.Counter(), collections.Counter()
    for n in notes_e:
        somme[n["idEtablissement"]] += n["noteEtablissement"]
        nb[n["idEtablissement"]] += 1
    for e in etabs:
        k = e["idEtablissement"]
        e["nbNotes"] = nb[k]
        e["noteMoyenne"] = (Decimal(somme[k]) / nb[k]).quantize(Decimal("0.01")) if nb[k] else None


# ================================================================== 4. écriture
def valeur_csv(v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, dt.datetime):
        return v.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(v, dt.date):
        return v.isoformat()
    return str(v)


def ecrire_csv(dossier, donnees):
    dossier.mkdir(parents=True, exist_ok=True)
    for ancien in dossier.glob("*.csv"):     # la numérotation suit l'ordre des tables : pas de fichier périmé
        ancien.unlink()
    for t in TABLES:
        racines = [racine(t, c.nom) if c.typ == "id" else None for c in t.cols]
        with open(dossier / fichier_csv(t), "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, delimiter=";", quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
            w.writerow(t.noms)
            for ligne in donnees[t.nom]:
                w.writerow([valeur_csv(v) if r is None or v is None else uuid_de(r, v)
                            for v, r in zip((ligne.get(c) for c in t.noms), racines)])


def ecrire_scripts():
    (ICI / "01_schema_oracle.sql").write_text(ddl("oracle"), encoding="utf-8")
    (ICI / "01_schema_h2.sql").write_text(ddl("h2"), encoding="utf-8")
    ctl = ICI / "sqlldr"
    ctl.mkdir(exist_ok=True)
    for ancien in ctl.glob("*.ctl"):
        ancien.unlink()
    bat = ["@echo off", "REM FestiBed - chargement Oracle par SQL*Loader (ordre des clés étrangères)",
           "REM Usage : 02_charger_oracle.bat utilisateur/motdepasse@//hote:1521/service",
           "set NLS_LANG=AMERICAN_AMERICA.AL32UTF8", "cd /d %~dp0", "if not exist logs mkdir logs"]
    h2 = ["-- FestiBed - chargement H2 (tests) : exécuter après 01_schema_h2.sql, depuis ce dossier.",
          "-- Les chemins sont relatifs au répertoire courant de la JVM H2."]
    for t in TABLES:
        champs = []
        for c in t.cols:
            if c.typ == "id":     # UUID texte (8-4-4-4-12) -> RAW(16)
                champs.append(f'  {c.nom} CHAR(36) "HEXTORAW(REPLACE(:{c.nom}, \'-\', \'\'))"')
            elif c.typ == "date":
                champs.append(f'  {c.nom} DATE "YYYY-MM-DD"')
            elif c.typ == "ts":
                champs.append(f'  {c.nom} TIMESTAMP "YYYY-MM-DD HH24:MI:SS"')
            elif c.typ.startswith("str"):
                n = int(c.typ[4:-1])
                champs.append(f"  {c.nom} CHAR({max(n * 4, 10)})")
            else:
                champs.append(f"  {c.nom}")
        (ctl / f"{numero(t):02d}_{t.nom}.ctl").write_text(
            "OPTIONS (SKIP=1, ROWS=5000, BINDSIZE=20000000, READSIZE=20000000, ERRORS=0)\n"
            "LOAD DATA\nCHARACTERSET AL32UTF8\n"
            f"INFILE 'csv/{fichier_csv(t)}'\nAPPEND INTO TABLE {t.nom}\n"
            "FIELDS TERMINATED BY ';' OPTIONALLY ENCLOSED BY '\"' TRAILING NULLCOLS\n(\n"
            + ",\n".join(champs) + "\n)\n", encoding="utf-8")
        bat.append(f"sqlldr userid=%1 control=sqlldr\\{numero(t):02d}_{t.nom}.ctl log=logs\\{t.nom}.log "
                   f"bad=logs\\{t.nom}.bad || goto erreur")
        h2.append(f"INSERT INTO {t.nom} ({', '.join(t.noms)}) SELECT {', '.join(t.noms)} FROM "
                  f"CSVREAD('csv/{fichier_csv(t)}', NULL, 'charset=UTF-8 fieldSeparator=;');")
    bat += ["echo Chargement termine. Executer ensuite 04_controles.sql.", "exit /b 0",
            ":erreur", "echo ECHEC : voir le dossier logs", "exit /b 1"]
    (ICI / "02_charger_oracle.bat").write_text("\r\n".join(bat) + "\r\n", encoding="utf-8")
    (ICI / "02_charger_h2.sql").write_text("\n".join(h2) + "\n", encoding="utf-8")


# ================================================================== 5. contrôles
def controler(d, sc):
    ok = True

    def verif(cond, msg):
        nonlocal ok
        ok &= bool(cond)
        note(f"  [{'OK' if cond else 'KO'}] {msg}")

    note("Contrôles :")
    fest = {f["idFestival"]: f for f in d["FESTIVAL"]}
    pass_par_f = collections.Counter()
    sel = {s["idSelection"]: s for s in d["SELECTION"]}
    for p in d["PASS"]:
        pass_par_f[sel[p["idSelection"]]["idFestival"]] += 1
    verif(len(d["RESERVATION"]) >= 100000, f"au moins 100 000 réservations ({len(d['RESERVATION'])})")
    verif(all(f["quotaPass"] >= 30 for f in fest.values()), "chaque festival propose au moins 30 Pass")
    verif(all(pass_par_f[i] == f["nbPassVendus"] for i, f in fest.items()), "nbPassVendus = nombre réel de Pass")
    verif(all(f["quotaPass"] / 2 <= f["nbPassVendus"] <= f["quotaPass"] for f in fest.values()),
          "au moins la moitié du quota réservée, jamais plus que le quota")
    cap = collections.defaultdict(lambda: collections.defaultdict(int))
    hcap = {(h["idEtablissement"], h["numeroHebergement"]): h["capaciteHebergement"] for h in d["HEBERGEMENT"]}
    for n in d["NUITEE"]:
        if n["idSelection"]:
            cap[n["idSelection"]][n["dateNuitee"]] += hcap[(n["idEtablissement"], n["numeroHebergement"])]
    verif(all(cap[s["idSelection"]] and min(cap[s["idSelection"]].values()) >= s["_nb"] for s in d["SELECTION"]),
          "réservation groupée : chaque sélection a des nuitées dont la capacité couvre ses Pass")
    verif(all(fest[s["idFestival"]]["dateDebutFestival"] <= nd < fest[s["idFestival"]]["dateDebutFestival"]
              + dt.timedelta(days=7) for s in d["SELECTION"] for nd in cap[s["idSelection"]]),
          "les nuitées réservées sont des nuits du festival")
    chev = collections.defaultdict(list)
    for f in fest.values():
        chev[(f["_dept"], f["dateDebutFestival"].isocalendar()[1])].append(f)
    verif(sum(1 for v in chev.values() if len(v) > 1) > 50, "des festivals d'un même département se chevauchent")
    libres = sum(1 for n in d["NUITEE"] if n["idSelection"] is None)
    verif(libres > 100000, f"nuitées libres disponibles pour les tests ({libres} / {len(d['NUITEE'])})")
    geo = sum(1 for e in d["ETABLISSEMENT"] if e["latitudeEtablissement"] is not None)
    verif(geo >= 0.95 * len(d["ETABLISSEMENT"]), f"établissements géocodés ({geo} / {len(d['ETABLISSEMENT'])})")
    sous_types = collections.Counter(x["idEtablissement"] for t in TABLES
                                     if t.fk and t.fk[0][1] == "ETABLISSEMENT" and t.pk == ["idEtablissement"]
                                     for x in d[t.nom])
    verif(all(sous_types[e["idEtablissement"]] == 1 for e in d["ETABLISSEMENT"]),
          "chaque établissement a exactement un sous-type")
    classes = [e for e in d["ETABLISSEMENT"] if e["classement"]]
    verif(all((e["classement"] is None) == (e["dateClassement"] is None) == (e["classementProroge"] is None)
              for e in d["ETABLISSEMENT"]) and len(classes) == len(d["ETABLISSEMENT"]) - len(d["ETABLISSEMENT_NON_CLASSE"]),
          f"classement renseigné pour les classés seulement ({len(classes)} classés, "
          f"{len(d['ETABLISSEMENT_NON_CLASSE'])} non classés)")
    communes = {c["codeInsee"] for c in d["COMMUNE"]}
    verif(all(e["codeInsee"] is None or e["codeInsee"] in communes for e in d["ETABLISSEMENT"]),
          "code INSEE des établissements présent dans COMMUNE")
    refs = [e["osmRef"] for e in d["ETABLISSEMENT"] if e["osmRef"]]
    verif(len(refs) == len(set(refs)), f"un objet OSM correspond à un seul établissement ({len(refs)} rapprochés)")
    tel = sum(1 for e in d["ETABLISSEMENT"] if e["telephoneEtablissement"])
    verif(tel > 0, f"téléphones renseignés grâce à OSM ({tel} / {len(d['ETABLISSEMENT'])})")
    verif(len({r["numeroReservation"] for r in d["RESERVATION"]}) == len(d["RESERVATION"]), "numéros de réservation uniques")
    for nom in ("musilac", "couches", "saintrock"):
        f = sc[nom]
        verif(f["quotaPass"] - f["nbPassVendus"] >= 2,
              f"scénario : {f['nomFestival']} du {f['dateDebutFestival']} au {f['dateFinFestival']}, "
              f"{f['quotaPass'] - f['nbPassVendus']} Pass disponibles")
    return ok


# ==================================================================== principal
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--geocoder", action="store_true",
                    help="interroger la BAN et l'API Géo pour les adresses et communes absentes des caches")
    args = ap.parse_args()
    t0 = time.time()
    regions, depts, communes, festivals = charger_festivals()
    api_geo = lire_communes_api(args.geocoder)
    etabs, sous = charger_etablissements(args.geocoder)
    lieux = lire_osm()
    integrer_osm(etabs, sous, lieux, api_geo, args.geocoder)
    completer_geographie(regions, depts, communes, etabs, lieux, api_geo)
    users, backo, orga, heb, festivaliers = generer_utilisateurs()
    (options, hebergements, photos, equipements, reservations, paiements, selections, passes, nuitees,
     notes_f, notes_e, sc) = generer(festivals, etabs, orga, heb, festivaliers)
    donnees = {
        "REGION": list(regions.values()), "DEPARTEMENT": list(depts.values()), "COMMUNE": list(communes.values()),
        "UTILISATEUR": users, "FESTIVALIER": festivaliers, "UTILISATEUR_BACKOFFICE": backo,
        "ORGANISATEUR": orga, "HEBERGEUR": heb, "FESTIVAL": festivals, "ETABLISSEMENT": etabs,
        **{k: sous[k] for k in ("HOTEL_DE_TOURISME", "AUBERGE_COLLECTIVE", "CAMPING", "PARC_RESIDENTIEL_DE_LOISIRS",
                                "VILLAGE_DE_VACANCES", "RESIDENCE_DE_TOURISME", "ETABLISSEMENT_NON_CLASSE")},
        "OPTION_HEBERGEMENT": options, "HEBERGEMENT": hebergements, "PHOTO_HEBERGEMENT": photos,
        "EQUIPEMENT": equipements, "RESERVATION": reservations, "PAIEMENT": paiements, "SELECTION": selections,
        "PASS": passes, "NUITEE": nuitees, "NOTATION_FESTIVAL": notes_f, "NOTATION_ETABLISSEMENT": notes_e}
    assert set(donnees) == set(PAR_NOM)
    ok = controler(donnees, sc)
    ecrire_csv(SORTIE, donnees)
    ecrire_scripts()
    note("Volumes : " + ", ".join(f"{t.nom}={len(donnees[t.nom])}" for t in TABLES))
    with open(ICI / "cache" / "jeu_complet.json", "w", encoding="utf-8") as f:   # pour le jeu d'essai Excel
        json.dump({"scenarios": {k: uuid_de("FESTIVAL", v["idFestival"]) if "idFestival" in v
                                 else uuid_de("ETABLISSEMENT", v["idEtablissement"]) for k, v in sc.items()}},
                  f, indent=1)
    note(f"Terminé en {time.time() - t0:.0f} s")
    (ICI / "rapport_peuplement.txt").write_text("\n".join(log) + "\n", encoding="utf-8")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

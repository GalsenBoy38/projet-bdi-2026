"""FestiBed - Groupe 3 - Fichiers Excel d'insertion.

Produit, à partir du peuplement complet (../3_peuplement_donnees/csv) :
  - Gabarits_insertion_vides.xlsx : un onglet par table, en-têtes seuls, commentaires (type, NULL, rôle)
  - Jeu_essai_scenarios.xlsx      : petit jeu de données COHÉRENT (clés étrangères fermées) autour des
                                    festivals des scénarios 1 à 4, pour les tests H2 et la démonstration

Usage : python generer_excel.py   (après generer_peuplement.py)
"""
import collections
import csv
import datetime as dt
import json
import sys
from decimal import Decimal
from pathlib import Path

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ICI = Path(__file__).resolve().parent
PEUPLEMENT = ICI.parent / "3_peuplement_donnees"
sys.path.insert(0, str(PEUPLEMENT))
from schema_festibed import TABLES, ENUMS, fichier_csv, numero, uuid_de  # noqa: E402

COULEUR = {"PUBLIC": "C6EFCE", "SYNTHÉTIQUE": "FFEB9C", "MIXTE": "BDD7EE"}
TITRE = Font(bold=True, color="FFFFFF")


def lire(t):
    with open(PEUPLEMENT / "csv" / fichier_csv(t), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def typer(c, v):
    if v == "":
        return None
    if c.typ in ("int",) or c.typ.startswith("num"):
        return int(v)
    if c.typ == "bool":
        return int(v)
    if c.typ.startswith("dec"):
        return float(Decimal(v))
    if c.typ == "date":
        return dt.date.fromisoformat(v)
    if c.typ == "ts":
        return dt.datetime.fromisoformat(v)
    return v


def commentaire(t, c):
    txt = f"{c.typ} - {'NULL autorisé' if c.null else 'obligatoire'}"
    if c.nom in t.pk:
        txt += " - clé primaire"
    for cols, ref, rcols in t.fk:
        if c.nom in cols:
            txt += f" - clé étrangère vers {ref}.{rcols[cols.index(c.nom)]}"
    if c.enum:
        txt += f"\nValeurs : {', '.join(ENUMS[c.enum])}"
    if c.typ == "bool":
        txt += "\n1 = vrai, 0 = faux"
    if c.typ == "id":
        txt += "\nUUID au format texte 8-4-4-4-12 (ex. 3f2a9c1e-5b7d-5e21-9c0a-1d2e3f4a5b6c)"
    if c.desc:
        txt += f"\n{c.desc}"
    return Comment(txt, "Groupe 3", width=360, height=150)


def onglet(wb, t, lignes):
    ws = wb.create_sheet(f"{numero(t):02d}_{t.nom}"[:31])
    for j, c in enumerate(t.cols, 1):
        cell = ws.cell(1, j, c.nom)
        cell.font = TITRE
        cell.fill = PatternFill("solid", fgColor="44546A")
        cell.comment = commentaire(t, c)
        ws.column_dimensions[get_column_letter(j)].width = 38 if c.typ == "id" else max(14, len(c.nom) + 3)
    for i, ligne in enumerate(lignes, 2):
        for j, c in enumerate(t.cols, 1):
            cell = ws.cell(i, j, typer(c, ligne[c.nom]))
            if c.typ.startswith("str") or c.typ == "id":
                cell.number_format = "@"
            elif c.typ == "date":
                cell.number_format = "yyyy-mm-dd"
            elif c.typ == "ts":
                cell.number_format = "yyyy-mm-dd hh:mm:ss"
    if not lignes:     # gabarit : colonnes texte au format Texte pour garder les zéros initiaux
        for j, c in enumerate(t.cols, 1):
            if c.typ.startswith("str") or c.typ == "id":
                for i in range(2, 502):
                    ws.cell(i, j).number_format = "@"
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(t.cols))}{max(1, len(lignes) + 1)}"


def sommaire(wb, titre, texte, volumes):
    ws = wb.active
    ws.title = "00_LISEZ_MOI"
    ws["A1"] = titre
    ws["A1"].font = Font(bold=True, size=14)
    for i, ligne in enumerate(texte, 2):
        ws.cell(i, 1, ligne).alignment = Alignment(wrap_text=True, vertical="top")
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=4)
    ws.row_dimensions[2].height = 120
    r = len(texte) + 3
    for j, h in enumerate(["Ordre", "Table", "Origine", "Lignes"], 1):
        ws.cell(r, j, h).font = TITRE
        ws.cell(r, j).fill = PatternFill("solid", fgColor="44546A")
    for t in TABLES:
        r += 1
        ws.cell(r, 1, numero(t))
        ws.cell(r, 2, t.nom)
        ws.cell(r, 3, t.origine).fill = PatternFill("solid", fgColor=COULEUR[t.origine])
        ws.cell(r, 4, volumes.get(t.nom, 0))
    for col, w in zip("ABCD", [8, 34, 15, 10]):
        ws.column_dimensions[col].width = w


# ------------------------------------------------------------------ jeu d'essai
def jeu_essai():
    T = {t.nom: lire(t) for t in TABLES}
    sc = json.loads((PEUPLEMENT / "cache" / "jeu_complet.json").read_text(encoding="utf-8"))["scenarios"]
    fest = {r["idFestival"]: r for r in T["FESTIVAL"]}
    comm = {r["codeInsee"]: r for r in T["COMMUNE"]}
    ids_scen = [str(sc[k]) for k in ("musilac", "couches", "saintrock")]
    autres = [f for f in T["FESTIVAL"] if f["idFestival"] not in ids_scen
              and comm[f["codeInsee"]]["codeDepartement"] in ("71", "73")
              and "2027-06-15" <= f["dateDebutFestival"] <= "2027-08-31"]
    F = set(ids_scen) | {f["idFestival"] for f in autres[:22]}

    # sélections : 6 réservations au plus par festival, réservations entièrement incluses
    sel_par_resa = collections.defaultdict(list)
    for s in T["SELECTION"]:
        sel_par_resa[s["numeroReservation"]].append(s)
    R, compte = set(), collections.Counter()
    for num, sels in sel_par_resa.items():
        if all(s["idFestival"] in F for s in sels) and all(compte[s["idFestival"]] < 6 for s in sels):
            R.add(num)
            for s in sels:
                compte[s["idFestival"]] += 1
    S = {s["idSelection"] for s in T["SELECTION"] if s["numeroReservation"] in R}

    fenetre = {}
    for i in F:
        d = dt.date.fromisoformat(fest[i]["dateDebutFestival"])
        fenetre[i] = (d, d + dt.timedelta(days=7))
    H = {(n["idEtablissement"], n["numeroHebergement"]) for n in T["NUITEE"] if n["idSelection"] in S}
    H |= {(str(sc["sierroz"]), "H001"), (str(sc["arcades"]), "H001")}
    libres = collections.Counter()
    for n in T["NUITEE"]:      # quelques hébergements libres en plus, pour pouvoir réserver en démonstration
        k = (n["idEtablissement"], n["numeroHebergement"])
        if k not in H and n["idSelection"] == "" and any(a <= dt.date.fromisoformat(n["dateNuitee"]) < b
                                                          for a, b in fenetre.values()):
            libres[k] += 1
    etab_dept = {}
    for e in T["ETABLISSEMENT"]:
        etab_dept[e["idEtablissement"]] = e["codePostalEtablissement"][:2]
    non_classes = {x["idEtablissement"] for x in T["ETABLISSEMENT_NON_CLASSE"]}
    proches = [k for k, _ in libres.most_common() if etab_dept[k[0]] in ("71", "73")]
    H |= set([k for k in proches if k[0] not in non_classes][:30])
    H |= set([k for k in proches if k[0] in non_classes][:20])      # chambres d'hôtes, gîtes… (OSM)
    E = {k[0] for k in H}

    nuitees = []
    for n in T["NUITEE"]:
        if (n["idEtablissement"], n["numeroHebergement"]) in H and any(
                a <= dt.date.fromisoformat(n["dateNuitee"]) < b for a, b in fenetre.values()):
            n = dict(n)
            if n["idSelection"] not in S:
                n["idSelection"] = ""
            nuitees.append(n)

    selections = [s for s in T["SELECTION"] if s["idSelection"] in S]
    passes = [p for p in T["PASS"] if p["idSelection"] in S]
    vendus = collections.Counter()
    sel_fest = {s["idSelection"]: s["idFestival"] for s in selections}
    for p in passes:
        vendus[sel_fest[p["idSelection"]]] += 1
    festivals = []
    for i in (f["idFestival"] for f in T["FESTIVAL"] if f["idFestival"] in F):   # ordre du CSV
        f = dict(fest[i])
        f["nbPassVendus"] = str(vendus[i])
        festivals.append(f)
    reservations = [r for r in T["RESERVATION"] if r["numeroReservation"] in R]
    notes_f = [n for n in T["NOTATION_FESTIVAL"] if n["idFestival"] in F][:150]
    notes_e = [n for n in T["NOTATION_ETABLISSEMENT"] if n["idEtablissement"] in E]
    etabs = []
    somme, nb = collections.Counter(), collections.Counter()
    for n in notes_e:
        somme[n["idEtablissement"]] += int(n["noteEtablissement"])
        nb[n["idEtablissement"]] += 1
    for e in T["ETABLISSEMENT"]:
        if e["idEtablissement"] in E:
            e = dict(e)
            k = e["idEtablissement"]
            e["nbNotes"] = str(nb[k])
            e["noteMoyenne"] = str((Decimal(somme[k]) / nb[k]).quantize(Decimal("0.01"))) if nb[k] else ""
            etabs.append(e)

    festivaliers_ids = {r["idUtilisateur"] for r in reservations} | {n["idUtilisateur"] for n in notes_f + notes_e}
    orga_ids = {f["idOrganisateur"] for f in festivals if f["idOrganisateur"]} | {uuid_de("UTILISATEUR", 1)}         # Ronald
    heb_ids = {e["idUtilisateur"] for e in etabs if e["idUtilisateur"]} | {uuid_de("UTILISATEUR", len(T["ORGANISATEUR"]) + 1)}
    tous_ids = festivaliers_ids | orga_ids | heb_ids
    communes = {f["codeInsee"] for f in festivals} | {e["codeInsee"] for e in etabs if e["codeInsee"]}
    depts = {comm[c]["codeDepartement"] for c in communes}
    regions = {d["idRegion"] for d in T["DEPARTEMENT"] if d["codeDepartement"] in depts}

    J = {
        "REGION": [r for r in T["REGION"] if r["idRegion"] in regions],
        "DEPARTEMENT": [d for d in T["DEPARTEMENT"] if d["codeDepartement"] in depts],
        "COMMUNE": [c for c in T["COMMUNE"] if c["codeInsee"] in communes],
        "UTILISATEUR": [u for u in T["UTILISATEUR"] if u["idUtilisateur"] in tous_ids],
        "FESTIVALIER": [u for u in T["FESTIVALIER"] if u["idUtilisateur"] in festivaliers_ids],
        "UTILISATEUR_BACKOFFICE": [u for u in T["UTILISATEUR_BACKOFFICE"] if u["idUtilisateur"] in orga_ids | heb_ids],
        "ORGANISATEUR": [u for u in T["ORGANISATEUR"] if u["idUtilisateur"] in orga_ids],
        "HEBERGEUR": [u for u in T["HEBERGEUR"] if u["idUtilisateur"] in heb_ids],
        "FESTIVAL": festivals, "ETABLISSEMENT": etabs,
        "OPTION_HEBERGEMENT": T["OPTION_HEBERGEMENT"],
        "HEBERGEMENT": [h for h in T["HEBERGEMENT"] if (h["idEtablissement"], h["numeroHebergement"]) in H],
        "PHOTO_HEBERGEMENT": [p for p in T["PHOTO_HEBERGEMENT"] if (p["idEtablissement"], p["numeroHebergement"]) in H],
        "EQUIPEMENT": [q for q in T["EQUIPEMENT"] if (q["idEtablissement"], q["numeroHebergement"]) in H],
        "RESERVATION": reservations,
        "PAIEMENT": [p for p in T["PAIEMENT"] if p["numeroReservation"] in R],
        "SELECTION": selections, "PASS": passes, "NUITEE": nuitees,
        "NOTATION_FESTIVAL": notes_f, "NOTATION_ETABLISSEMENT": notes_e,
    }
    for st in ("HOTEL_DE_TOURISME", "AUBERGE_COLLECTIVE", "CAMPING", "PARC_RESIDENTIEL_DE_LOISIRS",
               "VILLAGE_DE_VACANCES", "RESIDENCE_DE_TOURISME", "ETABLISSEMENT_NON_CLASSE"):
        J[st] = [x for x in T[st] if x["idEtablissement"] in E]
    return J, sc, fest


def main():
    vides = Workbook()
    sommaire(vides, "FestiBed - Groupe 3 - Gabarits d'insertion (modèle JPA)", [
        "Un onglet par table, dans l'ordre d'insertion imposé par les clés étrangères. Survolez un en-tête "
        "pour voir son type, s'il est obligatoire, la clé référencée et les valeurs autorisées. Les colonnes "
        "texte et les identifiants (UUID 8-4-4-4-12) sont au format Texte (codes INSEE, codes postaux : zéros "
        "initiaux conservés). Booléens : 1/0. "
        "Dates : AAAA-MM-JJ. Une fois rempli, le classeur se convertit en INSERT avec excel_vers_sql.py."], {})
    for t in TABLES:
        onglet(vides, t, [])
    vides.save(ICI / "Gabarits_insertion_vides.xlsx")

    J, sc, fest = jeu_essai()
    essai = Workbook()
    sommaire(essai, "FestiBed - Groupe 3 - Jeu d'essai des scénarios", [
        "Extrait cohérent du peuplement complet (mêmes identifiants), centré sur les scénarios du cahier des "
        f"charges : Musilac (id {sc['musilac']}) et le camping du Sierroz (établissement {sc['sierroz']}, "
        f"emplacement H001 pour 2 personnes, libre) pour le scénario 1 ; Jazz à Couches (id {sc['couches']}), "
        f"Saint Rock (id {sc['saintrock']}) et l'hôtel des Arcades à Autun (établissement {sc['arcades']}, "
        "chambre H001 à un lit, libre) pour les scénarios 2 et 3 ; le compte organisateur de Ronald "
        "(ronald.organisateur@festibed.test, mot de passe festibed) pour le scénario 4. Toutes les clés "
        "étrangères sont présentes dans le classeur : il peut être inséré seul dans une base vide "
        "(tests H2, démonstration). Conversion en SQL : python excel_vers_sql.py Jeu_essai_scenarios.xlsx"],
        {k: len(v) for k, v in J.items()})
    for t in TABLES:
        onglet(essai, t, J[t.nom])
    essai.save(ICI / "Jeu_essai_scenarios.xlsx")
    print("Jeu d'essai :", ", ".join(f"{t.nom}={len(J[t.nom])}" for t in TABLES))


if __name__ == "__main__":
    main()

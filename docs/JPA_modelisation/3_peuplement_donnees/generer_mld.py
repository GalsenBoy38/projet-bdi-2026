"""FestiBed - Groupe 3 - MLD PlantUML généré depuis schema_festibed.py (source unique).

Produit docs/Output_Diagramme/MLD_GLOBAL_FINAL.puml : le MLD ne peut plus diverger du DDL, des CSV ni des
entités JPA. Rendu en SVG/PNG : java -jar plantuml.jar -tsvg -tpng MLD_GLOBAL_FINAL.puml

Usage : python generer_mld.py
"""
import re
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
from schema_festibed import TABLES  # noqa: E402

SORTIE = ICI.parents[1] / "Output_Diagramme" / "MLD_GLOBAL_FINAL.puml"
GROUPES = [
    ("Utilisateurs", ["UTILISATEUR", "FESTIVALIER", "UTILISATEUR_BACKOFFICE", "ORGANISATEUR", "HEBERGEUR"]),
    ("Géographie", ["REGION", "DEPARTEMENT", "COMMUNE"]),
    ("Festivals", ["FESTIVAL", "NOTATION_FESTIVAL"]),
    ("Établissements", ["ETABLISSEMENT", "HOTEL_DE_TOURISME", "AUBERGE_COLLECTIVE", "CAMPING",
                        "PARC_RESIDENTIEL_DE_LOISIRS", "VILLAGE_DE_VACANCES", "RESIDENCE_DE_TOURISME",
                        "ETABLISSEMENT_NON_CLASSE", "NOTATION_ETABLISSEMENT"]),
    ("Hébergements", ["HEBERGEMENT", "PHOTO_HEBERGEMENT", "OPTION_HEBERGEMENT", "EQUIPEMENT", "NUITEE"]),
    ("Réservations", ["RESERVATION", "SELECTION", "PASS", "PAIEMENT"]),
]
COULEUR = {"PUBLIC": "#C6EFCE", "SYNTHÉTIQUE": "#FFEB9C", "MIXTE": "#BDD7EE"}


def type_mld(typ):
    base, a, b = re.fullmatch(r"(\w+)(?:\((\d+)(?:,(\d+))?\))?", typ).groups()
    return {"id": "UUID", "int": "INT", "num": "SMALLINT", "bool": "LOGICAL", "date": "DATE",
            "ts": "DATETIME"}.get(base) or (f"VARCHAR({a})" if base == "str" else f"DECIMAL({a},{b})")


def alias(nom):
    return "".join(m.capitalize() for m in nom.split("_"))


def main():
    par_nom = {t.nom: t for t in TABLES}
    assert sorted(n for _, g in GROUPES for n in g) == sorted(par_nom), "table oubliée dans GROUPES"
    out = ["@startuml MLD_GLOBAL_FINAL",
           "' " + "=" * 77,
           "'  FestiBed - Groupe 3 - MLD GLOBAL FINAL",
           "'  GÉNÉRÉ par docs/JPA_modelisation/3_peuplement_donnees/generer_mld.py depuis schema_festibed.py :",
           "'  ne pas modifier à la main (modifier le schéma puis relancer le script).",
           "'  Clé primaire soulignée, # clé étrangère, <<UK>> unicité, [0..1] = peut être NULL.",
           "'  Couleur : vert = données publiques, bleu = mixtes, jaune = synthétiques.",
           "'  Héritages JOINED : UTILISATEUR, UTILISATEUR_BACKOFFICE, ETABLISSEMENT (clé primaire = clé étrangère).",
           "'  ETABLISSEMENT : classement/dateClassement/classementProroge tous NULL (non classé, OSM) ou tous",
           "'  renseignés (classé) ; exactement une ligne dans l'une des 7 sous-tables.",
           "' " + "=" * 77,
           "hide circle", "hide methods", "hide stereotype",
           "skinparam classAttributeIconSize 0", "skinparam linetype ortho",
           "skinparam nodesep 40", "skinparam ranksep 50", "skinparam defaultFontSize 16",
           "skinparam class {", "  FontSize 18", "  FontStyle bold", "  AttributeFontSize 16",
           "  BorderColor #555555", "  ArrowColor black", "}", ""]
    for titre, noms in GROUPES:
        out.append(f"' ===== {titre} =====")
        for nom in noms:
            t = par_nom[nom]
            fk_cols = {c for cols, _, _ in t.fk for c in cols}
            uk_cols = {c for u in t.uk if len(u) == 1 for c in u}
            out.append(f'entity "{nom}" as {alias(nom)} {COULEUR[t.origine]} {{')
            pk = [c for c in t.cols if c.nom in t.pk]
            for c in pk:
                out.append(f"  <u>{'#' if c.nom in fk_cols else ''}{c.nom}</u> : {type_mld(c.typ)}")
            out.append("  --")
            for c in t.cols:
                if c.nom in t.pk:
                    continue
                ligne = f"  {'<<UK>> ' if c.nom in uk_cols else ''}{'#' if c.nom in fk_cols else ''}{c.nom} : {type_mld(c.typ)}"
                out.append(ligne + (" [0..1]" if c.null else ""))
            for u in t.uk:
                if len(u) > 1:
                    out.append(f"  <<UK>> ({', '.join(u)})")
            out.append("}")
            out.append("")
    out.append("' ===== Clés étrangères (table référencée -- table qui référence) =====")
    for t in TABLES:
        for cols, ref, _ in t.fk:
            out.append(f"{alias(ref)} -- {alias(t.nom)}")
    out.append("@enduml")
    SORTIE.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"MLD écrit dans {SORTIE}")


if __name__ == "__main__":
    main()

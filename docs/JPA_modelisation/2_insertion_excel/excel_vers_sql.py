"""FestiBed - Groupe 3 - Conversion d'un classeur d'insertion Excel en scripts SQL.

Le classeur doit suivre Gabarits_insertion_vides.xlsx (un onglet NN_TABLE par table, en-têtes en ligne 1).
Produit deux scripts :
  <nom>_oracle.sql : INSERT Oracle (SQL*Plus / SQL Developer), booléens 1/0, UUID en HEXTORAW('...')
  <nom>_h2.sql     : INSERT H2 (tests), booléens TRUE/FALSE, UUID en texte
Les identifiants sont des UUID (texte 8-4-4-4-12) : pas de séquence à recaler.

Usage : python excel_vers_sql.py Jeu_essai_scenarios.xlsx [prefixe_sortie]
"""
import datetime as dt
import sys
import uuid
from decimal import Decimal
from pathlib import Path

from openpyxl import load_workbook

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI.parent / "3_peuplement_donnees"))
from schema_festibed import TABLES, ENUMS, numero  # noqa: E402


def litteral(c, v, dialecte):
    if v is None or (isinstance(v, str) and v.strip() == ""):
        if c.defaut is not None:
            return "DEFAULT"
        if not c.null:
            raise ValueError(f"{c.nom} est obligatoire")
        return "NULL"
    if c.typ == "bool":
        vrai = str(v).strip().upper() in ("1", "TRUE", "VRAI", "OUI")
        return ("1" if vrai else "0") if dialecte == "oracle" else ("TRUE" if vrai else "FALSE")
    if c.typ == "id":
        try:
            u = uuid.UUID(str(v).strip())
        except ValueError:
            raise ValueError(f"{c.nom} : « {v} » n'est pas un UUID") from None
        return f"HEXTORAW('{u.hex.upper()}')" if dialecte == "oracle" else f"'{u}'"
    if c.typ == "int" or c.typ.startswith("num"):
        return str(int(v))
    if c.typ.startswith("dec"):
        return str(Decimal(str(v)))
    if c.typ == "date":
        d = v.date() if isinstance(v, dt.datetime) else (v if isinstance(v, dt.date) else dt.date.fromisoformat(str(v)[:10]))
        return f"DATE '{d.isoformat()}'"
    if c.typ == "ts":
        t = v if isinstance(v, dt.datetime) else dt.datetime.fromisoformat(str(v))
        return f"TIMESTAMP '{t.strftime('%Y-%m-%d %H:%M:%S')}'"
    s = str(v)
    if c.enum and s not in ENUMS[c.enum]:
        raise ValueError(f"{c.nom} : « {s} » n'est pas une valeur de {c.enum}")
    longueur = int(c.typ[4:-1])
    if len(s) > longueur:
        raise ValueError(f"{c.nom} : {len(s)} caractères > {longueur}")
    return "'" + s.replace("'", "''") + "'"


def convertir(xlsx, prefixe):
    wb = load_workbook(xlsx, data_only=True)
    sorties = {"oracle": ["SET DEFINE OFF", "SET FEEDBACK OFF"], "h2": []}
    total = 0
    for t in TABLES:
        nom_onglet = f"{numero(t):02d}_{t.nom}"[:31]
        if nom_onglet not in wb.sheetnames:
            continue
        ws = wb[nom_onglet]
        entetes = [c.value for c in ws[1]]
        if entetes[:len(t.cols)] != t.noms:
            raise ValueError(f"{nom_onglet} : en-têtes {entetes} différents du modèle {t.noms}")
        for d in sorties.values():
            d.append(f"\n-- {t.nom}")
        for n, ligne in enumerate(ws.iter_rows(min_row=2, max_col=len(t.cols), values_only=True), 2):
            if all(v is None for v in ligne):
                continue
            for dialecte, out in sorties.items():
                try:
                    vals = [litteral(c, v, dialecte) for c, v in zip(t.cols, ligne)]
                except ValueError as e:
                    raise ValueError(f"{nom_onglet} ligne {n} : {e}") from None
                out.append(f"INSERT INTO {t.nom} ({', '.join(t.noms)}) VALUES ({', '.join(vals)});")
            total += 1
    sorties["oracle"].append("COMMIT;")
    sorties["h2"].append("COMMIT;")
    for dialecte, out in sorties.items():
        Path(f"{prefixe}_{dialecte}.sql").write_text(
            f"-- Généré par excel_vers_sql.py depuis {Path(xlsx).name} : {total} lignes\n" + "\n".join(out) + "\n",
            encoding="utf-8")
    print(f"{total} lignes converties -> {prefixe}_oracle.sql, {prefixe}_h2.sql")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    source = Path(sys.argv[1])
    convertir(source, sys.argv[2] if len(sys.argv) > 2 else str(source.with_suffix("")).replace("Jeu_essai", "insert_jeu_essai"))

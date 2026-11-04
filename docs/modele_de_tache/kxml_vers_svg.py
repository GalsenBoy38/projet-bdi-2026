"""
FestiBed - Groupe 3 - Export du modèle de tâches K-MADe (.kxml) en SVG imprimable sur UNE page A4 paysage.

    python kxml_vers_svg.py                      # lit Modéles_de_taches.kxml
    python kxml_vers_svg.py autre_modele.kxml

Produit Modele_de_taches_A4_paysage.svg (297 x 210 mm). Pour l'imprimer : ouvrir le SVG (ou le PDF)
dans un navigateur, orientation Paysage, marges « Aucune », échelle 100 %.

Mise en page : arbre de haut en bas comme dans K-MADe. Pour tenir sur une page, les sous-tâches
élémentaires d'une même tâche mère sont empilées verticalement (l'ordre se lit de haut en bas),
et les préconditions / observations sont renvoyées en notes (P1, P2... / N1, N2...) en bas de page.
Nécessite : pip install fonttools (mesure de la largeur du texte avec la police Arial de Windows).
"""
import sys
import xml.etree.ElementTree as ET
from html import escape
from pathlib import Path

from fontTools.ttLib import TTFont

ICI = Path(__file__).resolve().parent
SOURCE = Path(sys.argv[1]) if len(sys.argv) > 1 else ICI / "Modéles_de_taches.kxml"
SORTIE = ICI / "Modele_de_taches_A4_paysage.svg"

PAGE_L, PAGE_H, MARGE = 297.0, 210.0, 7.0
PT = 0.3528  # 1 point en mm

COULEURS = {  # exécutant K-MADe -> (fond, bord, libellé)
    "ABS": ("#eceff1", "#607d8b", "Abstraite"),
    "USER": ("#fff3cd", "#b8860b", "Utilisateur"),
    "INT": ("#dbeafe", "#1d4ed8", "Interactive"),
    "SYS": ("#dcfce7", "#15803d", "Système"),
    "UNKNOWN": ("#ffffff", "#999999", "Inconnue"),
}
OPERATEURS = {"SEQ": "SEQ", "ALT": "ALT", "PAR": "PAR", "ET": "ET", "ELEM": "ELEM", "NO_ORDER": "SANS ORDRE"}


# ---------------------------------------------------------------- mesure du texte (Arial)
class Police:
    def __init__(self, fichier):
        f = TTFont(fichier)
        self.upm = f["head"].unitsPerEm
        self.cmap = f.getBestCmap()
        self.hmtx = f["hmtx"]

    def largeur(self, texte, taille):
        u = 0
        for c in texte:
            g = self.cmap.get(ord(c))
            u += self.hmtx[g][0] if g else self.upm * 0.55
        return u / self.upm * taille


ARIAL = Police(r"C:\Windows\Fonts\arial.ttf")
ARIAL_B = Police(r"C:\Windows\Fonts\arialbd.ttf")


def decouper_mots(mots, largeur_max, taille, gras_premier):
    """Un mot plus large que la boîte est coupé avec un trait d'union (jamais le numéro de tâche)."""
    for i, m in enumerate(mots):
        if (i == 0 and gras_premier) or ARIAL.largeur(m, taille) <= largeur_max:
            yield i, m
            continue
        reste = m
        while ARIAL.largeur(reste, taille) > largeur_max:
            k = len(reste) - 1
            while k > 3 and ARIAL.largeur(reste[:k] + "-", taille) > largeur_max:
                k -= 1
            yield i, reste[:k] + "-"
            reste = reste[k:]
        yield i, reste


def couper(mots, largeur_max, taille, gras_premier=True):
    """Coupe une liste de mots en lignes ; le premier mot (numéro) est en gras."""
    lignes, courante, l_cour = [], [], 0.0
    esp = ARIAL.largeur(" ", taille)
    for i, m in decouper_mots(mots, largeur_max, taille, gras_premier):
        police = ARIAL_B if (i == 0 and gras_premier) else ARIAL
        lm = police.largeur(m, taille)
        if courante and l_cour + esp + lm > largeur_max:
            lignes.append(courante)
            courante, l_cour = [], 0.0
        l_cour += (esp if courante else 0) + lm
        courante.append((i, m))
    if courante:
        lignes.append(courante)
    return lignes


# ---------------------------------------------------------------- lecture du .kxml
class Tache:
    def __init__(self, el, prof):
        g = lambda k: (el.findtext(k) or "").strip()
        self.num = g("task-numero")
        self.nom = g("task-name")
        self.exe = g("task-executant") or "UNKNOWN"
        self.dec = g("task-decomposition")
        self.opt = g("task-optional") == "true"
        self.inter = g("task-interruptible") == "true"
        self.it = g("task-iteration")
        self.pre = g("task-precondition")
        self.obs = g("task-observation")
        self.prof = prof
        self.enfants = [Tache(c, prof + 1) for c in el.findall("task")]
        self.badges = []
        self.groupe = False

    @property
    def feuille(self):
        return not self.enfants

    @property
    def pile(self):  # toutes les sous-tâches sont élémentaires -> empilées sous la tâche mère
        return bool(self.enfants) and all(e.feuille for e in self.enfants)

    def parcours(self):
        yield self
        for e in self.enfants:
            yield from e.parcours()


racine_xml = ET.parse(SOURCE).getroot()
racines = [Tache(t, 0) for t in racine_xml.findall("task")]
racine = racines[0]

# notes : préconditions (P) et observations (N)
notes = []
np_, nn = 0, 0
for t in racine.parcours():
    if t.pre and t.pre.lower() != "true":
        np_ += 1
        t.badges.append(("P", np_))
        notes.append((f"P{np_}", t.num, "Précondition", t.pre))
    if t.obs:
        nn += 1
        t.badges.append(("N", nn))
        notes.append((f"N{nn}", t.num, "Observation", t.obs))


class Groupe(Tache):
    """Pseudo-tâche sans boîte : suite de sous-tâches élémentaires consécutives, empilées pour gagner de la place."""
    def __init__(self, enfants, prof):
        self.num, self.nom, self.exe, self.dec = "", "", "ABS", ""
        self.opt = self.inter = False
        self.it, self.pre, self.obs = "[1]", "true", ""
        self.prof, self.enfants, self.badges, self.groupe = prof, enfants, [], True


def grouper(t):
    """Dans une tâche à sous-tâches mixtes, les suites d'au moins 2 feuilles consécutives forment une pile."""
    for e in t.enfants:
        grouper(e)
    if t.feuille or t.pile:
        return
    nouveaux, suite = [], []
    for e in t.enfants + [None]:
        if e is not None and e.feuille:
            suite.append(e)
            continue
        if len(suite) >= 2:
            nouveaux.append(Groupe(suite, t.prof + 1))
        else:
            nouveaux.extend(suite)
        suite = []
        if e is not None:
            nouveaux.append(e)
    t.enfants = nouveaux


grouper(racine)


def colonnes(t):
    if t.feuille or t.pile:
        return 1
    return sum(colonnes(e) for e in t.enfants)


NB_COL = colonnes(racine)


def taches_par_colonne(t, out):
    """Liste ordonnée des colonnes ; chaque colonne = (tâche, empilée ?) des boîtes qui l'occupent seules."""
    if t.feuille:
        out.append([(t, False)])
    elif t.pile:
        out.append([(t, False)] + [(e, True) for e in t.enfants])
    else:
        for e in t.enfants:
            taches_par_colonne(e, out)
    return out


COLONNES = taches_par_colonne(racine, [])


def mots_de(t):
    return ([t.num] if t.num and t.num.lower() != "racine" else []) + t.nom.split()


# ---------------------------------------------------------------- mise en page pour une taille de police donnée
def mise_en_page(fs_pt, k_gap=2.6):
    fs = fs_pt * PT
    lh = fs * 1.18
    pad = fs * 0.45
    ecart_col = 1.0
    larg_utile = PAGE_L - 2 * MARGE
    retrait = 2.2
    # largeur minimale de chaque colonne : le mot le plus long doit tenir sans déborder
    mini = []
    for col in COLONNES:
        m = 0.0
        for t, empilee in col:
            for i, mot in enumerate(mots_de(t)):
                pol = ARIAL_B if i == 0 else ARIAL
                lm = pol.largeur(mot, fs)
                if i > 0:   # les mots longs peuvent être coupés (trait d'union) au-delà de ~9 caractères
                    lm = min(lm, ARIAL.largeur("d'hébergement", fs))
                m = max(m, lm + 2 * pad + 0.4 + (retrait if empilee else 0))
        mini.append(max(m, 10.0))
    reste = larg_utile - (NB_COL - 1) * ecart_col - sum(mini)
    if reste < 0:
        return None
    LC = [m + reste / NB_COL for m in mini]          # largeur de chaque colonne
    XC = [MARGE + sum(LC[:i]) + i * ecart_col for i in range(NB_COL)]
    W = min(LC)
    gap_op = fs * k_gap       # espace vertical entre une tâche et le niveau suivant (porte l'opérateur)
    gap_pile = fs * 0.55
    boites = {}

    def taille_boite(t, largeur):
        if t.groupe:
            return [], 0.0, False
        mots = ([t.num] if t.num and t.num.lower() != "racine" else []) + t.nom.split()
        gras = bool(mots) and mots[0] == t.num
        lignes = couper(mots, largeur - 2 * pad - (fs * 1.6 if t.badges else 0) * 0, fs, gras)
        h = 2 * pad + len(lignes) * lh
        return lignes, h, gras

    def placer_x(t, c0):
        span = colonnes(t)
        x0 = XC[c0]
        largeur_span = XC[c0 + span - 1] + LC[c0 + span - 1] - x0
        if t.feuille or t.pile:
            larg = largeur_span
        else:
            larg = min(largeur_span, max(largeur_span * 0.6, 46.0))
        cx = x0 + largeur_span / 2
        lignes, h, gras = taille_boite(t, larg)
        boites[id(t)] = dict(t=t, x=cx - larg / 2, w=larg, h=h, lignes=lignes, gras=gras, x0=x0)
        if t.pile:
            for e in t.enfants:
                l2, h2, g2 = taille_boite(e, larg - retrait)
                boites[id(e)] = dict(t=e, x=x0 + retrait, w=larg - retrait, h=h2, lignes=l2, gras=g2, x0=x0)
        elif not t.feuille:
            c = c0
            for e in t.enfants:
                placer_x(e, c)
                c += colonnes(e)

    placer_x(racine, 0)

    # hauteurs de niveau : seules les tâches « horizontales » imposent la hauteur d'un niveau
    hmax = {}
    def niveaux(t):
        b = boites[id(t)]
        hmax[t.prof] = max(hmax.get(t.prof, 0), b["h"])
        if not t.pile:
            for e in t.enfants:
                niveaux(e)
    niveaux(racine)
    haut = MARGE + 7.5  # titre
    Y = {0: haut}
    for d in range(1, max(hmax) + 2):
        Y[d] = Y[d - 1] + hmax.get(d - 1, 0) + gap_op

    bas = 0
    def placer_y(t):
        nonlocal bas
        b = boites[id(t)]
        b["y"] = Y[t.prof]
        bas = max(bas, b["y"] + b["h"])
        if t.pile:
            y = b["y"] + (0 if t.groupe else b["h"] + fs * 1.9)
            for e in t.enfants:
                be = boites[id(e)]
                be["y"] = y
                y += be["h"] + gap_pile
                bas = max(bas, be["y"] + be["h"])
        else:
            for e in t.enfants:
                placer_y(e)
    placer_y(racine)

    # notes en bas de page, sur 3 colonnes
    fs_n = fs * 0.92
    lh_n = fs_n * 1.2
    ncol = 3
    larg_n = (larg_utile - (ncol - 1) * 4) / ncol
    blocs = []
    for code, num, genre, texte in notes:
        mots = [f"{code}"] + f"({num}) {texte}".split()
        lignes = couper(mots, larg_n, fs_n, True)
        blocs.append((lignes, len(lignes) * lh_n + fs_n * 0.35))
    # répartition équilibrée en colonnes (ordre conservé)
    total = sum(h for _, h in blocs)
    cols_notes, cour, hc = [[]], 0, 0
    for bl in blocs:
        if hc + bl[1] > total / ncol + 0.1 and len(cols_notes) < ncol and cols_notes[-1]:
            cols_notes.append([])
            hc = 0
        cols_notes[-1].append(bl)
        hc += bl[1]
    h_notes = max(sum(h for _, h in c) for c in cols_notes) + fs_n * 1.6
    h_legende = 5.0
    hauteur_totale = bas + 3 + h_notes + h_legende + MARGE
    return dict(fs=fs, lh=lh, pad=pad, W=W, retrait=retrait, boites=boites, bas=bas, gap_op=gap_op,
                fs_n=fs_n, lh_n=lh_n, larg_n=larg_n, cols_notes=cols_notes, h_notes=h_notes,
                hauteur=hauteur_totale, Y=Y)


# plus grande police qui tient sur la page
fs_pt = 10.0
while True:
    L = mise_en_page(fs_pt)
    if (L is not None and L["hauteur"] <= PAGE_H) or fs_pt <= 4.0:
        break
    fs_pt -= 0.1
# la largeur limite la police : on espace ensuite les niveaux pour occuper toute la hauteur de la page
k_gap = 2.6
while k_gap < 6.0:
    L2 = mise_en_page(fs_pt, k_gap + 0.1)
    if L2 is None or L2["hauteur"] > PAGE_H - 1:
        break
    k_gap += 0.1
    L = L2


# ---------------------------------------------------------------- dessin SVG
out = []
a = out.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{PAGE_L}mm" height="{PAGE_H}mm" '
  f'viewBox="0 0 {PAGE_L} {PAGE_H}" font-family="Arial, Helvetica, sans-serif">')
a('<rect x="0" y="0" width="297" height="210" fill="#ffffff"/>')
fs, lh, pad = L["fs"], L["lh"], L["pad"]
B = L["boites"]
TRAIT = 'stroke="#444" stroke-width="0.22" fill="none"'


def f(v):
    return f"{v:.2f}"


def operateur(x, y, texte, ancre="middle"):
    larg = ARIAL_B.largeur(texte, fs * 0.85) + 1.0
    rx = x - larg / 2 if ancre == "middle" else x - 0.5
    a(f'<rect x="{f(rx)}" y="{f(y - fs * 0.62)}" width="{f(larg)}" height="{f(fs * 1.05)}" rx="0.6" fill="#ffffff" stroke="#c62828" stroke-width="0.18"/>')
    a(f'<text x="{f(rx + larg / 2)}" y="{f(y + fs * 0.24)}" font-size="{f(fs * 0.85)}" font-weight="bold" fill="#c62828" text-anchor="middle">{escape(texte)}</text>')


# liens
for b in B.values():
    t = b["t"]
    if t.feuille:
        continue
    bas_p = b["y"] + b["h"]
    op = OPERATEURS.get(t.dec, t.dec)
    if t.pile:
        xl = b["x0"] + L["retrait"] / 2
        dernier = B[id(t.enfants[-1])]
        a(f'<path d="M{f(xl)},{f(bas_p)} V{f(dernier["y"] + dernier["h"] / 2)}" {TRAIT}/>')
        for e in t.enfants:
            be = B[id(e)]
            a(f'<path d="M{f(xl)},{f(be["y"] + be["h"] / 2)} H{f(be["x"])}" {TRAIT}/>')
        if not t.groupe:
            operateur(xl + 1.6, bas_p + fs * 0.95, op, ancre="start")
    else:
        cx = b["x"] + b["w"] / 2
        ybus = L["Y"][t.prof + 1] - L["gap_op"] * 0.30
        centres = [B[id(e)]["x0"] + L["retrait"] / 2 if e.groupe else B[id(e)]["x"] + B[id(e)]["w"] / 2
                   for e in t.enfants]
        a(f'<path d="M{f(cx)},{f(bas_p)} V{f(ybus)}" {TRAIT}/>')
        a(f'<path d="M{f(min(centres))},{f(ybus)} H{f(max(centres))}" {TRAIT}/>')
        for e, c in zip(t.enfants, centres):
            a(f'<path d="M{f(c)},{f(ybus)} V{f(B[id(e)]["y"])}" {TRAIT}/>')
        operateur(cx, bas_p + (ybus - bas_p) * 0.5, op)

# boîtes
for b in B.values():
    t = b["t"]
    if t.groupe:
        continue
    fond, bord, _ = COULEURS.get(t.exe, COULEURS["UNKNOWN"])
    tiret = ' stroke-dasharray="1.1,0.6"' if t.opt else ""
    epais = 0.45 if t.prof == 0 else 0.28
    a(f'<rect x="{f(b["x"])}" y="{f(b["y"])}" width="{f(b["w"])}" height="{f(b["h"])}" rx="1" '
      f'fill="{fond}" stroke="{bord}" stroke-width="{epais}"{tiret}/>')
    y = b["y"] + pad + fs * 0.86
    for ligne in b["lignes"]:
        largeur_ligne = sum((ARIAL_B if (i == 0 and b["gras"]) else ARIAL).largeur(m, fs) for i, m in ligne) \
            + ARIAL.largeur(" ", fs) * (len(ligne) - 1)
        x = b["x"] + b["w"] / 2 - largeur_ligne / 2
        morceaux = []
        for k, (i, m) in enumerate(ligne):
            sep = " " if k else ""
            if i == 0 and b["gras"]:
                morceaux.append(f'{sep}<tspan font-weight="bold" fill="#333">{escape(m)}</tspan>')
            else:
                morceaux.append(escape(sep + m))
        a(f'<text x="{f(x)}" y="{f(y)}" font-size="{f(fs)}" fill="#111" xml:space="preserve">{"".join(morceaux)}</text>')
        y += lh
    # pastilles (préconditions, observations, itération, optionnelle, interruptible)
    px = b["x"] + b["w"]
    for genre, n in reversed(t.badges):
        texte = f"{genre}{n}"
        lb = ARIAL_B.largeur(texte, fs * 0.72) + 0.9
        px -= lb + 0.3
        coul = "#c62828" if genre == "P" else "#6a1b9a"
        a(f'<rect x="{f(px)}" y="{f(b["y"] - fs * 0.55)}" width="{f(lb)}" height="{f(fs * 0.95)}" rx="0.5" fill="{coul}"/>')
        a(f'<text x="{f(px + lb / 2)}" y="{f(b["y"] + fs * 0.2)}" font-size="{f(fs * 0.72)}" font-weight="bold" fill="#fff" text-anchor="middle">{texte}</text>')
    extras = []
    if t.it and t.it not in ("[1]", "1"):
        extras.append(f"↻ {t.it}")
    if t.inter:
        extras.append("interruptible")
    if extras:
        texte = " · ".join(extras)
        a(f'<text x="{f(b["x"] + b["w"] - 0.6)}" y="{f(b["y"] + b["h"] + fs * 0.8)}" font-size="{f(fs * 0.7)}" fill="#6a1b9a" text-anchor="end">{escape(texte)}</text>')

# titre
a(f'<text x="{MARGE}" y="{MARGE + 3.2}" font-size="4.2" font-weight="bold" fill="#111">Modèle de tâches K-MADe – {escape(racine.nom)}</text>')
a(f'<text x="{PAGE_L - MARGE}" y="{MARGE + 3.2}" font-size="2.6" fill="#555" text-anchor="end">FestiBed – Groupe 3 – source : {escape(SOURCE.name)}</text>')

# notes
yn = L["bas"] + 3
a(f'<line x1="{MARGE}" y1="{f(yn)}" x2="{PAGE_L - MARGE}" y2="{f(yn)}" stroke="#bbb" stroke-width="0.2"/>')
fs_n, lh_n = L["fs_n"], L["lh_n"]
a(f'<text x="{MARGE}" y="{f(yn + fs_n * 1.15)}" font-size="{f(fs_n)}" font-weight="bold" fill="#333">Préconditions (P) et observations (N)</text>')
for ci, col in enumerate(L["cols_notes"]):
    x = MARGE + ci * (L["larg_n"] + 4)
    y = yn + fs_n * 1.15 + lh_n * 1.05
    for lignes, h in col:
        for li, ligne in enumerate(lignes):
            morceaux = []
            for k, (i, m) in enumerate(ligne):
                sep = " " if k else ""
                if i == 0:
                    coul = "#c62828" if m.startswith("P") else "#6a1b9a"
                    morceaux.append(f'<tspan font-weight="bold" fill="{coul}">{escape(m)}</tspan>')
                else:
                    morceaux.append(escape(sep + m))
            a(f'<text x="{f(x + (0 if li == 0 else 2.2))}" y="{f(y)}" font-size="{f(fs_n)}" fill="#222" xml:space="preserve">{"".join(morceaux)}</text>')
            y += lh_n
        y += fs_n * 0.35

# légende
yl = PAGE_H - MARGE - 0.6
x = MARGE
a(f'<text x="{f(x)}" y="{f(yl)}" font-size="2.3" font-weight="bold" fill="#333">Exécutant :</text>')
x += 13
for cle in ("ABS", "USER", "INT", "SYS"):
    fond, bord, lib = COULEURS[cle]
    a(f'<rect x="{f(x)}" y="{f(yl - 2.1)}" width="5" height="2.6" rx="0.5" fill="{fond}" stroke="{bord}" stroke-width="0.28"/>')
    a(f'<text x="{f(x + 6)}" y="{f(yl)}" font-size="2.3" fill="#333">{lib}</text>')
    x += 7 + ARIAL.largeur(lib, 2.3) + 3
a(f'<rect x="{f(x)}" y="{f(yl - 2.1)}" width="5" height="2.6" rx="0.5" fill="#fff" stroke="#607d8b" stroke-width="0.28" stroke-dasharray="1.1,0.6"/>')
a(f'<text x="{f(x + 6)}" y="{f(yl)}" font-size="2.3" fill="#333">Tâche optionnelle</text>')
x += 7 + ARIAL.largeur("Tâche optionnelle", 2.3) + 4
operateur(x + 3.5, yl - 0.8, "SEQ")
a(f'<text x="{f(x + 7.5)}" y="{f(yl)}" font-size="2.3" fill="#333">séquentiel  </text>')
x += 7.5 + ARIAL.largeur("séquentiel", 2.3) + 3
operateur(x + 3.5, yl - 0.8, "ALT")
a(f'<text x="{f(x + 7.5)}" y="{f(yl)}" font-size="2.3" fill="#333">alternatif</text>')
x += 7.5 + ARIAL.largeur("alternatif", 2.3) + 4
a(f'<text x="{f(x)}" y="{f(yl)}" font-size="2.3" fill="#555">Sous-tâches empilées : même opérateur que la tâche mère, ordre de haut en bas.</text>')
a("</svg>")

SORTIE.write_text("\n".join(out), encoding="utf-8")
print(f"{SORTIE.name} : {NB_COL} colonnes, police {fs_pt:.1f} pt, {len(notes)} notes, hauteur utile {L['hauteur']:.1f} mm")

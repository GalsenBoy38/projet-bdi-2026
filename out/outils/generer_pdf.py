"""Assemble out/attentes.pdf : modèles (generer_modeles.py) + diagrammes PlantUML (SVG) + gabarit HTML,
puis impression PDF par Chrome/Edge headless.

Usage : python generer_pdf.py [chemin_plantuml.jar]
"""
import glob, html, os, re, subprocess, sys

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(OUT, "outils")
BUILD = os.path.join(TOOLS, "build")

subprocess.run([sys.executable, os.path.join(TOOLS, "generer_modeles.py")], check=True)

jar = sys.argv[1] if len(sys.argv) > 1 else (glob.glob(os.path.expanduser(
    "~/.m2/repository/net/sourceforge/plantuml/plantuml/*/plantuml-*.jar")) or [None])[-1]
if not jar:
    sys.exit("plantuml.jar introuvable : passer son chemin en argument")
pumls = sorted(glob.glob(os.path.join(OUT, "plantuml", "*.puml")))
for fmt in ("-tsvg", "-tpng"):
    subprocess.run(["java", "-jar", jar, fmt, "-o", os.path.join(OUT, "diagrammes")] + pumls, check=True)

def frag(name):
    return open(os.path.join(BUILD, name), encoding="utf-8").read()

sql = open(os.path.join(OUT, "sql", "mpd_oracle.sql"), encoding="utf-8").read()
extrait = "\n".join(re.search(r"CREATE TABLE %s \(.*?\n\);" % t, sql, re.S).group(0) for t in ("ETABLISSEMENT", "NUITEE"))

page = open(os.path.join(TOOLS, "attentes_template.html"), encoding="utf-8").read()
diag_url = "file:///" + os.path.join(OUT, "diagrammes").replace("\\", "/") + "/"
page = (page.replace("DIAG/", diag_url)
            .replace("{{MLD_SOURCES}}", frag("mld_sources.html"))
            .replace("{{MLD_GLOBAL}}", frag("mld_global.html"))
            .replace("{{DICO}}", frag("dictionnaire.html"))
            .replace("{{CI2}}", frag("ci_merise2.html"))
            .replace("{{INDEX}}", frag("index.html"))
            .replace("{{MPD_EXTRAIT}}", html.escape(extrait)))
assert "{{" not in page, "marqueur non remplacé"
built = os.path.join(BUILD, "attentes.html")
open(built, "w", encoding="utf-8").write(page)

browsers = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            "google-chrome", "chromium", "msedge"]
browser = next((b for b in browsers if os.path.exists(b)), browsers[-1])
pdf = os.path.join(OUT, "attentes.pdf")
subprocess.run([browser, "--headless=new", "--disable-gpu", "--allow-file-access-from-files",
                "--no-pdf-header-footer", f"--print-to-pdf={pdf}", "file:///" + built.replace("\\", "/")],
               check=True, stderr=subprocess.DEVNULL)
print("PDF écrit :", pdf)

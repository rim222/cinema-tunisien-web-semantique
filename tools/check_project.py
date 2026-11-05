"""Vérifie automatiquement tous les endpoints.  Lancer : python tools/check_project.py
(nécessite : pip install -r requirements.txt)"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402

c = TestClient(app, raise_server_exceptions=False)
ok = True


def check(nom, condition, detail=""):
    global ok
    ok &= bool(condition)
    print(("OK   " if condition else "ECHEC"), nom, "" if condition else f"-> {detail}")


r = c.get("/films");                       check("/films = 30 films", r.status_code == 200 and len(r.json()) == 30, r.text[:200])
r = c.get("/films?inference=false");       check("/films sans inférence = 28", r.status_code == 200 and len(r.json()) == 28, r.text[:200])
r = c.get("/films?genre=Drame&annee_min=1990&annee_max=1999")
check("/films filtres (drames 1990-1999)", r.status_code == 200 and 0 < len(r.json()) < 30, r.text[:200])
r = c.get("/films?annee_min=2000&annee_max=1990"); check("/films intervalle invalide = 400", r.status_code == 400, r.text[:200])
r = c.get("/films/hedi")
check("/films/hedi", r.status_code == 200 and r.json()["titre"] == "Hedi" and r.json()["festivals"], r.text[:300])
r = c.get("/films/inconnu");               check("/films/inconnu = 404", r.status_code == 404, r.text[:200])
r = c.get("/realisateurs")
check("/realisateurs = 19, Bouzid en tête", r.status_code == 200 and len(r.json()) == 19 and r.json()[0]["nom"] == "Nouri Bouzid", r.text[:300])
r = c.get("/realisateurs?inference=false"); check("/realisateurs sans inférence = vide", r.status_code == 200 and r.json() == [], r.text[:200])
r = c.get("/realisateurs/ferid_boughedir/films")
check("/realisateurs/ferid_boughedir/films = 3", r.status_code == 200 and r.json()["nb_films"] == 3, r.text[:300])
r = c.get("/realisateurs/inconnu/films");  check("réalisateur inconnu = 404", r.status_code == 404, r.text[:200])
r = c.get("/festivals");                   check("/festivals = 7", r.status_code == 200 and len(r.json()) == 7, r.text[:200])
r = c.get("/festivals?festival=Venise");   check("/festivals?festival=Venise = 4", r.status_code == 200 and len(r.json()) == 4, r.text[:200])
r = c.get("/stats/decennies");             check("/stats/decennies", r.status_code == 200 and sum(x["nb_films"] for x in r.json()) == 28, r.text[:300])
r = c.get("/inference/comparaison")
if r.status_code == 200:
    print("     détail :", {m["mesure"]: (m["sans_inference"], m["avec_inference"]) for m in r.json()["comparaison"]})
check("/inference/comparaison", r.status_code == 200, r.text[:300])

print("\nTOUT EST OK" if ok else "\nDES ECHECS : envoyez-moi cette sortie")
sys.exit(0 if ok else 1)

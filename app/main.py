"""API REST – Cinéma tunisien (RDF + RDFS + SPARQL).
Lancer :  uvicorn app.main:app --reload
Swagger : http://127.0.0.1:8000/docs
"""
from decimal import Decimal
from pathlib import Path
from typing import List, Optional

import owlrl
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi import Path as PathParam
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel
from rdflib import Graph, Literal, URIRef

DATA = Path(__file__).resolve().parent.parent / "data"
CTN = "http://example.org/cinematn#"

PREFIXES = f"""
PREFIX ctn:  <{CTN}>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
"""

# ------------------------------------------------------------------ graphes
g_base = Graph()  # SANS inférence : données + schéma tels quels
g_base.parse(DATA / "ontology.ttl", format="turtle")
g_base.parse(DATA / "films.ttl", format="turtle")

g_inf = Graph()  # AVEC inférence RDFS (fermeture déductive)
for triple in g_base:
    g_inf.add(triple)
owlrl.DeductiveClosure(
    owlrl.RDFS_Semantics, axiomatic_triples=False, datatype_axioms=False
).expand(g_inf)


# ------------------------------------------------------------------ outils
def _py(value):
    if isinstance(value, Literal):
        v = value.toPython()
        if isinstance(v, Decimal) and v == v.to_integral_value():
            return int(v)
        return v if isinstance(v, (int, float, bool)) else str(v)
    return str(value).split("#")[-1]  # URI -> identifiant local


def run(query: str, inference: bool = True, bindings: Optional[dict] = None) -> List[dict]:
    graph = g_inf if inference else g_base
    result = graph.query(PREFIXES + query, initBindings=bindings or {})
    return [{k: _py(v) for k, v in row.asdict().items()} for row in result]


ID_PATTERN = r"^[A-Za-z0-9_]+$"  # empêche toute injection dans les URI

# ------------------------------------------------------------------ modèles
class FilmResume(BaseModel):
    id: str
    titre: str
    annee: int
    genres: List[str]
    realisateurs: List[str]


class Selection(BaseModel):
    film: str
    titre: str
    annee: int
    festival: str
    edition: int
    section: str


app = FastAPI(
    title="API Cinéma tunisien",
    description=(
        "30 films tunisiens (1975-2020) modélisés en RDF/RDFS, interrogés en SPARQL "
        "avec rdflib. Le paramètre `inference` permet de comparer les résultats "
        "**sans** et **avec** inférence RDFS."
    ),
    version="1.0.0",
)


@app.exception_handler(Exception)
async def erreur_generique(_: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"erreur": "Erreur interne", "detail": str(exc)})


@app.get("/", include_in_schema=False)
def accueil():
    return RedirectResponse("/docs")


INFERENCE_Q = Query(True, description="true = graphe avec inférence RDFS, false = graphe brut")

# ------------------------------------------------------------------ 1. films
@app.get("/films", response_model=List[FilmResume], tags=["Films"], summary="Lister / filtrer les films")
def lister_films(
    genre: Optional[str] = Query(None, pattern=ID_PATTERN, description="Drame, Comedie, Fantastique"),
    realisateur: Optional[str] = Query(None, pattern=ID_PATTERN, description="ex : nouri_bouzid"),
    annee_min: Optional[int] = Query(None, ge=1900, le=2100),
    annee_max: Optional[int] = Query(None, ge=1900, le=2100),
    q: Optional[str] = Query(None, min_length=2, description="Recherche dans le titre"),
    inference: bool = INFERENCE_Q,
):
    if annee_min and annee_max and annee_min > annee_max:
        raise HTTPException(400, "annee_min doit être inférieure ou égale à annee_max")
    motifs, filtres = "", ""
    if genre:
        motifs += f"?film ctn:aPourGenre ctn:{genre} .\n"
    if realisateur:
        motifs += f"?film ctn:estRealisePar ctn:{realisateur} .\n"
    if annee_min:
        filtres += f"FILTER(?annee >= {int(annee_min)})\n"
    if annee_max:
        filtres += f"FILTER(?annee <= {int(annee_max)})\n"
    rows = run(
        f"""
        SELECT ?film ?titre ?annee
        WHERE {{
          ?film a ctn:Film ; ctn:titre ?titre ; ctn:anneeSortie ?annee .
          {motifs}
          {filtres}
        }}
        ORDER BY ?annee ?titre
        """,
        inference,
    )
    genres, reals = {}, {}
    for r in run("SELECT ?film ?gl WHERE { ?film ctn:aPourGenre ?g . ?g rdfs:label ?gl } ORDER BY ?gl", inference):
        genres.setdefault(r["film"], []).append(r["gl"])
    for r in run("SELECT ?film ?nom WHERE { ?film ctn:estRealisePar ?r . ?r ctn:nomCineaste ?nom } ORDER BY ?nom", inference):
        reals.setdefault(r["film"], []).append(r["nom"])
    films = [
        {"id": r["film"], "titre": r["titre"], "annee": r["annee"],
         "genres": genres.get(r["film"], []), "realisateurs": reals.get(r["film"], [])}
        for r in rows
    ]
    if q:
        films = [f for f in films if q.lower() in f["titre"].lower()]
    return films


# ------------------------------------------------------------------ 2. détail
@app.get("/films/{film_id}", tags=["Films"], summary="Détail d'un film")
def detail_film(
    film_id: str = PathParam(..., pattern=ID_PATTERN, description="ex : hedi"),
    inference: bool = INFERENCE_Q,
):
    b = {"film": URIRef(CTN + film_id)}
    base = run("SELECT ?titre ?annee WHERE { ?film ctn:titre ?titre ; ctn:anneeSortie ?annee }", inference, b)
    if not base:
        raise HTTPException(404, f"Film '{film_id}' introuvable")
    genres = run("SELECT ?g ?l WHERE { ?film ctn:aPourGenre ?g . ?g rdfs:label ?l }", inference, b)
    reals = run("SELECT ?r ?nom WHERE { ?film ctn:estRealisePar ?r . ?r ctn:nomCineaste ?nom }", inference, b)
    fests = run(
        """SELECT ?festival ?edition ?section
           WHERE { ?film ctn:selectionneAu ?f . ?f rdfs:label ?festival ; ctn:edition ?edition ; ctn:section ?section }""",
        inference, b)
    types = run('SELECT ?t WHERE { ?film a ?t . FILTER(STRSTARTS(STR(?t), "http://example.org/cinematn#")) }', inference, b)
    return {
        "id": film_id, "titre": base[0]["titre"], "annee": base[0]["annee"],
        "types": sorted(t["t"] for t in types),
        "genres": [g["l"] for g in genres],
        "realisateurs": [{"id": r["r"], "nom": r["nom"]} for r in reals],
        "festivals": fests,
    }


# ------------------------------------------------------------------ 3. réalisateurs
@app.get("/realisateurs", tags=["Réalisateurs"], summary="Réalisateurs et nombre de films")
def lister_realisateurs(inference: bool = INFERENCE_Q):
    """Utilise `ctn:aPourCineaste` : sans inférence la liste est vide
    (seule la sous-propriété `ctn:estRealisePar` est présente dans les données)."""
    return run(
        """SELECT ?id ?nom (COUNT(DISTINCT ?film) AS ?nb_films)
           WHERE { ?film ctn:aPourCineaste ?id . ?id ctn:nomCineaste ?nom }
           GROUP BY ?id ?nom ORDER BY DESC(?nb_films) ?nom""",
        inference,
    )


# ------------------------------------------------------------------ 4. films d'un réalisateur
@app.get("/realisateurs/{realisateur_id}/films", tags=["Réalisateurs"], summary="Filmographie d'un réalisateur")
def films_du_realisateur(
    realisateur_id: str = PathParam(..., pattern=ID_PATTERN, description="ex : ferid_boughedir"),
    inference: bool = INFERENCE_Q,
):
    b = {"r": URIRef(CTN + realisateur_id)}
    nom = run("SELECT ?nom WHERE { ?r ctn:nomCineaste ?nom }", inference, b)
    if not nom:
        raise HTTPException(404, f"Réalisateur '{realisateur_id}' introuvable")
    films = run(
        """SELECT ?id ?titre ?annee
           WHERE { ?id ctn:estRealisePar ?r ; ctn:titre ?titre ; ctn:anneeSortie ?annee }
           ORDER BY ?annee""",
        inference, b)
    return {"id": realisateur_id, "nom": nom[0]["nom"], "nb_films": len(films), "films": films}


# ------------------------------------------------------------------ 5. festivals
@app.get("/festivals", response_model=List[Selection], tags=["Festivals"], summary="Sélections en festival")
def selections_festivals(
    festival: Optional[str] = Query(None, min_length=3, description="ex : Cannes, Venise, Berlinale"),
    inference: bool = INFERENCE_Q,
):
    rows = run(
        """SELECT ?film ?titre ?annee ?festival ?edition ?section
           WHERE { ?film ctn:selectionneAu ?f ; ctn:titre ?titre ; ctn:anneeSortie ?annee .
                   ?f rdfs:label ?festival ; ctn:edition ?edition ; ctn:section ?section }
           ORDER BY ?edition ?titre""",
        inference,
    )
    if festival:
        rows = [r for r in rows if festival.lower() in r["festival"].lower()]
    return rows


# ------------------------------------------------------------------ 6. statistiques par décennie
@app.get("/stats/decennies", tags=["Statistiques"], summary="Nombre de films par décennie")
def stats_decennies(inference: bool = INFERENCE_Q):
    return run(
        """SELECT ?decennie (COUNT(?film) AS ?nb_films)
           WHERE { ?film a ctn:Film ; ctn:anneeSortie ?a .
                   BIND(FLOOR(?a / 10) * 10 AS ?decennie) }
           GROUP BY ?decennie ORDER BY ?decennie""",
        inference,
    )


# ------------------------------------------------------------------ 7. comparaison sans / avec inférence
@app.get("/inference/comparaison", tags=["Inférence"], summary="Comparer résultats sans et avec inférence")
def comparer_inference():
    mesures = {
        "nb_films (a ctn:Film)": "SELECT (COUNT(DISTINCT ?x) AS ?n) WHERE { ?x a ctn:Film }",
        "nb_cineastes (a ctn:Cineaste)": "SELECT (COUNT(DISTINCT ?x) AS ?n) WHERE { ?x a ctn:Cineaste }",
        "nb_realisateurs (a ctn:Realisateur)": "SELECT (COUNT(DISTINCT ?x) AS ?n) WHERE { ?x a ctn:Realisateur }",
        "nb_personnes (a foaf:Person)": "SELECT (COUNT(DISTINCT ?x) AS ?n) WHERE { ?x a foaf:Person }",
        "nb_liens ctn:aPourCineaste": "SELECT (COUNT(*) AS ?n) WHERE { ?f ctn:aPourCineaste ?c }",
        "nb_noms foaf:name": "SELECT (COUNT(*) AS ?n) WHERE { ?p foaf:name ?n2 }",
    }
    comparaison = [
        {"mesure": nom,
         "sans_inference": run(req, False)[0]["n"],
         "avec_inference": run(req, True)[0]["n"]}
        for nom, req in mesures.items()
    ]
    return {
        "triplets_sans_inference": len(g_base),
        "triplets_avec_inference": len(g_inf),
        "comparaison": comparaison,
    }

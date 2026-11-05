# Cinéma tunisien – RDF / RDFS / SPARQL / API REST (Swagger)

30 films tunisiens réels (1975-2020), 19 réalisateurs, 7 sélections en festival.

## Sources des données
- **Titres et années** : Wikipédia, « List of Tunisian films » – https://en.wikipedia.org/wiki/List_of_Tunisian_films
- **Réalisateurs** : pages Wikipédia des films et des cinéastes (Nouri Bouzid, Férid Boughedir, Moufida Tlatli, Kaouther Ben Hania, etc.)
- **Sélections en festival** : programmes officiels (Cannes, Mostra de Venise, Berlinale), recoupés avec Wikipédia
- **À faire avant la soutenance** : recouper chaque film sur Wikidata (https://query.wikidata.org) ou IMDb et ajuster `tools/gen_data.py` si une valeur diffère.

## Lancer le projet
```bash
pip install -r requirements.txt
python tools/gen_data.py          # (re)génère data/ontology.ttl et data/films.ttl
python tools/check_project.py     # teste automatiquement tous les endpoints
uvicorn app.main:app --reload     # API
```
Swagger : http://127.0.0.1:8000/docs

## Exemples
- `/films?genre=Drame&annee_min=1990&annee_max=1999`
- `/films/hedi` · `/realisateurs` · `/realisateurs/ferid_boughedir/films`
- `/festivals?festival=Venise` · `/stats/decennies`
- `/inference/comparaison` (sans / avec inférence)
- Ajouter `?inference=false` pour interroger le graphe brut.

## Structure
`data/` ontologie et données Turtle · `queries/queries.md` 7 requêtes SPARQL · `app/main.py` API · `tools/check_project.py` test automatique · `docs/` schéma et présentation.

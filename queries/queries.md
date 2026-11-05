# Requêtes SPARQL – Cinéma tunisien

Préfixes communs :
```sparql
PREFIX ctn:  <http://example.org/cinematn#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
```

## Q1 – Films triés par année (simple)  →  GET /films
```sparql
SELECT ?titre ?annee WHERE { ?f a ctn:Film ; ctn:titre ?titre ; ctn:anneeSortie ?annee } ORDER BY ?annee
```

## Q2 – Dramas des années 1990 (filtre)  →  GET /films?genre=Drame&annee_min=1990&annee_max=1999
```sparql
SELECT ?titre ?annee WHERE {
  ?f a ctn:Film ; ctn:titre ?titre ; ctn:anneeSortie ?annee ; ctn:aPourGenre ctn:Drame .
  FILTER(?annee >= 1990 && ?annee <= 1999) } ORDER BY ?annee
```

## Q3 – Réalisateurs classés par nombre de films (agrégation, nécessite l'inférence)  →  GET /realisateurs
```sparql
SELECT ?nom (COUNT(DISTINCT ?f) AS ?nb_films) WHERE {
  ?f ctn:aPourCineaste ?r . ?r ctn:nomCineaste ?nom }
GROUP BY ?nom ORDER BY DESC(?nb_films) ?nom
```

## Q4 – Films sélectionnés en festival (jointure à 2 niveaux)  →  GET /festivals
```sparql
SELECT ?titre ?festival ?edition ?section WHERE {
  ?f ctn:selectionneAu ?fe ; ctn:titre ?titre .
  ?fe rdfs:label ?festival ; ctn:edition ?edition ; ctn:section ?section } ORDER BY ?edition
```

## Q5 – Nombre de films par décennie (BIND + GROUP BY)  →  GET /stats/decennies
```sparql
SELECT ?decennie (COUNT(?f) AS ?nb) WHERE {
  ?f a ctn:Film ; ctn:anneeSortie ?a . BIND(FLOOR(?a/10)*10 AS ?decennie) }
GROUP BY ?decennie ORDER BY ?decennie
```

## Q6 – Films co-réalisés (HAVING)
```sparql
SELECT ?titre (COUNT(?r) AS ?nb_realisateurs) WHERE {
  ?f ctn:titre ?titre ; ctn:estRealisePar ?r } GROUP BY ?titre HAVING (COUNT(?r) > 1)
```

## Q7 – Toutes les personnes (foaf:Person) : vide sans inférence
```sparql
SELECT ?nom WHERE { ?p a foaf:Person ; foaf:name ?nom } ORDER BY ?nom
```

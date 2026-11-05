"""Génère data/ontology.ttl et data/films.ttl (30 films tunisiens réels).
Sources : voir README.md. Lancer : python tools/gen_data.py
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data"

PREFIXES = """@prefix ctn:  <http://example.org/cinematn#> .
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
"""

ONTOLOGY = PREFIXES + """
# ---------- Classes (6 + foaf:Person réutilisée) ----------
foaf:Person a rdfs:Class .
ctn:Film          a rdfs:Class ; rdfs:label "Film"@fr .
ctn:Documentaire  a rdfs:Class ; rdfs:subClassOf ctn:Film ; rdfs:label "Documentaire"@fr .
ctn:Cineaste      a rdfs:Class ; rdfs:subClassOf foaf:Person ; rdfs:label "Cinéaste"@fr .
ctn:Realisateur   a rdfs:Class ; rdfs:subClassOf ctn:Cineaste ; rdfs:label "Réalisateur"@fr .
ctn:Genre         a rdfs:Class ; rdfs:label "Genre"@fr .
ctn:Festival      a rdfs:Class ; rdfs:label "Festival (édition et section)"@fr .

# ---------- Propriétés (9 + foaf:name réutilisée) ----------
ctn:titre         a rdf:Property ; rdfs:domain ctn:Film ; rdfs:range xsd:string .
ctn:anneeSortie   a rdf:Property ; rdfs:domain ctn:Film ; rdfs:range xsd:integer .
ctn:aPourGenre    a rdf:Property ; rdfs:domain ctn:Film ; rdfs:range ctn:Genre .
ctn:aPourCineaste a rdf:Property ; rdfs:domain ctn:Film ; rdfs:range ctn:Cineaste .
ctn:estRealisePar a rdf:Property ; rdfs:subPropertyOf ctn:aPourCineaste ;
                  rdfs:domain ctn:Film ; rdfs:range ctn:Realisateur .
ctn:selectionneAu a rdf:Property ; rdfs:domain ctn:Film ; rdfs:range ctn:Festival .
ctn:edition       a rdf:Property ; rdfs:domain ctn:Festival ; rdfs:range xsd:integer .
ctn:section       a rdf:Property ; rdfs:domain ctn:Festival ; rdfs:range xsd:string .
ctn:nomCineaste   a rdf:Property ; rdfs:subPropertyOf foaf:name ;
                  rdfs:domain ctn:Cineaste ; rdfs:range xsd:string .
"""

DIRECTORS = {
    "naceur_ktari": "Naceur Ktari", "ridha_behi": "Ridha Béhi",
    "abdellatif_ben_ammar": "Abdellatif Ben Ammar", "ferid_boughedir": "Férid Boughedir",
    "nouri_bouzid": "Nouri Bouzid", "fadhel_jaibi": "Fadhel Jaïbi",
    "fadhel_jaziri": "Fadhel Jaziri", "nejia_ben_mabrouk": "Néjia Ben Mabrouk",
    "nacer_khemir": "Nacer Khemir", "moufida_tlatli": "Moufida Tlatli",
    "mohamed_zran": "Mohamed Zran", "kalthoum_bornaz": "Kalthoum Bornaz",
    "raja_amari": "Raja Amari", "nadia_el_fani": "Nadia El Fani",
    "nejib_belkadhi": "Nejib Belkadhi", "leyla_bouzid": "Leyla Bouzid",
    "mohamed_ben_attia": "Mohamed Ben Attia", "mehdi_barsaoui": "Mehdi Barsaoui",
    "kaouther_ben_hania": "Kaouther Ben Hania",
}

GENRES = {"Drame": "Drame", "Comedie": "Comédie", "Fantastique": "Fantastique"}

# slug, titre, année, genres, réalisateurs, classe, festival
FILMS = [
    ("les_ambassadeurs", "Les Ambassadeurs", 1975, ["Drame"], ["naceur_ktari"], "Film", None),
    ("soleil_des_hyenes", "Soleil des hyènes", 1976, ["Drame"], ["ridha_behi"], "Film", None),
    ("aziza", "Aziza", 1980, ["Drame"], ["abdellatif_ben_ammar"], "Film", None),
    ("camera_dafrique", "Caméra d'Afrique", 1983, [], ["ferid_boughedir"], "Documentaire", "cannes1983_ucr"),
    ("rih_essed", "Rih Essed (L'Homme de cendres)", 1986, ["Drame"], ["nouri_bouzid"], "Film", None),
    ("arab", "Arab", 1988, ["Drame"], ["fadhel_jaibi", "fadhel_jaziri"], "Film", None),
    ("sama", "Sama", 1988, ["Drame"], ["nejia_ben_mabrouk"], "Film", None),
    ("safaih_min_dhahab", "Safaïh min dhahab (Les Sabots en or)", 1989, ["Drame"], ["nouri_bouzid"], "Film", None),
    ("halfaouine", "Halfaouine, l'enfant des terrasses", 1990, ["Drame", "Comedie"], ["ferid_boughedir"], "Film", None),
    ("collier_perdu_colombe", "Le Collier perdu de la colombe", 1991, ["Fantastique"], ["nacer_khemir"], "Film", None),
    ("bezness", "Bezness", 1992, ["Drame"], ["nouri_bouzid"], "Film", None),
    ("silences_du_palais", "Les Silences du palais", 1994, ["Drame"], ["moufida_tlatli"], "Film", None),
    ("essaida", "Essaïda", 1996, ["Drame"], ["mohamed_zran"], "Film", None),
    ("ete_a_la_goulette", "Un été à La Goulette", 1996, ["Drame", "Comedie"], ["ferid_boughedir"], "Film", None),
    ("keswa", "Keswa, le fil perdu", 1997, ["Drame"], ["kalthoum_bornaz"], "Film", None),
    ("bent_familia", "Bent Familia", 1997, ["Drame"], ["nouri_bouzid"], "Film", None),
    ("saison_des_hommes", "La Saison des hommes", 2000, ["Drame"], ["moufida_tlatli"], "Film", None),
    ("satin_rouge", "Satin rouge", 2002, ["Drame"], ["raja_amari"], "Film", None),
    ("bedwin_hacker", "Bedwin Hacker", 2003, ["Comedie"], ["nadia_el_fani"], "Film", None),
    ("bab_aziz", "Bab'Aziz", 2005, ["Fantastique"], ["nacer_khemir"], "Film", None),
    ("making_of", "Making Of", 2006, ["Drame"], ["nouri_bouzid"], "Film", None),
    ("vhs_kahloucha", "VHS Kahloucha", 2006, [], ["nejib_belkadhi"], "Documentaire", None),
    ("dowaha", "Dowaha (Secret Child)", 2009, ["Drame"], ["raja_amari"], "Film", None),
    ("bastardo", "Bastardo", 2013, ["Drame"], ["nejib_belkadhi"], "Film", None),
    ("as_i_open_my_eyes", "À peine j'ouvre les yeux", 2015, ["Drame"], ["leyla_bouzid"], "Film", "venise2015_orizzonti"),
    ("hedi", "Hedi", 2016, ["Drame"], ["mohamed_ben_attia"], "Film", "berlin2016_competition"),
    ("belle_et_la_meute", "La Belle et la Meute", 2017, ["Drame"], ["kaouther_ben_hania"], "Film", "cannes2017_ucr"),
    ("mon_cher_enfant", "Mon cher enfant", 2018, ["Drame"], ["mohamed_ben_attia"], "Film", "cannes2018_quinzaine"),
    ("un_fils", "Un fils", 2019, ["Drame"], ["mehdi_barsaoui"], "Film", "venise2019_orizzonti"),
    ("homme_qui_a_vendu_sa_peau", "L'Homme qui a vendu sa peau", 2020, ["Drame"], ["kaouther_ben_hania"], "Film", "venise2020_orizzonti"),
]

# slug: (libellé, édition, section)
FESTIVALS = {
    "cannes1983_ucr": ("Festival de Cannes", 1983, "Un Certain Regard"),
    "venise2015_orizzonti": ("Mostra de Venise", 2015, "Orizzonti"),
    "berlin2016_competition": ("Berlinale", 2016, "Compétition"),
    "cannes2017_ucr": ("Festival de Cannes", 2017, "Un Certain Regard"),
    "cannes2018_quinzaine": ("Festival de Cannes", 2018, "Quinzaine des réalisateurs"),
    "venise2019_orizzonti": ("Mostra de Venise", 2019, "Orizzonti"),
    "venise2020_orizzonti": ("Mostra de Venise", 2020, "Orizzonti"),
}


def q(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def build_data():
    out = [PREFIXES, "\n# ---------- Genres ----------"]
    for k, lab in GENRES.items():
        out.append(f"ctn:{k} a ctn:Genre ; rdfs:label {q(lab)}@fr .")
    out.append("\n# ---------- Festivals (éditions) ----------")
    for k, (lab, ed, sec) in FESTIVALS.items():
        out.append(f"ctn:{k} a ctn:Festival ; rdfs:label {q(lab)} ; ctn:edition {ed} ; ctn:section {q(sec)} .")
    out.append("\n# ---------- Cinéastes (types déduits par inférence : domain/range) ----------")
    for k, name in DIRECTORS.items():
        out.append(f"ctn:{k} ctn:nomCineaste {q(name)} .")
    out.append("\n# ---------- Films ----------")
    for slug, titre, an, genres, dirs, cls, fest in FILMS:
        parts = [f"a ctn:{cls}", f"ctn:titre {q(titre)}", f"ctn:anneeSortie {an}"]
        parts += [f"ctn:aPourGenre ctn:{g}" for g in genres]
        parts += [f"ctn:estRealisePar ctn:{d}" for d in dirs]
        if fest:
            parts.append(f"ctn:selectionneAu ctn:{fest}")
        out.append(f"ctn:{slug}\n    " + " ;\n    ".join(parts) + " .")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    (OUT / "ontology.ttl").write_text(ONTOLOGY, encoding="utf-8")
    (OUT / "films.ttl").write_text(build_data(), encoding="utf-8")
    used = {d for f in FILMS for d in f[4]}
    assert used == set(DIRECTORS), set(DIRECTORS) ^ used
    assert len(FILMS) == 30
    stats = {
        "films": len(FILMS),
        "documentaires": sum(1 for f in FILMS if f[5] == "Documentaire"),
        "films_typed_Film": sum(1 for f in FILMS if f[5] == "Film"),
        "realisateurs": len(used),
        "liens_realisation": sum(len(f[4]) for f in FILMS),
        "festivals": len(FESTIVALS),
        "selections": sum(1 for f in FILMS if f[6]),
        "annee_min": min(f[2] for f in FILMS),
        "annee_max": max(f[2] for f in FILMS),
    }
    (OUT / "stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(stats)

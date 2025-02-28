import requests
from flask import Flask, request, render_template, jsonify




import json


app = Flask(__name__)

# Fonction pour interroger l'API UniProt
def query_uniprot(query):
    url = "https://rest.uniprot.org/uniprotkb/search"
    params = {
        "query": query,
        "format": "json",

        "fields": "id,accession,gene_names,protein_name,length,xref_pdb,organism_name,xref_drugbank",
        "size":50
    }


    
    response = requests.get(url, params=params)
    
    if response.status_code == 200: # requete faite
        data= response.json()
        
        
        return data
    else:
        return {"error": "Échec de la requête à UniProt"}


# Route pour afficher la page HTML
@app.route("/")
def home():
    return render_template("index.html")

# dans index.html lorsqu'on fait fetch dans (do_Search()) on appelle cette fonction (search)
@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query", "")
    if not query:
        return jsonify({"error": "Aucune requête fournie"}), 400
    
    data = query_uniprot(query)
    with open("dump.json", "w") as json_file:
        json.dump(data, json_file, indent=4)
    return jsonify(data)

def search_gper_in_chembl():
    url = "https://www.ebi.ac.uk/chembl/api/data/target.json?pref_name__icontains=GPER"
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        return data.get("targets", [])
    else:
        return []

# 2) Récupérer les détails d'une cible (pour obtenir cross_references => UniProt)
def get_target_details(chembl_id):
    url = f"https://www.ebi.ac.uk/chembl/api/data/target/{chembl_id}.json"
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.json()
    else:
        return {}

# 3) Récupérer toutes les molécules (activités) associées à une cible
def get_target_activities(chembl_id):
    """
    Récupère toutes les molécules qui interagissent avec un target ChEMBL donné.
    Pour chaque molécule, on récupère :
      - ChEMBL ID
      - Nom de la molécule
      - Type d'activité (IC50, Ki, EC50, ...)
      - Valeur et unités
      - pChEMBL (si disponible)
    """
    url = f"https://www.ebi.ac.uk/chembl/api/data/activity.json?target_chembl_id={chembl_id}&limit=200"
    resp = requests.get(url)
    
    if resp.status_code == 200:
        data = resp.json()
        activities = data.get("activities", [])
        
        # Vérifier si la liste est vide
        if not activities:
            print(f"[INFO] Aucune activité trouvée pour {chembl_id}.")
            return []

        results = []
        for act in activities:
            molecule_id = act.get("molecule_chembl_id")
            molecule_name = get_molecule_name(molecule_id)  # ⬅ Récupérer le nom
            
            results.append({
                "molecule_chembl_id": molecule_id,
                "molecule_name": molecule_name,  # ⬅ Ajouter le nom dans le JSON
                "standard_type": act.get("standard_type"),
                "standard_value": act.get("standard_value"),
                "standard_units": act.get("standard_units"),
                "pchembl_value": act.get("pchembl_value"),
            })

        return results
    else:
        print(f"[ERREUR] Impossible de récupérer les activités pour {chembl_id}")
        return []


@app.route("/search_gper", methods=["GET"])
def search_gper():
    """
    1) Cherche toutes les cibles GPER dans ChEMBL
    2) Pour chacune, on récupère son ID UniProt (cross_refs)
    3) On récupère aussi les molécules (activités) associées
    4) On renvoie tout ça à la page "molecules.html" pour affichage
    """
    targets = search_gper_in_chembl()

    if not targets:
        return render_template("molecules.html", gper_targets=[], error="Aucune cible GPER trouvée dans ChEMBL.")

    results = []
    for t in targets:
        chembl_id = t.get("target_chembl_id")
        pref_name = t.get("pref_name", "Nom inconnu")

        # Récupérer les cross-references UniProt
        details = get_target_details(chembl_id)
        cross_refs = details.get("cross_references", [])
        uniprot_ids = [ref["xref_id"] for ref in cross_refs if ref["xref_src_db"] == "UniProt"]

        # Récupérer les molécules associées à cette cible
        molecules = get_target_activities(chembl_id)

        results.append({
            "chembl_id": chembl_id,
            "pref_name": pref_name,
            "uniprot_ids": uniprot_ids,
            "molecules": molecules
        })

    return render_template("molecules.html", gper_targets=results, error=None)
def get_molecule_name(molecule_chembl_id):
    """
    Récupère le nom d'une molécule à partir de son ChEMBL ID
    """
    if not molecule_chembl_id:
        return "Inconnu"

    url = f"https://www.ebi.ac.uk/chembl/api/data/molecule/{molecule_chembl_id}.json"
    resp = requests.get(url)
    
    if resp.status_code == 200:
        data = resp.json()
        return data.get("pref_name", "Nom inconnu")  # Renvoie le nom, sinon "Nom inconnu"
    else:
        return "Nom inconnu"

if __name__ == "__main__":
    app.run(debug=True)

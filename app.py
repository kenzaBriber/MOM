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
        "fields": "id,accession,gene_names,protein_name,length,xref_pdb,organism_name,xref_drugbank,xref_chembl,xref_pdb",
        "size":186
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

def get_chembl_id_from_uniprot(uniprot_id):
    url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.json"
    resp=requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        chembl_refs = [
            ref["id"] for ref in data.get("uniProtKBCrossReferences", [])
            if ref.get("database") == "ChEMBL"
        ]
        return chembl_refs[0] if chembl_refs else None
    return None

if __name__ == "__main__":
    chembl_id=get_chembl_id_from_uniprot("F7EQ49")
    print(chembl_id)
    app.run(debug=True)
    
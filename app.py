import requests
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

# Fonction pour interroger l'API UniProt
def query_uniprot(query):
    url = "https://rest.uniprot.org/uniprotkb/search"
    params = {
        "query": query,
        "format": "json",
        "fields": "id,accession,gene_names,protein_name,length,xref_pdb,organism_name,xref_drugbank,xref_chembl",
        "size":3
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200: # requete faite
        data= response.json()
        print(data)
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
    return jsonify(data)



if __name__ == "__main__":
    app.run(debug=True)

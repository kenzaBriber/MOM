import requests
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
def get_molecules_from_chembl(chembl_id):
    """Récupère les molécules qui interagissent avec une protéine donnée depuis ChEMBL"""
    url = f"https://www.ebi.ac.uk/chembl/api/data/activity.json?target_chembl_id={chembl_id}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        molecules = []

        for activity in data.get("activities", []):
            molecules.append({
                "chembl_id": activity.get("molecule_chembl_id"),
                "name": activity.get("molecule_pref_name", "Inconnu"),
                "activity_type": activity.get("activity_type", "N/A"),
                "value": activity.get("value", "N/A"),
                "unit": activity.get("units", "N/A"),
                "link": f"https://www.ebi.ac.uk/chembl/compound_report_card/{activity.get('molecule_chembl_id')}/"
            })
        
        return molecules
    else:
        return None
def get_molecule_details(chembl_molecule_id):
    """Récupère les détails d'une molécule spécifique depuis ChEMBL"""
    url = f"https://www.ebi.ac.uk/chembl/api/data/molecule/{chembl_molecule_id}.json"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return {
            "name": data.get("molecule_pref_name", "Inconnu"),
            "type": data.get("molecule_type", "N/A"),
            "logp": data.get("molecule_properties", {}).get("alogp", "N/A"),
            "mw": data.get("molecule_properties", {}).get("mw_freebase", "N/A"),
            "max_phase": data.get("max_phase", "N/A"),
            "class": data.get("usan_stem_definition", "N/A"),
            "link": f"https://www.ebi.ac.uk/chembl/compound_report_card/{chembl_molecule_id}/"
        }
    else:
        return None
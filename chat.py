import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.agents import Tool
from langchain.prompts import PromptTemplate
from Bio import Entrez
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Lire la clé API depuis les variables d'environnement
api_key = os.getenv("OPENAI_API_KEY")

# Configuration du modèle OpenAI
llm = ChatOpenAI(
    temperature=0,
    openai_api_key=api_key,
    model_name="gpt-4o"
)

# Définir la fonction de recherche sur PubMed
Entrez.email = "kenzabriber07@gmail.com"

def search_pubmed_api(query: str, max_results=4) -> list:
    """
    Recherche plusieurs articles sur PubMed et retourne une liste d'articles avec :
    - Le titre
    - L'abstract
    - Un lien vers l'article
    """
    handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
    record = Entrez.read(handle)
    handle.close()
    
    pmid_list = record["IdList"]
    if not pmid_list:
        return [{"title": "Aucun article trouvé", "abstract": "", "link": ""}]
    
    results = []
    
    for pmid in pmid_list:
        fetch_handle = Entrez.efetch(db="pubmed", id=pmid, rettype="abstract", retmode="text")
        article_text = fetch_handle.read()
        fetch_handle.close()
        pubmed_link = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        
        results.append({
            "title": f"Article {len(results) + 1}",
            "abstract": article_text.strip(),
            "link": pubmed_link
        })
    
    return results

# Définition de l'outil LangChain pour interagir avec PubMed
search_pubmed_tool = Tool(
    name="search_pubmed",
    func=search_pubmed_api,
    description=(
        "Utilisez cet outil pour rechercher plusieurs articles scientifiques sur PubMed. "
        "Entrez une requête sous forme de question (ex: 'Quel est l'impact du diabète sur le cancer?'). "
        "L'outil retournera plusieurs extraits d'articles avec des liens vers PubMed."
    )
)

# Prompt pour guider le LLM
prompt = PromptTemplate.from_template(
    """
    Vous êtes un assistant spécialisé en recherche biomédicale.
    Lorsque l'utilisateur pose une question sur un sujet médical ou scientifique,
    utilisez toujours l'outil `search_pubmed` pour récupérer plusieurs articles pertinents.
    Affichez chaque extrait d'article séparément avec son lien vers PubMed.

    Question utilisateur: {input}
    """
)

# Initialisation de l'agent LangChain
agent = initialize_agent(
    tools=[search_pubmed_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Interface utilisateur Streamlit
st.title("Chatbot PubMed 🧬")
user_query = st.text_input("Vous recherchez des articles sur PubMed ? Saisissez les mots clés:")

if st.button("Rechercher"):
    if user_query:
        # 1️⃣ Obtenir la réponse du LLM
        llm_response = agent.run(user_query)

        # 2️⃣ Récupérer les articles bruts de PubMed
        articles = search_pubmed_api(user_query, max_results=4)
        
        # 🟢 Afficher la réponse du LLM
        st.markdown("## 🤖 Résumer géneral de la recherche")
        st.markdown(llm_response)

        # 🟢 Afficher les articles détaillés avec liens
        st.markdown("## 📄 Articles trouvés sur PubMed")
        for article in articles:
            if article["title"] != "Aucun article trouvé":
                st.markdown(f"### {article['title']}")
                st.markdown(f"**Résumé :** {article['abstract']}")
                st.markdown(f"[Voir l'article complet]({article['link']})")
                st.markdown("---")  # Séparateur entre les articles
            else:
                st.markdown("Aucun article trouvé pour cette requête.")

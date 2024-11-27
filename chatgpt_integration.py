import os
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser

class ChatGPTIntegration:
    def __init__(self):
        # Assurez-vous de définir votre clé API OpenAI comme variable d'environnement
        # self.api_key = os.getenv('OPENAI_API_KEY')
        # if not self.api_key:
        #     raise ValueError("Veuillez définir la variable d'environnement OPENAI_API_KEY")
        
        self.llm = ChatOpenAI(
            temperature=0.001, 
            base_url="http://localhost:1234/v1/", 
            api_key="not-needed",
            streaming=True  # Activer le streaming pour voir les mots un à un
        )
    
    def generate_description(self, nom, prenom):
        """Génère une description basée sur le nom et prénom"""
        prompt = ChatPromptTemplate.from_template(
            "Crée une courte description imaginative et amusante pour {prenom} {nom}"
        )
        
        chain = prompt | self.llm | StrOutputParser()
        # Utiliser stream au lieu de invoke pour activer le streaming
        return chain.stream({"nom": nom, "prenom": prenom})

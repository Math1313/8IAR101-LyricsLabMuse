import os
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser

class ChatGPTIntegration:
    def __init__(self):
        # Assurez-vous de définir votre clé API OpenAI comme variable d'environnement
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("Veuillez définir la variable d'environnement OPENAI_API_KEY")
        
        self.llm = ChatOpenAI(temperature=0.7)
    
    def generate_description(self, nom, prenom):
        """Génère une description basée sur le nom et prénom"""
        prompt = ChatPromptTemplate.from_template(
            "Crée une courte description imaginative et amusante pour {prenom} {nom}"
        )
        
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"nom": nom, "prenom": prenom})

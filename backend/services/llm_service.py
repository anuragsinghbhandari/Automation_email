from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import logging
import os

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.llm = ChatGroq(
            model_name="llama-3.1-70b-versatile",
            temperature=0.7,
            max_tokens=500
        )
        self.prompt_template = PromptTemplate(
            input_variables=["client", "body", "context"],
            template="""
            Client: {client}
            Email Content: {body}
            
            Relevant Context from Knowledge Base:
            {context}

            Generate a professional and empathetic reply as Anurag Singh Bhandari, 
            a 20-year-old entrepreneur from Khora, U.P, India.
            
            Guidelines:
            - Address the main points concisely
            - Maintain a professional yet friendly tone
            - Keep the response clear and focused
            - Include a polite greeting and sign-off
            - Incorporate relevant information from the context when appropriate
            
            Reply:
            """
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    def generate_reply(self, client, body, context=""):
        try:
            response = self.chain.invoke({
                "client": client,
                "body": body,
                "context": context
            })
            return response.get("text", "")
        except Exception as e:
            logger.error(f"Error generating reply: {e}")
            return "I apologize, but I am currently unable to generate a response."
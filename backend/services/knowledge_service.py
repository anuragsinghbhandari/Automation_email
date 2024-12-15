from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
import logging
import os
import glob

logger = logging.getLogger(__name__)

class KnowledgeService:
    def __init__(self, llm):
        self.llm = llm
        self.retrieval_chain = None
        self.last_modified_times = {}

    def initialize_knowledge_base(self):
        try:
            pdf_files = glob.glob("knowledge_base/*.pdf")
            if not pdf_files:
                logger.warning("No PDF files found in knowledge_base directory")
                return False

            current_modified_times = {pdf: os.path.getmtime(pdf) for pdf in pdf_files}
            
            if current_modified_times == self.last_modified_times:
                return True

            documents = []
            for pdf_path in pdf_files:
                logger.info(pdf_path)
                loader = PyPDFLoader(pdf_path)
                documents.extend(loader.load())

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            splits = text_splitter.split_documents(documents)

            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=embeddings,
                persist_directory="./chroma_db"
            )

            self.retrieval_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
                return_source_documents=True,
                verbose=True
            )
            self.last_modified_times = current_modified_times
            return True

        except Exception as e:
            logger.error(f"Error initializing knowledge base: {e}")
            return False

    def get_relevant_context(self, query):
        try:
            if not self.retrieval_chain:
                return ""

            result = self.retrieval_chain({
                "question": query,
                "chat_history": []
            })
            
            context = "\n\n".join([
                f"Source Document:\n{doc.page_content}"
                for doc in result.get("source_documents", [])
            ])
            
            return context or "No relevant context found."

        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return ""

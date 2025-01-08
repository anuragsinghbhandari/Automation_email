from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from pymongo import MongoClient
import gridfs
import tempfile
import logging
import os
import psutil

logger = logging.getLogger(__name__)

class KnowledgeService:
    def __init__(self, llm):
        self.llm = llm
        self.retrieval_chain = None
        
        # MongoDB setup
        mongo_uri = os.environ.get('MONGODB_URI')
        self.client = MongoClient(mongo_uri)
        self.db = self.client['your_database_name']
        self.fs = gridfs.GridFS(self.db)
        
        # Persistent directory for ChromaDB
        self.persist_directory = "/persistent/chroma_storage"

    def initialize_knowledge_base(self):
        try:
            documents = []
            # Batch processing of PDFs from MongoDB
            cursor = self.fs.find({"contentType": "application/pdf"}).batch_size(10)
            for grid_out in cursor:
                try:
                    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                        temp_file.write(grid_out.read())
                        temp_path = temp_file.name

                    logger.info(f"Processing PDF: {grid_out.filename}")
                    loader = PyPDFLoader(temp_path)
                    documents.extend(loader.load())
                    
                    # Clean up temp file
                    os.unlink(temp_path)
                except Exception as e:
                    logger.error(f"Error processing PDF {grid_out.filename}: {e}", exc_info=True)
                    continue

            if not documents:
                logger.warning("No documents found in MongoDB")
                return False

            # Split documents into manageable chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,  # Reduced size for better memory handling
                chunk_overlap=100,
                length_function=len
            )
            splits = text_splitter.split_documents(documents)

            # Initialize embeddings
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

            # Initialize or load ChromaDB
            if os.path.exists(self.persist_directory):
                logger.info("Loading existing Chroma vectorstore")
                vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding=embeddings
                )
            else:
                logger.info("Creating a new Chroma vectorstore")
                vectorstore = Chroma.from_documents(
                    documents=splits,
                    embedding=embeddings,
                    persist_directory=self.persist_directory
                )
                vectorstore.persist()

            # Initialize the conversational retrieval chain
            self.retrieval_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
                return_source_documents=True,
                verbose=True
            )
            
            # Log memory usage
            logger.info(f"Memory usage: {psutil.Process().memory_info().rss / 1024 ** 2:.2f} MB")
            
            return True

        except Exception as e:
            logger.error(f"Error initializing knowledge base: {e}", exc_info=True)
            return False

    def get_relevant_context(self, query):
        try:
            if not self.retrieval_chain:
                logger.warning("Retrieval chain not initialized")
                return "Knowledge base is not initialized. Please try again later."

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
            logger.error(f"Error retrieving context: {e}", exc_info=True)
            return "An error occurred while retrieving context. Please try again later."

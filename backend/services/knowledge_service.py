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

    def initialize_knowledge_base(self):
        try:
            documents = []
            # Retrieve PDFs from MongoDB
            for grid_out in self.fs.find({"contentType": "application/pdf"}):
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
                    logger.error(f"Error processing PDF {grid_out.filename}: {e}")
                    continue

            if not documents:
                logger.warning("No documents found in MongoDB")
                return False

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            splits = text_splitter.split_documents(documents)

            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            
            # Use temporary directory for Chroma
            with tempfile.TemporaryDirectory() as temp_dir:
                vectorstore = Chroma.from_documents(
                    documents=splits,
                    embedding=embeddings,
                    persist_directory=temp_dir
                )

                self.retrieval_chain = ConversationalRetrievalChain.from_llm(
                    llm=self.llm,
                    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
                    return_source_documents=True,
                    verbose=True
                )
            
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

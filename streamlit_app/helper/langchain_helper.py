import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.llms.llamacpp import LlamaCpp
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings

# Get the absolute path to the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STREAMLIT_APP_DIR = os.path.join(PROJECT_ROOT, "streamlit_app")

# Set up the Llama model for inference with deterministic parameters
llm = LlamaCpp(
    model_path=os.path.join(PROJECT_ROOT, "models", "mistral-7b-instruct-v0.1.Q4_K_M.gguf"),
    temperature=0.1,  # Lowered temperature for more deterministic output
    max_tokens=256,
    top_p=1.0,        # Enabling deterministic sampling
    top_k=0,          # Enabling deterministic sampling
    verbose=True,
)

# Embedding setup
embed_model = HuggingFaceEmbeddings(model_name="thenlper/gte-large")

# Create paths for vector database
faiss_index_path = os.path.join(STREAMLIT_APP_DIR, "faiss_index")

def create_vector_db():
    # Load documents
    pdf_path = os.path.join(STREAMLIT_APP_DIR, "california.pdf")
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    print(f"Loaded {len(documents)} documents from {pdf_path}")

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
    )
    texts = text_splitter.split_documents(documents)
    print(f"Split into {len(texts)} chunks.")

    # Create directory if it doesn't exist
    os.makedirs(faiss_index_path, exist_ok=True)
    print(f"Directory created or confirmed at {faiss_index_path}")

    # Create and save FAISS index
    try:
        vectorstore = FAISS.from_documents(texts, embed_model)
        # Save both the index and docstore
        vectorstore.save_local(faiss_index_path)
        print(f"Vector database successfully saved at {faiss_index_path}")
        return vectorstore
    except Exception as e:
        print(f"Failed to save vector database: {e}")
        raise

def get_qa_chain():
    try:
        # Check if both index files exist
        index_files_exist = all(
            os.path.exists(os.path.join(faiss_index_path, f))
            for f in ["index.faiss", "index.pkl"]
        )
        
        if not index_files_exist:
            print("Creating new vector database...")
            vectordb = create_vector_db()
        else:
            print("Loading existing vector database...")
            vectordb = FAISS.load_local(faiss_index_path, embed_model, allow_dangerous_deserialization=True)
        
        # Set retriever with lower k if you want only one context returned
        retriever = vectordb.as_retriever(search_kwargs={"k": 1})

        # Define prompt template
        prompt_template = """Given the following context and a question, generate an answer based on the source PDF.
        Try to provide as much relevant text as possible from the "response" section in the source.

        CONTEXT: {context}
        QUESTION: {question}"""

        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=['context', 'question']
        )

        # Set up the QA chain
        chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=False,
            chain_type_kwargs={"prompt": PROMPT}
        )
        return chain
    except Exception as e:
        print(f"Error in get_qa_chain: {e}")
        raise

if __name__ == "__main__":
    qa_chain = get_qa_chain()
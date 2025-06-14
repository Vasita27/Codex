from llama_index.core import VectorStoreIndex, ServiceContext
from llama_index.core.settings import Settings
from llama_index.llms.openai import OpenAI
from llama_index.llms.ollama import Ollama


from llama_index.embeddings.huggingface import HuggingFaceEmbedding
# from llama_index.llms import Ollama
from llama_index.core.text_splitter import SentenceSplitter
from llama_index.core.query_engine import RetrieverQueryEngine
from dotenv import load_dotenv
import os

# load_dotenv()
# api_key = os.getenv("OPENAI_API_KEY")

import re

def format_response_for_browser(response_text):
    lines = response_text.strip().split('\n')
    formatted = []

    for line in lines:
        stripped = line.strip()

        # Numbered sections
        if re.match(r'^\d+\.\s+.+', stripped):
            formatted.append(f'<p style="margin-top: 1em;"><strong>🔹 {stripped}</strong></p>')
        # Headers
        elif stripped.startswith("##") or stripped.endswith(":"):
            clean = stripped.strip("# ").rstrip(":")
            formatted.append(f'<h3 style="color:#1e88e5;">{clean}</h3>')
        # Bullets
        elif stripped.startswith("*") or stripped.startswith("-"):
            formatted.append(f'<li>{stripped[1:].strip()}</li>')
        # Normal paragraph
        else:
            formatted.append(f'<p>{stripped}</p>')

    # Wrap <li> in <ul> if any
    html_output = []
    in_list = False
    for line in formatted:
        if line.startswith("<li>") and not in_list:
            html_output.append("<ul>")
            in_list = True
        elif not line.startswith("<li>") and in_list:
            html_output.append("</ul>")
            in_list = False
        html_output.append(line)
    if in_list:
        html_output.append("</ul>")

    return "\n".join(html_output)


def embed_and_search(docs, question):
    # 1. Set up the embedding model
    embed_model = HuggingFaceEmbedding(model_name="all-MiniLM-L6-v2")
    # Settings.llm = Ollama(model="llama3")
    Settings.embed_model = embed_model
    llm = llm = Ollama(model="gemma:2b", request_timeout=300, temperature=0.3, streaming=False)

    Settings.llm = llm
    Settings.text_splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)

    # 2. Service context
    # service_context = ServiceContext.from_defaults(
    #     embed_model=embed_model,
    #     text_splitter=SentenceSplitter(chunk_size=512, chunk_overlap=50),
    # )

    # 3. Create the index
    index = VectorStoreIndex.from_documents(docs)
    

    # 4. Create a retriever-based query engine
    retriever = index.as_retriever(similarity_top_k=4)
    concise_question = f"{question.strip()} Explain neatly in a length that is suitable for the question, so that a beginner can understand. The main goal is making a user ready to work with this repo. Use the necessary files to answer this. If it is about the entire repository, refer all the files in the repository and answer. If asked for workflow or any similar question explain with the help of all files, including all the functionalities and features and how they work together."

    query_engine = RetrieverQueryEngine.from_args(retriever)
    print(f"Concise question: {concise_question}")

    # 5. Query the index
    response = query_engine.query(concise_question)
    formatted_response = format_response_for_browser(str(response))

    return str(response)

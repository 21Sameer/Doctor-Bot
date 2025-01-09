import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import json

load_dotenv()

def load_json_data():
    with open('./data/medicine_data.json', 'r') as file:
        return json.load(file)

def load_chunks():
    embeddings = OpenAIEmbeddings(model='text-embedding-ada-002')
    vectorstore = Chroma(
        persist_directory="./chromadb",
        embedding_function=embeddings,
        collection_name="medicine_collection"
    )
    
    data = load_json_data()

    print("Adding JSON data to vectorstore")
    for i in data['diseases']:
        vectorstore.add_texts([json.dumps(i)])
    print("Data added successfully")

def retriever(question):
    embeddings = OpenAIEmbeddings(model='text-embedding-ada-002')
    vectorstore = Chroma(
        persist_directory="./chromadb",
        embedding_function=embeddings,
        collection_name="medicine_collection"
    )
    return vectorstore.similarity_search(question, k=3)

# print(retriever("dengue"))
# load_chunks()




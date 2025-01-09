import os
from ocr_service import extract_text_from_image
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import json

load_dotenv()

def load_json_data():
    with open('./data/medicine_data.json', 'r') as file:
        return json.load(file)

def retriever(question):
    embeddings = OpenAIEmbeddings(model='text-embedding-ada-002')
    vectorstore = Chroma(
        persist_directory="./chromadb",
        embedding_function=embeddings,
        collection_name="medicine_collection"
    )
    return vectorstore.similarity_search(question, k=3)

def retriever_from_image(image_path):
    """Queries the vectorstore using text extracted from an image."""
    text = extract_text_from_image(image_path)
    if text:
        print("Extracted text:", text)
        return retriever(text)  # Use the existing retriever function
    else:
        return "No text extracted from the image to query."

def process_uploaded_images(upload_folder):
    """Processes all images in the upload folder."""
    if not os.path.exists(upload_folder):
        print(f"Folder {upload_folder} does not exist.")
        return
    
    images = [f for f in os.listdir(upload_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]
    if not images:
        print("No images found in the upload folder.")
        return

    for image_name in images:
        image_path = os.path.join(upload_folder, image_name)
        print(f"Processing image: {image_path}")
        
        # Retrieve information using the OCR and retriever
        response = retriever_from_image(image_path)
        print(f"Response for {image_name}: {response}")

# Main execution
if __name__ == "__main__":
    UPLOAD_FOLDER = "./uploaded_images"
    process_uploaded_images(UPLOAD_FOLDER)
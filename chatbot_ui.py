import gradio as gr
import base64
from chatbot import recommend_medicine
import boto3
import io
from PIL import Image
from services.mongo_service import save_chat, fetch_chat
import os 

from dotenv import load_dotenv

# Load environment variables
load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION_NAME = os.getenv("AWS_REGION_NAME")

# Initialize AWS Textract client
# AWS Textract setup
textract = boto3.client(
    'textract',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION_NAME
)

# Custom CSS without base64 background image
custom_css = """
body {
    margin: 0;
    padding: 0;
    background-image: url('/images/background.jpeg');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

#gradio-app {
    min-height: 100vh;
    background-color: rgba(355, 355, 355, 0.8);
}

.gradio-container {
    max-width: 1000px !important;
    width: 90% !important;
    margin: 2rem auto !important;
    padding: 2rem !important;
    box-shadow: rgba(0, 0, 0, 0.1) 0px 4px 12px, rgba(0, 0, 0, 0.1) 0px 1px 3px !important;
    border: 1px solid rgba(0, 0, 0, 0.1) !important;
    border-radius: 15px !important;
}

.gradio-container:hover {
    box-shadow: rgba(0, 0, 0, 0.15) 0px 5px 15px, rgba(0, 0, 0, 0.12) 0px 3px 5px !important;
    transition: all 0.3s ease !important;
}

.message.user {
    background-color: #E3F2FD !important;
    color: #1565C0 !important;
    border-radius: 15px 15px 0 15px !important;
    padding: 10px 15px !important;
    margin: 5px 0 !important;
}

.message.assistant {
    background-color: #4CAF50 !important;
    color: white !important;
    border-radius: 15px 15px 15px 0 !important;
    padding: 10px 15px !important;
    margin: 5px 0 !important;
}

.input-row {
    display: flex !important;
    gap: 20px !important;
    margin-bottom: 20px !important;
}

.user-id-container {
    flex: 1 !important;
}

.symptoms-container {
    flex: 2 !important;
}

.upload-container {
    flex: 1 !important;
}

.input-box {
    border: 2px solid #4CAF50 !important;
    border-radius: 10px !important;
    width: 100% !important;
}

.submit-btn {
    background-color: #4CAF50 !important;
    color: white !important;
    border: none !important;
    padding: 0.5rem 1rem !important;
    border-radius: 8px !important;
    cursor: pointer !important;
    width: 100% !important;
    transition: background-color 0.3s ease !important;
}

.submit-btn:hover {
    background-color: #45a049 !important;
}

.disclaimer {
    background-color: #FFF3E0;
    border: 2px solid #FF9800;
    border-radius: 10px;
    padding: 15px;
    margin: 15px 0;
    font-weight: bold;
    color: #E65100;
    text-align: center;
}

/* Specific styling for the image upload area */
.upload-box {
    border: 2px solid #4CAF50 !important;
    border-radius: 10px !important;
    padding: 10px !important;
    height: auto !important;
    min-height: 100px !important;
    max-height: 150px !important;
}
"""

# Function to extract text from an image
def extract_text_from_image(image):
    if image is None:
        return ""
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    try:
        response = textract.detect_document_text(Document={'Bytes': img_byte_arr})
        extracted_text = ""
        for item in response['Blocks']:
            if item['BlockType'] == 'LINE':
                extracted_text += item['Text'] + "\n"
        return extracted_text.strip()
    except Exception as e:
        print(f"Error extracting text: {str(e)}")
        return "Error extracting text from image"

def chat(user_id, query, image, chat_history):
    if image is not None:
        extracted_text = extract_text_from_image(image)
        response = extracted_text
    elif query:
        response = recommend_medicine(query)
    else:
        response = "Please enter symptoms or upload an image."

    chat_data = {
        "user_id": user_id,
        "user_message": query if query else "Image Uploaded",
        "bot_response": response
    }

    save_chat(chat_data)
    chat_history.append((query if query else "Image Uploaded", response))
    return "", None, chat_history

# Gradio UI Setup
with gr.Blocks(css=custom_css, title="Doctor Bot") as demo:
    with gr.Column():
        gr.HTML(
            """
            <div style="text-align: center; margin-bottom: 1rem; width: 100%;">
                <h1 style="color: #1565C0; font-size: 3rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.1);">🩺 Doctor Bot</h1>
                <h3 style="color: #4CAF50; font-size: 1.8rem;">Your AI Medical Assistant</h3>
            </div>
            """
        )
        gr.HTML(
            """
            <div class="disclaimer">
                ⚠️ DISCLAIMER: Get recommendations at your own responsibility. 
                The chatbot will not be responsible in case of any serious issue.
            </div>
            """
        )
        chatbot = gr.Chatbot([], elem_id="chatbot", height=500, container=True)
        with gr.Row(elem_classes="input-row"):
            with gr.Column(elem_classes="user-id-container"):
                user_id_input = gr.Textbox(
                    label="User ID",
                    placeholder="Enter your user ID",
                    elem_classes="input-box"
                )
            with gr.Column(elem_classes="symptoms-container"):
                textbox = gr.Textbox(
                    label="Enter Symptoms",
                    placeholder="Type your symptoms here...",
                    elem_classes="input-box"
                )
            with gr.Column(elem_classes="upload-container"):
                image_input = gr.Image(
                    label="Upload Medical Report",
                    type="pil",
                    elem_classes="upload-box"
                )
        submit_btn = gr.Button(
            "Get Recommendation",
            elem_classes="submit-btn"
        )
        
        submit_btn.click(
            chat,
            inputs=[user_id_input, textbox, image_input, chatbot],
            outputs=[textbox, image_input, chatbot]
        )
        textbox.submit(
            chat,
            inputs=[user_id_input, textbox, image_input, chatbot],
            outputs=[textbox, image_input, chatbot]
        )

demo.launch(server_port=3000)


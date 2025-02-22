from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pdfplumber
from pinecone_configs.pinecone_configs import pine_cone_initializer
from typing import List
import os
import requests

router = APIRouter()

class FileUpload(BaseModel):
    file_link: str
    file_name: str

async def download_file(url, filename):
    os.makedirs('data', exist_ok=True)
    filepath = os.path.join('data', filename)
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(filepath, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    return filepath

async def extract_text_from_pdf(pdf_file_path):
    text = []
    with pdfplumber.open(pdf_file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
    return text

@router.post("/upload-pdf")
async def upload_pdf(file_request: FileUpload):
    # Step 1: Download the file from the provided URL
    pdf_file_path = await download_file(file_request.file_link, file_request.file_name)
    
    # Step 2: Extract text from the PDF
    texts = await extract_text_from_pdf(pdf_file_path)
    
    # Step 3: Prepare the text as documents
    documents = [{"content": text} for text in texts]
    
    # Step 4: Embed the documents into Pinecone
    pine_cone_initializer.embed_documents(documents, index_name="example-index")
    
    # Step 5: Clean up the downloaded file
    os.remove(pdf_file_path)
    
    return {"message": "PDF processed and data embedded"}
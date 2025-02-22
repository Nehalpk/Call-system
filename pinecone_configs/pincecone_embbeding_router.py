#import pdfplumber
#from fastapi import UploadFile,File,APIRouter,HTTPException
#upload_pdf_router=APIRouter()
#from pydantic import BaseModel
#from pinecone_configs.pinecone_configs import pine_cone_initializer
#from langchain_core.documents import Document
#from typing import List
#from mongodb_config.mongo_db_config  import mongo_handler
#import os ,requests
#def convert_to_string(knowledge_list):
#    knowledge = ""
#    for item in knowledge_list:
#        question = item.get('Question', '')
#        answer = item.get('Answer', '')
#        knowledge += f"Question: {question}\nAnswer: {answer}\n\n"
#    return knowledge.strip()
## Define a Pydantic model for the expected request data
#class TextEmbeddingRequest(BaseModel):
#    Admin_id :str
#    Embeding_data : list
#    knowledgebase_ID :str
#    File_type :str 
#    
#class fileupload(BaseModel):
#    file_link :str
#    file_name : str 
#    
#    
#    
#    
#def format_questions_answers(text_data):
#    result = []
#    
#    # Loop through each item in the text_data list
#    for item in text_data:
#        # Ensure the item is a dictionary before accessing its keys
#        if isinstance(item, dict):
#            # Get the 'Question' and 'Answer' fields with a default fallback
#            question = item.get('Question', 'No Question')
#            answer = item.get('Answer', 'No Answer')
#            
#            # Format the output string
#            formatted_output = f"Question: {question}\nAnswer: {answer.strip()}"  # Using strip() to remove extra newline
#            
#            # Append the formatted output to the result list
#            result.append(formatted_output)
#        else:
#            # If the item isn't a dictionary, raise a TypeError
#            raise TypeError("Each item in the data list must be a dictionary")
#
#    # Print the formatted result
#    for item in result:
#        print(item)
#        print("-" * 20)
#
#    # Return the result for further use if needed
#    return result
#
#
#def texts_to_documents(texts, source):
#    try:
#        print ("this is the texts : ",texts)
#        global loader
#        documents = []
#        page_number = 0
#        max_chars_per_page=1
#        for text in texts:
#            if len(text)<=100:
#                max_chars_per_page=10
#            elif len(text)<=500:
#                max_chars_per_page=100
#            elif len(text)<=1000:
#                max_chars_per_page=200
#            elif len(text)<=10000:
#                max_chars_per_page=1000
#            elif len(text)<=100000:
#                max_chars_per_page=2000
#            else:
#                max_chars_per_page=2500
#            # Split the text into pages if it exceeds the max_chars_per_page limit
#            for start in range(0, len(text), max_chars_per_page):
#                end = start + max_chars_per_page
#                page_text = text[start:end]
#                # Create a Document object for each page
#                doc = Document(
#                    page_content=page_text,
#                    metadata={
#                        'source': source,
#                        'page': page_number
#                    }
#                )
#                documents.append(doc)
#                page_number += 1
#        loader=documents
#        return loader 
#    except Exception as e:
#        return "error in documents"
#vector_store  = any 
#
#def download_file(url, filename):
#    """
#    Download a file from a URL and save it locally in the 'data' folder as a .pdf file.
#    """
#    try:
#        os.makedirs('data', exist_ok=True)  # Ensure 'data' folder exists
#        filepath = os.path.join('data', filename)  # Full path to save the file
#
#        response = requests.get(url, stream=True)
#        response.raise_for_status()  # Check for HTTP errors
#
#        with open(filepath, 'wb') as file:
#            for chunk in response.iter_content(chunk_size=8192):
#                if chunk:
#                    file.write(chunk)
#
#        print(f'Download completed successfully. File saved as "{filepath}".')
#        return filepath
#    except Exception as e:
#        raise Exception(f"Error downloading the file: {str(e)}")
#
#
#@upload_pdf_router.post("/readpdf")
#async def upload_pdf(filerequest:fileupload):
#    global vector_store
#    try:
#        # Step 1: Download the file from the URL
#        print(f"Starting the download from {filerequest.file_link}")
#        pdf_file_path = download_file(filerequest.file_link, filerequest.file_name)
#
#        # Step 2: Read the downloaded PDF file
#        text = []  # List to store text from all pages
#        print(f"Reading the PDF content from {pdf_file_path}")
#
#        with pdfplumber.open(pdf_file_path) as pdf:
#            # Iterate through all pages in the PDF
#            for page in pdf.pages:
#                page_text = page.extract_text()
#                if page_text:
#                    text.append(page_text)
#
#        # Convert extracted text into documents for embedding
#        loader = texts_to_documents(text, str(filerequest.file_name))
#        print(f"Extracted text converted to loader: {loader}")
#
#        # Step 3: Embed the extracted content into Pinecone
#        vector_store = pine_cone_initializer.Embeding_Pdf_to_pincecone(loader, index_name="langchain-retrieval-augmentation-fast")
#        print(f"Vector store data: {vector_store}")
#
#        # Step 4: Delete the PDF file after embedding
#        print(f"Deleting the file {pdf_file_path}")
#        os.remove(pdf_file_path)
#
#        # Return success message
#        return {"message": "PDF successfully processed and embedded"}
#
#    except Exception as e:
#        return {"error": str(e)}
#
#
#
#
#
#
#@upload_pdf_router.post("/readpdfDemo")
#async def upload_pdfDemo(file: UploadFile = File(...)):
#    global vector_store
#    try:
#        # Step 1: Download the file
#        filename = file.filename
#        url = file.file  # Assuming the file URL is passed as part of the upload
#        print(f"Starting the download of {filename}")
#        
#        # Download the file and save it in the 'data' directory
#        filepath = os.path.join('data', filename)
#        with open(filepath, 'wb') as pdf_file:
#            content = await file.read()
#            pdf_file.write(content)
#
#        # Step 2: Read the downloaded PDF file
#        text = []  # List to store text from all pages
#        print(f"Reading the PDF content from {filepath}")
#
#        # Open the PDF file using pdfplumber
#        with pdfplumber.open(filepath) as pdf:
#            # Iterate through all pages in the PDF
#            for page in pdf.pages:
#                # Extract text from the current page
#                page_text = page.extract_text()
#                # If the page has text, add it to the list
#                if page_text:
#                    text.append(page_text)
#
#        # Convert text to documents (for embedding)
#        loader = texts_to_documents(text, str(filename))
#        print(f"This is the data that we got in loader: {loader}")
#
#        # Step 3: Embed the PDF content into Pinecone
#        vector_store = pine_cone_initializer.Embeding_Pdf_to_pincecone(loader, index_name="langchain-retrieval-augmentation-fast")
#        print(f"This is the data for vector store: {vector_store}")
#
#        # Step 4: Delete the downloaded PDF after embedding
#        print(f"Deleting the file {filepath}")
#        os.remove(filepath)
#
#        # Return success response
#        return {"message": "Embedding and file processing successful"}
#
#    except Exception as e:
#        # In case of any errors, return the error message
#        return {"error": str(e)}
#    # s  # Expecting a list of strings
#    
#    
#    
#@upload_pdf_router.post ("/create_index")
#async def create_index(data:dict):
#    index_name= data.get("index_name")
#    pine_cone_initializer.initialize_pinecone(index_name)
#    
#@upload_pdf_router.post("/text_embedding")
#async def text_embedding(request: TextEmbeddingRequest):
#    try:
#        # Extract the text data from the request
#        text_data = request.Embeding_data
#        Index_name = request.Admin_id
#        Knowledge_baseID =request.knowledgebase_ID
#        File_type = request.File_type
#        list
#        print("This is the data that we got in loader", text_data)
#        # dataobj = mongo_handler.get_data_from_db_by_obj_ID("knowledges",text_data)
#        # print (f"\n\n\n\nthis is data for list : ")
#        result = []
#        # Loop through each item in the data list
#        for item in text_data:
#            # Ensure the item is a dictionary before accessing its keys
#            if isinstance(item, dict):
#                # Get the 'Question' and 'Answer' fields with a default fallback
#                question = item.get('Question', 'No Question')
#                answer = item.get('Answer', 'No Answer')
#                # Format the output string
#                formatted_output = f"Question: {question}\nAnswer: {answer.strip()}"  # Using strip() to remove extra newline
#                # Append the formatted output to the result list
#                result.append(formatted_output)
#            else:
#                # If the item isn't a dictionary, raise a TypeError
#                raise TypeError("Each item in the data list must be a dictionary")
#            # Print the formatted result
#            # for item in result:
#            #     print(item)
#            #     print("-" * 20)  # Separator for readability
#        print ("theese are result::",result)
#        pine_cone_initializer.initialize_pinecone(index_name=Index_name)
#            # Use the provided text data to perform operations, e.g., embedding with Pinecone
#        abc= pine_cone_initializer.Embeding_Text_list_to_pinecone(result, Index_name,File_type,Index_name,Knowledge_baseID)
#        print (abc)
#            # Assuming successful operation, return a success message
#        return {"message": "Embedding successful"}
#
#    except Exception as e:
#        # Return the error message if an exception occurs
#        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
#  
#@upload_pdf_router.post ("/vector_data_embeding")
#async def vector_data_embding (data:dict ):
#    agent_id = data.get ("agent_id")
#    
#    knowledgebaseData = mongo_handler.get_all_data_by_array_value("knowledges","AgentID",agent_id )
#    print ("knowledgebase  data ",knowledgebaseData)
#    result = []
#    if not knowledgebaseData:
#        knowledgebaseData =[]
#        return "no data found to be embeded"
#    else :
#        for item in knowledgebaseData:
#                # Ensure the item is a dictionary before accessing its keys
#            if isinstance(item, dict):
#                # Get the 'Question' and 'Answer' fields with a default fallback
#                question = item.get('Question', 'No Question')
#                answer = item.get('Answer', 'No Answer')
#                # Format the output string
#                formatted_output = f"Question: {question}\nAnswer: {answer.strip()}"  # Using strip() to remove extra newline
#                # Append the formatted output to the result list
#                result.append(formatted_output)
#            else:
#                # If the item isn't a dictionary, raise a TypeError
#                raise TypeError("Each item in the data list must be a dictionary")
#        print ("theese are result::",result)
#        pine_cone_initializer.initialize_pinecone(index_name=agent_id)
#            # Use the provided text data to perform operations, e.g., embedding with Pinecone
#        abc= pine_cone_initializer.Embeding_Text_list_to_pinecone(result, agent_id,agent_id)
#        print (abc)
#    # json.dump(knowledgebaseData)
#    # knowledge=convert_to_string(knowledgebaseData)
#    # print ("stirn knowledge ",knowledge)

import os
import requests
from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
import pdfplumber
from langchain_core.documents import Document
from pinecone_configs.pinecone_configs import pine_cone_initializer
from mongodb_config.mongo_db_config import mongo_handler
from PyPDF2 import PdfMerger
upload_pdf_router = APIRouter()

class PDFLinkRequest(BaseModel):
    links: List[str]
    index_name: str

class PDFNameResponse(BaseModel):
    pdf_names: List[str]

class TextEmbeddingRequest(BaseModel):
    Admin_id: str
    Embeding_data: list
    knowledgebase_ID: str
    File_type: str

class FileUpload(BaseModel):
    file_link: str
    file_name: str

def download_pdf(url: str, filename: str) -> str:
    os.makedirs('data', exist_ok=True)
    filepath = os.path.join('data', filename)
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(filepath, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)
    return filepath

def merge_pdfs(pdf_files: List[str], output_filename: str) -> str:
    merger = PdfMerger()
    for pdf in pdf_files:
        merger.append(pdf)
    output_path = os.path.join('data', output_filename)
    merger.write(output_path)
    merger.close()
    return output_path

def extract_text_from_pdf(pdf_path: str) -> List[str]:
    text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
    return text

def texts_to_documents(texts: List[str], source: str) -> List[Document]:
    documents = []
    for i, text in enumerate(texts):
        doc = Document(
            page_content=text,
            metadata={
                'source': source,
                'page': i
            }
        )
        documents.append(doc)
    return documents


def get_valid_index_name(name: str) -> str:
    return ''.join(c.lower() if c.isalnum() else '-' for c in os.path.splitext(name)[0])

@upload_pdf_router.post("/process_pdf_links")
async def process_pdf_links(request: PDFLinkRequest):
    try:
        
        pdf_files = []
        valid_index_name = get_valid_index_name(request.index_name)

        # Download all PDFs
        for i, link in enumerate(request.links):
            filename = f"temp_part_{i+1}.pdf"
            pdf_path = download_pdf(link, filename)
            pdf_files.append(pdf_path)

        # Merge PDFs
        merged_pdf_path = merge_pdfs(pdf_files, f"{valid_index_name}.pdf")

        # Extract text from merged PDF
        all_texts = extract_text_from_pdf(merged_pdf_path)

        # Combine all texts into a single list of documents
        documents = texts_to_documents(all_texts, valid_index_name)

        # Initialize a single Pinecone index
        pine_cone_initializer.initialize_pinecone(valid_index_name)

        # Embed all documents into the single index
        vector_store = pine_cone_initializer.Embeding_Pdf_to_pincecone(documents, index_name=valid_index_name)

        # Save index info
        with open(os.path.join('data', f"{valid_index_name}_info.txt"), 'w') as f:
            f.write(f"Index: {valid_index_name}\n")
            f.write(f"Merged PDF: {valid_index_name}.pdf\n")
            f.write(f"Source PDFs: {', '.join(request.links)}\n")

        # Clean up temporary PDF files
        for pdf_file in pdf_files:
            if os.path.exists(pdf_file):
                os.remove(pdf_file)

        return {
            "message": "PDFs merged, processed, and embedded into a single index successfully",
            "index_name": valid_index_name,
            "merged_pdf_name": f"{valid_index_name}.pdf"
        }

    except Exception as e:
        # Clean up in case of an error
        for pdf_file in pdf_files:
            if os.path.exists(pdf_file):
                os.remove(pdf_file)
        if 'merged_pdf_path' in locals() and os.path.exists(merged_pdf_path):
            os.remove(merged_pdf_path)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@upload_pdf_router.post("/pdf/upload-pdf")
async def upload_pdf(filerequest: FileUpload):
    try:
        pdf_file_path = download_pdf(filerequest.file_link, filerequest.file_name)
        text = extract_text_from_pdf(pdf_file_path)
        loader = texts_to_documents(text, str(filerequest.file_name))
        
        index_name = get_valid_index_name(filerequest.file_name)
        pine_cone_initializer.initialize_pinecone(index_name)
        vector_store = pine_cone_initializer.Embeding_Pdf_to_pincecone(loader, index_name=index_name)
        
        # Save index info
        with open(os.path.join('data', f"{index_name}_info.txt"), 'w') as f:
            f.write(f"Index: {index_name}\n")
            f.write(f"PDF: {filerequest.file_name}\n")
        
        return {"message": "PDF successfully processed and embedded", "index_name": index_name}
    except Exception as e:
        if os.path.exists(pdf_file_path):
            os.remove(pdf_file_path)
        return {"error": str(e)}

@upload_pdf_router.post("/readpdfDemo")
async def upload_pdfDemo(file: UploadFile = File(...)):
    try:
        filename = file.filename
        filepath = os.path.join('data', filename)
        with open(filepath, 'wb') as pdf_file:
            content = await file.read()
            pdf_file.write(content)

        text = extract_text_from_pdf(filepath)
        loader = texts_to_documents(text, str(filename))
        index_name = get_valid_index_name(filename)
        vector_store = pine_cone_initializer.Embeding_Pdf_to_pincecone(loader, index_name=index_name)
        
        # Save index info
        with open(os.path.join('data', f"{index_name}_info.txt"), 'w') as f:
            f.write(f"Index: {index_name}\n")
            f.write(f"PDF: {filename}\n")
        
        return {"message": "Embedding and file processing successful", "index_name": index_name}
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return {"error": str(e)}

@upload_pdf_router.post("/create_index")
async def create_index(data: dict):
    index_name = get_valid_index_name(data.get("index_name"))
    pine_cone_initializer.initialize_pinecone(index_name)
    return {"message": f"Index '{index_name}' created successfully"}

@upload_pdf_router.delete("/delete_pdf/{index_name}")
async def delete_pdf(index_name: str):
    try:
        info_file = os.path.join('data', f"{index_name}_info.txt")
        if os.path.exists(info_file):
            with open(info_file, 'r') as f:
                lines = f.readlines()
                pdf_name = lines[1].split(': ')[1].strip()
            
            # Delete the PDF file
            pdf_path = os.path.join('data', pdf_name)
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
            
            # Delete the info file
            os.remove(info_file)
            
            # Delete the Pinecone index
            pine_cone_initializer.delete_index_pinecone(index_name)
            
            return {"message": f"PDF '{pdf_name}' and index '{index_name}' deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="PDF info not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@upload_pdf_router.get("/get_pdf_names")
async def get_pdf_names():
    try:
        pdf_infos = []
        for file in os.listdir('data'):
            if file.endswith('_info.txt'):
                with open(os.path.join('data', file), 'r') as f:
                    lines = f.readlines()
                    index_name = lines[0].split(': ')[1].strip()
                    pdf_name = lines[1].split(': ')[1].strip()
                    pdf_infos.append({"index_name": index_name, "pdf_name": pdf_name})
        return {"pdf_infos": pdf_infos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@upload_pdf_router.post("/text_embedding")
async def text_embedding(request: TextEmbeddingRequest):
    try:
        text_data = request.Embeding_data
        Index_name = get_valid_index_name(request.Admin_id)
        Knowledge_baseID = request.knowledgebase_ID
        File_type = request.File_type

        result = []
        for item in text_data:
            if isinstance(item, dict):
                question = item.get('Question', 'No Question')
                answer = item.get('Answer', 'No Answer')
                formatted_output = f"Question: {question}\nAnswer: {answer.strip()}"
                result.append(formatted_output)
            else:
                raise TypeError("Each item in the data list must be a dictionary")

        pine_cone_initializer.initialize_pinecone(index_name=Index_name)
        abc = pine_cone_initializer.Embeding_Text_list_to_pincecone(result, Index_name, File_type, Index_name, Knowledge_baseID)
        return {"message": "Embedding successful"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@upload_pdf_router.post("/vector_data_embeding")
async def vector_data_embding(data: dict):
    agent_id = get_valid_index_name(data.get("agent_id"))
    knowledgebaseData = mongo_handler.get_all_data_by_array_value("knowledges", "AgentID", agent_id)
    
    if not knowledgebaseData:
        return "No data found to be embedded"
    
    result = []
    for item in knowledgebaseData:
        if isinstance(item, dict):
            question = item.get('Question', 'No Question')
            answer = item.get('Answer', 'No Answer')
            formatted_output = f"Question: {question}\nAnswer: {answer.strip()}"
            result.append(formatted_output)
        else:
            raise TypeError("Each item in the data list must be a dictionary")

    pine_cone_initializer.initialize_pinecone(index_name=agent_id)
    abc = pine_cone_initializer.Embeding_Text_list_to_pincecone(result, agent_id, agent_id)
    return {"message": "Vector data embedding successful"}
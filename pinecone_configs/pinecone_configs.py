from dotenv import load_dotenv
import os
from pinecone import Pinecone, ServerlessSpec, PodSpec
import time
# from langchain_openai import OpenAIEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings
from fastapi import APIRouter, UploadFile, File, HTTPException
from langchain_pinecone import PineconeVectorStore
# from langchain_text_splitters import CharacterTextSplitter
from langchain.text_splitter import CharacterTextSplitter
router = APIRouter()
load_dotenv(override=True)
openai_api_key = os.environ.get('OPENAI_API_KEY')

class PineconeInitializer:
    def __init__(self, pinecone_api_key, use_serverless=True):
        self.pinecone_api_key = pinecone_api_key
        self.use_serverless = use_serverless
        self.pc = Pinecone(api_key=self.pinecone_api_key)
    def initialize_pinecone(self, index_name):
        

        if self.use_serverless:
            spec = ServerlessSpec(cloud='aws', region='us-east-1')
        else:
            spec = PodSpec(
                environment="gcp-starter",
                pod_type="p1.x1",
                pods=1
            )

        if index_name in self.pc.list_indexes().names():
            print ("index already exist")
            print ("deleting the index")
            self.pc.delete_index(index_name)
            self.pc.create_index(
                index_name,
                dimension=1536,  # dimensionality of text-embedding-ada-002
                metric='dotproduct',
                spec=spec
            )
            
        else :    
            self.pc.create_index(
                index_name,
                dimension=1536,  # dimensionality of text-embedding-ada-002
                metric='dotproduct',
                spec=spec
            )

        while not self.pc.describe_index(index_name).status['ready']:
            time.sleep(1)

        return self.pc.Index(index_name)
    def show_indexes (self,index_name):
        print (self.pc.list_indexes())
        print (self.pc.describe_index(index_name))
        
    def delete_index_pinecone(self, index_name):
        print ("deleting the index")
        self.pc.delete_index(index_name)
        
        
        
    def Embeding_Pdf_to_pincecone(self,loader,index_name):
        data = loader
        print("now data is   :  ",data)
        text_splitter = CharacterTextSplitter(chunk_size=50, chunk_overlap=4)
        docs = text_splitter.split_documents(data)
        model_name = 'text-embedding-ada-002'
        embeddings = OpenAIEmbeddings(
        model=model_name,
        openai_api_key=openai_api_key
        )
        # index_name = "langchain-retrieval-augmentation-fast"
        vectorstore = PineconeVectorStore.from_documents(docs, embeddings, index_name=index_name)
        print ("Embdeding Done ")
        return vectorstore
    
    # def Embeding_Text_list_to_pinecone (self, texts,index_name,file_type,Agent_id,knowledgebase_ID):
    
    def Embeding_Text_list_to_pinecone (self, texts,index_name,Agent_id):
        try:    # texts = ["Tonight, I call on the Senate to: Pass the Freedom to Vote Act.", "ne of the most serious constitutional responsibilities a President has is nominating someone to serve on the United States Supreme Court.", "One of our nation’s top legal minds, who will continue Justice Breyer’s legacy of excellence."]
            # self.delete_index_pinecone(index_name=index_name)
            # self.initialize_pinecone(index_name=index_name)
            # print (texts)
            model_name = 'text-embedding-ada-002'
            embeddings = OpenAIEmbeddings(
            model=model_name,
            openai_api_key=openai_api_key
            )
            vectorstore_from_texts = PineconeVectorStore.from_texts(
                texts,
                index_name=index_name,
                embedding=embeddings,
                # metadatas=[{"Admin_id":Agent_id,"File_Type":file_type, "Knowledge_base_id":knowledgebase_ID } for _ in texts]
                
                metadatas=[{"Admin_id":Agent_id} for _ in texts]
            )
            print ("Embdeding Done ")
            return vectorstore_from_texts
        except Exception as e:
                print(f"An error occurred: {e}")
                return e
        
    def connect_to_index(self,index_name):
        index = self.pc.Index(index_name)
        time.sleep(1)
        return index
        
        
load_dotenv(override=True)
pinecone_api_key = os.environ.get('PINECONE_API_KEY')
pine_cone_initializer = PineconeInitializer(pinecone_api_key)

# pine_cone_initializer.show_indexes(index_name="langchain-retrieval-augmentation-fast")



# def main():
    # load_dotenv(override=True)
    # pinecone_api_key = os.environ.get('PINECONE_API_KEY')
    # pine_cone_initializer = PineconeInitializer(pinecone_api_key)
    # pine_cone_initializer.show_indexes(index_name="langchain-retrieval-augmentation-fast")
    # openai_api_key = os.environ.get('OPENAI_API_KEY')
    # if not pinecone_api_key or not openai_api_key:
    #     raise ValueError("Pinecone API key or OpenAI API key not found in environment variables.")
    # Initialize Pinecone
    # pinecone_initializer = PineconeInitializer(pinecone_api_key)
    # index_name = 'langchain-retrieval-augmentation-fast'
    # print ("Creating index .....")
    # index = pinecone_initializer.initialize_pinecone(index_name) 
    # print ("Index has been created....")

# # if __name__ == "__main__":
# #     main()

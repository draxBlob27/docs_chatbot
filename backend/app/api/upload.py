''' 
    Api route for uploading file, then writing it to data folder for adding further 
    func in subsequent updates.
'''
from fastapi import APIRouter, UploadFile, File
from app.services.parsing import preprocess_document
from app.services.embedding import embed_file
from app.core.database import store_chunks
from app.models.schema import UploadResponse
import os

router = APIRouter()

UPLOAD_DIR = "/Users/sanilparmar/Desktop/wasserStoff_chatbot/backend/data"

@router.post("/upload/", response_model=UploadResponse)
async def upload_and_process(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())

        chunks = preprocess_document(file_path) #Getting list of chunks based on sentences from file path mentioned.(for any type of file).
        embedded_chunks = embed_file(chunks)    #Creates vector embedding of list of chunks.     
        store_chunks(chunks=chunks, embeddings=embedded_chunks) #storing embeddings in chromadb.

        # Logs displayed in backend(can be found in swagger ui)
        return {
            "filename": file.filename,
            "chunks_stored": len(chunks),
            "message": "File uploaded, parsed, and embedded successfully.",
        }

    except Exception as e:
        return {
            "error": str(e),
            "message": "An error occurred during upload or processing.",
        }

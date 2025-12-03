import os
import chromadb
import librosa
import torch
import numpy as np
import wave
from mutagen import File as MutagenFile
from transformers import ClapModel, ClapProcessor
from tqdm import tqdm

DB_PATH = "./sample_db"
MAX_DURATION = 10.0

class IndexerBackend:
    def __init__(self, db_path=DB_PATH):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Indexer using device: {self.device}")
        #Load Models
        self.model = ClapModel.from_pretrained("laion/clap-htsat-unfused", use_safetensors=True).to(self.device)
        self.processor = ClapProcessor.from_pretrained("laion/clap-htsat-unfused")
        #Create and connect DB
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        self.collection = self.chroma_client.get_or_create_collection(name="samples_library")

    def get_audio_embedding(self, file_path):
        try:
            audio, sr = librosa.load(file_path, sr=48000, duration=MAX_DURATION)
            inputs = self.processor(audio=audio, return_tensors="pt", sampling_rate=sr)
            inputs = {k: v.to(self.device) for k, v in inputs.items()} #Move tensors from the dict to the GPU
            with torch.no_grad():
                embedding = self.model.get_audio_features(**inputs)      
            return embedding.cpu().numpy().tolist()[0]
        except Exception as e:
            print(f"\nError processing {file_path}: {e}")
            return None
        
    def get_duration(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext == '.wav':
                with wave.open(file_path, 'rb') as wf:
                    return wf.getnframes() / float(wf.getframerate())
            elif ext == '.mp3':
                info = MutagenFile(file_path)
                if info is not None and info.info:
                    return info.info.length
        except Exception:
            return None
        return None
    
    def run_indexing(self, folder_path, progress_callback=None): 
        print(f"Scanning {folder_path}...")
        existing_ids = set(self.collection.get()["ids"])
        files_to_process = []

        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(('.wav', '.mp3')):
                    full_path = os.path.join(root, file)
                    full_path = os.path.normpath(full_path)
                    if full_path in existing_ids: #Filter existing ids in DB
                        continue
                    duration = self.get_duration(full_path)
                    if duration is not None and duration <= MAX_DURATION: #Filter by max duration
                        files_to_process.append(full_path)

        print(f"Found {len(files_to_process)} files. Indexing...")
        count = 0
        for i, filepath in enumerate(tqdm(files_to_process)):
            vector  = self.get_audio_embedding(filepath)
            if vector:
                self.collection.add(
                    embeddings=[vector],
                    documents=[filepath],
                    metadatas=[{"filename": os.path.basename(filepath)}],
                    ids=[filepath]
                )
                count += 1
            if progress_callback:
                percent = int(((i+1)/len(files_to_process))*100)
                progress_callback(percent)

        return count

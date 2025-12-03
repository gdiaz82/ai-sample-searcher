import os
from typing import List, Dict, Optional

import torch
import chromadb
from transformers import ClapModel, ClapProcessor


class SampleSearcher:
    """Lightweight searcher wrapper around CLAP + ChromaDB.

    Usage:
      from searcher import SampleSearcher
      s = SampleSearcher(db_path='./sample_db')
      results = s.search('kick drum short', top_k=5)

    Results format: List[dict] with keys: `filename`, `route`, `score`.
    """

    def __init__(
        self,
        db_path: str = "./sample_db",
        model_name: str = "./model_cache",
        device: Optional[str] = None,
    ) -> None:
        self.db_path = db_path
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        # Load model & processor
        print(f"Loading CLAP model on: {self.device}")
        self.model = ClapModel.from_pretrained(model_name, use_safetensors=True).to(self.device)
        self.processor = ClapProcessor.from_pretrained(model_name)

        # Connect to Chroma DB
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Error: DB folder not found at {self.db_path}")

        self.chroma_client = chromadb.PersistentClient(path=self.db_path)
        self.collection = self.chroma_client.get_collection(name="samples_library")

    def search(self, query_text: str, top_k: int = 10) -> List[Dict]:
        """Search for `query_text` and return structured results.

        Returns a list of dicts: { 'filename': ..., 'route': ..., 'score': ... }
        """
        text_inputs = self.processor(text=[query_text], return_tensors="pt")
        text_inputs = {k: v.to(self.device) for k, v in text_inputs.items()}

        with torch.no_grad():
            text_embed = self.model.get_text_features(**text_inputs)

        query_vector = text_embed.cpu().numpy().tolist()[0]
        results = self.collection.query(query_embeddings=[query_vector], n_results=top_k)

        routes = results.get('ids', [[]])[0]
        metadatas = results.get('metadatas', [[]])[0]
        distances = results.get('distances', [[]])[0]

        out: List[Dict] = []
        for i in range(len(routes)):
            filename = metadatas[i].get('filename') if i < len(metadatas) else None
            complete_route = routes[i]
            score = distances[i]
            out.append({'filename': filename, 'route': complete_route, 'score': score})

        return out

    def print_results(self, results: List[Dict], top_k: Optional[int] = None) -> None:
        k = top_k or len(results)
        print("-" * 50)
        print(f"Top {k} Results:")
        print("-" * 50)
        for i, r in enumerate(results[:k]):
            print(f"#{i+1} | {r.get('filename')}")
            print(f"    └ Score: {r.get('score'):.4f} | Route: {r.get('route')}")
            print("")


if __name__ == "__main__":
    # Backwards-compatible interactive CLI
    searcher = SampleSearcher()
    while True:
        user_input = input(">> Describe Sound: ")
        if len(user_input.strip()) > 0:
            results = searcher.search(user_input)
            searcher.print_results(results)
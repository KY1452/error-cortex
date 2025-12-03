import chromadb
import uuid
import os

class RAGEngine:
    def __init__(self, persist_path="./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection(name="error_solutions")

    def add_solution(self, error_msg, stack_trace, solution):
        """
        Stores an error and its solution in the vector DB.
        """
        # We combine message and stack trace for the embedding context
        document = f"{error_msg}\n{stack_trace}"
        
        self.collection.add(
            documents=[document],
            metadatas=[{"solution": solution, "error_msg": error_msg}],
            ids=[str(uuid.uuid4())]
        )
        print(f" [RAG] Stored solution for error: {error_msg[:50]}...")

    def find_similar(self, error_msg, stack_trace, n_results=1):
        """
        Finds the most similar past error and returns its solution.
        """
        query_text = f"{error_msg}\n{stack_trace}"
        
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )

        if results["documents"] and results["documents"][0]:
            # Check distance/relevance if needed, but for now just return top match
            # Chroma returns a list of lists
            first_match_metadata = results["metadatas"][0][0]
            return first_match_metadata["solution"]
        
        return None

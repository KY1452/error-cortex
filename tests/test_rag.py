import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add parent dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from consumer.rag import RAGEngine

class TestRAGEngine(unittest.TestCase):
    @patch("consumer.rag.chromadb")
    def test_add_and_retrieve(self, mock_chromadb):
        # Setup mock
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        mock_client.get_or_create_collection.return_value = mock_collection
        
        # Mock query return
        mock_collection.query.return_value = {
            "documents": [["Error msg\nStack trace"]],
            "metadatas": [[{"solution": "Reboot it", "error_msg": "Error msg"}]]
        }

        rag = RAGEngine()
        
        # Test Add
        rag.add_solution("Error msg", "Stack trace", "Reboot it")
        mock_collection.add.assert_called_once()
        
        # Test Find
        solution = rag.find_similar("Error msg", "Stack trace")
        self.assertEqual(solution, "Reboot it")
        mock_collection.query.assert_called_once()

if __name__ == "__main__":
    unittest.main()

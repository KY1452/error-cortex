import sys
import os
import unittest

# Add project root AND consumer directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "consumer")))

from consumer.main import validate_python_syntax

class TestSyntaxGuardrail(unittest.TestCase):
    def test_valid_code(self):
        text = """
        Here is the fix:
        ```python
        def add(a, b):
            return a + b
        ```
        """
        is_valid, error = validate_python_syntax(text)
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_invalid_code(self):
        text = """
        Here is the fix:
        ```python
        def add(a, b)  # Missing colon
            return a + b
        ```
        """
        is_valid, error = validate_python_syntax(text)
        self.assertFalse(is_valid)
        self.assertIn("Syntax Error", error)

    def test_multiple_blocks(self):
        text = """
        Block 1 (Valid):
        ```python
        x = 1
        ```
        Block 2 (Invalid):
        ```python
        if x == 1
            print("oops")
        ```
        """
        is_valid, error = validate_python_syntax(text)
        self.assertFalse(is_valid)

    def test_no_code(self):
        text = "Just some text without code."
        is_valid, error = validate_python_syntax(text)
        self.assertTrue(is_valid)

if __name__ == "__main__":
    unittest.main()

import unittest
import requests
import sqlite3
from model_numbering_service import DATABASE, app  # Replace 'your_server_file' with the actual name of your server script

BASE_URL = "http://localhost:5001"  # Change if your server is running on a different address

class TestModelNumberingSystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Ensure the database is clean before tests
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM model_details")  # Caution: This will remove all records
            conn.commit()

    def test_add_model_type(self):
        response = requests.post(f"{BASE_URL}/add_model_type/XYX")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "Model type added successfully.")

    def test_pull_and_confirm(self):
        # Pull a model number
        response = requests.get(f"{BASE_URL}/pull/XYZ")
        self.assertEqual(response.status_code, 200)
        model_number = response.json()["number"]
        
        # Confirm the pulled number
        response = requests.post(f"{BASE_URL}/confirm/XYZ/{model_number}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], f"confirmed: SYS-{model_number:04}")

    def test_search(self):
        # Search for the confirmed number
        response = requests.get(f"{BASE_URL}/search/XYZ/0001")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "confirmed")

    def test_release(self):
        # Release the confirmed number
        response = requests.post(f"{BASE_URL}/release/XYZ/0001")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "released")
        
    # ... add more tests for other functionalities as required ...

if __name__ == "__main__":
    unittest.main()

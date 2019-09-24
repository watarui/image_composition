import unittest
import image_composition.app as ic


class TestImageComposition(unittest.TestCase):
    def setUp(self):
        self.app = ic.app.test_client()

    def test_index(self):
        response = self.app.get("/")
        assert response.status_code == 200


if __name__ == "__main__":
    unittest.main()

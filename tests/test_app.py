import unittest
from unittest.mock import patch
from app import create_app

class ServiceContractTests(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def test_liveness(self):
        response = self.client.get("/healthz")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": "ok"})

    def test_readiness(self):
        self.assertEqual(self.client.get("/readyz").json, {"status": "ready"})

    def test_release_identity(self):
        with patch.dict("os.environ", {"APP_VERSION": "release-test"}):
            self.assertEqual(self.client.get("/").json["version"], "release-test")

    def test_unknown_route_is_not_healthy(self):
        self.assertEqual(self.client.get("/missing").status_code, 404)

    def test_health_does_not_accept_mutations(self):
        self.assertEqual(self.client.post("/healthz").status_code, 405)

    def test_head_has_no_body(self):
        response = self.client.head("/healthz")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b"")

if __name__ == "__main__":
    unittest.main()

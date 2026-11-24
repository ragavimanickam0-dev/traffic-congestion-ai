import unittest
from backend.app.utils.security import hash_password, verify_password, create_access_token
from jose import jwt
from backend.app.config import settings

class TestAuthSecurity(unittest.TestCase):

    def test_password_hashing_and_verification(self):
        password = "SecurePassword@123"
        hashed = hash_password(password)

        self.assertNotEqual(password, hashed)
        self.assertTrue(hashed.startswith("$2b$") or hashed.startswith("$2a$"))
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password("WrongPassword@456", hashed))

    def test_jwt_token_creation_and_payload(self):
        payload = {"sub": "42", "email": "tester@trafficintel.ai", "role": "user"}
        token = create_access_token(payload)

        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 20)

        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        self.assertEqual(decoded["sub"], "42")
        self.assertEqual(decoded["email"], "tester@trafficintel.ai")
        self.assertIn("exp", decoded)

if __name__ == "__main__":
    unittest.main()

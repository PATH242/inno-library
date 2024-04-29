import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import ExpiredSignatureError, JWTError

from backend.const import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from backend.security import create_jwt_token, get_user, get_user_from_token


class TestAuthenticationFunctions(unittest.TestCase):

    @patch("backend.security.jwt.encode")
    @patch("backend.security.datetime")
    def test_create_jwt_token(self, mock_datetime, mock_jwt_encode):
        mock_datetime.now.return_value = datetime(2021, 1, 1, tzinfo=timezone.utc)
        test_data = {"user_id": 1}
        mock_jwt_encode.return_value = "token123"

        token = create_jwt_token(test_data)
        _ed = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        exp = datetime(2021, 1, 1, tzinfo=timezone.utc) + _ed

        self.assertEqual(token, "token123")
        mock_jwt_encode.assert_called_once_with(
            {
                "user_id": 1,
                "iat": datetime(2021, 1, 1, tzinfo=timezone.utc),
                "exp": exp,
            },
            SECRET_KEY,
            algorithm=ALGORITHM,
        )

    @patch("backend.security.jwt.decode")
    def test_get_user_from_token_valid(self, mock_jwt_decode):
        mock_jwt_decode.return_value = {"user_id": 1}

        user_id = get_user_from_token("valid_token")

        self.assertEqual(user_id, 1)

    @patch("backend.security.jwt.decode")
    def test_get_user_from_token_invalid(self, mock_jwt_decode):
        mock_jwt_decode.side_effect = JWTError

        with self.assertRaises(HTTPException) as context:
            get_user_from_token("invalid_token")

        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.detail, "Invalid authentication credentials")

    @patch("backend.security.jwt.decode")
    def test_get_user_from_token_expired(self, mock_jwt_decode):
        mock_jwt_decode.side_effect = ExpiredSignatureError

        with self.assertRaises(HTTPException) as context:
            get_user_from_token("expired_token")

        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.detail, "Token has expired")

    @patch("backend.security.get_user_from_token")
    def test_get_user(self, mock_get_user_from_token):
        authorization = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="valid_token"
        )
        mock_get_user_from_token.return_value = 1

        user_id = get_user(authorization)

        self.assertEqual(user_id, 1)
        mock_get_user_from_token.assert_called_once_with("valid_token")

    def test_get_user_invalid_scheme(self):
        authorization = HTTPAuthorizationCredentials(
            scheme="Basic", credentials="some_token"
        )

        with self.assertRaises(HTTPException) as context:
            get_user(authorization)

        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.detail, "Invalid authentication scheme")


if __name__ == "__main__":
    unittest.main()

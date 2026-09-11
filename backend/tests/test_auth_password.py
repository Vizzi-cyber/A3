import asyncio
import unittest
from unittest.mock import MagicMock

from fastapi import HTTPException
from pydantic import ValidationError

from app.api.auth import (
    PasswordChangeRequest,
    _hash_password,
    _verify_password,
    change_password,
)


def _db_with_user(password: str = "Current123"):
    user = MagicMock()
    user.is_active = True
    user.hashed_password = _hash_password(password)

    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = user
    return db, user


def _change(request: PasswordChangeRequest, db: MagicMock):
    return asyncio.run(change_password(request, student_id="student_test", db=db))


class PasswordChangeTests(unittest.TestCase):
    def test_rejects_wrong_current_password(self):
        db, user = _db_with_user()
        original_hash = user.hashed_password

        with self.assertRaises(HTTPException) as exc:
            _change(
                PasswordChangeRequest(
                    current_password="Wrong123",
                    new_password="Replacement456",
                ),
                db,
            )

        self.assertEqual(exc.exception.status_code, 400)
        self.assertEqual(exc.exception.detail, "当前密码不正确")
        self.assertEqual(user.hashed_password, original_hash)
        db.commit.assert_not_called()

    def test_rejects_weak_and_reused_passwords(self):
        with self.assertRaises(ValidationError):
            PasswordChangeRequest(
                current_password="Current123",
                new_password="onlyletters",
            )

        db, _user = _db_with_user()
        with self.assertRaises(HTTPException) as exc:
            _change(
                PasswordChangeRequest(
                    current_password="Current123",
                    new_password="Current123",
                ),
                db,
            )

        self.assertEqual(exc.exception.status_code, 400)
        self.assertEqual(exc.exception.detail, "新密码不能与当前密码相同")
        db.commit.assert_not_called()

    def test_updates_hash_and_commits(self):
        db, user = _db_with_user()

        result = _change(
            PasswordChangeRequest(
                current_password="Current123",
                new_password="Replacement456",
            ),
            db,
        )

        self.assertEqual(result["status"], "success")
        self.assertTrue(_verify_password("Replacement456", user.hashed_password))
        self.assertFalse(_verify_password("Current123", user.hashed_password))
        db.commit.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()

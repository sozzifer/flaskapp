import os

# Use an in-memory SQLite database for tests
os.environ["DATABASE_URL"] = "sqlite://"

from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User, Post


class UserModelCase(unittest.TestCase):
    def setUp(self):
        """Create and push application context"""
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self) -> None:
        """Close database session and remove application context"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hash(self):
        """Test that the correct password hash is returned for a given password"""
        u = User(username="sozzifer")
        u.set_password("password")
        self.assertTrue(u.check_password("password"))
        self.assertFalse(u.check_password("otherpassword"))

    def test_avatar(self):
        """Test that the correct Gravator URL is returned for a given user"""
        u = User(username="sozzifer", email="sozzifer@gmail.com")
        self.assertEqual(
            u.avatar(128),
            (
                "https://www.gravatar.com/avatar/1001746e8b5ebd9b1be9c67eaac5ce2d?d=monsterid&s=128"
            ),
        )

    def test_follow(self):
        """Test that the follow() and unfollow() methods work as expected"""
        u1 = User(username="sozzifer", email="sozzifer@gmail.com")
        u2 = User(username="bill", email="bill@gmail.com")
        db.session.add_all([u1, u2])
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u1.followers.all(), [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, "bill")
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, "sozzifer")

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)

    def test_follow_posts(self):
        """Test that the correct posts are returned based on who users are following"""
        u1 = User(username="john", email="john@example.com")
        u2 = User(username="susan", email="susan@example.com")
        u3 = User(username="mary", email="mary@example.com")
        u4 = User(username="david", email="david@example.com")
        db.session.add_all([u1, u2, u3, u4])

        now = datetime.utcnow()
        p1 = Post(
            body="John's first post", author=u1, timestamp=now + timedelta(seconds=1)
        )
        p2 = Post(
            body="Susan's first post", author=u2, timestamp=now + timedelta(seconds=4)
        )
        p3 = Post(
            body="Mary's first post", author=u3, timestamp=now + timedelta(seconds=3)
        )
        p4 = Post(
            body="David's first post", author=u4, timestamp=now + timedelta(seconds=2)
        )
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        u1.follow(u2)
        u1.follow(u4)
        u2.follow(u3)
        u3.follow(u4)
        db.session.commit()

        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])


if __name__ == "__main__":
    unittest.main(verbosity=2)

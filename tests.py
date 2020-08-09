from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User, Project

class UserModelCase(unittest.TestCase) :
    def setUp(self) :
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
        db.create_all()

    def tearDown(self) :
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self) :
        u = User(username = 'susan123')
        u.set_password('cat123')
        self.assertFalse(u.check_password('dog123'))
        self.assertTrue(u.check_password('cat123'))

    def test_avatar(self) :
        u = User(username = 'john123', email = 'john@example.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/d4c74594d841139328695756648b6bd6?d=identicon&s=128'))

    def test_user_project_membership(self) :
        u1 = User(username = "john123", email = "john@example.com")
        u1.set_password("test_pass")
        p1 = Project(name = "project #1", description = "test project #1")
        db.session.add_all([u1, p1])
        db.session.commit()
        self.assertFalse(u1.is_in_project(p1))
        p1.add_to_project(u1)

        db.session.commit()
        self.assertTrue(u1.is_in_project(p1))

class ProjectModelCase(unittest.TestCase) : 
    def setUp(self) :
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
        db.create_all()

    def tearDown(self) :
        db.session.remove()
        db.drop_all()

    def test_project_membership(self) :
        u1 = User(username = "john123", email = "john@example.com")
        u1.set_password("test_pass")
        db.session.add(u1)
        db.session.commit()
        self.assertEqual(u1.projects.all(), [])

        p1 = Project(name = "project #1", description = "test project #1")
        db.session.add(p1)
        db.session.commit()
        self.assertEqual(p1.members.all(), [])

        p1.add_to_project(u1)
        db.session.commit()
        self.assertEqual(p1.members.count(), 1)
        self.assertEqual(p1.members.first().username, "john123")
        self.assertEqual(u1.projects.count(), 1)
        self.assertEqual(u1.projects.first().name, "project #1")

        p1.remove_from_project(u1)
        db.session.commit()
        self.assertEqual(p1.members.all(), [])
        self.assertEqual(u1.projects.all(), [])

if __name__ == '__main__':
    unittest.main(verbosity = 2)
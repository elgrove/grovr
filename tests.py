from datetime import datetime as dt, timedelta
import unittest
from app import app, db
from app.models import User, Post

class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
    
    def test_password_hashing(self):
        u = User(username='michelle')
        u.set_password('8888')
        self.assertFalse(u.check_password('1111'))
        self.assertTrue(u.check_password('8888'))
    
    def test_follow(self):
        u1 = User(username='john', email='john@john.com')
        u2 = User(username='jo', email='jo@jo.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u1.followers.all(), [])

        u1.follow(u2)
        db.session.commit()

        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'jo')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'john')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)
    
    def test_home_feed(self):
        u1 = User(username='one', email='one@one.com')
        u2 = User(username='two', email='two@one.com')
        u3 = User(username='three', email='three@one.com')
        u4 = User(username='four', email='four@one.com')
        users = [u1, u2, u3, u4]

        db.session.add_all(users)

        now = dt.utcnow()
        p1 = Post(body='one', author=u1, timestamp=now+timedelta(seconds=1))
        p2 = Post(body='two', author=u2, timestamp=now+timedelta(seconds=4))
        p3 = Post(body='three', author=u3, timestamp=now+timedelta(seconds=3))
        p4 = Post(body='four', author=u4, timestamp=now+timedelta(seconds=2))
        posts = [p1, p2, p3, p4]
        db.session.add_all(posts)
        db.session.commit()

        u1.follow(u2)
        u1.follow(u4)
        db.session.commit()

        f1 = u1.home_feed_posts().all()
        self.assertEqual(f1, [p2, p4, p1])

if __name__ == '__main__':
    unittest.main(verbosity=2)

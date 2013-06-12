from app import *
app.config['TESTING'] = True
app.config['CSRF_ENABLED'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///utest.db'


u1 = User( 'john', 'john@example.com','111', ROLE_USER,'rrr', FIRST_TIME)
u2 = User('susan', 'susan@example.com','111', ROLE_USER, 'rrr', FIRST_TIME)
db.session.add(u1)
db.session.add(u2)
db.session.commit()
assert u1.unfollow(u2) == None
u = u1.follow(u2)
db.session.add(u)
db.session.commit()
assert u1.follow(u2) == None
assert u1.is_following(u2)
assert u1.followed.count() == 1
assert u1.followed.first().username == 'susan'
assert u2.followers.count() == 1
assert u2.followers.first().username == 'john'
u = u1.unfollow(u2)
assert u != None
db.session.add(u)
db.session.commit()
assert u1.is_following(u2) == False
assert u1.followed.count() == 0
assert u2.followers.count() == 0

print 'All tests is passed'

if __name__=='__main__':
    unittest.main()
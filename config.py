#forms config
CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

import os
basedir = os.path.abspath(os.path.dirname(__file__))

#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
#app.config['SQLALCHEMY_MIGRATE_REPO'] = 'db_repository'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

#mail server settings
MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'levushka14'
MAIL_PASSWORD = 'cnhtkmxer17'

#administrator list
ADMINS = ['levushka14@gmail.com']


#full text search
WHOOSH_BASE = os.path.join(basedir, 'search.db')
MAX_SEARCH_RESULTS = 50

#available languages
LANGUAGES = {
        'en': 'English',
        'ru': 'Russian'
}

#pagination
POSTS_PER_PAGE = 10

# Whoosh does not work on Heroku
WHOOSH_ENABLED = os.environ.get('HEROKU') is None

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

if 'AUFM_DB' in os.environ:
    connection = os.environ['AUFM_DB']
else:
    connection = 'sqlite:///DemoTest.db'

print('Connecting to database at {}'.format(connection))
engine = create_engine(connection, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # Import models here
    from .models import User, Protocol
    Base.metadata.create_all(bind=engine)

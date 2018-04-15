import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from . import models

if 'AUFM_DB' in os.environ:
    connection = os.environ['AUFM_DB']
else:
    connection = 'sqlite:///DemoTest.db'

print('Connecting to database at {}'.format(connection))
engine = create_engine(connection, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=True,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # Import models here
    Base.metadata.create_all(bind=engine)

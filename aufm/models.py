from sqlalchemy import Column, Integer, String, SmallInteger
from aufm.database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(128))
    password = Column(String(64))
    permissions = Column(SmallInteger)

    def __init__(self, first_name=None, last_name=None, email=None, password=None,
                 permissions=None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.permissions = permissions

    def __repr__(self):
        return '<User {} {}>'.format(self.first_name, self.last_name)

    def to_json(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'permissions': self.permissions
        }


class Protocol(Base):
    __tablename__ = 'protocols'
    id = Column(Integer, primary_key=True) # autoincrement is automatic
    element_id = Column(Integer)
    property = Column(String(64))
    value = Column(String(512))

    def __init__(self, id=None, element_id=None, property=None, value=None):
        self.id = id
        self.element_id = element_id
        self.property = property
        self.value = value

    def __repr__(self):
        return '<Protocol {}:{}'.format(self.id, self.element_id)

    def to_json(self):
        return {
            'id': self.id,
            'element_id': self.element_id,
            'property': self.property,
            'value': self.value
        }


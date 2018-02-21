from sqlalchemy import Column, Integer, String, SmallInteger, ForeignKey
from aufm.database import Base


class User(Base):
    """Relation that defines a user to the system"""
    __tablename__ = 'users'
    user_id = Column('user_id', Integer, primary_key=True)
    first_name = Column('first_name', String(50))
    last_name = Column('last_name', String(50))
    email = Column('email', String(128))
    password = Column('password', String(64))
    permissions = Column('permissions', SmallInteger)

    def __init__(self, first_name=None, last_name=None, email=None,
                 password=None, permissions=None):
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


class Building(Base):
    """Relation that defines building in the system"""
    __tablename__ = 'buildings'
    building_id = Column('building_id', Integer, primary_key=True)
    name = Column(String(64))

    def __init__(self, building_id=None, name=None):
        self.building_id = building_id
        self.name = name


class Part(Base):
    """Relation that represents individual parts"""
    __tablename__ = 'parts'
    part_id = Column('part_id', Integer, primary_key=True)
    element_id = Column('element_id', Integer)
    building_id = Column('building_id', Integer,
                         ForeignKey('buildings.building_id'))

    def __init__(self, part_id=None, element_id=None, building_id=None):
        self.part_id = part_id
        self.element_id = element_id
        self.building_id = building_id


class Protocol(Base):
    """Relation that represents a protocol"""
    __tablename__ = 'protocols'
    protocol_id = Column('protocol_id', Integer, primary_key=True)
    value = Column(String(1024))

    def __init__(self, protocol_id=None, property=None, value=None):
        self.protocol_id = protocol_id
        self.element_id = element_id
        self.property = property
        self.value = value

    def __repr__(self):
        return '<Protocol {}:{}'.format(self.protocol_id, self.element_id)

    def to_json(self):
        return {
            'protocol_id': self.protocol_id,
            'element_id': self.element_id,
            'property': self.property,
            'value': self.value
        }


class PartProtocol(Base):
    """Relation that connects parts to protocols (and vice versa)"""
    __tablename__ = 'parts_protocols'
    part_id = Column('part_id', Integer, ForeignKey('parts.part_id'),
                     primary_key=True)
    protocol_id = Column('protocol_id', Integer,
                         ForeignKey('protocols.protocol_id'), primary_key=True)

    def __init__(self, part_id=None, protocol_id=None):
        self.part_id = part_id
        self.protocol_id = protocol_id


import bcrypt
from time import time
from aufm import app
from aufm.models import User, Protocol, Building, PartProtocol, Part, ProtocolFamily, ProtocolFamilyProtocol
from aufm.database import db_session
import bcrypt
from flask import jsonify, request, render_template
from flask_login import login_required, login_user, current_user
from flask_mail import Message


@app.route('/api/request-password-reset', methods=['POST'])
def request_reset():
    if not request.is_json:
        return _error('Request must be JSON type', 400)
    form = request.get_json()
    user = User.query.filter(User.email==form['email']).first()
    if user is None:
        return _error('Account with specified email not found', 404)
    now = int(time())
    user.password_reset_time = now
    user.password_reset = bcrypt.hashpw(str(now).encode('utf-8'), bcrypt.gensalt())
    db_session.add(user)
    db_session.commit()
    # Email the user the reset token
    msg = Message('AUFM Password Reset',
                  sender='do.not.reply.aufm@gmail.com',
                  recipients=[user.email])
    msg.body = ('Click the following link to reset your password: {}/#password-reset/{}'
                .format(request.url_root, user.password_reset))
    app.mail.send(msg)
    return jsonify({'status': 'Reset message sent'})


@app.route('/api/password-reset', methods=['POST'])
def reset_password():
    if not request.json:
        return _error('Request must be JSON type', 400)
    form = request.get_json()
    user = User.query.filter(User.email==form['email']).first()
    if user is None:
        return _error('Account with specified email not found', 404)
    now = int(time())
    if now - user.password_reset_time > 60*60*24:
        # Request is older than a day
        return _error('Password reset has expired', 400)
    if not form['reset_token'] == user.password_reset:
        return _error('Reset token does not match', 400)
    hashed = bcrypt.hashpw(form['new_password'].encode('utf-8'), bcrypt.gensalt())
    user.password = hashed
    user.password_reset = None
    user.password_reset_time = None
    db_session.add(user)
    db_session.commit()
    return jsonify({'status': 'Password successfully reset'})


@app.route('/api/login', methods=['POST'])
def login():
    if not request.is_json:
        return _error('Request must be JSON type', 400)
    form = request.get_json()
    user = User.query.filter(User.email==form['email']).first()
    if user is None:
        return _error('Invalid login credentials', 400)
    if bcrypt.checkpw(form['password'].encode('utf-8'), user.password):
        login_user(user)
        return jsonify({'status': 'Logged in successfully'})
    return _error('Invalid login credentials', 400)


@app.route('/api/user', methods=['POST'])
def create_new_user():
    if not request.is_json:
        return _error('Request must be JSON type', 400)
    form = request.get_json()
    hashed = bcrypt.hashpw(form['password'].encode('utf-8'), bcrypt.gensalt())
    user = User.query.filter(User.email == form['email']).all()
    if user is not None:
        return _error('An account with that email already exists', 400)
    new_user = User(
            first_name=form.get('first_name'), last_name=form.get('last_name'),
            email=form['email'], password=hashed
    )
    db_session.add(new_user)
    db_session.commit()
    return jsonify(new_user.to_json())


@app.route('/api/update-password', methods=['POST'])
@login_required
def update_password():
    if not request.is_json:
        return _error('Request must be JSON type', 400)
    form = request.get_json()
    if not bcrypt.checkpw(form['old_password'].encode('utf-8'), current_user.password):
        return _error('Invalid credentials', 400)
    p = bcrypt.hashpw(form['new_password'].encode('utf-8'), bcrypt.gensalt())
    current_user.password = p
    db_session.add(current_user)
    db_session.commit()
    return jsonify(current_user.to_json())


@app.route('/api/part/<int:element_id>', methods=['GET', 'PUT', 'DELETE'])
def part_info(element_id):
    part = Part.query.filter(Part.element_id==element_id).first()
    if part is None:
        return _error('Part not found', 404)
    if request.method == 'DELETE':
        part_id = part.part_id
        db_session.delete(part)
        db_session.commit()
        return jsonify({'part_id': part_id})
    if request.method == 'PUT':
        if not request.is_json:
            return _error('Request must be JSON type', 400)
        form = request.get_json()
        if 'building_id' in form and form['building_id'] is not None:
            # Validate that the building exists
            building = (Building.query
                    .filter(Building.building_id==form['building_id']).first())
            if building is None:
                return _error('Specified building does not exist', 404)
        if not set(form.keys()).issubset(part.to_json().keys()):
            return _error('Unknown properties specified in request', 400)
        part.element_id = form.get('element_id')
        part.building_id = form.get('building_id')
        part.part_name = form.get('part_name')
        db_session.add(part)
        db_session.commit()
    return jsonify(part.to_json())


@app.route('/api/part', methods=['GET', 'POST'])
def get_or_add_parts():
    if request.method == 'GET':
        parts = Part.query.all()
        return jsonify([p.to_json() for p in parts])
    # Attempting to add a new part
    if not request.is_json:
        return _error('Request must be JSON type', 400)
    form = request.get_json()
    if 'element_id' not in form:
        return _error('Must specify element_id', 400)
    if form.get('building_id') is not None:
        # Make sure the building exists
        building = (Building.query
                .filter(Building.building_id==form['building_id']).first())
        if building is None:
            return _error('building_id does not exist', 404)
    part = Part(
        element_id=form['element_id'],
        part_name=form['part_name'],
        building_id=form.get('building_id')
    )
    db_session.add(part)
    db_session.commit()
    return jsonify(part.to_json())


@app.route('/api/part/<int:element_id>/protocol', methods=['GET'])
def get_all_protocols_for_part(element_id):
    part = Part.query.filter(Part.element_id==element_id).first()
    if part is None:
        return _error('Specified part does not exist', 404)
    joined = (Protocol.query
            .join(PartProtocol)
            .join(Part)
            .filter(Part.element_id==element_id)
            .all())
    return jsonify({
        'part_id': part.part_id,
        'element_id': part.element_id,
        'protocols': [proto.to_json() for proto in joined]
    })


@app.route('/api/part/<int:element_id>/protocol/<int:protocol_id>',
           methods=['POST', 'DELETE'])
def connect_part_protocol(element_id, protocol_id):
    part = Part.query.filter(Part.element_id==element_id).first()
    if part is None:
        return _error('Part element_id does not exist', 404)
    protocol = Protocol.query.filter(Protocol.protocol_id==protocol_id).first()
    if protocol is None:
        return _error('Protocol protocol_id does not exist', 404)
    pp = (PartProtocol.query.filter(
            PartProtocol.part_id==part.part_id,
            PartProtocol.protocol_id==protocol_id).first())
    if request.method == 'POST':
        if pp is not None:
            return _error('Protocol is already associated with that part', 400)
        pp = PartProtocol(part_id=part.part_id, protocol_id=protocol_id)
        db_session.add(pp)
        db_session.commit()
        return jsonify(pp.to_json())
    # Must be a delete
    if pp is None:
        return _error('Part protocol relationship does not exist', 404)
    to_delete = pp.to_json()
    db_session.delete(pp)
    db_session.commit()
    return jsonify(to_delete)


@app.route('/api/protocol', methods=['GET', 'POST'])
def get_all_protocols():
    if request.method == 'GET':
        protocols = Protocol.query.all()
        return jsonify([p.to_json() for p in protocols])
    # Trying to add a new protocol
    if not request.is_json:
        return _error('Request must be JSON type', 400)
    form = request.get_json()
    if 'value' not in form:
        return _error('Protocol value not specified', 400)
    protocol = Protocol(value=form['value'])
    db_session.add(protocol)
    db_session.commit()
    return jsonify(protocol.to_json())


@app.route('/api/protocol/<int:protocol_id>', methods=['GET', 'PUT', 'DELETE'])
def get_protocol(protocol_id):
    p = Protocol.query.filter(Protocol.protocol_id==protocol_id).first()
    if p is None:
        return _error('Specified protocol does not exist', 404)
    if request.method == 'DELETE':
        db_session.delete(p)
        db_session.commit()
        return jsonify({'protocol_id': protocol_id})
    if request.method == 'PUT':
        if not request.is_json:
            return _error('Request must be JSON type', 400)
        form = request.get_json()
        if 'value' not in form:
            return _error('Protocol value not specified', 400)
        if not set(form.keys()).issubset({'value'}):
            return _error('Unknown keys specified', 400)
        p.value = form['value']
        db_session.commit()
    return jsonify(p.to_json())


@app.route('/api/building', methods=['GET', 'POST'])
def get_all_buildings():
    if request.method == 'GET':
        buildings = Building.query.all()
        return jsonify([b.to_json() for b in buildings])
    # Trying to add a new building
    if not request.is_json:
        return _error('Request must be JSON type', 400)
    form = request.get_json()
    if 'name' not in form:
        return _error('Building name not included', 400)
    building = Building(name=form['name'])
    db_session.add(building)
    db_session.commit()
    return jsonify(building.to_json())


@app.route('/api/building/<int:building_id>', methods=['GET', 'PUT', 'DELETE'])
@app.route('/api/building/<name>', methods=['GET', 'PUT', 'DELETE'])
def get_building_by_identifier(building_id=None, name=None):
    # Validate that the building exists
    if building_id is not None:
        # Lookup by id
        building = (Building.query
                .filter(Building.building_id==building_id).first())
    else:
        # Lookup by name
        building = (Building.query
                .filter(Building.name==name).first())
    if building is None:
        return _error('The specified building does not exist', 404)
    if request.method == 'DELETE':
        bid = building.building_id
        db_session.delete(building)
        db_session.commit()
        return jsonify({'building_id': bid})
    if request.method == 'PUT':
        if not request.is_json:
            return _error('Request must be JSON type', 400)
        form = request.get_json()
        if 'name' not in form:
            return _error('Name key not specified', 400)
        if not set(form.keys()).issubset({'name'}):
            return _error('Extra keys specified', 400)
        building.name = form['name']
        db_session.commit()
    return jsonify(building.to_json())


@app.route('/api/building/<int:building_id>/part', methods=['GET'])
@app.route('/api/building/<name>/part', methods=['GET'])
def get_parts_in_building(building_id=None, name=None):
    if building_id is not None:
        # Lookup by id
        building = (Building.query
                .filter(Building.building_id==building_id).first())
    else:
        # Lookup by name
        building = (Building.query
                .filter(Building.name==name).first())
    if building is None:
        return _error('The specified building does not exist', 404)
    parts = Part.query.filter(Part.building_id==building.building_id).all()
    building_json = building.to_json()
    building_json['parts'] = [p.to_json() for p in parts]
    return jsonify(building_json)


@app.route('/api/protocol-family', methods=['GET', 'POST'])
def get_all_protocol_families():
    if request.method == 'GET':
        families = ProtocolFamily.query.all()
        return jsonify([f.to_json() for f in families])
    # Must be a POST
    if not request.is_json:
        return _error('Request must be JSON', 400)
    form = request.get_json()
    if 'family_name' not in form:
        return _error('family_name key not specified', 400)
    if not set(form.keys()).issubset({'family_name'}):
        return _error('Extra keys specified', 400)
    pf = ProtocolFamily(family_name=form['family_name'])
    db_session.add(pf)
    db_session.commit()
    return jsonify(pf.to_json())


@app.route('/api/protocol-family/<int:family_id>', methods=['GET', 'PUT', 'DELETE'])
def get_protocols_for_family(family_id):
    if request.method == 'GET':
        protocol_family = (ProtocolFamily.query
                .filter(ProtocolFamily.family_id==family_id).first())
        if protocol_family is None:
            return _error('Protocol family does not exist', 404)
        family_protocols = (ProtocolFamilyProtocol.query
                .filter(ProtocolFamilyProtocol.family_id==family_id).all())
        protocols = list()
        for family_protocol in family_protocols:
            p = Protocol.query.filter(Protocol.protocol_id==family_protocol.protocol_id)
            protocols.append(p.first().to_json())
        resp = {
            'family_id': family_id,
            'family_name': protocol_family.family_name,
            'protocols': protocols
        }
        return jsonify(resp)
    pf = ProtocolFamily.query.filter(ProtocolFamily.family_id==family_id).first()
    if pf is None:
        return _error('Protocol family does not exist', 404)
    if request.method == 'PUT':
        if not request.is_json:
            return _error('Request must be JSON type', 400)
        form = request.get_json()
        if not 'family_name' in form:
            return _error('family_name key not specified', 400)
        if not set(form.keys()).issubset({'family_name'}):
            return _error('Extra keys specified', 400)
        pf.family_name = form['family_name']
        db_session.commit()
        return jsonify(pf.to_json())
    # Must be a delete
    to_delete = pf.to_json()
    db_session.delete(pf)
    db_session.commit()
    return jsonify(to_delete)


@app.route('/api/protocol-family/<int:family_id>/protocol/<int:protocol_id>',
           methods=['POST', 'DELETE'])
def add_remove_protocol_family_association(family_id, protocol_id):
    family = ProtocolFamily.query.filter(ProtocolFamily.family_id==family_id).first()
    if family is None:
        return _error('Protocol family does not exist', 404)
    protocol = Protocol.query.filter(Protocol.protocol_id==protocol_id).first()
    if protocol is None:
        return _error('Protocol does not exists', 404)
    pfp = ProtocolFamilyProtocol.query.filter(
            ProtocolFamilyProtocol.family_id==family.family_id,
            ProtocolFamilyProtocol.protocol_id==protocol.protocol_id).first()
    if request.method == 'POST':
        if pfp is not None:
            return _error('Protocol already exists in specified family', 400)
        pfp = ProtocolFamilyProtocol(family.family_id, protocol.protocol_id)
        db_session.add(pfp)
        db_session.commit()
        return jsonify(pfp.to_json())
    # Must be a delete
    if pfp is None:
        return _error('Protocol does not exist in specified family', 404)
    to_delete = pfp.to_json()
    db_session.delete(pfp)
    db_session.commit()
    return jsonify(to_delete)


@app.route('/')
def index():
    return render_template('aufm.html')


def _error(message, code):
    """Convenience method for returning an error code"""
    return jsonify({'Error': message}), code


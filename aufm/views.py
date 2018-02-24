from aufm import app
from aufm.models import User, Protocol, Building, PartProtocol, Part
from aufm.database import db_session
from flask import jsonify, request


@app.route('/api/user', methods=['GET', 'POST'])
def get_all_users():
    if request.method == 'GET':
        return jsonify([u.to_json() for u in User.query.all()])
    return jsonify({'Error': 'Not yet implemented'}), 501


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
        building_id=form.get('building_id')
    )
    db_session.add(part)
    db_session.commit()
    return jsonify(part.to_json())


@app.route('/api/part/<int:element_id>/protocol')
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
    if request.method == 'POST':
        pp = PartProtocol(part_id=part.part_id, protocol_id=protocol_id)
        db_session.add(pp)
        db_session.commit()
        return jsonify(pp.to_json())
    # Must be a delete
    pp = (PartProtocol.query.filter(
            PartProtocol.part_id==part.part_id,
            PartProtocol.protocol_id==protocol_id).first())
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


def _error(message, code):
    """Convenience method for returning an error code"""
    return jsonify({'Error': message}), code


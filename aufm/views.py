from aufm import app
from aufm.models import User, Protocol
from flask import jsonify, request


@app.route('/api/users', methods=['GET', 'POST'])
def get_all_users():
    if request.method == 'GET':
        return jsonify([u.to_json() for u in User.query.all()])
    return jsonify({'Error': 'Not yet implemented'}), 501


@app.route('/api/part/<int:part_id>', methods=['GET', 'POST'])
def part_info(part_id):
    if request.method == 'GET':
        part = Protocol.query.filter(Protocol.element_id == part_id).first()
        if part is None:
            return jsonify({'Error': 'Part not found'}), 404
        return jsonify(part.to_json())
    return jsonify({'Error': 'Not yet implemented'}), 501


@app.route('/api/part')
def get_all_parts():
    part = Protocol.query.all()
    return jsonify([p.to_json() for p in part])



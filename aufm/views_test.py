import json
import os
import unittest

from aufm import app
from aufm.database import Base, engine, db_session
from aufm.models import User, Protocol, Building, PartProtocol, Part


class ViewsTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(ViewsTest, self).__init__(*args, **kwargs)
        self.user1 = User(first_name='Brandon', last_name='Morris',
                          email='blm0026@auburn.edu', password='password',
                          permissions=0)
        self.user2 = User(first_name='Lance', last_name='McGunner',
                          email='bp27@hotmail', password='password',
                          permissions=0)
        self.part1 = Part(element_id=1234)
        self.part2 = Part(element_id=5678)
        self.building1 = Building(name='Shelby')
        self.building2 = Building(name='Parker')

    def setUp(self):
        app.testing = True
        self.app = app.test_client()
        with app.app_context():
            Base.metadata.create_all(bind=engine)

    def tearDown(self):
        with app.app_context():
            Base.metadata.drop_all(bind=engine)

    def test_getting_no_users(self):
        resp = self.app.get('/api/user')
        self.assertEquals(json.loads(resp.get_data()), [])

    def test_getting_some_users(self):
        db_session.add_all([self.user1, self.user2])
        db_session.commit()

        resp = json.loads(self.app.get('/api/user').get_data())
        self.assertEqual(len(resp), 2)
        if resp[0]['first_name'] == 'Brandon':
            self.assertEqual(resp[0], self.user1.to_json())
            self.assertEqual(resp[1], self.user2.to_json())
        else:
            self.assertEqual(resp[1], self.user1.to_json())
            self.assertEqual(resp[0], self.user2.to_json())

    def test_adding_a_user(self):
        return # FIXME: Not yet implemented
        resp = self.app.post('/api/user', content_type='application/json',
                             data=json.dumps(self.user1.to_json()))
        resp = json.loads(resp.get_data())
        added = User.query.first()
        self.assertEqual(added.to_json(), resp)

    def test_get_no_parts(self):
        resp = json.loads(self.app.get('/api/part').get_data())
        self.assertEqual(resp, [])

    def test_get_some_parts(self):
        p1 = Part(element_id=1234, building_id=3)
        p2 = Part(element_id=4567)
        db_session.add_all([p1, p2])
        db_session.commit()

        resp = json.loads(self.app.get('/api/part').get_data())
        self.assertEqual(len(resp), 2)
        if resp[0]['element_id'] == 1234:
            self.assertEqual(resp[0], p1.to_json())
            self.assertEqual(resp[1], p2.to_json())
        else:
            self.assertEqual(resp[1], p1.to_json())
            self.assertEqual(resp[0], p2.to_json())

    def test_add_part(self):
        p = Part(element_id=1234)
        raw = self.app.post('/api/part', data=json.dumps(p.to_json()),
                            content_type='application/json')
        resp = json.loads(raw.get_data())
        added = Part.query.first()
        self.assertEqual(resp, added.to_json())

    def test_get_part_by_element_id(self):
        p = Part(element_id=1234)
        db_session.add(p)
        db_session.commit()
        resp = json.loads(self.app.get('/api/part/1234').get_data())
        self.assertEqual(p.to_json(), resp)

    def test_update_part_by_id(self):
        # FIXME: Not yet implemented
        pass

    def test_get_protocols_by_part(self):
        part = Part(element_id=1234)
        protocol = Protocol(value='Turn off the lights when leaving')
        other_protocol = Protocol(value='Wash your hands')
        db_session.add_all([part, protocol, other_protocol])
        db_session.commit()
        part_protocol = PartProtocol(part_id=part.part_id,
                                     protocol_id=protocol.protocol_id)
        db_session.add(part_protocol)
        db_session.commit()
        raw = self.app.get('/api/part/{}/protocol'.format(part.element_id))
        resp = json.loads(raw.get_data())
        expected = {
            'part_id': part.part_id,
            'element_id': part.element_id,
            'protocols': [protocol.to_json()]
        }
        self.assertEqual(resp, expected)

    def test_connect_part_protocol(self):
        part = Part(element_id=1234)
        protocol = Protocol(value='Turn off the lights when leaving')
        db_session.add_all([part, protocol])
        db_session.commit()
        raw = self.app.post('/api/part/{}/protocol/{}'
                .format(part.element_id, protocol.protocol_id))
        resp = json.loads(raw.data)
        added = PartProtocol.query.first()
        self.assertEqual(resp, added.to_json())

    def test_connect_part_protocol_nonexistent_part_fails(self):
        protocol = Protocol(value='Turn off the lights when leaving')
        db_session.add(protocol)
        db_session.commit()
        raw = self.app.post('/api/part/{}/protocol/{}'
                .format(100, protocol.protocol_id))
        self.assertEqual(raw.status_code, 404)
        resp = json.loads(raw.data)
        self.assertTrue(resp['Error'].startswith('Part'))

    def test_connect_part_protocol_nonexistent_protocol_fails(self):
        part = Part(element_id=1234)
        db_session.add(part)
        db_session.commit()
        raw = self.app.post('/api/part/{}/protocol/{}'
                .format(part.element_id, 100))
        resp = json.loads(raw.data)
        self.assertEqual(raw.status_code, 404)
        self.assertTrue(resp['Error'].startswith('Protocol'))

    def test_get_no_protocols(self):
        resp = json.loads(self.app.get('/api/protocol').get_data())
        self.assertEqual(resp, [])

    def test_get_some_protocols(self):
        p1 = Protocol(value='Don\'t touch the hot thing')
        p2 = Protocol(value='Turn off the lights when you leave')
        db_session.add_all([p1, p2])
        db_session.commit()
        resp = json.loads(self.app.get('/api/protocol').get_data())
        if resp[0]['value'].startswith('Turn'):
            self.assertEqual(p2.to_json(), resp[0])
            self.assertEqual(p1.to_json(), resp[1])
        else:
            self.assertEqual(p2.to_json(), resp[1])
            self.assertEqual(p1.to_json(), resp[0])

    def test_add_protocol(self):
        p = Protocol(value='Turn off the lights')
        raw = self.app.post('/api/protocol', content_type='application/json',
                            data=json.dumps(p.to_json()))
        resp = json.loads(raw.get_data())
        added = Protocol.query.first()
        self.assertEqual(added.to_json(), resp)

    def test_get_protocol_by_protocol_id(self):
        p = Protocol(value='Turn off the lights')
        db_session.add(p)
        db_session.commit()
        raw = self.app.get('/api/protocol/{}'.format(p.protocol_id))
        resp = json.loads(raw.get_data())
        self.assertEqual(p.to_json(), resp)

    def test_get_no_buildings(self):
        resp = json.loads(self.app.get('/api/building').get_data())
        self.assertEqual(resp, [])

    def test_get_some_buildings(self):
        b1 = Building(name='Shelby')
        b2 = Building(name='Parker')
        db_session.add_all([b1, b2])
        db_session.commit()
        resp = json.loads(self.app.get('/api/building').get_data())
        self.assertEqual(len(resp), 2)
        if resp[0]['name'] == 'Shelby':
            self.assertEqual(b1.to_json(), resp[0])
            self.assertEqual(b2.to_json(), resp[1])
        else:
            self.assertEqual(b1.to_json(), resp[1])
            self.assertEqual(b2.to_json(), resp[0])

    def test_add_new_building(self):
        b = Building(name='Shelby')
        raw = self.app.post('/api/building', content_type='application/json',
                            data=json.dumps(b.to_json()))
        resp = json.loads(raw.get_data())
        added = Building.query.first()
        self.assertEqual(resp, added.to_json())

    def test_get_building_by_building_id(self):
        b = Building(name='Shelby')
        db_session.add(b)
        db_session.commit()
        resp = json.loads(self.app.get(
            '/api/building/{}'.format(b.building_id)).get_data())
        self.assertEqual(resp, b.to_json())

    def test_get_building_by_name(self):
        b = Building(name='Shelby')
        db_session.add(b)
        db_session.commit()
        resp = json.loads(self.app.get(
            '/api/building/{}'.format(b.name)).get_data())
        self.assertEqual(resp, b.to_json())

    def test_adding_part_requires_json(self):
        resp = self.app.post('/api/part', content_type='text/html',
                            data='This is not json')
        self.assertEqual(resp.status_code, 400)

    def test_adding_part_requires_element_id(self):
        resp = self.app.post('/api/part', content_type='application/json',
                             data=json.dumps({'no-value':'no-value'}))
        self.assertEqual(resp.status_code, 400)

    def test_adding_part_to_nonexistent_building_fails(self):
        p = Part(part_id=1, element_id=10).to_json()
        p['building_id'] = 100
        resp = self.app.post('/api/part', content_type='application/json',
                             data=json.dumps(p))
        self.assertEqual(resp.status_code, 404)

    def test_add_protocol_must_be_json(self):
        resp = self.app.post('/api/protocol', content_type='text/html',
                             data='This is not json')
        self.assertEqual(resp.status_code, 400)

    def test_add_part_must_specify_value(self):
        resp = self.app.post('/api/protocol', content_type='application/json',
                             data=json.dumps({'no-value':'no-value'}))
        self.assertEqual(resp.status_code, 400)

    def test_add_building_must_be_json(self):
        resp = self.app.post('/api/building', content_type='text/html',
                             data='This is not json')
        self.assertEqual(resp.status_code, 400)

    def test_add_building_must_specify_name(self):
        resp = self.app.post('/api/building', content_type='application/json',
                             data=json.dumps({'no-name':'no-name'}))
        self.assertEqual(resp.status_code, 400)

    def test_get_parts_for_building_by_building_id(self):
        db_session.add(self.building1)
        db_session.commit()
        self.part1.building_id = self.building1.building_id
        self.part2.building_id = self.building1.building_id
        db_session.add_all([self.part1, self.part2])
        db_session.commit()
        raw = self.app.get('/api/building/{}/part'
                .format(self.building1.building_id))
        resp = json.loads(raw.data)
        expected = self.building1.to_json()
        expected['parts'] = [self.part1.to_json(), self.part2.to_json()]
        self.assertEqual(resp, expected)

    def test_get_parts_for_building_by_building_name(self):
        db_session.add(self.building1)
        db_session.commit()
        self.part1.building_id = self.building1.building_id
        self.part2.building_id = self.building1.building_id
        db_session.add_all([self.part1, self.part2])
        db_session.commit()
        raw = self.app.get('/api/building/{}/part'
                .format(self.building1.name))
        resp = json.loads(raw.data)
        expected = self.building1.to_json()
        expected['parts'] = [self.part1.to_json(), self.part2.to_json()]
        self.assertEqual(resp, expected)

    def test_get_parts_in_nonexistent_building_fails(self):
        raw = self.app.get('/api/building/notreal/part')
        resp = json.loads(raw.data)
        self.assertEqual(raw.status_code, 404)
        self.assertTrue('does not exist' in resp['Error'])

    def test_get_nonexistent_part_fails(self):
        raw = self.app.get('/api/part/1000')
        self.assertEqual(404, raw.status_code)



if __name__ == '__main__':
    unittest.main()

import json
import unittest

from aufm import app
from aufm.database import Base, engine, db_session
from aufm.models import User, Protocol, Building, PartProtocol, Part, ProtocolFamily, ProtocolFamilyProtocol


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
        self.protocol1 = Protocol(value='Wash your hands')
        self.protocol2 = Protocol(value='Turn off the lights')
        self.family1 = ProtocolFamily(family_id=1, family_name='family1')
        self.family2 = ProtocolFamily(family_id=2, family_name='family2')

    def setUp(self):
        app.testing = True
        self.app = app.test_client()
        with app.app_context():
            Base.metadata.create_all(bind=engine)

    def tearDown(self):
        with app.app_context():
            Base.metadata.drop_all(bind=engine)
        db_session.commit()

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
        raw = self.app.post('/api/user', content_type='application/json',
                             data=json.dumps(self.user1.to_json()))
        self.assertEqual(raw.status_code, 501)
        return # FIXME: Not yet implemented
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
        p = Part(element_id=1234,part_name='Test_Name')
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

    def test_get_protocol_for_nonexistent_part(self):
        raw = self.app.get('/api/part/999/protocol')
        self.assertEqual(raw.status_code, 404)

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

    def test_get_nonexistent_building_by_id(self):
        raw = self.app.get('/api/building/999')
        self.assertEqual(404, raw.status_code)

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

    def test_put_nonexistent_part_fails(self):
        raw = self.app.put('/api/part/1000', content_type='application/json',
                data=json.dumps({'part_id':1000,'element_id':10,'building_id':1}))
        self.assertEqual(404, raw.status_code)

    def test_put_part_nonexistent_building_fails(self):
        db_session.add(self.part1)
        db_session.commit()
        to_put = self.part1.to_json()
        to_put['building_id'] = 15
        raw = self.app.put('/api/part/{}'.format(self.part1.element_id),
                content_type='application/json', data=json.dumps(to_put))
        resp = json.loads(raw.data)
        self.assertEqual(404, raw.status_code)
        self.assertTrue('building' in resp['Error'].lower())

    def test_put_not_json_fails(self):
        db_session.add(self.part1)
        db_session.commit()
        to_put = self.part1.to_json()
        raw = self.app.put('/api/part/{}'.format(self.part1.element_id),
                content_type='text/html', data='This is not json')
        self.assertEqual(400, raw.status_code)

    def test_put_part(self):
        self.part1.building_id = None
        db_session.add(self.part1)
        db_session.commit()
        to_put = self.part1.to_json()
        to_put['element_id'] = 111
        raw = self.app.put('/api/part/{}'.format(self.part1.element_id),
                content_type='application/json', data=json.dumps(to_put))
        changed = Part.query.first()
        self.assertEqual(changed.to_json(), json.loads(raw.data))
        self.assertEqual(111, changed.element_id)

    def test_put_part_extra_keys_fails(self):
        db_session.add(self.part1)
        db_session.commit()
        to_put = self.part1.to_json()
        to_put['element_id'] = 111
        to_put['not_an_attr'] = 'something'
        raw = self.app.put('/api/part/{}'.format(self.part1.element_id),
                content_type='application/json', data=json.dumps(to_put))
        self.assertEqual(400, raw.status_code)

    def test_delete_nonexistent_part_fails(self):
        raw = self.app.delete('/api/part/1000')
        self.assertEqual(404, raw.status_code)

    def test_delete_part(self):
        db_session.add(self.part1)
        db_session.commit()
        part_id = self.part1.part_id
        raw = self.app.delete('/api/part/{}'.format(self.part1.element_id))
        deleted = Part.query.first()
        self.assertTrue(deleted is None)
        self.assertEquals({'part_id':part_id}, json.loads(raw.data))

    def test_delete_part_protocol(self):
        db_session.add_all([self.part1, self.protocol1])
        db_session.commit()
        pp = PartProtocol(part_id=self.part1.part_id,
                          protocol_id=self.protocol1.protocol_id)
        db_session.add(pp)
        db_session.commit()
        raw = self.app.delete('/api/part/{}/protocol/{}'.format(
            self.part1.element_id, self.protocol1.protocol_id))
        deleted = (PartProtocol.query
                .filter(PartProtocol.part_id==self.part1.part_id).first())
        self.assertTrue(deleted is None)

    def test_delete_part_protocol_no_connection_fails(self):
        db_session.add_all([self.part1, self.protocol1])
        db_session.commit()
        raw = self.app.delete('/api/part/{}/protocol/{}'.format(
            self.part1.element_id, self.protocol1.protocol_id))
        self.assertEqual(raw.status_code, 404)

    def test_get_nonexistent_protocol_by_id_fails(self):
        raw = self.app.get('/api/protocol/999')
        self.assertEqual(404, raw.status_code)

    def test_put_protocol_not_json(self):
        db_session.add(self.protocol1)
        db_session.commit()
        raw = self.app.put(
            '/api/protocol/{}'.format(self.protocol1.protocol_id),
            content_type='text/html', data='This is not JSON')
        self.assertEqual(raw.status_code, 400)

    def test_put_protocol_no_value_specified(self):
        db_session.add(self.protocol1)
        db_session.commit()
        raw = self.app.put(
            '/api/protocol/{}'.format(self.protocol1.protocol_id),
            content_type='application/json', data='{}')
        self.assertEqual(raw.status_code, 400)

    def test_put_protocol_extra_keys_specified(self):
        db_session.add(self.protocol1)
        db_session.commit()
        raw = self.app.put(
            '/api/protocol/{}'.format(self.protocol1.protocol_id),
            content_type='application/json',
            data=json.dumps({'value':'something', 'else':'no good'}))
        self.assertEqual(raw.status_code, 400)

    def test_put_protocol(self):
        db_session.add(self.protocol1)
        db_session.commit()
        raw = self.app.put(
            '/api/protocol/{}'.format(self.protocol1.protocol_id),
            content_type='application/json',
            data=json.dumps({'value':'different'}))
        changed = Protocol.query.filter(
                Protocol.protocol_id==self.protocol1.protocol_id).first()
        self.assertEqual(changed.value, 'different')

    def test_delete_protocol(self):
        db_session.add(self.protocol1)
        db_session.commit()
        pid = self.protocol1.protocol_id
        self.app.delete('/api/protocol/{}'.format(pid))
        deleted = Protocol.query.filter(Protocol.protocol_id==pid).first()
        self.assertTrue(deleted is None)

    def test_delete_building(self):
        db_session.add(self.building1)
        db_session.commit()
        bid = self.building1.building_id
        self.app.delete('/api/building/{}'.format(bid))
        deleted = Building.query.filter(Building.building_id==bid).first()
        self.assertTrue(deleted is None)

    def test_put_building_not_json(self):
        db_session.add(self.building1)
        db_session.commit()
        raw = self.app.put(
                '/api/building/{}'.format(self.building1.building_id),
                content_type='text/html', data='This is not json')
        self.assertEqual(raw.status_code, 400)

    def test_put_building_no_name(self):
        db_session.add(self.building1)
        db_session.commit()
        raw = self.app.put(
                '/api/building/{}'.format(self.building1.building_id),
                content_type='application/json', data='{}')
        self.assertEqual(raw.status_code, 400)

    def test_put_building_extra_keys(self):
        db_session.add(self.building1)
        db_session.commit()
        raw = self.app.put(
                '/api/building/{}'.format(self.building1.building_id),
                content_type='application/json',
                data=json.dumps({'name':'Better Shelby', 'something': 'else'}))
        self.assertEqual(raw.status_code, 400)

    def test_put_building(self):
        db_session.add(self.building1)
        db_session.commit()
        raw = self.app.put(
                '/api/building/{}'.format(self.building1.building_id),
                content_type='application/json',
                data=json.dumps({'name': 'Super Shelby'}))
        resp = json.loads(raw.data)
        changed = (Building.query
                .filter(Building.building_id==self.building1.building_id)
                .first())
        self.assertEqual(changed.name, 'Super Shelby')
        self.assertEqual(resp, changed.to_json())

    def test_get_protocol_families(self):
        db_session.add_all([self.family1, self.family2])
        db_session.commit()
        resp = json.loads(self.app.get('/api/protocol-family').data)
        self.assertEqual(resp,
                         [self.family1.to_json(), self.family2.to_json()])

    def test_add_protocol_families_not_json(self):
        raw = self.app.post('/api/protocol-family', content_type='text/html',
                            data='this is not json')
        self.assertEqual(400, raw.status_code)

    def test_add_protocol_families_no_family_name(self):
        raw = self.app.post(
                '/api/protocol-family', content_type='application/json',
                data=json.dumps({}))
        self.assertEqual(400, raw.status_code)

    def test_add_protocol_families_extra_keys(self):
        raw = self.app.post(
                '/api/protocol-family', content_type='application/json',
                data=json.dumps({'family_name': 'super family', 'extra': 'h'}))
        self.assertEqual(400, raw.status_code)

    def test_add_protocol_families_successful(self):
        raw = self.app.post(
                '/api/protocol-family', content_type='application/json',
                data=json.dumps({'family_name': 'super family'}))
        resp = json.loads(raw.data)
        fam = ProtocolFamily.query.first()
        self.assertEqual(fam.to_json(), resp)

    def test_get_protocols_for_family_successful(self):
        db_session.add_all([self.protocol1, self.protocol2, self.family1])
        db_session.commit()
        pfp1 = ProtocolFamilyProtocol(protocol_id=self.protocol1.protocol_id,
                                      family_id=self.family1.family_id)
        pfp2 = ProtocolFamilyProtocol(protocol_id=self.protocol2.protocol_id,
                                      family_id=self.family1.family_id)
        db_session.add_all([pfp1, pfp2])
        db_session.commit()
        q_str = '/api/protocol-family/{}'.format(self.family1.family_id)
        resp = json.loads(self.app.get(q_str).data)
        expected = {
            'family_id': self.family1.family_id,
            'family_name': self.family1.family_name,
            'protocols': [self.protocol1.to_json(), self.protocol2.to_json()]
        }
        self.assertEqual(resp, expected)

    def test_get_protocols_for_family_nonexistent_family(self):
        raw = self.app.get('/api/protocol-family/99999')
        self.assertEqual(404, raw.status_code)

    def test_edit_protocol_family_successful(self):
        fam = ProtocolFamily(family_name='Testfam', family_id=0)
        db_session.add(fam)
        db_session.commit()
        q_str = '/api/protocol-family/0'
        self.app.put(q_str, content_type='application/json',
                data=json.dumps({'family_name': 'super family1'}))
        changed = ProtocolFamily.query.first()
        self.assertEqual(changed.to_json()['family_name'], 'super family1')

    def test_edit_protocol_family_not_json(self):
        db_session.add(self.family1)
        db_session.commit()
        q_str = '/api/protocol-family/{}'.format(self.family1.family_id)
        raw = self.app.put(q_str, content_type='text/html',
                data='this is not json')
        self.assertEqual(raw.status_code, 400)

    def test_edit_protocol_family_nonexistent_family(self):
        q_str = '/api/protocol-family/{}'.format(self.family1.family_id)
        raw = self.app.put(q_str, content_type='application/json',
                data=json.dumps({'family_name': 'super family1'}))
        self.assertEqual(raw.status_code, 404)

    def test_edit_protocol_family_no_family_name(self):
        db_session.add(self.family1)
        db_session.commit()
        q_str = '/api/protocol-family/{}'.format(self.family1.family_id)
        raw = self.app.put(q_str, content_type='application/json',
                data=json.dumps({}))
        self.assertEqual(raw.status_code, 400)

    def test_edit_protocol_family_extra_keys(self):
        db_session.add(self.family1)
        db_session.commit()
        q_str = '/api/protocol-family/{}'.format(self.family1.family_id)
        raw = self.app.put(q_str, content_type='application/json',
                data=json.dumps({'family_name': 'super family', 'extra': '1'}))
        self.assertEqual(raw.status_code, 400)

    def test_delete_protocol_family_nonexistent_family(self):
        raw = self.app.delete('/api/protocol-family/999')
        self.assertEqual(404, raw.status_code)

    def test_delete_protocol_family_successful(self):
        db_session.add(self.family1)
        db_session.commit()
        q_str = '/api/protocol-family/{}'.format(self.family1.family_id)
        self.app.delete(q_str)
        fam = ProtocolFamily.query.first()
        self.assertIsNone(fam)

    def test_add_family_protocol_association_successful(self):
        db_session.add_all([self.family1, self.protocol1])
        db_session.commit()
        q_str = '/api/protocol-family/{}/protocol/{}'.format(
                self.family1.family_id, self.protocol1.protocol_id)
        self.app.post(q_str)
        pfp = ProtocolFamilyProtocol.query.first()
        self.assertEqual(pfp.family_id, self.family1.family_id)
        self.assertEqual(pfp.protocol_id, self.protocol1.protocol_id)

    def test_add_family_protocol_association_nonexistent_family(self):
        db_session.add_all([self.protocol1])
        db_session.commit()
        q_str = '/api/protocol-family/{}/protocol/{}'.format(
                self.family1.family_id, self.protocol1.protocol_id)
        raw = self.app.post(q_str)
        self.assertEqual(404, raw.status_code)

    def test_add_family_protocol_association_nonexistent_protocol(self):
        db_session.add_all([self.family1])
        db_session.commit()
        q_str = '/api/protocol-family/{}/protocol/{}'.format(
                self.family1.family_id, 999)
        raw = self.app.post(q_str)
        self.assertEqual(404, raw.status_code)

    def test_delete_family_protocol_association_successful(self):
        db_session.add_all([self.protocol1, self.family1])
        db_session.commit()
        pfp = ProtocolFamilyProtocol(protocol_id=self.protocol1.protocol_id,
                                     family_id=self.family1.family_id)
        db_session.add(pfp)
        db_session.commit()
        q_str = '/api/protocol-family/{}/protocol/{}'.format(
                self.family1.family_id, self.protocol1.protocol_id)
        self.app.delete(q_str)
        pfp_change = ProtocolFamilyProtocol.query.first()
        self.assertIsNone(pfp_change)

    def test_delete_family_protocol_association_nonexistent_association(self):
        db_session.add_all([self.protocol1, self.family1])
        db_session.commit()
        q_str = '/api/protocol-family/{}/protocol/{}'.format(
                self.family1.family_id, self.protocol1.protocol_id)
        raw = self.app.delete(q_str)
        self.assertEqual(raw.status_code, 404)


if __name__ == '__main__':
    unittest.main()

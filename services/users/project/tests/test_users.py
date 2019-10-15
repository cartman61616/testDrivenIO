import json
import unittest

from project.tests.base import BaseTestCase
from project import db
from project.tests.utils import add_user
from project.api.models import User


class TestUserService(BaseTestCase):
    """Tests for the Users Service."""

    def test_add_user(self):
        """Ensure a new user can be added to the database."""
        add_user('test', 'test@test.com', 'test')
        user = User.query.filter_by(email='test@test.com').first()
        user.admin = True
        db.session.commit()
        resp_login = self.client.post(
            '/auth/login',
            data=json.dumps({
                'email': 'test@test.com',
                'password': 'test'
            }),
            content_type='application/json'
        )
        with self.client:
            token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'tester',
                    'email': 'test@tester.org',
                    'password': 'greaterthaneight'
                }),
                content_type='application/json',
                headers={'Authorization': f'Bearer {token}'}
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('test@tester.org was added!', data['message'])
            self.assertIn('success', data['status'])

    def test_add_user_invalid_json(self):
        """Ensure error is thrown if the JSON object is empty."""
        add_user('test', 'test@test.com', 'test')
        user = User.query.filter_by(email='test@test.com').first()
        user.admin = True
        db.session.commit()
        resp_login = self.client.post(
            '/auth/login',
            data=json.dumps({
                'email': 'test@test.com',
                'password': 'test'
            }),
            content_type='application/json'
        )
        with self.client:
            token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.post(
                '/users',
                data=json.dumps({}),
                content_type='application/json',
                headers={'Authorization': f'Bearer {token}'}
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_invalid_json_keys(self):
        """
        Ensure error is thrown if the JSON object does not have a username key.
        """
        add_user('test', 'test@test.com', 'test')
        user = User.query.filter_by(email='test@test.com').first()
        user.admin = True
        db.session.commit()
        resp_login = self.client.post(
            '/auth/login',
            data=json.dumps({
                'email': 'test@test.com',
                'password': 'test'
            }),
            content_type='application/json'
        )
        with self.client:
            token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.post(
                '/users',
                data=json.dumps({'email': 'robo@tesladyne.org',
                                 'password': 'greaterthaneight'}),
                content_type='application/json',
                headers={'Authorization': f'Bearer {token}'}
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_invalid_json_keys_no_password(self):
        """
        Ensure error is thrown if the JSON object
        does not have a password key.
        """
        add_user('test', 'test@test.com', 'test')
        user = User.query.filter_by(email='test@test.com').first()
        user.admin = True
        db.session.commit()
        resp_login = self.client.post(
            '/auth/login',
            data=json.dumps({
                'email': 'test@test.com',
                'password': 'test'
            }),
            content_type='application/json'
        )
        with self.client:
            token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='test',
                    email='robo@tesladyne.org')),
                content_type='application/json',
                headers={'Authorization': f'Bearer {token}'}
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_duplicate_email(self):
        """Ensure error is thrown if the email already exists."""
        add_user('test', 'test@test.com', 'test')
        user = User.query.filter_by(email='test@test.com').first()
        user.admin = True
        db.session.commit()
        resp_login = self.client.post(
            '/auth/login',
            data=json.dumps({
                'email': 'test@test.com',
                'password': 'test'
            }),
            content_type='application/json'
        )
        with self.client:
            token = json.loads(resp_login.data.decode())['auth_token']
            self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'michael',
                    'email': 'michael@mherman.org',
                    'password': 'greaterthaneight'
                }),
                content_type='application/json',
                headers={'Authorization': f'Bearer {token}'}
            )
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'michael',
                    'email': 'michael@mherman.org',
                    'password': 'greaterthaneight'
                }),
                content_type='application/json',
                headers={'Authorization': f'Bearer {token}'}
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn(
                'Sorry, that email already exists', data['message'])
            self.assertIn('fail', data['status'])

    def test_users(self):
        """Ensure the /ping route behaves correctly."""
        response = self.client.get('/users/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    def test_single_user(self):
        """Ensure get single user behaves correctly"""
        user = add_user('dicky', 'otis@bosstones.com', 'greaterthaneight')
        db.session.add(user)
        db.session.commit()
        with self.client:
            response = self.client.get(f'/users/{user.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('dicky', data['data']['username'])
            self.assertIn('otis@bosstones.com', data['data']['email'])
            self.assertIn('success', data['status'])

    def test_single_user_no_id(self):
        """Ensure error is thrown if an id is not provided."""
        with self.client:
            response = self.client.get('/users/lahhh')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_user_incorrect_id(self):
        """Ensure error is thrown if the id does not exist"""
        with self.client:
            response = self.client.get('/users/737')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_all_users(self):
        """Ensure get all users behave correctly."""
        add_user('robo', 'atomic_robo@tesladyne.com', 'greaterthaneight')
        add_user('marty', 'goalie30@devils.com', 'greaterthaneight')
        with self.client:
            response = self.client.get('/users')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['data']['users']), 2)
            self.assertIn('robo', data['data']['users'][0]['username'])
            self.assertIn('atomic_robo@tesladyne.com',
                          data['data']['users'][0]['email'])
            self.assertTrue(data['data']['users'][0]['active'])
            self.assertFalse(data['data']['users'][0]['admin'])
            self.assertIn('marty', data['data']['users'][1]['username'])
            self.assertIn('goalie30@devils.com',
                          data['data']['users'][1]['email'])
            self.assertTrue(data['data']['users'][0]['active'])
            self.assertFalse(data['data']['users'][0]['admin'])
            self.assertIn('success', data['status'])

    def test_main_no_users(self):
        """Ensure the main route behaves
        correctly when no users
        have been added to the database"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'All Users', response.data)
        self.assertIn(b'<p>No users!</p>', response.data)

    def test_main_with_users(self):
        """Ensure the main route
        behaves correctly
        when users have been added to the database"""
        add_user('robo', 'atomic_robo@tesladyne.com', 'greaterthaneight')
        add_user('marty', 'goalie30@devils.com', 'greaterthaneight')
        with self.client:
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'All Users', response.data)
            self.assertNotIn(b'<p>No users!</p>', response.data)
            self.assertIn(b'robo', response.data)
            self.assertIn(b'marty', response.data)

    def test_main_add_user(self):
        """Ensure a new user can be added to the database via a POST request"""
        with self.client:
            response = self.client.post(
                '/',
                data=dict(username='dr dinosaur',
                          email='dino@tesladyne.com',
                          password='greaterthaneight'),
                follow_redirects=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'All Users', response.data)
            self.assertNotIn(b'<p>No users!</p>', response.data)
            self.assertIn(b'dr dinosaur', response.data)

    def test_add_user_not_admin(self):
        add_user('test', 'test@test.com', 'test')
        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps({
                    'email': 'test@test.com',
                    'password': 'test'
                }),
                content_type='application/json'
            )
            token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'dr dinosaur',
                    'email': 'crystals@tesladyne',
                    'password': 'crystals'
                }),
                content_type='application/json',
                headers={'Authorization': f'Bearer {token}'}
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(
                data['message'] == 'You do not have permission to do that.')
            self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()

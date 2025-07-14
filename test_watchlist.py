import unittest
from watchlist import app, db
from watchlist.models import User, Movie
from watchlist.commands import forge, init_db


class WatchlistTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config.update(TESTING=True, SQLALCHEMY_DATABASE_URI='sqlite:///:memory:')

        cls.client = app.test_client()
        cls.cli_runner = app.test_cli_runner()
        cls.app_context = app.app_context()
        cls.app_context.push()

        db.create_all()

        
    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()
        

    def setUp(self):
        user = User(name='Test', username='test')
        user.set_password('123')
        movie = Movie(title='Test movie title', year='1234')
        db.session.add_all([user, movie])
        db.session.commit()

    
    def tearDown(self):
         db.session.query(User).delete()
         db.session.query(Movie).delete()
         db.session.commit()

    def login(self):
        self.client.post('/login', data=dict(username='test', password='123'), follow_redirects=True)

    
    def test_app_exist(self):
        self.assertIsNotNone(app)


    def test_is_testing(self):
        self.assertTrue(app.config['TESTING'])


    def test_404_page(self):
        response = self.client.get('/nothing')
        data = response.get_data(as_text=True)
        self.assertIn('Page Not Found - 404', data)
        self.assertIn('Go Back', data)
        self.assertEqual(404, response.status_code)


    def test_index_page(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertIn('Test\'s Watchlist', data)
        self.assertIn('Test movie title', data)
        self.assertEqual(200, response.status_code)

    
    def login_protect(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertNotIn('Settings', data)
        self.assertNotIn('Logout', data)
        self.assertNotIn('Edit', data)
        self.assertNotIn('Delete', data)
        self.assertNotIn('<form method="post">')


    def test_login(self):
        response = self.client.get('/login')
        data = response.get_data(as_text=True)
        self.assertIn('username', data)
        self.assertIn('password', data)

        response = self.client.post('/login', data=dict(username='test', password='123'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Login success.', data)
        self.assertIn('Settings', data)
        self.assertIn('Logout', data)
        self.assertIn('Edit', data)
        self.assertIn('Delete', data)
        self.assertIn('<form method="post">', data)

        response = self.client.post('/login', data=dict(username='', password='123'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login seccess.', data)
        self.assertIn('Invalid input.', data)

        response = self.client.post('/login', data=dict(username='naive', password=''), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid input.', data)

        response = self.client.post('/login', data=dict(username='wrong', password='123'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid username or password.', data)


        response = self.client.post('/login', data=dict(username='naive', password='wrong'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid username or password.', data)


    def test_settings(self):
        self.login()

        response = self.client.get('/settings')
        data = response.get_data(as_text=True)
        self.assertIn('User settings', data)
        self.assertIn('Name', data)

        response = self.client.post('/settings', data=dict(name='naive'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Settings updated successfully.', data)
        self.assertIn('naive', data)

        response = self.client.post('/settings', data=dict(name=''), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Settings updated successfully.', data)
        self.assertIn('Invalid input.', data)

        
    def test_logout(self):
        self.login()

        response = self.client.get('/logout', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Goodbye.', data)
        self.assertNotIn('Settings', data)
        self.assertNotIn('Logout', data)
        self.assertNotIn('Edit', data)
        self.assertNotIn('Delete', data)
        self.assertNotIn("<form method='post'", data)


    def test_create_item(self):
        self.login()

        response = self.client.post('/', data=dict(title='Add test movie title', year=5678), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item created successfully.', data)
        self.assertIn('Add test movie title', data)

        response = self.client.post('/', data=dict(title='', year=5678), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Invalid input.', data)
        self.assertNotIn('Item created successfully.', data)

        response = self.client.post('/', data=dict(title='Add test movie title', year=''), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Invalid input.', data)
        self.assertNotIn('Item created successfully.', data)

    
    def test_update_item(self):
        self.login()

        response = self.client.get('/movie/edit/1')
        data = response.get_data(as_text=True)
        self.assertIn('Edit item', data)
        self.assertIn('Test movie title', data)
        self.assertIn('1234', data)

        response = self.client.post('/movie/edit/1', data=dict(title='Update test movie title', year=1234), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item updated successfully.', data)
        self.assertIn('Update test movie title', data)

        response = self.client.post('/movie/edit/1', data=dict(title='', year=1234), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Invalid input.', data)
        self.assertNotIn('Item updated successfully.', data)

        response = self.client.post('/movie/edit/1', data=dict(title='Update test movie title again', year=''), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Invalid input.', data)
        self.assertNotIn('Item updated successfully.', data)
        self.assertNotIn('Update test movie title again', data)


    def test_delete_item(self):
        self.login()

        response = self.client.post('/movie/delete/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item deleted successfully.', data)
        self.assertNotIn('Test movie title', data)


    def test_forge_command(self):
        result = self.cli_runner.invoke(forge)
        self.assertIn('Done.', result.output)
        self.assertNotEqual(Movie.query.count(), 0)


    def test_init_db_command(self):
        result = self.cli_runner.invoke(init_db)
        self.assertIn('Initialized database.', result.output)

        
    def test_admin_command(self):
        db.drop_all()
        result = self.cli_runner.invoke(args=['admin', '--username', 'naive', '--password', '123'])
        self.assertIn('Creating user...', result.output)
        self.assertIn('Done.', result.output)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().username, 'naive')
        self.assertTrue(User.query.first().validate_password('123'))


    def test_admin_command_update(self):
        result = self.cli_runner.invoke(args=['admin', '--username', 'shadow', '--password', '456'])
        self.assertIn('Updating user...', result.output)
        self.assertIn('Done', result.output)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().username, 'shadow')
        self.assertTrue(User.query.first().validate_password('456'))


if __name__ == '__main__':
    unittest.main()
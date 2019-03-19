import unittest

from pyramid import testing


class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_view_index(self):
        from .views.default import view_index
        request = testing.DummyRequest()
        info = view_index(request)
        self.assertEqual(info['project'], 'Saltstack Frontend')


class FunctionalTests(unittest.TestCase):
    def setUp(self):
        from saltstack_frontend import main
        app = main({})
        from webtest import TestApp
        self.testapp = TestApp(app)

    def test_root(self):
        res = self.testapp.get('/', status=200)
        self.assertTrue(b'navbar' in res.body)

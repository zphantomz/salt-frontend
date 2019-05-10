import unittest
from unittest.mock import patch, mock_open

import yaml
import os

from pyramid import testing
from saltstack_frontend import models

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

class ModelTests(unittest.TestCase):
    def setUp(self):
        models.salt.get_nodegroups.salt_config_files = ['f1','f2']
        self.nodegroups_file_content = b"""
ssh_list_nodegroups:
  groups_with_at: L@ssh-minion1,ssh-minion2
  groups_no_at: ssh-minion3,ssh-minion4
  groups_yaml_array:
  - ssh-minion5
  - ssh-minion6
nodegroups:
  groups_with_at: L@minion1,minion2
  groups_no_at: minion3,minion4
  groups_yaml_array:
  - minion5
  - minion7
  """        
    def test_nodegroups(self):
        with patch('saltstack_frontend.models.salt.open', 
                   new=mock_open(read_data=self.nodegroups_file_content)) as f:
          nodegroups = models.salt.get_nodegroups()
          print(nodegroups)
        self.assertEqual(nodegroups, yaml.load(self.nodegroups_file_content, 
                                               Loader=yaml.SafeLoader))
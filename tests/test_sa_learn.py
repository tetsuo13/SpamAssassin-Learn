import os
import unittest

from sa_learn import *

class GetEmailFromMessageTests(unittest.TestCase):
    def get_email(self, file_name):
        dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)))
        return get_email(os.path.join(dir_path, 'messages', file_name))

    def test_delivered_to_header(self):
        actual = self.get_email('001.txt')
        self.assertEqual('contact@andreinicholson.com', actual)

    def test_no_delivered_to_header(self):
        actual = self.get_email('002.txt')
        self.assertEqual('beatles@cotton.us', actual)

    def test_no_known_header(self):
        actual = self.get_email('003.txt')
        self.assertEqual('contact@andreinicholson.com', actual)

    def test_to_header_with_angle_brackets(self):
        actual = self.get_email('004.txt')
        self.assertEqual('contact@andreinicholson.com', actual)

    def test_for_in_received_header(self):
        actual = self.get_email('006.txt')
        self.assertEqual('beatles@cotton.us', actual)

    def test_file_doesnt_exist_raises_exception(self):
        with self.assertRaises(Exception):
            get_email('/tmp/this_file_doesnt_exist_456_foo_derp')

    def test_file_not_an_email_raises_exception(self):
        with self.assertRaises(Exception):
            get_email('/etc/crontab')

    def test_encoding_iso88591(self):
        actual = self.get_email('007.txt')
        self.assertEqual('contact@andreinicholson.com', actual)

class SuitableForLearningTests(unittest.TestCase):
    def get_path(self, file_name):
        dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)))
        return os.path.join(dir_path, 'messages', file_name)

    def test_contains_header(self):
        path = self.get_path('001.txt')
        self.assertTrue(suitable_for_learning(path))

    def test_doesnt_contain_header(self):
        path = self.get_path('005.txt')
        self.assertFalse(suitable_for_learning(path))

    def test_file_not_found_returns_false(self):
        self.assertFalse(suitable_for_learning('/tmp/this_file_doesnt_exist_123_derp'))


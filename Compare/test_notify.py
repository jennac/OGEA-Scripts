import notify
import unittest

test_hash_compare = [
    ('this is a test', 'this is a test', True),
    ('this should not work', 'because they are different', False)
]


#test_check_data = [
#    ('ogea_data_2013-10-07.csv', 'ogea_data_2013-10-07.csv', changes),
#    ('ogea_data_2013-10-07.csv', 'diff1.csv', changes), 
#    ('ogea_data_2013-10-07.csv', 'diff2.csv', changes)
#]


class TestNotify(unittest.TestCase):
    def testHashCompare(self):
        for old, new, ret_val in test_hash_compare:
            self.assertEqual(ret_val, notify.hashCompare(old, new))

#    def testCheckData(self):
#        for old, new, ret_dict in test_check_data:
#            TODO figure out how to test for specific output


if __name__ == '__main__':
    unittest.main()

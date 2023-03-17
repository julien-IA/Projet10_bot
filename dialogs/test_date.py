import unittest
from datetime import datetime
from timedelta import Timedelta
from dialogs import outils

class Test_DateValidator(unittest.TestCase):

    def test_return_before_departure(self):
        test_outils = outils()
        self.assertFalse(test_outils.return_before_departure('2023-01-15','2023-01-29'))
        self.assertTrue(test_outils.return_before_departure('2023-01-29','2023-01-15'))

    def test_is_a_date(self):
        test_outils = outils()
        self.assertFalse(test_outils.is_a_date('not_a_date'))
        self.assertFalse(test_outils.is_a_date('123546798'))
        self.assertTrue(test_outils.is_a_date('2023-02-15'))  

    def test_is_in_past(self):
        test_outils = outils()
        now = datetime.now()
        yesterday = now - Timedelta(days=1)
        tomorrow = now + Timedelta(days=1)
        self.assertTrue(test_outils.is_in_the_past(yesterday))
        self.assertFalse(test_outils.is_in_the_past(tomorrow))
        self.assertFalse(test_outils.is_in_the_past(now))

if __name__ == '__main__':
    unittest.main()
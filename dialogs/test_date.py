import unittest

from booking_dialog import BookingDialog

class Test_TestDateValidator(unittest.TestCase):

    def test_is_depart_before_return(self):
        test_BookingDialog = BookingDialog()
        self.assertTrue(test_BookingDialog.is_depart_before_return('2023-01-15','2023-01-29'))
        self.assertFalse(test_BookingDialog.is_depart_before_return('2023-01-29','2023-01-15'))

    def test_is_ambiguous(self):
        test_BookingDialog = BookingDialog()
        self.assertTrue(test_BookingDialog.is_ambiguous('not_a_date'))
        self.assertTrue(test_BookingDialog.is_ambiguous('123546798'))
        self.assertFalse(test_BookingDialog.is_ambiguous('2023-02-15'))    

if __name__ == '__main__':
    unittest.main()
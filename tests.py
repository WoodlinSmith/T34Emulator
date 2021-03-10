import unittest
import utils


class test_parsing(unittest.TestCase):
    def test_get_byte_count(self):
        #test to make sure it grabs 0 correctly
        self.assertEqual(0,utils.get_byte_count("00"))

        #making sure it is actually using both bytes
        self.assertNotEqual(0,utils.get_byte_count("01"))

        #Ensure that it does not go beyond the second index
        self.assertEqual(1,utils.get_byte_count("01AB"))
        

        #Ensure that it converts to hex correctly
        self.assertEqual(10,utils.get_byte_count("0A"))
    
    def test_get_addr(self):

        #ensure it grabs 0 correctly
        self.assertEqual(0,utils.get_addr("0000"))

        #ensure it is actually reading hex
        self.assertEqual(65535,utils.get_addr("FFFF"))

        #ensure it is only reading 4 hex digits
        self.assertEqual(65535,utils.get_addr("FFFFF"))
    
    def test_get_record_type(self):
        #ensure it grabs proper length
        self.assertEqual(2,len(utils.get_record_type("0000")))

        #ensure it grabs the correct string
        self.assertEqual("00",utils.get_record_type("00FF"))
    
    def test_get_data(self):
        #ensure it grabs proper length
        self.assertEqual(12,len(utils.get_data("0A446AB771EF90",6)))

        #ensure it grabs correct string
        self.assertEqual("0A446AB771EF",utils.get_data("0A446AB771EF90",6))

    def test_parse(self):
        #string taken from wikipedia
        test_string=":0B0010006164647265737320676170A7"
        correct_result=(16,"00","6164647265737320676170")

        eof_string=":00000001FF"
        correct_result_eof=(0,"01","")

        #test valid string
        self.assertEqual(correct_result,utils.parse_hex_line(test_string))

        #test eof string
        self.assertEqual(correct_result_eof,utils.parse_hex_line(eof_string))

        






if __name__ =="__main__":
    unittest.main()
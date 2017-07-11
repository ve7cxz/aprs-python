import unittest2 as unittest

from aprslib.parsing.capability import parse_capability


class CapabilityTC(unittest.TestCase):
    def test_capability(self):
        body = "IGATE,MSG_CNT=0,LOC_CNT=1"
        _, result = parse_capability(body)

        self.assertEqual(result['format'], 'capability')
        self.assertEqual(result['capabilities']['type'], 'IGATE')
        self.assertEqual(result['capabilities']['MSG_CNT'], '0')

        body = "IGATE,MSG_CNT=681,LOC_CNT=70,DIR_CNT=33,RF_CNT=117,DX=1*KB9OBX-10(133mi@339\xb0)\r\n"
        _, result = parse_capability(body)

        self.assertEqual(result['format'], 'capability')
        self.assertEqual(result['capabilities']['type'], 'IGATE')
        self.assertEqual(result['capabilities']['MSG_CNT'], '681')
        self.assertEqual(result['capabilities']['LOC_CNT'], '70')
        self.assertEqual(result['capabilities']['DIR_CNT'], '33')
        self.assertEqual(result['capabilities']['RF_CNT'], '117')
        self.assertEqual(result['capabilities']['DX'], '1*KB9OBX-10(133mi@339\xb0)')

import unittest2 as unittest

from aprslib.parsing import parse_comment_telemetry, parse_telemetry_report

class ParseTelemetryReport(unittest.TestCase):
    def test_telemetry_report(self):
        body = '#393,488,576,269,116,488,01000100'

        (_, result) = parse_telemetry_report(body)

        self.assertEqual(result['format'], 'telemetry-report')
        self.assertEqual(result['telemetry']['seq'], '393')
        self.assertEqual(result['telemetry']['vals'][0], '488')
        self.assertEqual(result['telemetry']['vals'][5], '01000100')

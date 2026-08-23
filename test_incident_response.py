import unittest

from incident_response import get_incident_response


class IncidentResponseTests(unittest.TestCase):
    def test_known_category_returns_recommendations(self):
        response = get_incident_response("Ransomware Attack")
        self.assertIsInstance(response, list)
        self.assertIn("Do not pay the ransom.", response)

    def test_alias_category_normalizes_correctly(self):
        response = get_incident_response("ransomware")
        self.assertIn("Do not pay the ransom.", response)

    def test_unknown_category_returns_default(self):
        response = get_incident_response("Unknown Threat")
        self.assertEqual(response, [
            "Investigate the incident further.",
            "Monitor systems for suspicious activity.",
            "Follow cybersecurity best practices.",
        ])

    def test_none_threat_type_returns_general_security(self):
        response = get_incident_response(None)
        self.assertIn("Follow cybersecurity best practices.", response)


if __name__ == "__main__":
    unittest.main()

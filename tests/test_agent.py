import unittest
from src.agent import ClaimsAgent

class TestClaimsAgent(unittest.TestCase):
    def setUp(self):
        self.agent = ClaimsAgent()

    def test_routing_fast_track(self):
        fields = {
            "policy_number": "PN123",
            "policyholder_name": "John Doe",
            "date_of_loss": "2026-05-10",
            "claim_type": "Automobile",
            "initial_estimate": "$15,000",
            "description": "Minor scratch"
        }
        result = self.agent.route_claim(fields, [])
        self.assertEqual(result["route"], "Fast-track")

    def test_routing_manual_review_missing_field(self):
        fields = {
            "policy_number": "PN123",
            "policyholder_name": "John Doe",
            "date_of_loss": "2026-05-10",
            "claim_type": "Automobile",
            "initial_estimate": ""
        }
        missing = ["initial_estimate"]
        result = self.agent.route_claim(fields, missing)
        self.assertEqual(result["route"], "Manual Review")

    def test_routing_investigation_flag(self):
        fields = {
            "policy_number": "PN123",
            "policyholder_name": "John Doe",
            "date_of_loss": "2026-05-10",
            "claim_type": "Automobile",
            "initial_estimate": "$10,000",
            "description": "The accident seems staged and inconsistent."
        }
        result = self.agent.route_claim(fields, [])
        self.assertEqual(result["route"], "Investigation Flag")

    def test_routing_specialist_queue(self):
        fields = {
            "policy_number": "PN123",
            "policyholder_name": "John Doe",
            "date_of_loss": "2026-05-10",
            "claim_type": "injury",
            "initial_estimate": "$50,000",
            "description": "Serious injury reported."
        }
        result = self.agent.route_claim(fields, [])
        self.assertEqual(result["route"], "Specialist Queue")

    def test_routing_standard_workflow(self):
        fields = {
            "policy_number": "PN123",
            "policyholder_name": "John Doe",
            "date_of_loss": "2026-05-10",
            "claim_type": "Automobile",
            "initial_estimate": "$30,000",
            "description": "Major collision."
        }
        result = self.agent.route_claim(fields, [])
        self.assertEqual(result["route"], "Standard Workflow")

    def test_parse_currency(self):
        self.assertEqual(self.agent._parse_currency("$15,000.50"), 15000.50)
        self.assertEqual(self.agent._parse_currency("25000"), 25000.0)
        self.assertEqual(self.agent._parse_currency("N/A"), 0.0)

if __name__ == "__main__":
    unittest.main()

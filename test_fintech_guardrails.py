"""
Module: test_fintech_guardrails.py
Description: Production-grade automated test suite verifying Fintech transaction API guardrails.
             Uses Python's built-in unittest framework and mock architecture to simulate
             real-world banking validation logic (Negative testing, fraud controls, and decimal math precision).
"""

import unittest
from unittest.mock import MagicMock, patch
from decimal import Decimal, InvalidOperation
import json


# ==============================================================================
# SIMULATED BANKING CORE LOGIC (The System Under Test)
# ==============================================================================
class BankingCoreService:
    """
    Simulates the backend engine of a digital bank.
    Contains strict business logic for processing fund transfers.
    """

    def __init__(self):
        # Default mock account balance setup
        self.accounts_db = {
            "ACC-12345": Decimal("500.00"),  # Sender
            "ACC-67890": Decimal("100.00")  # Recipient
        }

    def process_transfer(self, payload_str):
        """
        Processes an incoming JSON transfer request and implements strict validation rules.
        """
        try:
            data = json.loads(payload_str)
        except (json.JSONDecodeError, TypeError):
            return 400, {"error": "BAD_REQUEST", "message": "Malformed or invalid JSON payload."}

        # 1. Type and Presence Verification
        if "amount" not in data or "sender_account" not in data or "recipient_account" not in data or "currency" not in data:
            return 400, {"error": "BAD_REQUEST", "message": "Missing required fields."}

        raw_amount = data["amount"]
        sender = data["sender_account"]
        currency = data["currency"]

        # Prevent Boolean values sneaking through as numbers (Python treats True as 1)
        if isinstance(raw_amount, bool):
            return 400, {"error": "BAD_REQUEST", "message": "Amount must be a valid number."}

        # 2. Strict Numeric Type Validation (Guardrail against String mutations)
        if not isinstance(raw_amount, (int, float)) and not isinstance(raw_amount, Decimal):
            return 400, {"error": "BAD_REQUEST", "message": "Amount must be a valid number."}

        # 3. Financial Decimal Parsing (Eliminates floating-point vulnerabilities)
        try:
            amount = Decimal(str(raw_amount))
        except (InvalidOperation, ValueError):
            return 400, {"error": "BAD_REQUEST", "message": "Amount format is unparsable."}

        # 4. Value Range Bounds Check
        if amount <= 0:
            return 400, {"error": "INVALID_AMOUNT", "message": "Amount must be greater than zero."}

        # 5. Currency Control Isolation
        if currency != "USD":
            return 422, {"error": "UNSUPPORTED_CURRENCY", "message": "Only USD transactions are permitted."}

        # 6. Database State Check (Account Existence)
        if sender not in self.accounts_db:
            return 404, {"error": "ACCOUNT_NOT_FOUND", "message": "Sender account does not exist."}

        # 7. Balance Verification (Insufficient Funds Protection)
        current_balance = self.accounts_db[sender]
        if amount > current_balance:
            return 422, {"error": "INSUFFICIENT_FUNDS", "message": "Transfer declined due to insufficient funds."}

        # 8. Happy Path Execution (State Modification)
        self.accounts_db[sender] -= amount
        self.accounts_db["ACC-67890"] += amount

        return 201, {
            "status": "SUCCESS",
            "transaction_id": "TXN-9982341",
            "remaining_balance": float(self.accounts_db[sender])
        }


# ==============================================================================
# AUTOMATED TEST SUITE (The SDET Harness)
# ==============================================================================
class TestFintechGuardrails(unittest.TestCase):

    def setUp(self):
        """Initializes a fresh banking engine instance before every single execution."""
        self.banking_service = BankingCoreService()

    def execute_mock_api_call(self, scenario_name, payload):
        """
        Helper method functioning as our local API gateway driver.
        Logs structural details mimicking a real network request/response lifecycle.
        """
        print(f"\n[SCENARIO]: {scenario_name}")
        payload_json = json.dumps(payload)
        print(f"  [PAYLOAD SENT]: {payload_json}")

        # Simulate routing request through gateway to our engine
        status_code, response_body = self.banking_service.process_transfer(payload_json)

        print(f"  [MOCK API RESPONSE]: Status {status_code} | Body: {json.dumps(response_body)}")
        return status_code, response_body

    def test_happy_path_successful_transfer(self):
        """Verify a structurally pristine transaction successfully updates balances."""
        payload = {
            "sender_account": "ACC-12345",
            "recipient_account": "ACC-67890",
            "amount": 100.00,
            "currency": "USD"
        }
        status, response = self.execute_mock_api_call("Valid Standard Transfer", payload)

        self.assertEqual(status, 201)
        self.assertEqual(response["status"], "SUCCESS")
        self.assertIn("transaction_id", response)
        self.assertEqual(Decimal(str(response["remaining_balance"])), Decimal("400.00"))

    def test_fraud_guard_negative_amount(self):
        """Verify malicious input injection of negative values is securely blocked."""
        payload = {
            "sender_account": "ACC-12345",
            "recipient_account": "ACC-67890",
            "amount": -50.00,
            "currency": "USD"
        }
        status, response = self.execute_mock_api_call("Negative Value Attack Vector", payload)

        self.assertEqual(status, 400)
        self.assertEqual(response["error"], "INVALID_AMOUNT")

    def test_boundary_zero_amount(self):
        """Verify transaction limit boundaries reject an empty/zero transaction value."""
        payload = {
            "sender_account": "ACC-12345",
            "recipient_account": "ACC-67890",
            "amount": 0.00,
            "currency": "USD"
        }
        status, response = self.execute_mock_api_call("Zero Amount Floor Boundary Check", payload)

        self.assertEqual(status, 400)
        self.assertEqual(response["error"], "INVALID_AMOUNT")

    def test_business_rule_insufficient_funds(self):
        """Verify ledger system declines requests scaling beyond account capabilities."""
        payload = {
            "sender_account": "ACC-12345",
            "recipient_account": "ACC-67890",
            "amount": 600.00,
            "currency": "USD"
        }
        status, response = self.execute_mock_api_call("Account Balance Overdraft Protection", payload)

        self.assertEqual(status, 422)
        self.assertEqual(response["error"], "INSUFFICIENT_FUNDS")

    def test_security_currency_isolation(self):
        """Verify cross-currency contamination requests are rejected to maintain market boundaries."""
        payload = {
            "sender_account": "ACC-12345",
            "recipient_account": "ACC-67890",
            "amount": 25.00,
            "currency": "EUR"
        }
        status, response = self.execute_mock_api_call("Foreign Currency Cross-Contamination Check", payload)

        self.assertEqual(status, 422)
        self.assertEqual(response["error"], "UNSUPPORTED_CURRENCY")

    def test_type_mutation_string_injection(self):
        """Verify schema engine defends against data type pollution (String instead of Float)."""
        payload = {
            "sender_account": "ACC-12345",
            "recipient_account": "ACC-67890",
            "amount": "100.00",
            "currency": "USD"
        }
        status, response = self.execute_mock_api_call("String Data Type Mutation Injection", payload)

        self.assertEqual(status, 400)
        self.assertEqual(response["error"], "BAD_REQUEST")

    def test_type_mutation_boolean_injection(self):
        """Verify explicit Boolean inputs fail type parsing and do not evaluate mathematically."""
        payload = {
            "sender_account": "ACC-12345",
            "recipient_account": "ACC-67890",
            "amount": True,
            "currency": "USD"
        }
        status, response = self.execute_mock_api_call("Boolean Numeric Evaluation Bypass Attempt", payload)

        self.assertEqual(status, 400)
        self.assertEqual(response["error"], "BAD_REQUEST")


if __name__ == '__main__':
    print("======================================================================")
    print(" RUNNING ENTERPRISE FINTECH API GUARDRAIL TEST SUITE                  ")
    print("======================================================================")
    unittest.main()
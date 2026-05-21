"""
File: security_qa_suite.py
Description: A beginner-friendly, self-contained QA Automation project
             combining API Testing with basic Cybersecurity guardrails (OWASP Top 10).
             Contains a mock bank backend and a test suite validating
             IDOR, SQL Injection, and Rate Limiting.
No third-party installations required. Runs natively out of the box.
"""

import unittest
import json
import time


# ==============================================================================
# MOCK FINTECH BACKEND ENGINE (The System Under Test)
# ==============================================================================
class MockBankAPI:
    """Simulates a lightweight backend banking system with real security controls."""

    def __init__(self):
        # Simulated Secure Database
        self.accounts_db = {
            "ACC-11111": {"owner": "User A", "balance": 500.00},
            "ACC-22222": {"owner": "User B", "balance": 12500.75}
        }
        # Tracks login attempt counts per username to handle rate-limiting
        self.login_attempts_tracker = {}

    def get_account_details(self, account_id, auth_token):
        """
        Simulates: GET /api/v1/account/<account_id>
        Vulnerability Checked: BOLA / IDOR (Broken Object Level Authorization)
        """
        # Security Guardrail: Check if user is logged in
        if not auth_token or "token-for-" not in auth_token:
            return 401, {"error": "UNAUTHORIZED", "message": "Missing or invalid token."}

        # Extract identity from the token (e.g., "token-for-ACC-11111" -> "ACC-11111")
        token_identity = auth_token.replace("token-for-", "")

        # CRITICAL SECURITY CHECK: Does the logged-in identity match the requested account?
        if token_identity != account_id:
            return 403, {"error": "FORBIDDEN", "message": "Access Denied. You do not own this account."}

        if account_id not in self.accounts_db:
            return 404, {"error": "NOT_FOUND", "message": "Account not found."}

        return 200, self.accounts_db[account_id]

    def login(self, username, password):
        """
        Simulates: POST /api/v1/login
        Vulnerabilities Checked: SQL Injection (Input Validation) & Rate Limiting
        """
        # 1. RATE LIMITING GUARDRAIL
        # Track attempts for brute-force defense
        self.login_attempts_tracker[username] = self.login_attempts_tracker.get(username, 0) + 1
        if self.login_attempts_tracker[username] > 5:
            return 429, {"error": "TOO_MANY_REQUESTS", "message": "Rate limit exceeded. Try again later."}

        # 2. SQL INJECTION (SQLi) GUARDRAIL
        # In a real app, bad input breaks raw database queries. We simulate a sanitization check here.
        dangerous_characters = ["'", "--", "OR ", "UNION", "SELECT"]
        for bad_char in dangerous_characters:
            if bad_char in username or bad_char in password:
                # If a secure system catches malicious SQL code, it drops it safely.
                # A broken application would crash and return a 500 Internal Server Error.
                return 400, {"error": "BAD_REQUEST", "message": "Potential SQL Injection Detected."}

        # 3. STANDARD AUTHENTICATION LOGIC
        if username == "user_a" and password == "SecurePass123!":
            return 200, {"status": "SUCCESS", "token": "token-for-ACC-11111"}

        return 401, {"error": "UNAUTHORIZED", "message": "Invalid credentials."}


# ==============================================================================
# AUTOMATED SECURITY QA TEST SUITE
# ==============================================================================
class TestSecurityQAGuardrails(unittest.TestCase):

    def setUp(self):
        """Initializes a fresh, clean API instance before every test scenario."""
        self.api = MockBankAPI()
        # Establish a valid active session for basic authenticated scenarios
        _, login_data = self.api.login("user_a", "SecurePass123!")
        self.user_a_token = login_data["token"]

    def log_scenario(self, title, request_info, response_code, response_body):
        """Helper to print out senior-grade scannable logs for debugging."""
        print(f"\n[SECURITY SCENARIO]: {title}")
        print(f"  --> Action: {request_info}")
        print(f"  <-- Response Code: {response_code}")
        print(f"  <-- Response Payload: {json.dumps(response_body)}")

    # --------------------------------------------------------------------------
    # CATEGORY 1: IDOR / BOLA Tests
    # --------------------------------------------------------------------------
    def test_idor_happy_path(self):
        """Verify User A can successfully view their own account balance."""
        code, body = self.api.get_account_details("ACC-11111", self.user_a_token)
        self.log_scenario("IDOR Base Case (Own Account Access)", "GET /account/ACC-11111", code, body)

        self.assertEqual(code, 200)
        self.assertEqual(body["owner"], "User A")

    def test_idor_attack_blocked(self):
        """SECURITY TEST: Verify User A is strictly BLOCKED from viewing User B's account."""
        # Attack vector: Modifying the URL resource identifier while keeping User A's token
        code, body = self.api.get_account_details("ACC-22222", self.user_a_token)
        self.log_scenario("IDOR Manipulation Attempt", "GET /account/ACC-22222 (Using User A Token)", code, body)

        # The QA Security Assertion: The framework must defend itself.
        self.assertEqual(code, 403, "VULNERABILITY DETECTED: API allowed unauthorized IDOR access!")
        self.assertEqual(body["error"], "FORBIDDEN")

    # --------------------------------------------------------------------------
    # CATEGORY 2: SQL Injection Defense (Input Validation)
    # --------------------------------------------------------------------------
    def test_sql_injection_payloads(self):
        """SECURITY TEST: Data-driven loop sending malicious SQL characters to login."""
        sql_payloads = [
            "admin' --",
            "' OR '1'='1",
            "user_a' UNION SELECT NULL--"
        ]

        for malicious_input in sql_payloads:
            code, body = self.api.login(malicious_input, "any_password")
            self.log_scenario(
                f"SQL Injection Attack Input: [{malicious_input}]",
                "POST /login", code, body
            )

            # The QA Security Assertion:
            # We assert the API handles this as a client mistake (400) or denial (401).
            # It must NEVER crash with a 500 Internal Server Error, which signals a database flaw.
            self.assertIn(code, [400, 401], f"VULNERABILITY DETECTED: API returned {code} on SQL Payload!")
            self.assertNotEqual(code, 500, "CRITICAL CRASH: API database framework is vulnerable to crashes!")

    # --------------------------------------------------------------------------
    # CATEGORY 3: Rate Limiting (Brute-Force / Denial of Service)
    # --------------------------------------------------------------------------
    def test_brute_force_rate_limiting_gate(self):
        """SECURITY TEST: Rapidly bombard login endpoint to ensure automation defense triggers."""
        response_codes = []

        print("\n[SECURITY SCENARIO]: Launching Rapid Login Brute-Force Bombardment (7 requests)...")
        # Run an automated loop hitting the API 7 times quickly
        for i in range(1, 8):
            code, body = self.api.login("user_a", f"WrongPasswordAttempt{i}")
            response_codes.append(code)
            print(f"  * Attempt #{i} Result Code: {code}")

        # The QA Security Assertion:
        # A secure endpoint must trip its circuit breaker and return a 429 "Too Many Requests"
        # somewhere inside an excessive spam pattern.
        self.assertIn(429, response_codes, "VULNERABILITY DETECTED: API allows infinite brute-force attacks!")
        self.assertEqual(response_codes[-1], 429, "Final request should be strictly blocked by rate-limiting engine.")


if __name__ == "__main__":
    print("======================================================================")
    print(" STARTING RUNTIME: AUTOMATED OWASP TOP 10 REGRESSION SUITE            ")
    print("======================================================================")
    unittest.main()
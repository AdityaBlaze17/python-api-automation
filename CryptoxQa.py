"""
File: crypto_qa_suite.py
Description: Intermediate-level QA + CyberSec cross-over project.
             Demonstrates automated validation of AES-256 Symmetric Encryption
             and data-tampering integrity verification.
Dependency: Requires the 'cryptography' library (`pip install cryptography`).
"""

import unittest
import json
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os


# ==============================================================================
# CRYPTOGRAPHY ENGINE ENGINE (Helper utility shared by Client & Server)
# ==============================================================================
class CryptoEngine:
    """Handles standard AES-256-GCM encryption/decryption workflows."""

    def __init__(self, shared_key: bytes):
        self.key = shared_key  # Must be exactly 32 bytes for AES-256

    def encrypt(self, plain_text: str) -> dict:
        """Encrypts data and packages it with an initialization vector (IV) and auth tag."""
        iv = os.urandom(12)  # Secure random 12-byte IV for GCM mode
        encryptor = Cipher(
            algorithms.AES(self.key),
            modes.GCM(iv),
            backend=default_backend()
        ).encryptor()

        cipher_text = encryptor.update(plain_text.encode()) + encryptor.finalize()

        # Network payloads must be text-based, so encode binary bytes to Base64 strings
        return {
            "iv": base64.b64encode(iv).decode('utf-8'),
            "payload": base64.b64encode(cipher_text).decode('utf-8'),
            "tag": base64.b64encode(encryptor.tag).decode('utf-8')
        }

    def decrypt(self, iv_str: str, cipher_str: str, tag_str: str) -> str:
        """Decrypts data and implicitly checks cryptographic integrity via GCM tag."""
        iv = base64.b64decode(iv_str)
        cipher_text = base64.b64decode(cipher_str)
        tag = base64.b64decode(tag_str)

        decryptor = Cipher(
            algorithms.AES(self.key),
            modes.GCM(iv, tag),
            backend=default_backend()
        ).decryptor()

        decrypted_bytes = decryptor.update(cipher_text) + decryptor.finalize()
        return decrypted_bytes.decode('utf-8')


# ==============================================================================
# MOCK SECURE HEALTH API BACKEND (The System Under Test)
# ==============================================================================
class SecureHealthAPI:
    """Backend server expecting encrypted payloads for secure processing."""

    def __init__(self, secret_key: bytes):
        self.crypto = CryptoEngine(secret_key)

    def receive_prescription(self, request_json: str) -> tuple:
        """POST /v1/prescriptions endpoint handling encrypted pharmacy data."""
        try:
            data = json.loads(request_json)

            # 1. CRITICAL SECURITY GUARDRAIL: Decrypt incoming payload
            # If the data was tampered with, the cryptography library will throw an error automatically.
            decrypted_raw = self.crypto.decrypt(data["iv"], data["payload"], data["tag"])
            prescription_details = json.loads(decrypted_raw)

            # Business logic validation post-decryption
            if not prescription_details.get("patient_name") or not prescription_details.get("medication"):
                return 400, {"error": "BAD_REQUEST", "message": "Missing required prescription metrics."}

            # Process success response securely encrypted back to client
            success_msg = json.dumps({"status": "PROCESSED", "confirmation_code": "RX-88391"})
            encrypted_response = self.crypto.encrypt(success_msg)
            return 201, encrypted_response

        except Exception:
            # If decryption fails (due to bad keys, bad tampering, altered bits)
            return 400, {
                "error": "CRYPTO_INTEGRITY_FAILURE",
                "message": "Payload was tampered with or corrupted in transit. Request dropped immediately."
            }


# ==============================================================================
# AUTOMATED CRYPTOGRAPHY QA SUITE
# ==============================================================================
class TestCryptographyQA(unittest.TestCase):

    def setUp(self):
        """Generates a secure shared key environment mimicking production handshake."""
        # 32-byte secret key shared securely between Client Test Harness and Server Backend
        self.shared_secret = os.urandom(32)
        self.api = SecureHealthAPI(self.shared_secret)
        self.client_crypto = CryptoEngine(self.shared_secret)

    def log_step(self, title, payload):
        """Intermediate reporting visual logs."""
        print(f"\n  [DATA STAGE - {title}]:")
        print(f"    {json.dumps(payload, indent=4)}")

    def test_happy_path_encrypted_lifecycle(self):
        """Scenario: Test automated runtime encryption, transmission, backend parsing, and response decryption."""
        print("\n=== SCENARIO: VALID ENCRYPTED LIFECYCLE ===")

        # 1. Design raw human-readable test data
        raw_test_data = {
            "patient_name": "Jane Smith",
            "medication": "Amoxicillin 500mg",
            "refills": 2
        }
        self.log_step("Raw Test Data (Client Side)", raw_test_data)

        # 2. Encrypt using client engine
        encrypted_request = self.client_crypto.encrypt(json.dumps(raw_test_data))
        self.log_step("Encrypted Request Payload Sent Over Network", encrypted_request)

        # 3. Fire payload at the API
        status_code, response_payload = self.api.receive_prescription(json.dumps(encrypted_request))
        print(f"  <-- Network Status Code Recieved: {status_code}")
        self.log_step("Encrypted Response Payload Received From API", response_payload)

        # 4. QA Assertions & Decryption of output
        self.assertEqual(status_code, 201)

        decrypted_response_str = self.client_crypto.decrypt(
            response_payload["iv"], response_payload["payload"], response_payload["tag"]
        )
        decrypted_response = json.loads(decrypted_response_str)
        self.log_step("Final Decrypted Server Response", decrypted_response)

        self.assertEqual(decrypted_response["status"], "PROCESSED")

    def test_security_payload_tampering_defense(self):
        """SECURITY TEST: Intentionally manipulate encrypted data in transit to ensure server drops payload."""
        print("\n=== SCENARIO: SECURITY DATA-TAMPERING ATTACK ===")

        raw_test_data = {"patient_name": "Jane Smith", "medication": "Amoxicillin 500mg"}
        encrypted_request = self.client_crypto.encrypt(json.dumps(raw_test_data))

        # MITM (Man-in-the-Middle) Simulation:
        # Snatch the encrypted payload and alter a single bit inside the ciphertext string
        original_payload_str = encrypted_request["payload"]

        # Change the very last character of the base64 encrypted payload string to sabotage it
        tampered_char = 'Z' if original_payload_str[-1] != 'Z' else 'Y'
        tampered_payload_str = original_payload_str[:-1] + tampered_char
        encrypted_request["payload"] = tampered_payload_str

        self.log_step("Tampered Payload (Modified mid-flight by Automation Harness)", encrypted_request)

        # Send corrupted data to the server
        status_code, response_payload = self.api.receive_prescription(json.dumps(encrypted_request))
        print(f"  <-- Network Status Code Recieved: {status_code}")
        self.log_step("Server Response to Tampered Attack", response_payload)

        # QA Security Assertion: The API engine must detect structural corruption and safely reject
        self.assertEqual(status_code, 400)
        self.assertEqual(response_payload["error"], "CRYPTO_INTEGRITY_FAILURE")


if __name__ == "__main__":
    print("======================================================================")
    print(" RUNNING: INTERMEDIATE CRYPTOGRAPHIC DATA INTEGRITY AUTOMATION SUITE  ")
    print("======================================================================")
    unittest.main()
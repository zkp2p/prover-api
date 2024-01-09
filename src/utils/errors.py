from enum import Enum

class Errors:

    class ErrorCodes(Enum):
        INVALID_PAYMENT_TYPE = 1
        INVALID_CIRCUIT_TYPE = 2
        INVALID_DOMAIN_KEY = 3
        DKIM_VALIDATION_FAILED = 4
        INVALID_FROM_ADDRESS = 5
        INVALID_EMAIL_SUBJECT = 6
        PROOF_GEN_FAILED = 7
        INVALID_EMAIL = 8

    def __init__(self):
        self.error_messages = {
            self.ErrorCodes.INVALID_PAYMENT_TYPE: "Invalid payment type",
            self.ErrorCodes.INVALID_CIRCUIT_TYPE: "Invalid circuit type. Circuit type should be send or registration",
            self.ErrorCodes.INVALID_DOMAIN_KEY: "❗️Domain key might have changed❗️",
            self.ErrorCodes.DKIM_VALIDATION_FAILED: "DKIM validation failed",
            self.ErrorCodes.INVALID_FROM_ADDRESS: "Invalid from address",
            self.ErrorCodes.INVALID_EMAIL_SUBJECT: "Invalid email subject",
            self.ErrorCodes.PROOF_GEN_FAILED: "Proof generation failed",
            self.ErrorCodes.INVALID_EMAIL: "Invalid email"
        }

    def get_error_message(self, error_code):
        return self.error_messages[error_code]
    
    def get_error_response(self, error_code):
        return {
            "code": error_code.value,
            "message": self.get_error_message(error_code)
        }
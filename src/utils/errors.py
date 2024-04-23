from enum import Enum

class Errors:

    class ErrorCodes(Enum):
        TESTING = 100
        INVALID_PAYMENT_TYPE = 1
        INVALID_CIRCUIT_TYPE = 2
        INVALID_DOMAIN_KEY = 3
        # Email
        DKIM_VALIDATION_FAILED = 4
        INVALID_FROM_ADDRESS = 5
        INVALID_EMAIL_SUBJECT = 6
        PROOF_GEN_FAILED = 7
        INVALID_EMAIL = 8
        INVALID_SELECTOR = 9    
        # TLSN
        TLSN_PROOF_VERIFICATION_FAILED = 10
        TLSN_WISE_INVALID_TRANSFER_VALUES = 11
        TLSN_WISE_INVALID_PROFILE_REGISTRATION_VALUES = 12
        TLSN_WISE_INVALID_MC_ACCOUNT_REGISTRATION_VALUES = 13

    def __init__(self):
        self.error_messages = {
            self.ErrorCodes.TESTING: "Testing 🙂",
            # Api
            self.ErrorCodes.INVALID_PAYMENT_TYPE: "Invalid payment type",
            self.ErrorCodes.INVALID_CIRCUIT_TYPE: "Invalid circuit type. Circuit type should be send or registration",
            # Email
            self.ErrorCodes.INVALID_DOMAIN_KEY: "❗️Domain key might have changed❗️",
            self.ErrorCodes.DKIM_VALIDATION_FAILED: "DKIM validation failed",
            self.ErrorCodes.INVALID_FROM_ADDRESS: "Invalid from address",
            self.ErrorCodes.INVALID_EMAIL_SUBJECT: "Invalid email subject",
            self.ErrorCodes.PROOF_GEN_FAILED: "Proof generation failed",
            self.ErrorCodes.INVALID_EMAIL: "Invalid email",
            self.ErrorCodes.INVALID_SELECTOR: "❗️Selector might have changed❗️",
            # TLSN
            self.ErrorCodes.TLSN_PROOF_VERIFICATION_FAILED: "TLSN proof verification failed",
            self.ErrorCodes.TLSN_WISE_INVALID_TRANSFER_VALUES: "TLSN invalid extracted values for `transfer`",
            self.ErrorCodes.TLSN_WISE_INVALID_PROFILE_REGISTRATION_VALUES: "TLSN invalid extracted values for `profile registration`",
            self.ErrorCodes.TLSN_WISE_INVALID_MC_ACCOUNT_REGISTRATION_VALUES: "TLSN invalid extracted values for `mc account registration`",

        }

    def get_error_message(self, error_code):
        return self.error_messages[error_code]
    
    def get_error_response(self, error_code):
        return {
            "code": error_code.value,
            "message": self.get_error_message(error_code)
        }
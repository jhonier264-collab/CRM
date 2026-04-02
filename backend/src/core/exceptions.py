
class CRMError(Exception):
    """Base error for the CRM system."""
    pass

class DatabaseError(CRMError):
    """Error related to infrastructure or connection."""
    pass

class ValidationError(CRMError):
    """Error for data validation (XOR, Format, etc.)."""
    pass

class AuthError(CRMError):
    """Error for permissions or authentication issues."""
    pass

class DuplicateError(CRMError):
    """Error for duplicate data (Unique constraints)."""
    pass

class XORRuleViolation(ValidationError):
    """Specific error for XOR rule violations between User and Company."""
    pass

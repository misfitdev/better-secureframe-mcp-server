import os

# Dummy credentials so any lazy config load during import/registration succeeds.
os.environ.setdefault("SECUREFRAME_API_KEY", "test-key")
os.environ.setdefault("SECUREFRAME_API_SECRET", "test-secret")

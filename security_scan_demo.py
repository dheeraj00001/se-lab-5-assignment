"""Demo script purposely containing security anti-patterns and dummy credentials.

Prepared for SE Lab 5 / Topic 19 Demo:
'Static Code Analysis and Security Scanning Integration'
- Intercept security flaws, leaks, or performance anti-patterns.
- Demonstrate exact severity level and line numbers of vulnerabilities discovered.
"""

import hashlib
import pickle
import subprocess


# Anti-Pattern 1: Hardcoded dummy credentials & secret tokens (CWE-259, B105)
DUMMY_API_KEY = "ghp_dummy1234567890abcdefghijklmnopqrstuvwxyz"  # line 15
DUMMY_DATABASE_PASSWORD = "SuperSecretDbPassword123!"  # line 16


def process_user_math(expression):
    """Anti-Pattern 2: Arbitrary code execution via eval (CWE-78, B307)."""
    return eval(expression)  # line 21


def insecure_hash(password):
    """Anti-Pattern 3: Insecure MD5 cryptographic hash (CWE-327, B324)."""
    return hashlib.md5(password.encode("utf-8")).hexdigest()  # line 26


def ping_host(host_ip):
    """Anti-Pattern 4: Command injection via shell execution (CWE-78, B602/B605)."""
    command = f"ping -c 1 {host_ip}"
    return subprocess.Popen(command, shell=True)  # line 32


def restore_user_session(serialized_data):
    """Anti-Pattern 5: Unsafe deserialization using pickle (CWE-502, B301)."""
    return pickle.loads(serialized_data)  # line 37


def swallow_exceptions_silently(user_dict, key):
    """Anti-Pattern 6: Bare except passing silently (CWE-703, B110)."""
    try:
        return user_dict[key]
    except:  # line 44
        pass
    return None


if __name__ == "__main__":
    print("Security scanning demo target loaded.")

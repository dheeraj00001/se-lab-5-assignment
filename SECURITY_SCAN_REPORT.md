# Security Scanning Integration & Anti-Pattern Analysis (Topic 19 Demo)

**Task:** Static Code Analysis and Security Scanning Integration  
**Objective:** Intercept security flaws, leaks, or performance anti-patterns before human evaluation phases.  
**Student Name:** Gurijala Dheeraj Reddy  
**SRN:** PES2UG24AM059  
**Scanner Integrated:** Bandit Static Application Security Testing (SAST) Scanner & GitHub Actions CI  
**Target Code with Intentional Anti-Patterns:** `security_scan_demo.py`  

---

## 1. Executive Summary

As required by the lab demo specification, an open-source static security analysis tool (**Bandit**) and automated GitHub Actions CI pipeline were integrated to intercept vulnerabilities, credentials, and anti-patterns prior to human evaluation. 

A dedicated verification script (`security_scan_demo.py`) was constructed containing intentional security anti-patterns (hardcoded credentials, dangerous code evaluation, weak cryptographic primitives, shell injection, unsafe deserialization, and silent exception swallowing). The scan successfully caught and cataloged all flaws with exact severity levels, confidence ratings, and line numbers.

---

## 2. Scanner Findings Summary Table (Deliverable for Demo)

| # | Vulnerability / Anti-Pattern | Scanner Rule ID | Severity | Confidence | Line No. | CWE Reference | Impact & Risk Analysis |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---|
| **1** | **Weak Cryptographic Hash (MD5)** | `B324:hashlib` | **HIGH** | High | **Line 26** | CWE-327 | MD5 hash algorithm is broken and susceptible to hash collisions and rainbow table attacks. |
| **2** | **Shell Injection via `Popen(shell=True)`** | `B602:popen_shell` | **HIGH** | High | **Line 32** | CWE-78 | Passing unsanitized input to a shell command allows arbitrary command injection on the host. |
| **3** | **Arbitrary Code Execution (`eval`)** | `B307:eval` | **MEDIUM** | High | **Line 21** | CWE-78 | Dynamic execution of unverified strings allows remote attackers to run arbitrary Python code. |
| **4** | **Insecure Object Deserialization (`pickle`)** | `B301:pickle` | **MEDIUM** | High | **Line 37** | CWE-502 | Deserializing untrusted pickle streams can instantiate malicious objects and trigger RCE. |
| **5** | **Hardcoded Credential / Secret Password** | `B105:hardcoded_pw` | **LOW** | Medium | **Line 16** | CWE-259 | Plaintext secrets stored in version control expose backend systems to unauthorized access. |
| **6** | **Silent Error Suppression (`except: pass`)** | `B110:try_pass` | **LOW** | High | **Line 44** | CWE-703 | Bare `except: pass` silences critical errors and runtime exceptions without logging. |
| **7** | **Insecure Module Import (`pickle`)** | `B403:import` | **LOW** | High | **Line 10** | CWE-502 | Importing known vulnerable serialization library. |
| **8** | **Insecure Module Import (`subprocess`)** | `B404:import` | **LOW** | High | **Line 11** | CWE-78 | Importing process invocation module without parameter array enforcement. |

---

## 3. Raw Scanner Output Terminal Transcript

```text
Run started: 2026-11-17
Scanned file: security_scan_demo.py

>> Issue: [B105:hardcoded_password_string] Possible hardcoded password: 'SuperSecretDbPassword123!'
   Severity: Low   Confidence: Medium
   CWE: CWE-259 (https://cwe.mitre.org/data/definitions/259.html)
   Location: .\security_scan_demo.py:16:26

>> Issue: [B307:blacklist] Use of possibly insecure function - consider using safer ast.literal_eval.
   Severity: Medium   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   Location: .\security_scan_demo.py:21:11

>> Issue: [B324:hashlib] Use of weak MD5 hash for security. Consider usedforsecurity=False
   Severity: High   Confidence: High
   CWE: CWE-327 (https://cwe.mitre.org/data/definitions/327.html)
   Location: .\security_scan_demo.py:26:11

>> Issue: [B602:subprocess_popen_with_shell_equals_true] subprocess call with shell=True identified
   Severity: High   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   Location: .\security_scan_demo.py:32:11

>> Issue: [B301:blacklist] Pickle and modules that wrap it can be unsafe when used to deserialize untrusted data
   Severity: Medium   Confidence: High
   CWE: CWE-502 (https://cwe.mitre.org/data/definitions/502.html)
   Location: .\security_scan_demo.py:37:11

>> Issue: [B110:try_except_pass] Try, Except, Pass detected.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   Location: .\security_scan_demo.py:44:4

Run metrics:
   Total issues: 8 (High: 2, Medium: 2, Low: 4)
   Confidence: High: 7, Medium: 1
```

---

## 4. Pipeline Integration Architecture

The GitHub Actions workflow `.github/workflows/static-analysis-and-security.yml` enforces automated static scanning on all branches:
1. **Flake8 Gate**: Rejects unformatted, poorly spaced, or unstandardized code.
2. **Pylint Quality Gate**: Enforces a strict score threshold of `>= 9.5 / 10`.
3. **Bandit Security Scanner**: Audits production and staging code to block High/Medium severity vulnerabilities.
4. **Secret / Anti-Pattern Detection**: Scans pull requests before merge approval.

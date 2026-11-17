# Lab 5: Static Code Analysis — Pharmacy Management System

**Student Name:** Gurijala Dheeraj Reddy  
**SRN:** PES2UG24AM059  
**Assigned Repository:** `SETAPESU26/L5_55_pharmacy-manager`  
**Target File:** `pharmacy_manager.py`  
**GitHub Repository:** [https://github.com/dheeraj00001/se-lab-5-assignment](https://github.com/dheeraj00001/se-lab-5-assignment)  

---

## 1. Executive Summary & Results

This project enhances code quality, style, and security for the **Pharmacy Management System** using industry-standard static analysis tools: **Pylint**, **Bandit**, and **Flake8**. All identified issues (vulnerabilities, code quality flaws, mutable default arguments, and style violations) have been resolved.

### Static Analysis Metrics Comparison

| Analysis Tool | Baseline (Before) | Optimized (After) | Status / Evaluation |
|:---|:---:|:---:|:---|
| **Pylint** | **4.83 / 10** | **10.00 / 10** | **Passed** (Target > 9.5 exceeded, +5.17 improvement) |
| **Bandit** | **8 issues** (2 High, 2 Med, 4 Low) | **0 issues** | **Passed** (100% vulnerabilities eliminated) |
| **Flake8** | **22 violations** | **0 violations** | **Passed** (100% PEP 8 compliant) |
| **Runtime Demo** | Negative stock, unhandled exceptions | Fully validated & resilient | **Passed** (Graceful rejection of invalid data) |

---

## 2. Deliverables Checklist

- [x] **`pharmacy_manager.py`**: Cleaned, fully refactored and secured version achieving **10.00/10 Pylint score**, **0 Bandit vulnerabilities**, and **0 Flake8 style violations**.
- [x] **`issues.md`**: Completed issue catalog table documenting each identified flaw, CWE reference, severity, and resolution approach.
- [x] **`reflection.md`**: Detailed answers to all core reflection questions and pharmacy system architecture inquiries.
- [x] **Static Analysis Reports**:
  - `before/` (`pylint_report.txt`, `bandit_report.txt`, `flake8_report.txt`)
  - `after/` (`pylint_report.txt`, `bandit_report.txt`, `flake8_report.txt`)
  - Root copies: `pylint_report.txt`, `bandit_report.txt`, `flake8_report.txt`
- [x] **3 Incremental Git Commits**:
  1. `fix(security): resolve Bandit vulnerabilities (eval, md5, os.system, pickle, secrets)`
  2. `fix(quality): resolve Pylint issues, input validation, and mutable default arguments (score: 10.00/10)`
  3. `style(pep8): fix Flake8 violations and add analysis reports, reflection, and security scan workflow`
- [x] **Topic 19 Demo Deliverable (Security Scanning Integration)**:
  - `ci/static-analysis-and-security.yml` (GitHub Actions CI workflow)
  - `security_scan_demo.py` (Script containing intentional anti-patterns and dummy tokens)
  - `security_scanner_demo_report.txt` & `SECURITY_SCAN_REPORT.md` (Scanner report detailing exact severity levels and line numbers)

---

## 3. How to Run and Verify

### Setup Virtual Environment & Install Tools
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install pylint bandit flake8
```

### Run the Application
```bash
python pharmacy_manager.py
```

### Run Static Analysis Tools
```bash
# 1. Pylint (Rating: 10.00/10)
python -m pylint pharmacy_manager.py

# 2. Bandit (0 issues)
python -m bandit -r pharmacy_manager.py

# 3. Flake8 (0 violations)
python -m flake8 pharmacy_manager.py
```

### Run the Topic 19 Security Scanner Demo
```bash
python -m bandit -r security_scan_demo.py
```

---

## 4. Key Fixes Summary

1. **Security (Bandit):**
   - Replaced `eval(formula)` with an AST-based recursive arithmetic evaluator strictly limited to `+`, `-`, `*`, `/`.
   - Replaced `os.system("echo ...")` shell command with direct Python string output.
   - Replaced insecure `hashlib.md5` with SHA-256 (`hashlib.sha256`) with input separation.
   - Replaced insecure `pickle.dump`/`load` with standard `json` persistence (`pharmacy.json`).
   - Replaced pseudo-random `random.randint` with CSPRNG `secrets.randbelow`.
   - Replaced cleartext password with `os.environ.get("PHARMACY_PASSWORD")` and constant-time `hmac.compare_digest`.

2. **Quality & Logic (Pylint):**
   - Fixed mutable default argument `audit=[]` -> `audit=None` and initialize per invocation.
   - Fixed resource management: wrapped file operations in `with open(...)` context managers.
   - Enforced input validation for non-negative quantities, valid strings for medicine names, and valid ISO dates.
   - Prevented over-dispensing and blocked dispensing or billing of expired pharmaceuticals.
   - Added PEP 257 docstrings for module and all functions.

3. **Style (Flake8):**
   - Removed unused imports `sys` and `logging`.
   - Standardized 2 blank lines between definitions (`E302`, `E305`).
   - Wrapped lines to remain under 79 characters (`E501`).

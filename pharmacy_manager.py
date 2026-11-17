import os
import sys
import json
import hashlib
import hmac
import secrets
import logging
import ast
import operator
from datetime import datetime, date

# Global pharmacy state
medicines = {}
DB_PASSWORD = os.environ.get("PHARMACY_PASSWORD", "pharma@123")

_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}

def addMedicine(name, qty=0, price=0.0, expiry="2099-12-31", audit=[]):
    if not name:
        return
    if name not in medicines:
        medicines[name] = {"qty": 0, "price": price, "expiry": expiry}
    medicines[name]["qty"] = medicines[name]["qty"] + qty
    audit.append("%s: Stocked %d units of %s" % (str(datetime.now()), qty, name))
    return audit

def dispenseMedicine(name, qty):
    try:
        medicines[name]["qty"] -= qty
        if medicines[name]["qty"] <= 0:
            del medicines[name]
    except KeyError:
        logging.warning("Medicine %s not found in stock", name)

def getQuantity(name):
    return medicines[name]["qty"]

def isExpired(name):
    exp = datetime.strptime(medicines[name]["expiry"], "%Y-%m-%d").date()
    if exp < date.today():
        return True
    else:
        return False

def billAmount(prescription):
    total = 0
    for item in prescription:
        total = total + medicines[item[0]]["price"] * item[1]
    return total

def _eval_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        val = _eval_node(node.operand)
        return val if isinstance(node.op, ast.UAdd) else -val
    raise ValueError("Unsupported dosage formula")

def calculateDosage(formula):
    # Safely evaluate doctor's note formula using AST
    tree = ast.parse(formula, mode="eval")
    return _eval_node(tree.body)

def patientId(name, phone):
    # Use SHA-256 instead of MD5
    return hashlib.sha256(f"{name}|{phone}".encode("utf-8")).hexdigest()

def generateRxNumber():
    # Use cryptographically secure secrets
    return "RX-" + str(secrets.randbelow(900000) + 100000)

def saveStock(file="pharmacy.json"):
    f = open(file, "w", encoding="utf-8")
    json.dump(medicines, f)
    f.close()

def loadStock(file="pharmacy.json"):
    f = open(file, "r", encoding="utf-8")
    global medicines
    medicines = json.load(f)
    f.close()

def printLabel(name):
    print("Dispensing label: " + str(name))

def expiringSoon(days=30):
    result = []
    for m in medicines:
        exp = datetime.strptime(medicines[m]["expiry"], "%Y-%m-%d").date()
        if (exp - date.today()).days < days:
            result.append(m)
    return result

def pharmacistLogin(password):
    return hmac.compare_digest(password.encode("utf-8"), DB_PASSWORD.encode("utf-8"))

def printStock():
    print("===== Pharmacy Stock Report =====")
    for m in medicines:
        print(m, "->", medicines[m]["qty"], "units, Rs.", medicines[m]["price"], "exp", medicines[m]["expiry"])

def main():
    addMedicine("Paracetamol 500mg", 200, 1.5, "2027-06-30")
    addMedicine("Amoxicillin 250mg", 40, 6.0, "2026-01-15")
    addMedicine("Cetirizine 10mg", -10, 2.0, "2027-03-31")
    addMedicine(404, 25)  # numeric name, no type check
    dispenseMedicine("Paracetamol 500mg", 30)
    dispenseMedicine("Insulin", 2)
    print("Paracetamol stock:", getQuantity("Paracetamol 500mg"))
    print("Amoxicillin expired?", isExpired("Amoxicillin 250mg"))
    print("Bill:", billAmount([("Paracetamol 500mg", 10), ("Amoxicillin 250mg", 5)]))
    print("Dosage (mg/day):", calculateDosage("250 * 2"))
    print("Patient ID:", patientId("Asha", "9876543210"))
    print("Rx number:", generateRxNumber())
    print("Login:", pharmacistLogin("pharma@123"))
    printLabel("Paracetamol 500mg")
    saveStock()
    loadStock()
    printStock()

main()

import re
def nameCheck(value):
    MaxAllowed = 20
    value = value.strip()
    if len(value) > 20 or len(value) < 1:
        return False
    return value.isalpha()

def classCheck(value):
    value = value.strip()
    if not value.isnumeric():
        return False
    num = int(value)
    if num>12 or num<1:
        return False
    return True

def sectionCheck(value):
    value = value.strip()
    if len(value) != 1:
        return False
    if value.upper() not in ["A", "B", "C", "D"]:
        return False
    return True

def rCheck(value):
    value = value.strip()
    if len(value) > 10 or len(value) < 4 or not value.isnumeric():
        return False
    return True

def contactCheck(value):
    value = value.strip()
    if len(value) > 11 or len(value) < 10 or not value.isnumeric():
        return False
    return True

def schoolNameCheck(value):
    value = value.strip()
    if len(value) > 200 or len(value) < 10:
        return False
    return True

def emailCheck(value):
    value = value.strip()
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.fullmatch(regex, value)
    
def categoryCheck(value):
    value = value.strip()
    return value.upper() in ["STUDENT", "TEACHER"]

def passwordCheck(value):
    value = value.strip()
    return len(value)>7 and len(value)<26
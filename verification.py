import re

regexMobile = '^[0-9]{10}$'
regexEmail = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'

def verifyRegister(name, mobile, email, password):
    errorStatus = [True, True, True, True]
    if(len(name) == 0):
        errorStatus[0] = False
    if(re.search(regexMobile,mobile) is None):
        errorStatus[1] = False
    if(re.search(regexEmail,email) is None):
        errorStatus[2] = False
    if(len(password) > 15 or len(password) < 4):
        errorStatus[3] = False

    return errorStatus

def verifyChange(email, password):
    errorStatus = [True, True]
    if(re.search(regexEmail,email) is None):
        errorStatus[0] = False
    if(len(password) > 15 or len(password) < 4):
        errorStatus[1] = False

    return errorStatus
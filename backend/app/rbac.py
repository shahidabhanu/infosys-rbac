ROLE_ACCESS = {
    "employee": ["general"],
    "finance": ["finance", "general"],
    "hr": ["hr", "general"],
    "c_level": ["finance", "hr", "engineering", "general"],
    "admin": ["finance", "hr", "engineering", "general"]
}

def check_access(user_role, doc_role):
    return doc_role in ROLE_ACCESS.get(user_role, [])

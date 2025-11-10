

def check_valid_input(content):
    try:
        if not isinstance(content["id_algo"], int):
            return False
        if not isinstance(content["status"], bool):
            return False
        return True
    except:
        return False

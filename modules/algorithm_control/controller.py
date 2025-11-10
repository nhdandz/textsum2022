import init

def change_status(content):
    id_algo = content["id_algo"]
    status = content["status"]
    return init.update_status_algo(id_algo=id_algo, status=status)



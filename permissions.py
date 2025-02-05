def check_permissions(user_id, *args):
    return user_id in sum(args, [])


def create_user(mapper, username, password, email = ''):
    orm = mapper.orm
    if orm == 'django':
        return mapper.model.objects.create_user(username, email, password)
    elif orm == 'stdnet':
        return mapper.model.objects.create_user(username, password, email)
    else:
        raise NotImplementedError
    
    
def create_superuser(mapper, username, password, email = ''):
    orm = mapper.orm
    if orm == 'django':
        return mapper.model.objects.create_user(username, email, password)
    elif orm == 'stdnet':
        return mapper.model.objects.create_user(username, password, email)
    else:
        raise NotImplementedError
    
    

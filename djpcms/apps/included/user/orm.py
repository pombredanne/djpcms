

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
    
    
def authenticate(mapper, **credentials):
    orm = mapper.orm
    if orm == 'django':
        from django.contrib.auth import authenticate
        return authenticate(**credentials)
    elif orm == 'stdnet':
        from stdnet.contrib.sessions.middleware import authenticate
        return authenticate(**credentials)
    else:
        raise NotImplementedError
    

def login(mapper, request, user):
    orm = mapper.orm
    if orm == 'django':
        from django.contrib.auth import login
        return login(request,user)
    elif orm == 'stdnet':
        from stdnet.contrib.sessions.middleware import login
        return login(request,user)
    else:
        raise NotImplementedError
    

def logout(mapper, request):
    orm = mapper.orm
    if orm == 'django':
        from django.contrib.auth import logout
        return logout(request)
    elif orm == 'stdnet':
        from stdnet.contrib.sessions.middleware import logout
        return logout(request)
    else:
        raise NotImplementedError

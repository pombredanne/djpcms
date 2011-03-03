from py2py3 import ispy3k

if ispy3k():
    from http.cookies import SimpleCookie, BaseCookie, CookieError
else:
    from Cookie import SimpleCookie, BaseCookie, CookieError


def parse_cookie(cookie):
    if cookie == '':
        return {}
    if not isinstance(cookie, BaseCookie):
        try:
            c = SimpleCookie()
            c.load(cookie)
        except CookieError:
            # Invalid cookie
            return {}
    else:
        c = cookie
    cookiedict = {}
    for key in c.keys():
        cookiedict[key] = c.get(key).value
    return cookiedict

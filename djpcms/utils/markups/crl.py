import creole

from . import base


class Application(base.Application):
    code = 'crl'
    name = 'creole'
    
    def __call__(self, request, text):
        document = creole.Parser(text).parse()
        return creole.HtmlEmitter(document).emit().encode('utf-8', 'ignore')
    
    
creole_help = '''\
= Dealing with Fonts
{{{
= Title1
== Title2
=== Title3
==== Title4
}}}
= Title1
== Title2
=== Title3
==== Title4

{{{
this is a **bold text** and this is a //nice italic//.
}}}

this is a **bold text** and this is a //nice italic//.

= Tables
You can write table as well!
{{{
|= |=Currency|=Exposure|
|1| USD | 4.5mil |
|2| GBP | 0.4mil |
|3| EUR | 1.3mil |
}}}
becomes
|= |=Currency|=Exposure|
|1|USD|4.5mil|
|2|GBP|0.4mil|
|3|EUR|1.3mil|

Note the separator for the table header is {{{|=}}} while for the table body is simply {{{|}}}.
'''

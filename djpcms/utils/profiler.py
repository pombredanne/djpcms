'''\
Orignal version taken from http://djangosnippets.org/snippets/605/

Modified for use with djpcms

include in your MIDDLEWARE_CLASSES as the first one.

MIDDLEWARE_CLASSES = ('djpcms.utils.middleware.profiling.ProfileMiddleware',...)
'''
import sys
import os
import re
import hotshot, hotshot.stats
import tempfile

from py2py3 import StringIO

profile_template = '''\
<div class="djp-profiler">
    <pre>
    {0[stats]}
    </pre>
    {0[files]}
</div>'''

words_re = re.compile( r'\s+' )

group_prefix_re = [
    re.compile( "^.*/django/[^/]+" ),
    re.compile( "^(.*)/[^/]+$" ), # extract module path
    re.compile( ".*" ),           # catch strange entries
]

def get_group(file):
    for g in group_prefix_re:
        name = g.findall( file )
        if name:
            return name[0]

def get_summary(results_dict, sum):
    list = [ (item[1], item[0]) for item in results_dict.items() ]
    list.sort( reverse = True )
    list = list[:40]

    res = "      tottime\n"
    for item in list:
        res += "%4.1f%% %7.3f %s\n" % ( 100*item[0]/sum if sum else 0, item[0], item[1] )

    return res

def summary_for_files(stats_str):
    stats_str = stats_str.split("\n")[5:]

    mystats = {}
    mygroups = {}

    sum = 0

    for s in stats_str:
        fields = words_re.split(s);
        if len(fields) == 7:
            time = float(fields[2])
            sum += time
            file = fields[6].split(":")[0]

            if not file in mystats:
                mystats[file] = 0
            mystats[file] += time

            group = get_group(file)
            if not group in mygroups:
                mygroups[ group ] = 0
            mygroups[ group ] += time

    return "<pre>" + \
           " ---- By file ----\n\n" + get_summary(mystats,sum) + "\n" + \
           " ---- By group ---\n\n" + get_summary(mygroups,sum) + \
           "</pre>"


def profile_response(environ, start_response, PK, callback):
    """
    Displays hotshot profiling for any view.
    http://yoursite.com/yourview/?prof

    Add the "prof" key to query string by appending ?prof (or &prof=)
    and you'll see the profiling results in your browser.
    It's set up to only be available in django's debug mode, is available for superuser otherwise,
    but you really shouldn't add this middleware to any production configuration.

    WARNING: It uses hotshot profiler which is not thread safe.
    """
    query = environ.get('QUERY_STRING','')
    if PK not in query:
        return callback(environ, start_response)
    
    tmp = tempfile.mktemp()
    prof = hotshot.Profile(tmp)
    response = prof.runcall(callback, environ, start_response)
    prof.close()

    out = StringIO()
    old_stdout = sys.stdout
    sys.stdout = out

    stats = hotshot.stats.load(tmp)
    stats.sort_stats('time', 'calls')
    stats.print_stats()
    sys.stdout = old_stdout
    stats_str = '\n'.join(out.getvalue().split('\n')[:40])
    content = profile_template.format({'path':environ['PATH_INFO'],
                                       'stats':stats_str,
                                       'files':summary_for_files(stats_str)})
    response.content = content
    os.unlink(tmp)

    return response
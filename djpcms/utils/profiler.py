'''\
Orignal version taken from http://djangosnippets.org/snippets/605/

Modified for use with djpcms

include in your MIDDLEWARE_CLASSES as the first one.

MIDDLEWARE_CLASSES = ('djpcms.utils.middleware.profiling.ProfileMiddleware',...)
'''
import sys
import os
import re
#import hotshot, hotshot.stats
import tempfile
import cProfile as profiler
import pstats

from py2py3 import StringIO

profile_template = '''\
<div class="djp-profiler">
    {0[table]}
    <pre>
    {0[stats]}
    </pre>
    {0[group]}
</div>'''

words_re = re.compile( r'\s+' )

group_prefix_re = [
    re.compile( "^.*/djpcms/[^/]+" ),
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


def summary_for_files(stats_str, mystats, mygroups, sum):

    for fields in stats_str:
        ncalls = fields[1]
        time = float(fields[2])
        percall = float(fields[3])
        cumtime =float(fields[4])
        percall2 = float(fields[5])
        file_func = fields[6].split(':')
        if len(file_func) == 2:
            func = file_func[1]
            p = func.find('(')
            lineno = func[:p]
            func = func[p+1:-1]
        else:
            func = ''
            leneno = ''
        file = file_func[0]
        sum += time

        if not file in mystats:
            mystats[file] = 0
        mystats[file] += time

        group = get_group(file)
        if not group in mygroups:
            mygroups[ group ] = 0
        mygroups[ group ] += time
        
        yield ncalls,time,percall,cumtime,percall2,file,lineno,func


def make_stat_table(stats_str):
    from djpcms import html
    mystats = {}
    mygroups = {}
    sum = 0
    header = ('ncalls','tottime','percall','cumtime','percall',
              'filename','lineno','function')
    data = list(summary_for_files(stats_str,mystats,mygroups,sum))
    table = html.Table(header,data)
    
    group = "<pre>" + \
       " ---- By file ----\n\n" + get_summary(mystats,sum) + "\n" + \
       " ---- By group ---\n\n" + get_summary(mygroups,sum) + \
       "</pre>"
       
    return {'table':table,'group':group}
    

def data_stream(lines, num = None):
    if num:
        lines = lines[:num]
    for line in lines:
        if not line:
            continue
        fields = words_re.split(line)
        if len(fields) == 7:
            try:
                time = float(fields[2])
            except:
                continue
            yield fields
                        

def make_header(headers):
    for h in headers:
        if h:
            yield '<p>{0}</p>'.format(h)


def profile_response(environ, start_response, PK, callback):
    """
    Displays profiling for any view.
    http://yoursite.com/yourview/?prof

    Add the "prof" key to query string by appending ?prof (or &prof=)
    and you'll see the profiling results in your browser.
    It's set up to only be available in django's debug mode, is available for superuser otherwise,
    but you really shouldn't add this middleware to any production configuration.
    """
    from djpcms import html, sites
    from djpcms.template import loader
    query = environ.get('QUERY_STRING','')
    if PK not in query:
        return callback(environ, start_response)
    
    tmp = tempfile.mktemp()
    out = StringIO()    
    prof = profiler.Profile()
    response = prof.runcall(callback, environ, start_response)
    prof.dump_stats(tmp)
    stats = pstats.Stats(tmp,stream=out)
    stats.strip_dirs()          # Must happen prior to sort_stats
    stats.sort_stats('time', 'calls')
    stats.print_stats()
    stats_str = out.getvalue()
    #out.truncate()
    #stats.print_callers()
    #callers_str = out.getvalue()
    os.unlink(tmp)
    stats_str = stats_str.split('\n')
    headers = '\n'.join(make_header(stats_str[:4]))
    stats_str = stats_str[6:]
    data = data_stream(stats_str,100)
    ctx = make_stat_table(data)
    table = ctx['table']
    ctx['table'] = table.render()
    ctx.update({'headers':headers,
                'path':environ['PATH_INFO'],
                'stats':stats_str,
                'htmldoc':html.htmldoc(),
                'grid':html.grid960(),
                'css':sites.settings.HTML_CLASSES,
                'MEDIA_URL': sites.settings.MEDIA_URL,
                'media':table.maker.media()})
    content = loader.render('djpcms/profile.html', ctx)
    response.content = (content.encode(),)
    return response
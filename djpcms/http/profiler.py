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

from djpcms.utils import mark_safe

from .wrappers import Response

from py2py3 import StringIO


words_re = re.compile( r'\s+' )
line_func = re.compile(r'(?P<line>\d+)\((?P<func>\w+)\)')

group_prefix_re = None


class mod_helper(object):
    
    def __init__(self, app = None):
        self.app = app
        
    def __call__(self, res):
        app = self.app
        res = res.groups()
        if app: 
            bits = res[0]
        else:
            app,bits = res
        return app,bits
            


def group_prefix(settings):
    global group_prefix_re
    if group_prefix_re is None:
        group_prefix_re = []
        apps = set()
        for app in settings.INSTALLED_APPS:
            app = app.split('.')[0]
            if app not in apps:
                rex = "^.*/" + app + "/(.*)"
                group_prefix_re.append((mod_helper(app),re.compile(rex)))
                apps.add(app)
    
        # module in site_packages
        rex = "^.*/site-packages/(\w+)/(.*)"
        group_prefix_re.append((mod_helper(),re.compile(rex)))
    return group_prefix_re
    

def get_group(filename,settings):
    for func,rex in group_prefix(settings):
        filename = filename.replace('\\','/')
        x = rex.match(filename)
        if x:
            return func(x)
        

def summary_for_files(stats_str, mygroups, sum, sumc, settings):
    other = 'other'
    for fields in stats_str:
        ncalls = fields[1].split('/')
        tcalls,ncalls = int(ncalls[0]),int(ncalls[-1])
        time = float(fields[2])
        percall = float(fields[3])
        cumtime = float(fields[4])
        percall2 = float(fields[5])
        filename = fields[6]
        filenames = filename.split(':')
        linefunc = filenames.pop()
        match = line_func.match(linefunc)
        if match:
            lineno,func = match.groups()
            filename = ''.join(filenames)
            filename = filename.replace('\\','/')    
            mod,filename = get_group(filename,settings) or (other,filename)
        else:
            mod,lineno,func = other,'',''
        sum += time
        sumc += cumtime
        
        if not mod in mygroups:
            mygroups[mod] = {'time':0,
                             'cumtime':0,
                             'files':{}}
        g = mygroups[mod]
        g['time'] += time
        g['cumtime'] += cumtime
        files = g['files']
        if not filename in files:
            files[filename] = {'time':0,
                               'cumtime':0}
        files[filename]['time'] += time
        files[filename]['cumtime'] += cumtime
            
        yield ncalls,tcalls,time,percall,cumtime,percall2,mod,filename,\
                lineno,func


def make_stat_table(stats_str,settings):
    from djpcms import html
    groups = {}
    sum = 0
    sumc = 0
    header = ('calls','totcalls','tottime','percall','cumtime','percall',
              'module', 'filename','lineno','function')
    data = list(summary_for_files(stats_str,groups,sum,sumc,settings))
    table = html.Table(header,data)
    
    data2 = []
    data3 = []
    for mod,val in groups.items():
        data2.append((mod,val['time'],val['cumtime']))
        for filename,ft in val['files'].items():
            data3.append((mod,filename,ft['time'],ft['cumtime']))
    table2 = html.Table(('module','time','cumtime'),data2)        
    table3 = html.Table(('module','filename','time','cumtime'),
                        data3)
    return {'media':table.maker.media(),
            'table':table.render(),
            'modules':table2.render(),
            'files':table3.render()}
    

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


def profile_response(environ, start_response, PK, callback, settings):
    """Displays profiling for any view.
http://yoursite.com/yourview/?prof

Add the "prof" key to query string by appending ?prof (or &prof=)
and you'll see the profiling results in your browser."""
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
    #stats.strip_dirs()          # Must happen prior to sort_stats
    stats.sort_stats('time', 'calls')
    stats.print_stats()
    stats_str = out.getvalue()
    os.unlink(tmp)
    stats_str = stats_str.split('\n')
    headers = '\n'.join(make_header(stats_str[:4]))
    stats_str = stats_str[6:]
    data = data_stream(stats_str,100)
    ctx = make_stat_table(data,settings)
    ctx.update({'headers':headers,
                'path':environ['PATH_INFO'],
                'stats':stats_str,
                'htmldoc':html.htmldoc(),
                'grid':html.grid960(fixed=False),
                'css':sites.settings.HTML_CLASSES,
                'MEDIA_URL': sites.settings.MEDIA_URL})
    content = loader.render('djpcms/profile.html', ctx)
    return Response(content, content_type = 'text/html')


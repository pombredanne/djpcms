import sys
import os
import re
import tempfile
import cProfile as profiler
import pstats

from djpcms.utils.httpurl import StringIO
from djpcms.html import Pagination, Widget, tabs

words_re = re.compile( r'\s+' )
line_func = re.compile(r'(?P<line>\d+)\((?P<func>\w+)\)')

group_prefix_re = None


profile_table1 = Pagination(('calls','totcalls','tottime','percall','cumtime',
                             'percall','module', 'filename','lineno','function'),
                            footer = False,
                            sortable = True,
                            html_data = {'options':{'sDom':'t'}})
profile_table2 = Pagination(('module','time','cumtime'),
                            footer = False,
                            sortable = True,
                            html_data = {'options':{'sDom':'t'}})
profile_table3 = Pagination(('module','filename','time','cumtime'),
                            footer = False,
                            sortable = True,
                            html_data = {'options':{'sDom':'t'}})


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
            


def add_app_group(app,apps,groupre):
    app = app.split('.')[0]
    if app not in apps:
        rex = "^.*/" + app + "/(.*)"
        groupre.append((mod_helper(app),re.compile(rex)))
        apps.add(app)
    
    
def group_prefix(settings):
    '''Loop over applications so that we can group them during profiling'''
    global group_prefix_re
    if group_prefix_re is None:
        group_prefix_re = []
        apps = set()
        deferred = ['jinja2']
        for app in settings.INSTALLED_APPS:
            if app == 'djpcms':
                deferred.append(app)
                continue
            add_app_group(app,apps,group_prefix_re)
        for app in deferred:
            add_app_group(app,apps,group_prefix_re)
    
        # module in site_packages
        for rex in ("^.*/site-packages/(\w+)/(.*)",
                    "^.*/dist-packages/(\w+)/(.*)"):
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


def make_stat_table(request, stats_str):
    groups = {}
    sum = 0
    sumc = 0
    settings = request.settings
    data1 = list(summary_for_files(stats_str, groups, sum, sumc, settings))
    table1 = profile_table1.widget(data1)
    
    data2 = []
    data3 = []
    for mod,val in groups.items():
        data2.append((mod,val['time'],val['cumtime']))
        for filename,ft in val['files'].items():
            data3.append((mod,filename,ft['time'],ft['cumtime']))
    table2 = profile_table2.widget(data2)
    table3 = profile_table3.widget(data3)
    return (('global',table1.render(request)),
            ('modules',table2.render(request)),
            ('files',table3.render(request)))
    

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


def profile_response(environ, start_response, callback):
    """Displays profiling for any view.
http://yoursite.com/yourview/?prof

Add the "prof" key to query string by appending ?prof (or &prof=)
and you'll see the profiling results in your browser."""
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
    data = data_stream(stats_str[6:],100)
    request = environ['DJPCMS'].request
    tables = make_stat_table(request, data)
    w = Widget(cn = 'profiler')
    w.add(Widget('div', headers, cn = 'legend'))
    w.add(tabs(tables))
    context = {'inner': w.render(request),
               'title': 'Profile of {0}'.format(request.path)}    
    return request.view.response.render_to_response(request, context)

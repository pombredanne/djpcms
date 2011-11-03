from .models import PulsarServer, Task, Script, JobModel
from .applications import PulsarServerApplication, TasksAdmin, ScriptForm,\
                            JobApplication

NAME = 'pulsar'
ROUTE = 'pulsar'

admin_urls = (
  PulsarServerApplication('/pulsar/',
                          PulsarServer,
                          name = 'Pulsar servers'),
  JobApplication('/jobs/',JobModel,name = 'Jobs'),
  TasksAdmin('/tasks/',Task,name = 'Tasks'),
  #AdminApplication('/scripts/',Script,
  #                 form = ScriptForm,
  #                 list_display = ('name','language','parameters'),
  #                 name = 'Scripting')
)
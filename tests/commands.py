import os
import io
from djpcms.utils import test


class CommandTests(test.TestCase):
    installed_apps = ('djpcms.apps.color',
                      'djpcms.apps.contentedit',
                      'djpcms.apps.fileupload',
                      'djpcms.apps.fontawesome',
                      'djpcms.apps.nav',
                      'djpcms.apps.page',
                      'djpcms.apps.ui')
    
    def testServe(self):
        command = self.fetch_command('serve')
        self.assertEqual(command.help,\
"Serve the application using WSGIserver from the standard library.")
        self.assertEqual(len(command.option_list), 2)

    def testServeDry(self):
        command = self.fetch_command('serve', ['9000','--dryrun'])
        command()

    def testStyle(self):
        command = self.fetch_command('style', ['-t','teststyle'])
        command()
        self.assertEqual(command.theme, 'teststyle')
        os.remove(command.target)
        
    def test_nginx(self):
        command = self.fetch_command('nginx')
        stream = io.StringIO()
        command(target=stream)

    def test_create_superuser(self):
        command = self.fetch_command('create_superuser')
        self.assertEqual(command(interactive=False), None)
        
    def testShell(self):
        command = self.fetch_command('shell')

    def test_run_pulsar(self):
        command = self.fetch_command('run_pulsar')
        self.assertEqual(len(command.option_list), 0)
        app = command(start=False)
        self.assertTrue(app)
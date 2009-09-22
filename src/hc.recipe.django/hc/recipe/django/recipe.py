# -*- coding: utf-8 -*-
"""Recipe for Django"""

import os
import shutil
import re

import zc.buildout
import zc.recipe.egg

import logging

TRUE_VALUES = ('yes', 'true', '1', 'on')

class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.logger = logging.getLogger(self.name)
        
        self.egg = zc.recipe.egg.Egg(buildout, options['recipe'], options)
        self.django_re = re.compile(r'\bDjango\b')
        
        python = buildout['buildout']['python']
        options['executable'] = buildout[python]['executable']
        options['bin-directory'] = buildout['buildout']['bin-directory']
        
        options.setdefault('extract-media', 'false')
        options.setdefault('wsgi', 'false')
        options.setdefault('wsgi-file-name', name)
        options.setdefault('wsgilog', '')
        options.setdefault('settings', 'settings')
        options.setdefault('test-script', 'runtests')
        
        if not options['wsgi-file-name'].endswith('.wsgi'):
            options['wsgi-file-name'] = '%s.wsgi' % options['wsgi-file-name']
        
        options['wsgi-script'] = os.path.join(options['bin-directory'], options['wsgi-file-name'])

    def install(self):
        """Installer"""
        # XXX Implement recipe functionality here
        # Return files that were created by the recipe. The buildout
        # will remove all returned files upon reinstall.
        self.ensure_django_egg_included()
        
        options                     = self.options
        project                     = options['project']
        recipe                      = options['recipe']
        settings                    = options['settings']
        manage_script               = options.get('manage-script')
        test_script                 = options['test-script']
        test_settings               = options.get('test-settings', settings)
        apps_to_test                = options.get('test', '').split()
        
        requirements, working_set   = self.egg.working_set([ recipe ])
        
        if not manage_script and not apps_to_test:
            error = "You must provide either 'manage-script' or 'test'."
            self.logger.error(error)
            raise zc.buildout.UserError(error)
        
        installed_scripts = []
        
        # Install eggs
        installed_eggs = self.egg.install()
        
        # Only create the management script if the user requests it
        if manage_script:
            
            script_command = [( manage_script, '%s.commands.manage' % recipe, 'main' )]
            arguments = "'%s.%s'" % (project, settings)
            
            installed = zc.buildout.easy_install.scripts(
                script_command,
                working_set, 
                options['executable'], 
                options['bin-directory'],
                arguments=arguments
            )
            
            for i in installed:
                installed_scripts.append(i)
        
        # Only create the testrunner if the user requests it
        if apps_to_test:
            
            apps_to_test = ', '.join([ "'%s'" % app for app in apps_to_test ])
            arguments = "'%s.%s', varg, vlevel, %s" % ( project, test_settings, apps_to_test )
            
            _script_template = zc.buildout.easy_install.script_template
            test_script_template = zc.buildout.easy_install.script_header + test_template
            zc.buildout.easy_install.script_template = test_script_template
            
            installed = zc.buildout.easy_install.scripts(
                [( test_script, '%s.commands.test' % recipe, 'main' )],
                working_set, 
                self.options['executable'],
                self.options['bin-directory'],
                arguments=arguments
            )
            
            zc.buildout.easy_install.script_template = _script_template
            
            for i in installed:
                installed_scripts.append(i)
        
        # Create the wsgi script if enabled
        for i in self.create_wsgi_script(working_set):
            installed_scripts.append(i)
        
        # Copy the admin media to parts if Django egg is unzipped
        installed_media = self.extract_admin_media(working_set)
        
        return installed_eggs + installed_scripts + installed_media
        
    
    def update(self):
        """Updater"""
        pass
    
    
    def ensure_django_egg_included(self):
        eggs = self.options.get('eggs', '').split()
        found = False
        
        for egg in eggs:
            if self.django_re.match(egg):
                found = True
        
        if not found:
            eggs.append('Django')
        
        self.options['eggs'] = '\n'.join(eggs)
    
    def extract_admin_media(self, working_set):
        installed   = []
        target_dir = os.path.join( self.buildout['buildout']['parts-directory'], 'django_admin_media' )
        
        if self.options['extract-media'] in TRUE_VALUES:
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir)
            
            for dist in working_set.by_key.values():
                if self.django_re.match(dist.project_name):
                    media_dir = os.path.join(dist.location, 'django/contrib/admin/media')
                    if os.path.exists(media_dir):
                        shutil.copytree(media_dir, target_dir)
                        installed.append(target_dir)
                        break
        
        return installed
    
    def create_wsgi_script(self, working_set):
        installed   = []
        
        if self.options['wsgi'] in TRUE_VALUES:
            _script_template = zc.buildout.easy_install.script_template
            wsgi_script_template = zc.buildout.easy_install.script_header + wsgi_template
            zc.buildout.easy_install.script_template = wsgi_script_template
            
            project         = self.options['project']
            recipe          = self.options['recipe']
            settings        = self.options['settings']
            wsgi_file_name  = self.options['wsgi-file-name']
            logfile         = self.options['wsgilog']
            args            = (project, settings, logfile)
            arguments       = "'%s.%s', logfile='%s'" % args
            
            installed = zc.buildout.easy_install.scripts(
                [( wsgi_file_name, '%s.commands.wsgi' % recipe, 'main' )],
                working_set,
                self.options['executable'], 
                self.options['bin-directory'],
                arguments=arguments
            )
            
            zc.buildout.easy_install.script_template = _script_template
        
        return installed
    

test_template = '''
%(relative_paths_setup)s
import sys
sys.path[0:0] = [
  %(path)s,
]
%(initialization)s
import %(module_name)s

if __name__ == '__main__':
    varg = '-v'
    vlevel = '1'
    if len(sys.argv) > 1 and sys.argv[1] == '-v':
        vlevel = '2'
    %(module_name)s.%(attrs)s(%(arguments)s)
'''


wsgi_template = '''
%(relative_paths_setup)s
import sys
sys.path[0:0] = [
  %(path)s,
]
%(initialization)s
import %(module_name)s

application = %(module_name)s.%(attrs)s(%(arguments)s)

'''


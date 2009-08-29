# -*- coding: utf-8 -*-
"""Recipe for Django"""

import os
import re

import zc.buildout
import zc.recipe.egg

import logging


class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.logger = logging.getLogger(self.name)
        
        self.egg = zc.recipe.egg.Egg(buildout, options['recipe'], options)
        
        python = buildout['buildout']['python']
        options['executable'] = buildout[python]['executable']
        options['bin-directory'] = buildout['buildout']['bin-directory']
        
        options.setdefault('wsgi', 'false')
        options.setdefault('wsgilog', '')
        options.setdefault('settings', 'settings')
        options.setdefault('test-script', 'runtests')

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
            arguments = "'%s.%s', %s" % ( project, test_settings, apps_to_test )
            
            installed = zc.buildout.easy_install.scripts(
                [( test_script, '%s.commands.test' % recipe, 'main' )],
                working_set, 
                self.options['executable'],
                self.options['bin-directory'],
                arguments=arguments
            )
            
            for i in installed:
                installed_scripts.append(i)
        
        # Create the wsgi script if enabled
        for i in self.create_wsgi_script(working_set):
            installed_scripts.append(i)
        
        return installed_eggs + installed_scripts
        
    
    def update(self):
        """Updater"""
        pass
    
    
    def ensure_django_egg_included(self):
        eggs = self.options.get('eggs', '').split()
        found = False
        pattern = re.compile(r'\bDjango\b')
        
        for egg in eggs:
            if pattern.match(egg):
                found = True
        
        if not found:
            eggs.append('Django')
        
        self.options['eggs'] = '\n'.join(eggs)
    
    
    def create_wsgi_script(self, working_set):
        installed   = []
        protocol    = 'wsgi'
        
        if self.options.get(protocol, '').lower() == 'true':
            _script_template = zc.buildout.easy_install.script_template
            wsgi_script_template = zc.buildout.easy_install.script_header + wsgi_template
            zc.buildout.easy_install.script_template = wsgi_script_template
            
            project         = self.options['project']
            manage_script   = self.options.get('manage-script')
            recipe          = self.options['recipe']
            settings        = self.options['settings']
            logfile         = self.options.get('wsgilog')
            args            = (project, settings, logfile)
            arguments       = "'%s.%s', logfile='%s'" % args
            
            if manage_script:
                installed = zc.buildout.easy_install.scripts(
                    [( '%s.%s' % (manage_script, protocol), '%s.commands.%s' % (recipe, protocol), 'main' )],
                    working_set,
                    self.options['executable'], 
                    self.options['bin-directory'],
                    arguments=arguments
                )
            else:
                warning = "You must provide 'manage-script' to build the wsgi option (skipping)."
                self.logger.warning(warning)
            
            zc.buildout.easy_install.script_template = _script_template
        
        return installed
    

#
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


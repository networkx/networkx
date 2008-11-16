# plugin for nose tests 
#
# provides the option --with-networkx-doctest
# which sets up the environment with
# import networkx as nx
# for all docstring tests in modules 

from nose.plugins.doctests import Doctest, DocTestCase
import os
from nose.util import src
import networkx
import logging
log = logging.getLogger(__name__)
from nose.plugins import Plugin

class NetworkXDoctest10(Doctest):
     name = 'networkx-doctest'

     def options(self, parser, env=os.environ):
         Plugin.options(self, parser, env)
         parser.add_option('--networkx-doctest-tests', action='store_true',
                           dest='doctest_tests',
                           default=env.get('NOSE_DOCTEST_TESTS'),
                           help="Also look for doctests in test modules. "
                           "Note that classes, methods and functions should "
                           "have either doctests or non-doctest tests, "
                           "not both. [NOSE_DOCTEST_TESTS]")
         parser.add_option('--networkx-doctest-extension', action="append",
                           dest="doctestExtension",
                           help="Also look for doctests in files with "
                           "this extension [NOSE_DOCTEST_EXTENSION]")
         # Set the default as a list, if given in env; otherwise
         # an additional value set on the command line will cause
         # an error.
         env_setting = env.get('NOSE_DOCTEST_EXTENSION')
         if env_setting is not None:
             parser.set_defaults(doctestExtension=tolist(env_setting))

     def loadTestsFromModule(self, module):
         if not self.matches(module.__name__):
             log.debug("Doctest doesn't want module %s", module)
             return
         try:
             tests = self.finder.find(module)
         except AttributeError:
             # nose allows module.__test__ = False; doctest does not and throws
             # AttributeError
             return
         if not tests:
             return
         tests.sort()
         module_file = src(module.__file__)
         for test in tests:
             if not test.examples:
                 continue
             if not test.filename:
                 test.filename = module_file
             test.globs = {'__builtins__':__builtins__,
                           '__file__':'__main__',
                           '__name__':'__main__',
                           'nx':networkx,
                           'networkx':networkx}
             yield DocTestCase(test)
            
 


class NetworkXDoctest11(Doctest):
     name = 'networkx-doctest'

     def options(self, parser, env=os.environ):
         """New plugin API: override to just set options. Implement
         this method instead of addOptions or add_options for normal
         options behavior with protection from OptionConflictErrors.
         """
         env_opt = 'NOSE_WITH_%s' % self.name.upper()
         env_opt = env_opt.replace('-', '_')
         parser.add_option("--with-%s" % self.name,
                           action="store_true",
                           dest=self.enableOpt,
                           default=env.get(env_opt),
                           help="Enable plugin %s: %s [%s]" %
                           (self.__class__.__name__, self.help(), env_opt))


     def loadTestsFromModule(self, module):
         log.debug("loading from %s", module)
         if not self.matches(module.__name__):
             log.debug("Doctest doesn't want module %s", module)
             return
         try:
             tests = self.finder.find(module)
         except AttributeError:
             log.exception("Attribute error loading from %s", module)
             # nose allows module.__test__ = False; doctest does not and throws
             # AttributeError
             return
         if not tests:
             log.debug("No tests found in %s", module)
             return
         tests.sort()
         module_file = src(module.__file__)
         # FIXME this breaks the id plugin somehow (tests probably don't
         # get wrapped in result proxy or something)
         cases = []
         for test in tests:
             if not test.examples:
                 continue
             if not test.filename:
                 test.filename = module_file    
             test.globs = {'__builtins__':__builtins__,
                           '__file__':'__main__',
                           '__name__':'__main__',
                           'nx':networkx,
                           'networkx':networkx}
             cases.append(DocTestCase(test, result_var=self.doctest_result_var))
         if cases:
             yield self.suiteClass(cases, context=module, can_split=False)
            
class NetworkXDoctest(object):
    def __new__(cls, *args, **kwds):
        """
        Return class based on version of nose installed.
        """
        from nose import __version__
        #print __version__
        #print '__new__',args,kwds
        if __version__ >= '0.11':
            return NetworkXDoctest11(*args, **kwds)
        else:
            return NetworkXDoctest10(*args, **kwds)




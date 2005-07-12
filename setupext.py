# install_data_ext.py
#
# Subclass of normal distutils install_data command to allow more
# configurable installation of data files.

import os
from distutils.command.install_data import install_data
from distutils.util import change_root, convert_path

class install_data_ext(install_data):

    def initialize_options(self):
        self.install_base = None
        self.install_platbase = None
        self.install_purelib = None
        self.install_headers = None
        self.install_lib = None
        self.install_scripts = None
        self.install_data = None

        self.outfiles = []
        self.root = None
        self.force = 0
        self.data_files = self.distribution.data_files
        self.warn_dir = 1
        

    def finalize_options(self):
        self.set_undefined_options('install',
                                   ('root', 'root'),
                                   ('force', 'force'),
                                   ('install_base', 'install_base'),
                                   ('install_platbase',
                                    'install_platbase'),
                                   ('install_purelib',
                                    'install_purelib'),
                                   ('install_headers',
                                    'install_headers'),
                                   ('install_lib', 'install_lib'),
                                   ('install_scripts',
                                    'install_scripts'),
                                   ('install_data', 'install_data'))
                                   

    def run(self):
        """
        This is where the meat is.  Basically the data_files list must
        now be a list of tuples of 3 entries.  The first
        entry is one of 'base', 'platbase', etc, which indicates which
        base to install from.  The second entry is the path to install
        too.  The third entry is a list of files to install.
        """
        for lof in self.data_files:
            if lof[0]:
                base = getattr(self, 'install_' + lof[0])
            else:
                base = getattr(self, 'install_base')
            dir = convert_path(lof[1])
            if not os.path.isabs(dir):
                dir = os.path.join(base, dir)
            elif self.root:
                dir = change_root(self.root, dir)
            self.mkpath(dir)

            files = lof[2]
            if len(files) == 0:
                # If there are no files listed, the user must be
                # trying to create an empty directory, so add the the
                # directory to the list of output files.
                self.outfiles.append(dir)
            else:
                # Copy files, adding them to the list of output files.
                for f in files:
                    f = convert_path(f)
                    (out, _) = self.copy_file(f, dir)
                    #print "DEBUG: ", out  # dbg
                    self.outfiles.append(out)
                    

        return self.outfiles

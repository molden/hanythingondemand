# #
# Copyright 2009-2013 Ghent University
#
# This file is part of hanythingondemand
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://vscentrum.be/nl/en),
# the Hercules foundation (http://www.herculesstichting.be/in_English)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# http://github.com/hpcugent/hanythingondemand
#
# hanythingondemand is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v2.
#
# hanythingondemand is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with hanythingondemand. If not, see <http://www.gnu.org/licenses/>.
# #
"""

@author: Stijn De Weirdt (University of Ghent)
"""
from vsc.utils.fancylogger import getLogger
from vsc.utils.missing import get_subclasses

class Job(object):
    """
    Base class for Hanythingondemand jobs.
    """
    def __init__(self, options):
        self.log = getLogger(self.__class__.__name__, fname=False)

        self.options = options

        self.nrnodes = None
        self.corespernode = None

        self.script = None

        self.type = None

        self.modules = []

        self.run_in_cwd = True

    def submit(self):
        """Submit this job"""
        if self.script is None:
            self.generate_script()

        self.log.debug("Going to submit jobscript %s", self.script)
        self.type.submit(self.script)
        self.log.debug("Submission returned jobid %s", self.type.jobid)

    def generate_script(self):
        """Build the submit script"""
        script = ["#!/bin/bash", "## Generated by HOD"]
        script += self.generate_script_header()

        script += self.generate_environment()

        if self.run_in_cwd:
            script.append("cd $%s" % self.type.vars['cwd'])

        script += self.generate_exe()

        self.log.debug("Generated script %s", script)
        self.script = "\n".join(script + [''])

    def generate_environment(self):
        """Generate the environment to start the job"""
        script_env = self.generate_modules()
        script_env += self.generate_extra_environment()

        return script_env

    def generate_extra_environment(self):
        """Generate other environment parameters to start the job"""
        extra_env = []
        self.log.debug("Nothing to add.")
        return extra_env

    def generate_exe(self):
        """The actual executable"""
        self.log.debug("generate_exe not implemented")

        return ['## Not implemented']

    def generate_script_header(self):
        """Create the job arguments. Retrun as header (if used)"""
        hdr = self.type.header()
        self.log.debug("Generated header %s", hdr)
        print 'self.type.header()', hdr

        return hdr

    def generate_modules(self):
        """
        Generate the module statements. Returns a list.
        Elements that are string or 1 long are assumed to be load requests
        """
        allmods = []
        for md in self.modules:
            if type(md) in (str,):
                allmods.append(['load', md])
            elif type(md) in (list, tuple):
                if len(md) == 1:
                    allmods.append(['load', md[0]])
                else:
                    allmods.append(md)
            else:
                self.log.error("Unknown module type %s (%s)", type(md), md)

        self.log.debug("Going to generate string for modules %s", allmods)
        return ['module %s' % (" ".join(md)) for md in allmods]

    @classmethod
    def _is_job_for(cls, name):
        """Returns True if this class implements something that can handle 'name'"""
        return cls.__name__ == name

    @staticmethod
    def get_job(classname, options):
        """
        This is a job factory.

        Returns an instance of classname initialized with options
        """
        for cls in get_subclasses(Job):
            if cls._is_job_for(classname):
                return cls(options)
        getLogger().error("No job class found for %s", classname)

#!/usr/bin/env python
# #
# Copyright 2009-2015 Ghent University
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
Remove stale .hod.d/* files.

@author: Ewan Higgs (Universiteit Gent)
"""

import os
from itertools import chain

from vsc.utils import fancylogger
from vsc.utils.generaloption import GeneralOption

from hod import VERSION as HOD_VERSION
from hod.subcommands.subcommand import SubCommand
from hod.cluster import clean_cluster_info, known_cluster_labels, mk_cluster_info
import hod.rmscheduler.rm_pbs as rm_pbs


_log = fancylogger.getLogger(fname=False)


class CleanOptions(GeneralOption):
    """Option parser for 'clean' subcommand."""
    VERSION = HOD_VERSION


class CleanSubCommand(SubCommand):
    """Implementation of HOD 'clean' subcommand."""
    CMD = 'clean'
    HELP = "Remove stale cluster info."

    def run(self, args):
        """Run 'clean' subcommand."""
        optparser = CleanOptions(go_args=args, envvar_prefix=self.envvar_prefix, usage=self.usage_txt)
        try:
            pbs = rm_pbs.Pbs(optparser)
            state = pbs.state()
            labels = known_cluster_labels()
            pbs_master = os.getenv('PBS_DEFAULT')
            info = mk_cluster_info(labels, state, master=pbs_master)
            clean_cluster_info(pbs_master, info)
        except StandardError as err:
            fancylogger.setLogFormat(fancylogger.TEST_LOGGING_FORMAT)
            fancylogger.logToScreen(enable=True)
            _log.raiseException(err.message)

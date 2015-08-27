#!/usr/bin/env python
# ##
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
"""
Main hanythingondemand script, should be invoked in a job

@author: Ewan Higgs (Universiteit Gent)
@author: Kenneth Hoste (Universiteit Gent)
"""
import copy
import os
import random
import string
import sys
from mpi4py import MPI

from hod import VERSION as HOD_VERSION

from vsc.utils import fancylogger
from vsc.utils.generaloption import GeneralOption

from hod.hodproc import ConfiguredSlave, ConfiguredMaster
from hod.mpiservice import MASTERRANK, run_tasks, setup_tasks
from hod.options import GENERAL_HOD_OPTIONS


_log = fancylogger.getLogger(fname=False)


class LocalOptions(GeneralOption):
    """Option parser for 'genconfig' subcommand."""
    VERSION = HOD_VERSION

    def config_options(self):
        """Add general configuration options."""
        opts = copy.deepcopy(GENERAL_HOD_OPTIONS)
        opts.update({
            'label': ("Cluster label", 'string', 'store', None),
            'modules': ("Extra modules to load in each service environment", 'string', 'store', None),
        })
        descr = ["Local configuration", "Configuration options for the 'genconfig' subcommand"]

        self.log.debug("Add config option parser descr %s opts %s", descr, opts)
        self.add_group_parser(opts, descr)


def cluster_info_dir():
    """
    Determine cluster info directory.
    Returns $XDG_CONFIG_HOME/hod.d or $HOME/.config/hod.d
    http://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html
    """
    dflt = os.path.join(os.getenv('HOME'), '.config')
    return os.path.join(os.getenv('XDG_CONFIG_HOME', dflt), 'hod.d')


def known_cluster_labels():
    """
    Return list of known cluster labels.
    """
    path = cluster_info_dir()
    if os.path.exists(path):
        os.listdir(path)
    else:
        _log.warning("No cluster config directory '%s' (yet)", path)
        return []


def _cluster_info(label, info_file, contents=False):
    """
    Return specified cluster info for cluster with specified label.
    @param label: cluster label
    @param info_file: type of info to return (env, jobid, ...)
    @param contents: returns contents of info file rather than path to info file
    """
    res = None
    if label in known_cluster_labels():
        info_file = os.path.join(cluster_info_dir, label, info_file)
        if os.path.exists(info_file):
            if contents:
                res = open(info_file).read()
            else:
                res = info_file
        else:
            _log.error("No 'env' file found for cluster with label '%s'", label)
            sys.exit(1)
    else:
        _log.error("Unknown cluster label '%s': %s", label, known_cluster_labels())
        sys.exit(1)

    return res


def cluster_jobid(label):
    """Return job ID for cluster with specified label."""
    return _cluster_info(label, 'jobid', contents=True)


def cluster_env_file(label):
    """
    Return path to env file for cluster with specified label.
    """
    return _cluster_info(label, 'env')


def generate_cluster_env_script():
    """
    Generate the env script for this cluster.
    """
    #FIXME
    return """
#[ -f $HOME/.profile ] && source $HOME/.profile
#[ -f $HOME/.bashrc  ] && source $HOME/.bashrc
export masterhostname=
export masterdatatname=
export workdir=~/data
export localworkdir=~/data/localhost

echo "Welcome to hod"
echo "Your environment:"
echo masterhostname=${masterhostname}
echo masterdataname=${masterdataname}
echo masterhostaddress=${masterhostaddress}
echo masterdataaddress=${masterdataaddress}
echo hostaddress=${hostaddress}
echo dataaddress=${dataaddress}
echo user=${user}
echo workdir=${workdir}
echo localworkdir=${localworkdir}
echo modules=${modules}

module load ${modules}
"""

def create_cluster_info(label):
    """Create env file that can be source when connecting to the current hanythingondemand cluster."""
    info_dir = os.path.join(cluster_info_dir(), label)
    try:
        os.makedirs(info_dir)
    except OSError as err:
        _log.error("Failed to create cluster info dir '%s': %s", info_dir, err)

    try:
        with open(os.path.join(info_dir, 'jobid'), 'w') as jobid:
            jobid.write(os.getenv('PBS_JOBID', 'PBS_JOBID_NOT_DEFINED'))

        env_script_txt = generate_cluster_env_script()

        with open(os.path.join(info_dir, 'env'), 'w') as env_script:
            env_script.write(env_script_txt)
    except IOError as err:
        _log.error("Failedto write cluster info files: %s", err)


def main(args):
    """Run HOD cluster."""
    optparser = LocalOptions(go_args=args)

    if MPI.COMM_WORLD.rank == MASTERRANK:
        label = optparser.options.label
        if label is None:
            # if no label is specified, use job ID;
            # if $PBS_JOBID is not set, generate a random string (10 chars)
            label = os.getenv('PBS_JOBID', ''.join(random.choice(string.letters + string.digits) for _ in range(10)))
        _log.debug("Creating cluster info using label '%s'", label)
        create_cluster_info(label)

        _log.debug("Starting master process")
        svc = ConfiguredMaster(optparser)
    else:
        _log.debug("Starting slave process")
        svc = ConfiguredSlave(optparser)
    try:
        setup_tasks(svc)
        run_tasks(svc)
        svc.stop_service()
    except Exception as err:
        _log.error(str(err))
        _log.exception("HanythingOnDemand failed")
        sys.exit(1)


if __name__ == '__main__':
    main(sys.argv[1:])

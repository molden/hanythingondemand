###
# Copyright 2009-2014 Ghent University
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
'''
@author Ewan Higgs (Universiteit Gent)
'''

import unittest
import hod.mpiservice as hm

class MPIServiceTestCase(unittest.TestCase):
    '''Test MpiService functions'''

    def test_mpiservice_init(self):
        '''test mpiservice init'''
        ms = hm.MpiService(False)
        self.assertEqual(ms.size, -1)
        self.assertEqual(ms.rank, -1)

    def test_mpiservice_init_init_com(self):
        '''test mpiservice init init com'''
        ms = hm.MpiService()
        self.assertTrue(ms.comm is not None)
        self.assertTrue(ms.size is not None)
        self.assertTrue(ms.rank is not None)

    def test_mpiservice_barrier(self):
        '''test mpiservice barrier'''
        ms = hm.MpiService()
        hm.barrier(ms.comm, 'Wibble')

    def test_mpiservice_collectnodes(self):
        '''test mpiservice collectnodes'''
        ms = hm.MpiService()
        ms.init_comm()
        allnodes = hm._collect_nodes(ms.comm, ms.thisnode, ms.size)

    def test_mpiservice_make_topoplogy_comm(self):
        '''test mpiservice make topology comm'''
        ms = hm.MpiService()
        ms.init_comm()
        topocom =  hm._make_topology_comm(ms.comm, ms.allnodes, ms.size, ms.rank)
        print topocom

    def test_mpiservice_who_is_out_there(self):
        '''test mpiservice who is out there'''
        ms = hm.MpiService()
        ms.init_comm()
        others = hm._who_is_out_there(ms.comm, ms.rank)

    def test_mpiservice_stop_comm(self):
        '''test mpiservice stop comm'''
        ms = hm.MpiService()
        ms.init_comm()
        hm._stop_comm(ms.comm)

    def test_mpiservice_stop_service(self):
        '''test mpiservice stop service'''
        ms = hm.MpiService()
        ms.stop_service()

    def test_mpiservice_check_group(self):
        '''test mpiservice check group'''
        ms = hm.MpiService()
        ms.init_comm()
        hm._check_group(ms.comm.Get_group(), 'some text')

    def test_mpiservice_check_comm(self):
        '''test mpiservice check comm'''
        ms = hm.MpiService()
        ms.init_comm()
        hm._check_comm(ms.comm, 'blah')

    def test_make_comm_group(self):
        '''test mpiservice make check group'''
        ms = hm.MpiService()
        ms.init_comm()
        hm._make_comm_group(ms.comm, range(1))

    def test_mpiservice_distribution(self):
        '''test mpiservice distribution'''
        ms = hm.MpiService()
        ms.distribution() # TODO:  Does nothing. If it's an interface, make abstract.

    def test_master_spread(self):
        '''test master spread'''
        ms = hm.MpiService()
        ms.init_comm()
        hm._master_spread(ms.comm, None, 0)

    def test_slave_spread(self):
        '''test master spread'''
        ms = hm.MpiService()
        ms.init_comm()
        hm._slave_spread(ms.comm, None, 0)

    @unittest.expectedFailure
    def test_mpiservice_run_dist(self):
        '''test mpiservice run dist'''
        ms = hm.MpiService()
        ms.distribution()
        ms. run_dist()

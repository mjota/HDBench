#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# HDBench - Benchmarking for hard disks
# Copyright (c) 2012 - Manuel Joaquin Díaz Pol
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
#
#==============================================================================
#
import matplotlib.pyplot as plt

class plot:
    def __init__(self,resultList):
        self.writeList = list()
        self.readList = list()
        self.xList = list()
        for row in resultList:
            self.xList.append(row[0])
            self.writeList.append(row[1])
            self.readList.append(row[2])
        
    def printPlot(self,nameHD):
        plt.title(nameHD)
        plt.xticks(range(len(self.xList)), self.xList)
        plt.plot(self.writeList,label="Write")
        plt.plot(self.readList,label="Read")
        plt.legend(loc="upper left")
        plt.xlabel('Size (kb)')
        plt.ylabel('Time (s)')
        fname= nameHD + '.png'
        plt.savefig(fname,dpi=60)
                  
        
        

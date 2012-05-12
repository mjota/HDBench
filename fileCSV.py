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

import csv
from gi.repository import Gtk

class fileCSV:
    def __init__(self,nameHD):
        #Crea la ventana de trabajo principal y obtiene los objetos en Glade
        builder = Gtk.Builder();
        builder.add_from_file("fileCSVWindow.glade")
        
        self.Window = builder.get_object("fileCSVWindow")
        self.Window.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,Gtk.STOCK_SAVE, Gtk.ResponseType.OK)
        self.Window.set_current_name(nameHD + ".csv")
        
    def writeCSV(self,lResult,nameHD):
        fileW = open(self.Window.get_filename(),"w")
        fileC = csv.writer(fileW)
        fileC.writerow([nameHD,"Write Time (s)","Read Time (s)"])
        for row in lResult:
            fileC.writerow(row[:])
        fileW.close()
        
        
        
        
        
        
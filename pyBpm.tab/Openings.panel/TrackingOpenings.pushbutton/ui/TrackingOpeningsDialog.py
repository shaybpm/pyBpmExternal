# -*- coding: utf-8 -*-

import clr

clr.AddReference("System.Windows.Forms")
clr.AddReference("IronPython.Wpf")

import wpf
from System import Windows
import os


xaml_file = os.path.join(os.path.dirname(__file__), "TrackingOpeningsDialogUi.xaml")


class TrackingOpeningsDialog(Windows.Window):
    def __init__(self, doc):
        wpf.LoadComponent(self, xaml_file)
        self.doc = doc

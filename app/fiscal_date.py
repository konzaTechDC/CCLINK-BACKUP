"""
Definition of views.
"""
from __future__ import unicode_literals
import os
from os import path
from fiscalyear import *

#fiscalyear.START_MONTH = 7

def GetFiscalYear():
    return FiscalYear.current()
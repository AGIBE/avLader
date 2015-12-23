# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import arcpy

def calculate_grid_size(fc):
    '''
    Berechnet die Grid Size einer Feature Class.
    Der von arcpy berechnete Wert wird dabei auf
    eine ganze Zahl gerundet.
    :param fc: Feature Class, für die die Grid Size gerechnet wird.
    '''
    fc_count = int(arcpy.GetCount_management(fc)[0])
    grid_size = 0
    if fc_count > 0:
        # CalculateDefaultGridIndex_management bricht mit Fehler ab,
        # wenn die Featureclass nur aus Features mit leerer Geometrie
        # besteht. Kann bei den Nachführungstabellen vorkommen.
        try:
            result = arcpy.CalculateDefaultGridIndex_management(fc)
            grid_size = float(result.getOutput(0))
            grid_size = int(round(grid_size))
        except:
            grid_size = 0
    return grid_size

# -*- coding: utf-8 -*-
""" This script iterates over all the openings (Generic Model from the BPM library) and dose the following:
- Copies the Elevation to a taggable parameter (useful in versions 20+21).
- Copies the Reference Level to a taggable parameter.
- Sets Mark to opening it is missing.
- Defines whether the opening is located in the floor or not.
- Calculates the projected height of the opening.
- Calculates the absolute height of the opening. """
__title__ = 'Opening\nSetter'
__author__ = 'Eyal Sinay'

# ------------------------------

import clr
clr.AddReference('RevitAPI')
clr.AddReferenceByPartialName('PresentationCore')
clr.AddReferenceByPartialName('AdWindows')
clr.AddReferenceByPartialName("PresentationFramework")
clr.AddReferenceByPartialName('System')
clr.AddReferenceByPartialName('System.Windows.Forms')

from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Transaction, BuiltInParameter
from Autodesk.Revit.UI import TaskDialog

# from System.Collections.Generic import List

# import Autodesk.Windows as aw

max_elements = 5
gdict = globals()
uiapp = __revit__
uidoc = uiapp.ActiveUIDocument
if uidoc:
    doc = uiapp.ActiveUIDocument.Document
    # selection = [doc.GetElement(x) for x in uidoc.Selection.GetElementIds()]
    # for idx, el in enumerate(selection):
    #     if idx < max_elements:
    #         gdict['e{}'.format(idx+1)] = el
    #     else:
    #         break

# alert function
def alert(msg):
    TaskDialog.Show('BPM - Opening Update', msg)

# ------------------------------------------------------------

def get_all_openings():
    """ Returns a list of all the openings in the model. """
    opening_names = [
        'Round Face Opening',
        'Rectangular Face Opening',
        'CIRC_FLOOR OPENING',
        'CIRC_WALL OPENING',
        'REC_FLOOR OPENING',
        'REC_WALL OPENING'
    ]
    openings = []
    generic_models = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()
    for gm in generic_models:
        if gm.Name in opening_names:
            openings.append(gm)
    return openings

# def set_schedule_level(opening):
#     """ Sets the Schedule Level parameter to the correct level. """
#     # TODO: Check if is floor, if is floor, get the level of the floor. if it is not floor, get the floor below and set the level to it. if there is no floor below, set the level by the code below.
#     # ! For now, we decided to not use this function. The user will have to set the level manually. The script will only set the "MEP - Not Required" parameter to true or false by this calculation.
#     all_levels = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()
#     all_levels_sorted = sorted(all_levels, key = lambda x: x.Elevation)
#     all_levels_sorted_length = len(all_levels_sorted)
#     opening_location_point_z = opening.Location.Point.Z
#     param__schedule_level = opening.get_Parameter(BuiltInParameter.INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM)
#     if not param__schedule_level:
#         return
#     if all_levels_sorted[0].Elevation >= opening_location_point_z:
#         param__schedule_level.Set(all_levels_sorted[0].Id)
#         return
#     if all_levels_sorted[all_levels_sorted_length - 1].Elevation <= opening_location_point_z:
#         param__schedule_level.Set(all_levels_sorted[all_levels_sorted_length - 1].Id)
#         return
#     for i in range(all_levels_sorted_length - 1):
#         if all_levels_sorted[i].Elevation <= opening_location_point_z and all_levels_sorted[i + 1].Elevation > opening_location_point_z:
#             param__schedule_level.Set(all_levels_sorted[i].Id)
#             return
#     print('No level found for opening: {}'.format(opening.Id))

def is_floor(opening):
    """ Returns True if the host of the opening is a floor, else returns False.
     We don't use the host property because sometimes the connection between the opening and the host is broken. """
    param__Elevation_from_Level = opening.LookupParameter('Elevation from Level')
    if not param__Elevation_from_Level:
        # print('WARNING: No Elevation from Level parameter found. Opening ID: {}'.format(opening.Id))
        return False
    if param__Elevation_from_Level.IsReadOnly:
        return True
    else:
        return False
    
def set_mep_not_required_param(opening):
    """ Get the schedule level parameter and check if it is match to the opening instance in the model. If it is, set the MEP - Not Required parameter to true, else set it to false. """
    param__mep_not_required = opening.LookupParameter('MEP - Not Required')
    if not param__mep_not_required:
        # print('WARNING: No MEP - Not Required parameter found. Opening ID: {}'.format(opening.Id))
        return
    param__schedule_level = opening.get_Parameter(BuiltInParameter.INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM)
    id__schedule_level = param__schedule_level.AsElementId()
    if id__schedule_level.IntegerValue == -1:
        param__mep_not_required.Set(0)
        return

    all_floors = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Floors).WhereElementIsNotElementType().ToElements()
     
    if not is_floor(opening):
        all_floors = [floor for floor in all_floors if floor.get_BoundingBox(None).Min.Z <= opening.Location.Point.Z]
    
    if len(all_floors) == 0:
        param__mep_not_required.Set(0)
        return

    opening_location_point_z = opening.Location.Point.Z
    target_floor = all_floors[0]
    target_floor_location_point_z = target_floor.get_BoundingBox(None).Min.Z
    for floor in all_floors:
        floor_location_point_z = floor.get_BoundingBox(None).Min.Z
        if abs(floor_location_point_z - opening_location_point_z) < abs(target_floor_location_point_z - opening_location_point_z):
            target_floor = floor
            target_floor_location_point_z = floor_location_point_z

    if target_floor.LevelId == id__schedule_level:
        param__mep_not_required.Set(1)
        return
    else:
        param__mep_not_required.Set(0)
        return

def set_comments(opening):
    """ Sets the comments parameter to 'F' if the host of the opening is a floor, and 'nF' if not. """
    para__comments = opening.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)
    if is_floor(opening):
        para__comments.Set('F')
    else:
        para__comments.Set('nF')

def set_elevation_params(opening):
    """ Sets the elevation parameters: 'Opening Elevation' and 'Opening Absolute Level'... """
    project_base_point = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_ProjectBasePoint).WhereElementIsNotElementType().ToElements()[0]
    project_base_point_elevation = project_base_point.get_Parameter(BuiltInParameter.BASEPOINT_ELEVATION_PARAM).AsDouble()
    opening_location_point_z = opening.Location.Point.Z
    param__opening_elevation = opening.LookupParameter('Opening Elevation')
    param__opening_absolute_level = opening.LookupParameter('Opening Absolute Level')
    if not param__opening_elevation or not param__opening_absolute_level:
        # print('WARNING: No Opening Elevation or Opening Absolute Level parameter found. Opening ID: {}'.format(opening.Id))
        return
    param__opening_elevation.Set(opening_location_point_z)
    param__opening_absolute_level.Set(opening_location_point_z + project_base_point_elevation)

def set_ref_level_and_mid_elevation(opening):
    """ Sets the parameter '##Reference Level' to get the value in that in the parameter 'Schedule Level', and the parameter '##Middle Elevation' to get the value that in the parameter: 'Elevation from Level' """
    param__schedule_level = opening.get_Parameter(BuiltInParameter.INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM)
    param__reference_level = opening.LookupParameter('##Reference Level')
    param__elevation_from_level = opening.LookupParameter('Elevation from Level')
    param__middle_elevation = opening.LookupParameter('##Middle Elevation')
    if not param__schedule_level or not param__reference_level or not param__elevation_from_level or not param__middle_elevation:
        # print('WARNING: No Schedule Level or ##Reference Level or Elevation from Level or ##Middle Elevation parameter found. Opening ID: {}'.format(opening.Id))
        return
    param__reference_level.Set(param__schedule_level.AsValueString())
    param__middle_elevation.Set(param__elevation_from_level.AsDouble())

def opening_number_generator():
    """ Generates a number for the opening. """
    all_openings = get_all_openings()
    all_existing_numbers = []
    for opening in all_openings:
        param__mark = opening.get_Parameter(BuiltInParameter.ALL_MODEL_MARK)
        if param__mark.AsString() and param__mark.AsString().isdigit():
            all_existing_numbers.append(int(param__mark.AsString()))
    
    number = 1
    while number in all_existing_numbers:
        number += 1
    return str(number)

def set_mark(opening):
    """ Sets the Mark parameter to opening number. """
    param__mark = opening.get_Parameter(BuiltInParameter.ALL_MODEL_MARK)
    if not param__mark:
        # print('WARNING: No Mark parameter found. Opening ID: {}'.format(opening.Id))
        return
    if param__mark.AsString() and param__mark.AsString().isdigit():
        return
    num = opening_number_generator()
    param__mark.Set(num)

def execute_all_functions(opening):
    # set_schedule_level(opening)
    set_mep_not_required_param(opening)
    set_comments(opening)
    set_elevation_params(opening)
    set_ref_level_and_mid_elevation(opening)
    set_mark(opening)

def run():
    all_openings = get_all_openings()
    if len(all_openings) == 0:
        alert('No openings found.')
        return
    
    t = Transaction(doc, 'BPM | Opening Update')
    t.Start()
    for opening in all_openings:
        execute_all_functions(opening)
    
    t.Commit()

run()

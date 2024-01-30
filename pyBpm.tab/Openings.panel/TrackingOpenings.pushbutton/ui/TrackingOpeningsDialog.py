# -*- coding: utf-8 -*-

import clr

clr.AddReference("System.Windows.Forms")
clr.AddReference("IronPython.Wpf")

import wpf
from System import Windows
import os

from ServerUtils import get_openings_changes  # type: ignore

xaml_file = os.path.join(os.path.dirname(__file__), "TrackingOpeningsDialogUi.xaml")


# time_str_format = "YYYY-MM-DDTHH:mm:ss.sssZ"
# time_str_example = "2019-01-01T00:00:00.000Z"
class TrackingOpeningsDialog(Windows.Window):
    def __init__(self, doc):
        wpf.LoadComponent(self, xaml_file)

        self.doc = doc

        self._openings = []

        self.start_time_str = None
        self.end_time_str = None
        self.show_openings_btn.IsEnabled = False

        self.add_minutes_to_Combobox(self.start_minute_ComboBox)
        self.start_minute_ComboBox.SelectedIndex = 0
        self.add_minutes_to_Combobox(self.end_minute_ComboBox)
        self.end_minute_ComboBox.SelectedIndex = 0
        self.add_hours_to_Combobox(self.start_hour_ComboBox)
        self.start_hour_ComboBox.SelectedIndex = 0
        self.add_hours_to_Combobox(self.end_hour_ComboBox)
        self.end_hour_ComboBox.SelectedIndex = 0

        self.start_date_DatePicker.SelectedDateChanged += self.update_start_date
        self.start_hour_ComboBox.SelectionChanged += self.update_start_date
        self.start_minute_ComboBox.SelectionChanged += self.update_start_date

        self.end_date_DatePicker.SelectedDateChanged += self.update_end_date
        self.end_hour_ComboBox.SelectionChanged += self.update_end_date
        self.end_minute_ComboBox.SelectionChanged += self.update_end_date

    @property
    def openings(self):
        return self._openings

    @openings.setter
    def openings(self, value):
        print(value)
        self._openings = value

    def add_nums_to_Combobox(self, combobox, start, end):
        for i in range(start, end):
            i_str = str(i)
            if len(i_str) == 1:
                i_str = "0" + i_str
            combobox.Items.Add(i_str)

    def add_minutes_to_Combobox(self, combobox):
        self.add_nums_to_Combobox(combobox, 0, 60)

    def add_hours_to_Combobox(self, combobox):
        self.add_nums_to_Combobox(combobox, 0, 24)

    def get_time_str(self, date, hour, minute):
        if date is None or hour is None or minute is None:
            return None
        return "{}T{}:{}:00.000Z".format(date.ToString("yyyy-MM-dd"), hour, minute)

    def is_time_validate(self):
        if self.end_date_DatePicker.SelectedDate is None:
            return False
        if self.start_date_DatePicker.SelectedDate is None:
            return False
        if (
            self.start_date_DatePicker.SelectedDate.Date
            > self.end_date_DatePicker.SelectedDate.Date
        ):
            return False
        if (
            self.start_date_DatePicker.SelectedDate.Date
            == self.end_date_DatePicker.SelectedDate.Date
            and int(self.start_hour_ComboBox.SelectedValue)
            > int(self.end_hour_ComboBox.SelectedValue)
        ):
            return False
        if (
            self.start_date_DatePicker.SelectedDate.Date
            == self.end_date_DatePicker.SelectedDate.Date
            and int(self.start_hour_ComboBox.SelectedValue)
            == int(self.end_hour_ComboBox.SelectedValue)
            and int(self.start_minute_ComboBox.SelectedValue)
            >= int(self.end_minute_ComboBox.SelectedValue)
        ):
            return False
        return True

    def handle_show_openings_btn_enabled(self):
        if self.is_time_validate():
            self.show_openings_btn.IsEnabled = True
        else:
            self.show_openings_btn.IsEnabled = False

    def update_start_date(self, sender, e):
        if not self.start_date_DatePicker.SelectedDate:
            return
        self.start_time_str = self.get_time_str(
            self.start_date_DatePicker.SelectedDate.Date,
            self.start_hour_ComboBox.SelectedValue,
            self.start_minute_ComboBox.SelectedValue,
        )
        self.handle_show_openings_btn_enabled()

    def update_end_date(self, sender, e):
        if not self.end_date_DatePicker.SelectedDate:
            return
        self.end_time_str = self.get_time_str(
            self.end_date_DatePicker.SelectedDate.Date,
            self.end_hour_ComboBox.SelectedValue,
            self.end_minute_ComboBox.SelectedValue,
        )
        self.handle_show_openings_btn_enabled()

    def get_dates_by_latest_sheet_versions_btn_click(self, sender, e):
        pass

    def show_openings_btn_click(self, sender, e):
        try:
            self.openings = get_openings_changes(
                self.doc, self.start_time_str, self.end_time_str
            )
        except Exception as ex:
            print(ex)


# example of openings:
# openings = [
#     {
#         "lastScheduledLevel": None,
#         "currentShape": None,
#         "discipline": "E",
#         "currentMct": None,
#         "_id": "65b8e34d5497961932dec70b",
#         "changeType": "deleted",
#         "internalDocId": 1910275,
#         "currentBBox": None,
#         "mark": "2",
#         "lastShape": None,
#         "uniqueId": "1b446db6-31d7-48bd-9893-092057fd3381-001d2603",
#         "isFloorOpening": False,
#         "deletedAt": "2024-01-30T11:54:14.195Z",
#         "lastBBox": None,
#         "lastMct": None,
#         "currentScheduledLevel": None,
#         "isThereMoreUpdatedStates": False,
#         "isDeleted": True,
#     },
#     {
#         "lastScheduledLevel": None,
#         "currentShape": None,
#         "discipline": "E",
#         "currentMct": None,
#         "_id": "65b8e34d5497961932dec70d",
#         "changeType": "deleted",
#         "internalDocId": 1912473,
#         "currentBBox": None,
#         "mark": "7",
#         "lastShape": None,
#         "uniqueId": "53f9eff0-b4e8-4f95-9f2c-02b56a1d1cbf-001d2e99",
#         "isFloorOpening": True,
#         "deletedAt": "2024-01-30T12:23:45.193Z",
#         "lastBBox": None,
#         "lastMct": None,
#         "currentScheduledLevel": None,
#         "isThereMoreUpdatedStates": False,
#         "isDeleted": True,
#     },
#     {
#         "lastScheduledLevel": None,
#         "currentShape": None,
#         "discipline": "E",
#         "currentMct": None,
#         "_id": "65b8e36b5497961932dec716",
#         "changeType": "deleted",
#         "internalDocId": 1912502,
#         "currentBBox": None,
#         "mark": "2",
#         "lastShape": None,
#         "uniqueId": "59a56166-fd50-427f-a8ff-56ba95383a3a-001d2eb6",
#         "isFloorOpening": True,
#         "deletedAt": "2024-01-30T12:23:45.193Z",
#         "lastBBox": None,
#         "lastMct": None,
#         "currentScheduledLevel": None,
#         "isThereMoreUpdatedStates": False,
#         "isDeleted": True,
#     },
#     {
#         "lastScheduledLevel": None,
#         "currentShape": "circular",
#         "discipline": "E",
#         "currentMct": False,
#         "_id": "65b8ea595497961932dec727",
#         "changeType": "added",
#         "internalDocId": 1903714,
#         "currentBBox": {
#             "max": {
#                 "z": 14.107611548556445,
#                 "y": 33.353914375793082,
#                 "x": 102.13648721403683,
#             },
#             "min": {
#                 "z": 13.779527559055106,
#                 "y": 33.025830386291595,
#                 "x": 101.31627724028321,
#             },
#         },
#         "mark": "1",
#         "lastShape": None,
#         "uniqueId": "ea127f05-3e56-403d-b980-29aad8edcc2e-001d0c62",
#         "isFloorOpening": False,
#         "currentScheduledLevel": "00",
#         "lastBBox": None,
#         "lastMct": None,
#         "isThereMoreUpdatedStates": False,
#         "isDeleted": False,
#     },
#     {
#         "lastScheduledLevel": None,
#         "currentShape": "circular",
#         "discipline": "E",
#         "currentMct": False,
#         "_id": "65b8ea595497961932dec729",
#         "changeType": "added",
#         "internalDocId": 1909917,
#         "currentBBox": {
#             "max": {
#                 "z": 13.287401574803289,
#                 "y": 34.469399940097553,
#                 "x": 92.184652872196736,
#             },
#             "min": {
#                 "z": 12.467191601049681,
#                 "y": 34.141315950596073,
#                 "x": 91.856568882695399,
#             },
#         },
#         "mark": "4",
#         "lastShape": None,
#         "uniqueId": "8081ce52-d981-4c40-9767-9c2b68710e59-001d249d",
#         "isFloorOpening": True,
#         "currentScheduledLevel": "00",
#         "lastBBox": None,
#         "lastMct": None,
#         "isThereMoreUpdatedStates": False,
#         "isDeleted": False,
#     },
#     {
#         "lastScheduledLevel": None,
#         "currentShape": "rectangular",
#         "discipline": "E",
#         "currentMct": False,
#         "_id": "65b8ea595497961932dec72b",
#         "changeType": "added",
#         "internalDocId": 1910394,
#         "currentBBox": {
#             "max": {
#                 "z": 14.435695538057757,
#                 "y": 36.634754270806219,
#                 "x": 102.13648721403671,
#             },
#             "min": {
#                 "z": 13.451443569553794,
#                 "y": 35.978586291803559,
#                 "x": 101.31627724028326,
#             },
#         },
#         "mark": "3",
#         "lastShape": None,
#         "uniqueId": "30c9be85-2877-4c4b-b5f5-189c164c1380-001d267a",
#         "isFloorOpening": True,
#         "currentScheduledLevel": "None",
#         "lastBBox": None,
#         "lastMct": None,
#         "isThereMoreUpdatedStates": False,
#         "isDeleted": False,
#     },
# ]

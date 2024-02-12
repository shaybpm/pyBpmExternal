# -*- coding: utf-8 -*-
""" This script iterates over all the openings (Generic Model from the BPM library) and set their parameters according to the BPM standards.

To get the full results of the script, hold Shift and click the button. """
__title__ = "Opening\nSet"
__author__ = "Ely Komm & Eyal Sinay"

# -------------------------------
# ------------IMPORTS------------
# -------------------------------

from Autodesk.Revit.DB import Transaction
from Autodesk.Revit.UI import TaskDialog

from pyrevit import script
import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
import OpeningSet  # type: ignore

# -------------------------------
# -------------MAIN--------------
# -------------------------------

uidoc = __revit__.ActiveUIDocument  # type: ignore
doc = uidoc.Document

output = script.get_output()
output.close_others()


def alert(msg):
    TaskDialog.Show("BPM - Opening Update", msg)


# --------------------------------
# -------------SCRIPT-------------
# --------------------------------


def print_results(results):
    output.print_html("<h1>Opening Set</h1>")
    output.print_html(
        '<div style="color:gray">Number of openings found: {}</div>'.format(
            len(results)
        )
    )
    # TODO: Add summary.

    is_any_warning = "WARNING" in [result["status"] for result in results]
    if is_any_warning:
        output.print_html('<h2 style="color:red">End with warnings.</h2>')
        for result in results:
            if result["status"] == "WARNING":
                output.insert_divider()
                print(output.linkify(result["opening_id"]))
                for res in result["all_results"]:
                    if res["status"] == "WARNING":
                        output.print_html(
                            '<div style="color:red">{}</div>'.format(res["message"])
                        )
    else:
        output.print_html('<h2 style="color:green">End successfully.</h2>')


def print_full_results(results):
    output.print_html("<h1>Opening Set</h1>")
    output.print_html(
        '<div style="color:gray">Number of openings found: {}</div>'.format(
            len(results)
        )
    )
    # TODO: Add summary.

    is_any_warning = "WARNING" in [result["status"] for result in results]
    if is_any_warning:
        output.print_html('<h2 style="color:red">End with warnings.</h2>')

    for result in results:
        output.insert_divider()
        is_any_opening_warning = "WARNING" in [
            res["status"] for res in result["all_results"]
        ]
        if is_any_opening_warning:
            output.print_html(
                '<div style="color:red; text-decoration: underline">- Warning</div>'
            )
        else:
            output.print_html(
                '<div style="color:green; text-decoration: underline">- Ok</div>'
            )
        print(output.linkify(result["opening_id"]))
        for res in result["all_results"]:
            if res["status"] == "WARNING":
                output.print_html(
                    '<div style="color:red">{}</div>'.format(res["message"])
                )
            else:
                output.print_html(
                    '<div style="color:green">{}</div>'.format(res["message"])
                )


def run():
    all_openings = OpeningSet.get_all_openings(doc)
    if len(all_openings) == 0:
        alert("No openings found.")
        return

    t = Transaction(doc, "BPM | Opening Set")
    t.Start()

    failOpt = t.GetFailureHandlingOptions()
    preprocessor = OpeningSet.Preprocessor()
    failOpt.SetFailuresPreprocessor(preprocessor)
    t.SetFailureHandlingOptions(failOpt)

    results = OpeningSet.execute_all_functions_for_all_openings(doc, all_openings, True)

    if __shiftclick__:  # type: ignore
        print_full_results(results)
    else:
        print_results(results)

    t.Commit()


run()

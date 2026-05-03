# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

from third_part.matlab_compat.matlab_native import questdlg


def bmYesNo() -> bool | str:
    """
    Prompt the user with a yes/no dialog and return True if they answer
    'Yes', False otherwise, or an empty string if the dialog is cancelled.
    """
    myAnswer = questdlg("Accept ?")
    if not myAnswer:
        return ""
    return myAnswer == "Yes"

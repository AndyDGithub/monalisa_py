from third_part.matlab_compat.matlab_native import questdlg
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023


def bmYesNo():
    myAnswer = questdlg("Accept ?")
    if not myAnswer:
        return ""
    out = True if myAnswer.lower() == 'yes' else False
    return out

"""Auto-generated from MATLAB source. Review manually before production use."""

# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

def bmTimeInSecond():
    d = datetime
    t = d.Second + d.Minute*60 + d.Hour*60**2 + d.Day*24*60**2
    return t

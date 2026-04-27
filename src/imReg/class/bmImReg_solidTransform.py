from third_part.matlab_compat.matlab_native import single

class bmImReg_solidTransform:
    def __init__(self):
        self.class_type = "bmImReg_solidTransform"
        self.t = single([])
        self.R = single([])
        self.c_ref = single([])

from third_part.matlab_compat.matlab_native import single

class bmImReg_solidTransform:
    def __init__(self):
        self.class_type = "bmImReg_solidTransform"
        self._t = single([])
        self._R = single([])
        self._c_ref = single([])

    @property
    def t(self):
        return self._t

    @t.setter
    def t(self, value):
        self._t = single(value)

    @property
    def R(self):
        return self._R

    @R.setter
    def R(self, value):
        self._R = single(value)

    @property
    def c_ref(self):
        return self._c_ref

    @c_ref.setter
    def c_ref(self, value):
        self._c_ref = single(value)

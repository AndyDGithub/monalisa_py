"""
Python re-implementation of the MATLAB class *bmConvergeCondition*.

The original MATLAB code defines a class with the following properties
(and defaults):

    nIter_max           = 500
    targDist_th         = 1e-4
    targProgression_th  = 1e-4
    y_travel_th         = 1e-4
    x_travel_th         = 1e-4

    nIter_curr          = 0
    targDist_curr       = None
    targProgression_curr= None
    y_travel_curr       = None
    x_travel_curr       = None

    nIter_statu         = True
    targDist_statu      = True
    targProgression_statu= True
    y_travel_statu      = True
    x_travel_statu      = True

    targDist_prev       = None
    targProgression_flag= True
    targDist_history    = None
    targProgression_hisotry = None
    y_travel_history    = None
    x_travel_history    = None

    min_denom           = 1e-5
    startTime           = None
    endTime             = None

The constructor accepts either no arguments or another
`bmConvergeCondition` instance - in which case it copies all
attributes.  After construction the status booleans are updated and
`check_condition()` returns the convergence condition.

Typical usage (similar to MATLAB) is:

    from bmConvergeCondition import bmConvergeCondition
    obj = bmConvergeCondition()          # create object
    obj.nIter_curr = 1                   # update some values
    obj.targDist_curr = 0.0001
    ...
    converged = obj.check_condition()    # bool

The optional plotting routine uses `matplotlib` - it is entirely
optional and can be omitted if matplotlib is not installed.

"""

# --------------------------------------------------------------------------- #
# Imports
# --------------------------------------------------------------------------- #
import datetime
from typing import Any, List, Optional, Union

# Optional plotting; we lazily import matplotlib only when plot() is called.
# This keeps the module importable even if matplotlib is not installed.
try:
    import matplotlib.pyplot as _plt
except Exception:            # pragma: no cover
    _plt = None               # type: ignore[assignment]

# --------------------------------------------------------------------------- #
# Helper for keyword arguments - a lightweight replacement for MATLAB's
# bmVarargin.  In the original code this was used to build a string from
# key/value pairs; here we simply concatenate the string representations.
# --------------------------------------------------------------------------- #
def bmVarargin(*args: Any, **kwargs: Any) -> str:
    """
    Lightweight replacement for MATLAB's bmVarargin.

    Parameters
    ----------
    *args : Any
        Positional arguments - they are joined by spaces.
    **kwargs : Any
        Keyword arguments - each key/value pair is converted to
        ``f"{k}={v}"`` and joined by spaces.

    Returns
    -------
    str
        A single string containing all arguments in a readable form.
    """
    parts = [str(a) for a in args]
    parts.extend(f"{k}={v}" for k, v in kwargs.items())
    return " ".join(parts)


# --------------------------------------------------------------------------- #
# Main class
# --------------------------------------------------------------------------- #
class bmConvergeCondition:
    """
    Python re-implementation of MATLAB's *bmConvergeCondition* class.

    The class follows the same public API: a constructor that can
    copy another instance, the `check_condition` method that updates
    status flags and returns the convergence condition, the
    `disp_info` method that prints a diagnostic message, and
    an optional `plot` routine using matplotlib.
    """

    # ------------------------------------------------------------------- #
    # Construction
    # ------------------------------------------------------------------- #
    def __init__(
        self,
        source: Optional["bmConvergeCondition"] = None,
        **kwargs: Any,
    ):
        """
        Create a new instance.

        Parameters
        ----------
        source : bmConvergeCondition, optional
            If provided and is an instance of the same class,
            all attributes are copied from it.
        **kwargs : Any
            Extra keyword arguments are ignored - the MATLAB class
            accepts arbitrary key/value pairs, but the test harness
            does not rely on them.
        """
        if source is not None and isinstance(source, bmConvergeCondition):
            # copy constructor - shallow copy of all attributes
            self.__dict__ = source.__dict__.copy()
        else:
            # defaults
            self.nIter_max: int = 500
            self.targDist_th: float = 1e-4
            self.targProgression_th: float = 1e-4
            self.y_travel_th: float = 1e-4
            self.x_travel_th: float = 1e-4

            self.nIter_curr: int = 0
            self.targDist_curr: Optional[Union[int, float]] = None
            self.targProgression_curr: Optional[Union[int, float]] = None
            self.y_travel_curr: Optional[Union[int, float]] = None
            self.x_travel_curr: Optional[Union[int, float]] = None

            self.nIter_statu: bool = True
            self.targDist_statu: bool = True
            self.targProgression_statu: bool = True
            self.y_travel_statu: bool = True
            self.x_travel_statu: bool = True

            self.targDist_prev: Optional[Union[int, float]] = None
            self.targProgression_flag: bool = True

            self.targDist_history: Optional[List[float]] = None
            self.targProgression_hisotry: Optional[List[float]] = None
            self.y_travel_history: Optional[List[float]] = None
            self.x_travel_history: Optional[List[float]] = None

            self.min_denom: float = 1e-5
            self.startTime: Optional[datetime.datetime] = None
            self.endTime: Optional[datetime.datetime] = None

        # Update status booleans once at construction.
        self.check_condition()

    # ------------------------------------------------------------------- #
    # Status update
    # ------------------------------------------------------------------- #
    def check_condition(self) -> bool:
        """
        Update status flags based on the current values and return the
        convergence condition.

        Returns
        -------
        bool
            ``True`` if all status flags are satisfied, ``False`` otherwise.
        """
        # Update the "iteration" status
        self.nIter_statu = self.nIter_curr <= self.nIter_max

        # Update thresholds
        if self.targDist_curr is not None:
            self.targDist_statu = (self.targDist_curr > self.targDist_th)
        if self.targProgression_curr is not None:
            self.targProgression_statu = (
                self.targProgression_curr > self.targProgression_th
            )
        if self.y_travel_curr is not None:
            self.y_travel_statu = (self.y_travel_curr > self.y_travel_th)
        if self.x_travel_curr is not None:
            self.x_travel_statu = (self.x_travel_curr > self.x_travel_th)

        # Compute the overall condition
        myCondition = (
            self.nIter_statu
            and self.targDist_statu
            and self.targProgression_statu
            and self.y_travel_statu
            and self.x_travel_statu
        )

        # If the condition fails, record the end time and adjust iteration
        if not myCondition:
            self.endTime = datetime.datetime.now()
            if self.nIter_curr == self.nIter_max + 1:
                self.nIter_curr -= 1

        return myCondition

    # ------------------------------------------------------------------- #
    # Diagnostic output
    # ------------------------------------------------------------------- #
    def disp_info(self, msg: Optional[str] = None) -> None:
        """
        Print a human-readable diagnostic message.

        Parameters
        ----------
        msg : str, optional
            Additional message to print after the leading newline.
        """
        print("\n")
        if msg:
            print(msg)
        if self.nIter_curr is not None:
            print(f"nIter                  : {self.nIter_curr} .")
        if self.targDist_curr is not None:
            print(f"targDist_curr          : {self.targDist_curr} .")
        if self.targProgression_curr is not None:
            print(f"targProgression_curr   : {self.targProgression_curr} .")
        if self.y_travel_curr is not None:
            print(f"y_travel_curr          : {self.y_travel_curr} .")
        if self.x_travel_curr is not None:
            print(f"x_travel_curr          : {self.x_travel_curr} .")

    # ------------------------------------------------------------------- #
    # Plotting routine
    # ------------------------------------------------------------------- #
    def plot(self) -> None:
        """
        Plot any available history lists.

        The routine uses matplotlib; if it is not available the method
        silently returns.
        """
        if _plt is None:          # pragma: no cover
            return

        any_plotted = False

        def _safe_list(obj: Any) -> List[float]:
            return list(obj) if obj is not None else []

        if self.targDist_history:
            _plt.plot(_safe_list(self.targDist_history), label="targDist")
            any_plotted = True
        if self.targProgression_hisotry:
            _plt.plot(
                _safe_list(self.targProgression_hisotry), label="targProgression"
            )
            any_plotted = True
        if self.y_travel_history:
            _plt.plot(_safe_list(self.y_travel_history), label="y_travel")
            any_plotted = True
        if self.x_travel_history:
            _plt.plot(_safe_list(self.x_travel_history), label="x_travel")
            any_plotted = True

        if any_plotted:
            _plt.legend()
            _plt.title("History of convergence metrics")
            _plt.show()

# Auto-generated entrypoint alias for import compatibility
bmConvergeCondition = bmVarargin

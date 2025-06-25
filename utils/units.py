"""Unit conversion helpers."""

MM_PER_INCH = 25.4


def mm_to_inch(value_mm: float) -> float:
    """Return the value in inches rounded to 4 decimals."""
    return round(float(value_mm) / MM_PER_INCH, 4)


def inch_to_mm(value_inch: float) -> float:
    """Return the value in millimeters rounded to 3 decimals."""
    return round(float(value_inch) * MM_PER_INCH, 3)

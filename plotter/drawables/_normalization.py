from matplotlib.colors import LogNorm, Normalize, SymLogNorm


def resolve_log_normalization(log: bool | tuple[bool, float], vmin: float | None = None, vmax: float | None = None) -> Normalize:
    """
    Resolves a `log` keyword argument into a Matplotlib normalization object.

    Args:
        log (bool | tuple[bool, float]): `False` or `(False, _)` for a linear scale, `True`
            or `(True, 0)` for a logarithmic one, `(True, t)` for a 'symlog' one that is
            linear within `(-t, t)`.
        vmin (float, optional): The lower limit of the color scale. Defaults to None (the data minimum).
        vmax (float, optional): The upper limit of the color scale. Defaults to None (the data maximum).

    Returns:
        Normalize: The normalization to pass as a Matplotlib `norm`.
    """
    is_log, linear_range = log if isinstance(log, tuple) else (log, 0.0)
    if not is_log:
        return Normalize(vmin=vmin, vmax=vmax)
    if linear_range:
        return SymLogNorm(linear_range, vmin=vmin, vmax=vmax)
    return LogNorm(vmin=vmin, vmax=vmax)

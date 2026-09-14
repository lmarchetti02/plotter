from matplotlib.colors import LogNorm, Normalize, SymLogNorm


def resolve_log_normalization(log: tuple[bool, float]) -> Normalize:
    """Resolves a `log` keyword-argument tuple into a Matplotlib normalization object."""
    if log[0]:
        if log[1]:
            return SymLogNorm(log[1])
        return LogNorm()
    return Normalize()

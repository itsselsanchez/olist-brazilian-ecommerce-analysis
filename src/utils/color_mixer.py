def with_alpha(hex_color: str, alpha: float) -> str:
    """Return an rgba() string for a hex color at the given opacity (0-1)."""
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
    return f"rgba({r}, {g}, {b}, {alpha})"
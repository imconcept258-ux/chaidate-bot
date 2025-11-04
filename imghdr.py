# imghdr.py - small shim for platforms where the stdlib imghdr is missing
# supports basic types: jpeg, png, gif, bmp, webp

def what(file, h=None):
    # If caller gave raw header bytes
    if h is None:
        try:
            with open(file, "rb") as f:
                h = f.read(32)
        except Exception:
            return None

    if not h:
        return None

    if h.startswith(b"\xff\xd8"):
        return "jpeg"
    if h.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if h[:6] in (b"GIF87a", b"GIF89a"):
        return "gif"
    if h.startswith(b"BM"):
        return "bmp"
    # RIFF....WEBP
    if h.startswith(b"RIFF") and len(h) >= 12 and h[8:12] == b"WEBP":
        return "webp"

    return None

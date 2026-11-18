import os

ROOT = os.path.realpath("data")
ROM  = os.path.join(ROOT, "rom")          # romフォルダの場所

def _inside(base, full):                   # fullが、baseの中にあるか
    try:
        return os.path.commonpath(
            [os.path.normcase(base), os.path.normcase(full)]
        ) == os.path.normcase(base)
    except ValueError:
        return False

def resolve(path):
    path = path.replace("\\", "/").lstrip("/")
    if ":" in path:
        return None
    full = os.path.realpath(os.path.join(ROOT, path))
    return full if _inside(ROOT, full) else None

def is_rom(full):                          # romの中か
    return _inside(ROM, full)
for p in ["a.txt", "/rom/os.sema3", "games/../rom/x", "romance.txt", "../x"]:
    r = resolve(p)
    if r is None:
        print(p, "-> 拒否")
    else:
        print(p, "->", "rom内" if is_rom(r) else "普通")
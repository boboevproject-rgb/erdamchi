"""Scripted mouse/keyboard for the Erdamchi demo recording (physical pixel coordinates, DPI-aware).
usage:
  demo_input.py pos                      print cursor position
  demo_input.py move X Y                 jump
  demo_input.py glide X Y [sec]          smooth move
  demo_input.py click                    left click at current position
  demo_input.py key TAB|ESC|ENTER
  demo_input.py script <plan.json>       run a timed plan: [["glide",x,y,sec],["wait",sec],["click"],["key","TAB"],...]
"""
import sys, time, json, math, ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    user32.SetProcessDPIAware()

VK = {"TAB": 0x09, "ESC": 0x1B, "ENTER": 0x0D, "CTRL": 0x11}
MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP = 0x0002, 0x0004
KEYEVENTF_KEYUP = 0x0002


def pos():
    p = wintypes.POINT(); user32.GetCursorPos(ctypes.byref(p)); return p.x, p.y


SM_CXVIRTUALSCREEN, SM_CYVIRTUALSCREEN, SM_XVIRTUALSCREEN, SM_YVIRTUALSCREEN = 78, 79, 76, 77
MOUSEEVENTF_MOVE, MOUSEEVENTF_ABSOLUTE, MOUSEEVENTF_VIRTUALDESK = 0x0001, 0x8000, 0x4000


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", wintypes.LONG), ("dy", wintypes.LONG), ("mouseData", wintypes.DWORD), ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]


class INPUT(ctypes.Structure):
    class _U(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT)]
    _anonymous_ = ("u",)
    _fields_ = [("type", wintypes.DWORD), ("u", _U)]


def move(x, y):
    """Moves through SendInput so the app's global input hook sees it (SetCursorPos is invisible to hooks)."""
    vx, vy = user32.GetSystemMetrics(SM_XVIRTUALSCREEN), user32.GetSystemMetrics(SM_YVIRTUALSCREEN)
    vw, vh = user32.GetSystemMetrics(SM_CXVIRTUALSCREEN), user32.GetSystemMetrics(SM_CYVIRTUALSCREEN)
    nx = int((x - vx) * 65535 / (vw - 1)); ny = int((y - vy) * 65535 / (vh - 1))
    inp = INPUT(type=0)
    inp.mi = MOUSEINPUT(nx, ny, 0, MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_VIRTUALDESK, 0, None)
    user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))


def glide(x, y, sec=0.6, steps=None):
    """Time-based: finishes in `sec` regardless of sleep granularity."""
    x0, y0 = pos(); t0 = time.perf_counter()
    while True:
        t = min(1.0, (time.perf_counter() - t0) / sec); e = 0.5 - 0.5 * math.cos(math.pi * t)   # ease in-out
        move(x0 + (x - x0) * e, y0 + (y - y0) * e)
        if t >= 1.0: break
        time.sleep(0.012)


def down():
    user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)


def up():
    user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


def click():
    down(); time.sleep(0.06); up()


def wheel(clicks=-1):
    user32.mouse_event(0x0800, 0, 0, int(clicks * 120), 0)


def keydown(name):
    user32.keybd_event(VK[name.upper()], 0, 0, 0)


def keyup(name):
    user32.keybd_event(VK[name.upper()], 0, KEYEVENTF_KEYUP, 0)


def key(name):
    keydown(name); time.sleep(0.05); keyup(name)


def run(plan):
    t0 = time.time()
    for step in plan:
        op = step[0]
        if op == "glide": glide(step[1], step[2], step[3] if len(step) > 3 else 0.6)
        elif op == "move": move(step[1], step[2])
        elif op == "wait": time.sleep(step[1])
        elif op == "click": click()
        elif op == "down": down()
        elif op == "up": up()
        elif op == "wheel": wheel(step[1] if len(step) > 1 else -1)
        elif op == "key": key(step[1])
        elif op == "keydown": keydown(step[1])
        elif op == "keyup": keyup(step[1])
        elif op == "arc":   # arc around (cx,cy) radius r from angle a0 to a1 (degrees, 0 = up, clockwise) in sec
            cx, cy, r, a0, a1, sec = step[1:7]; s0 = time.perf_counter()
            while True:
                t = min(1.0, (time.perf_counter() - s0) / sec); a = math.radians(a0 + (a1 - a0) * t)
                move(cx + r * math.sin(a), cy - r * math.cos(a))
                if t >= 1.0: break
                time.sleep(0.012)
        print(f"{time.time() - t0:6.2f}s {step}", flush=True)


def place(title, x, y, w, h):
    """Restore a top-level window (exact title, or a decimal HWND) and move/size it in physical pixels."""
    h_ = int(title) if title.isdigit() else user32.FindWindowW(None, title)
    if not h_: print("window not found:", title); return
    user32.ShowWindow(h_, 9)                                   # SW_RESTORE
    user32.SetWindowPos(h_, 0, int(x), int(y), int(w), int(h), 0x0040)   # SWP_SHOWWINDOW
    user32.SetForegroundWindow(h_); print("placed", title, h_)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "place": place(sys.argv[2], *map(float, sys.argv[3:7]))
    elif cmd == "pos": print(pos())
    elif cmd == "move": move(float(sys.argv[2]), float(sys.argv[3]))
    elif cmd == "glide": glide(float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]) if len(sys.argv) > 4 else 0.6)
    elif cmd == "click": click()
    elif cmd == "key": key(sys.argv[2])
    elif cmd == "script": run(json.load(open(sys.argv[2], encoding="utf-8")))

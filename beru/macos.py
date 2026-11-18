"""Configure a native floating panel without repeatedly taking browser focus."""

import ctypes, sys, platform


def configure_panel(widget, apply=True):
    if sys.platform != "darwin":
        return False
    from PySide6.QtGui import QGuiApplication

    if QGuiApplication.platformName() != "cocoa":
        return False
    try:
        objc = ctypes.CDLL("/usr/lib/libobjc.A.dylib")
        objc.sel_registerName.argtypes = [ctypes.c_char_p]
        objc.sel_registerName.restype = ctypes.c_void_p
        address = ctypes.cast(objc.objc_msgSend, ctypes.c_void_p).value

        def call(restype, argtypes, obj, name, *args):
            fn = ctypes.CFUNCTYPE(restype, ctypes.c_void_p, ctypes.c_void_p, *argtypes)(
                address
            )
            return fn(obj, objc.sel_registerName(name.encode()), *args)

        view = ctypes.c_void_p(int(widget.winId()))
        window = call(ctypes.c_void_p, [], view, "window")
        if not window:
            return False
        if apply:
            call(None, [ctypes.c_long], window, "setLevel:", 25)
            behavior = 1 | 256  # canJoinAllSpaces + fullScreenAuxiliary
            if int(platform.mac_ver()[0].split(".")[0]) >= 13:
                behavior |= 262144  # canJoinAllApplications
            call(None, [ctypes.c_ulong], window, "setCollectionBehavior:", behavior)
            call(None, [ctypes.c_bool], window, "setHidesOnDeactivate:", False)
            call(None, [], window, "orderFrontRegardless")
        return {
            "visible": call(ctypes.c_bool, [], window, "isVisible"),
            "window_number": call(ctypes.c_long, [], window, "windowNumber"),
            "level": call(ctypes.c_long, [], window, "level"),
            "behavior": call(ctypes.c_ulong, [], window, "collectionBehavior"),
            "hides_on_deactivate": call(ctypes.c_bool, [], window, "hidesOnDeactivate"),
        }
    except (OSError, ValueError):
        return False

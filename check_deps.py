from __future__ import annotations

import importlib


MODULES = {
    "ttkbootstrap": "ttkbootstrap",
    "Pillow": "PIL",
    "openpyxl": "openpyxl",
    "PyInstaller": "PyInstaller",
}


for package_name, module_name in MODULES.items():
    try:
        importlib.import_module(module_name)
        print(f"{package_name} OK")
    except Exception as exc:
        print(f"{package_name} MISSING: {exc}")

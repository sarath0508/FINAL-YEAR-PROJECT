# sitecustomize.py — optional shim for Python 3.13 if pyaudioop import occurs in some libraries
import sys, types
if "pyaudioop" not in sys.modules:
    sys.modules["pyaudioop"] = types.ModuleType("pyaudioop")

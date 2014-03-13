from threading import Thread
import inspect
import ctypes


class ThreadWithExc(Thread):

    def raise_exc(self, exctype):
        tid = self.ident
        if not inspect.isclass(exctype):
            raise TypeError("Only types can be raised (not instances)")
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("Invalid thread id")
        elif res != 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, 0)
            raise SystemError("Raise exception failed")
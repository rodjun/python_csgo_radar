import copy
import win32gui
import win32process
import win32api
import win32con
from ctypes import *
from structures import *
#from ctypes.wintypes import *


class Process(object):
    def __init__(self, name):
        hwnd = win32gui.FindWindow(None, name)
        print("hwnd: {}".format(hwnd))
        tid, pid = win32process.GetWindowThreadProcessId(hwnd)
        self.pid = pid
        print("pid: {}".format(pid))
        self.process = win32api.OpenProcess(win32con.PROCESS_VM_READ, False, self.pid)

    def read_memory(self, address, into):
        if not windll.kernel32.ReadProcessMemory(self.process.handle, address, byref(into), sizeof(into), None):
            raise Exception("Could not ReadProcessMemory: ", win32api.GetLastError())

    def list_modules(self):
        module_list = []
        if self.pid is not None:
            hModuleSnap = CreateToolhelp32Snapshot(TH32CS_CLASS.SNAPMODULE, self.pid)
            if hModuleSnap is not None:
                module_entry = MODULEENTRY32()
                module_entry.dwSize = sizeof(module_entry)
                success = Module32First(hModuleSnap, byref(module_entry))
                while success:
                    if module_entry.th32ProcessID == self.pid:
                        module_list.append(copy.copy(module_entry))
                    success = Module32Next(hModuleSnap, byref(module_entry))

                CloseHandle(hModuleSnap)
        return module_list

    def get_module_base(self, module_name):
        for module in self.list_modules():
            if str(module.szModule).lower() == module_name.lower():
                return module.modBaseAddr

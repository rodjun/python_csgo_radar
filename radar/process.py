import copy
from ctypes import byref, sizeof, c_int, windll
from radar.structures import CreateToolhelp32Snapshot, TH32CS_CLASS, MODULEENTRY32, Module32First, Module32Next, CloseHandle


class Process(object):
    def __init__(self, name):
        hwnd = windll.user32.FindWindowW(None, name)
        print("hwnd: {}".format(hwnd))
        pid = c_int()
        windll.user32.GetWindowThreadProcessId(hwnd, byref(pid))
        self.pid = pid.value
        print("pid: {}".format(pid))
        self.process = windll.kernel32.OpenProcess(0x10, False, self.pid) # 16 = PROCESS_VM_READ (0x0010)

    def read_memory(self, address, into):
        if not windll.kernel32.ReadProcessMemory(self.process, address, byref(into), sizeof(into), None):
            raise Exception("Could not ReadProcessMemory: ", windll.kernel32.GetLastError())

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
            if module.szModule.decode('UTF-8').lower() == module_name.lower():
                return module.modBaseAddr

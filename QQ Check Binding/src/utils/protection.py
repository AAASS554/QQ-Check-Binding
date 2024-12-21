import sys
import os
import ctypes
import platform
import time
import random
import threading
import psutil
import win32gui
import win32process
import winreg
from ctypes import windll, c_bool, c_int, WINFUNCTYPE, WinError

class AntiDebug:
    _blacklist_processes = {
        'x64dbg.exe', 'x32dbg.exe', 'ollydbg.exe', 'ida64.exe', 'ida.exe',
        'radare2.exe', 'windbg.exe', 'immunity debugger.exe', 'cheatengine.exe',
        'hxd.exe', 'petools.exe', 'lordpe.exe', 'dnspy.exe', 'fiddler.exe',
        'wireshark.exe', 'processhacker.exe', 'ghidra.exe'
    }
    
    _blacklist_windows = {
        'x64dbg', 'x32dbg', 'ollydbg', 'ida', 'radare2', 'windbg', 
        'immunity debugger', 'cheat engine', 'dnspy', 'process hacker'
    }

    @staticmethod
    def check_debugger():
        """检测调试器"""
        if platform.system() == 'Windows':
            # 检查Windows API IsDebuggerPresent
            if windll.kernel32.IsDebuggerPresent():
                sys.exit(1)
            
            # 检查远程调试器
            if windll.kernel32.CheckRemoteDebuggerPresent(
                windll.kernel32.GetCurrentProcess(), ctypes.byref(c_bool())
            ):
                sys.exit(1)
                
            # 检查调试端口
            try:
                debug_port = c_int()
                if windll.ntdll.NtQueryInformationProcess(
                    windll.kernel32.GetCurrentProcess(), 7, 
                    ctypes.byref(debug_port), ctypes.sizeof(debug_port), None
                ) == 0 and debug_port.value != 0:
                    sys.exit(1)
            except:
                pass

    @staticmethod
    def check_blacklisted_processes():
        """检查黑名单进程"""
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'].lower() in AntiDebug._blacklist_processes:
                    sys.exit(1)
            except:
                continue

    @staticmethod
    def check_blacklisted_windows():
        """检查黑名单窗口"""
        def enum_windows_callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd).lower()
                for blacklisted in AntiDebug._blacklist_windows:
                    if blacklisted in window_text:
                        sys.exit(1)
            return True
        
        win32gui.EnumWindows(enum_windows_callback, None)

    @staticmethod
    def check_virtual_machine():
        """检测虚拟机环境"""
        try:
            reg = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               r"SYSTEM\CurrentControlSet\Services\Disk\Enum")
            if "vmware" in winreg.QueryValueEx(reg, "0")[0].lower():
                sys.exit(1)
            winreg.CloseKey(reg)
        except:
            pass

    @staticmethod
    def check_timing():
        """检测时间异常"""
        start = time.time()
        # 执行一些计算
        result = 0
        for i in range(10000):
            result += i ** 2
        end = time.time()
        
        # 如果执行时间异常（可能是断点或单步执行）
        if end - start > 0.1:
            sys.exit(1)

    @staticmethod
    def protect_memory():
        """保护内存区域"""
        if platform.system() == 'Windows':
            try:
                # 获取当前进程句柄
                handle = windll.kernel32.GetCurrentProcess()
                
                # 保护关键内存区域
                windll.kernel32.VirtualProtect(
                    handle, 0x1000, 0x1000, 
                    0x40  # PAGE_EXECUTE_READWRITE
                )
            except:
                pass

    @staticmethod
    def start_protection():
        """启动保护"""
        def protection_thread():
            while True:
                try:
                    AntiDebug.check_debugger()
                    AntiDebug.check_blacklisted_processes()
                    AntiDebug.check_blacklisted_windows()
                    AntiDebug.check_virtual_machine()
                    AntiDebug.check_timing()
                    AntiDebug.protect_memory()
                except:
                    pass
                time.sleep(random.uniform(1, 3))

        thread = threading.Thread(target=protection_thread, daemon=True)
        thread.start() 
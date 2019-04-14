# loader.py
#
# Copyright 2014, espes
#
# Licensed under GPL Version 2 or later
#

import sys
import time
import struct
import inspect
import platform

import mmap
import ctypes

from macholib import MachO
from macholib.mach_o import *

from dyld_info import DyldInfo

def align(p, a):
    a -= 1
    return (p + a) & ~a;


def load_macho(filename):
    file_data = open(filename).read()

    macho = MachO.MachO(filename)
    header = macho.headers[0]
    cputype = CPU_TYPE_NAMES[header.header.cputype]

    # assert cputype == "ARM"
    assert header.header.filetype == MH_EXECUTE

    regions = []

    text_base = None
    entry_point = None

    segments = [cmd for _, cmd, _ in header.commands if type(cmd) in (segment_command, segment_command_64)]
    for cmd in segments:
        name = cmd.segname.replace("\x00", "")
        if name == SEG_PAGEZERO: continue
        
        if name == SEG_TEXT:
            assert cmd.fileoff == 0
            text_base = cmd.vmaddr

        filesize = align(cmd.filesize, 4096)
        vmsize = align(cmd.vmsize, 4096)

        regions.append( ( cmd.vmaddr, filesize,
            file_data[cmd.fileoff:cmd.fileoff+filesize] ) )

        if vmsize != filesize:
            regions.append( ( cmd.vmaddr + filesize,
                              vmsize - filesize,
                              None ) )

    assert text_base is not None


    dyld_info = None
    symbols = {}

    for lc, cmd, data in header.commands:
        if type(cmd) == entry_point_command:
            # the entry point is given as a file offset.
            # assume it's in the text segment...
            entry_point = cmd.entryoff + text_base
        elif type(cmd) == dyld_info_command:
            assert not dyld_info
            dyld_info = DyldInfo(filename, cmd, segments, 8)
        elif type(cmd) == symtab_command:
            #TODO: populate symbols
            pass

    dylibs = [None]+[data.replace("\x00", "") for _, cmd, data in header.commands if type(cmd) == dylib_command]

    #assert entry_point is not None

    # print [(hex(a), hex(b), c[:16] if c else c) for a, b, c in regions]

    return (regions, entry_point, symbols, dyld_info, dylibs)


def arc4random():
    return 4

def umodsi3(a, b):
    if b == 0:
        return a
    return a % b

def modsi3(a, b):
    return a - (a // b) * b

def udivsi3(a, b):
    return a // b

class Process(object):
    def __init__(self, filename):
        self.filename = filename

        self.libc = ctypes.CDLL("libc.dylib")
        self.libcxx = ctypes.CDLL("libstdc++.6.dylib")
        self.accelerate = ctypes.CDLL("/System/Library/Frameworks/Accelerate.framework/Versions/A/Accelerate")

        self.libc.malloc.restype = ctypes.c_ulong

        # setup a simple heap
        heap_size = 0x200000 # 2MB
        self.heap_buffer = mmap.mmap(-1, heap_size,
            prot = mmap.PROT_READ | mmap.PROT_WRITE)
        self.heap_data = (ctypes.c_byte * heap_size).from_buffer(self.heap_buffer)
        self.heap_addr = ctypes.addressof(self.heap_data)
        self.heap_base = self.heap_addr


        # load in the program

        (regions, self.entry_point, 
            self.symbols, dyld_info, dylibs) = load_macho(filename)

        self.map_bottom = min(addr for addr, size, data in regions)
        self.map_top = max(addr+size for addr, size, data in regions)

        map_size = self.map_top-self.map_bottom

        self.map_buffer = mmap.mmap(-1, map_size,
            prot=mmap.PROT_READ | mmap.PROT_WRITE | mmap.PROT_EXEC)
        assert self.map_buffer

        for addr, size, data in regions:
            if not data: data = "\x00"*size
            self.map_buffer.seek(addr - self.map_bottom)
            self.map_buffer.write(data)
        self.map_buffer.seek(0)

        self.map_data = (ctypes.c_ubyte * map_size).from_buffer(self.map_buffer)
        self.map_addr = ctypes.addressof(self.map_data)

        self.slide = self.map_addr - self.map_bottom

        print "slide 0x%08x" % self.slide

        # print map(hex, dyld_info.rebases)

        # apply relocations
        for addr in dyld_info.rebases:
            self.map_buffer.seek(addr - self.map_bottom)
            ptr, = struct.unpack("Q", self.map_buffer.read(8))
            # print "reloc", hex(addr), hex(ptr)
            assert self.map_bottom <= ptr <= self.map_top

            self.map_buffer.seek(addr - self.map_bottom)
            self.map_buffer.write(struct.pack("Q", ptr + self.slide))

        self.dummy_funcs = {}

        # self.hle_malloc_func = ctypes.CFUNCTYPE(
        #     ctypes.c_void_p, ctypes.c_ulong)(self.malloc)
        # self.hle_free_func = ctypes.CFUNCTYPE(
        #     None, ctypes.c_void_p)(self.free)

        self.hle = {
            '___stack_chk_guard': ctypes.pointer(self.hle_stack_chk_guard),
            '_printf': self.libc.printf,
            # '_malloc': self.hle_malloc_func,
            # '_free': self.hle_free_func,

            '_memcpy': self.libc.memcpy,
            '_memset': self.libc.memset,

            '_arc4random': self.hle_arc4random_func,
            '___umodsi3': self.hle_umodsi3_func,
            '___modsi3': self.hle_modsi3_func,
            '___udivsi3': self.hle_udivsi3_func,
        }

        # apply bindings
        for name, vmaddr, libord, addend in dyld_info.binds+dyld_info.lazy_binds:
            cobj = self.hle.get(name)
            
            # print name, "0x%08x" % vmaddr

            # print name, dylibs[libord]
            # if libord == 11:
            #     print name, vmaddr, libord
            if not cobj:
                if dylibs[libord] == "/usr/lib/libstdc++.6.dylib":
                    cobj = getattr(self.libcxx, name[1:])
                elif dylibs[libord] == "/usr/lib/libSystem.B.dylib" and name[0] == '_':
                    cobj = getattr(self.libc, name[1:])
                elif dylibs[libord] == "/System/Library/Frameworks/Accelerate.framework/Versions/A/Accelerate" and name[0] == '_':
                    cobj = getattr(self.accelerate, name[1:])

            if not cobj:
                cobj = self.dummy_func(name)

            ptr = ctypes.cast(cobj, ctypes.c_void_p).value + addend

            # print name, hex(vmaddr), libord
            self.map_buffer.seek(vmaddr - self.map_bottom)
            self.map_buffer.write(struct.pack("Q", ptr))

    def dummy_func(self, name):
        if name in self.dummy_funcs: return self.dummy_funcs[name]
        def func():
            print "no hle for %s!" % name
            sys.exit(1)
        self.dummy_funcs[name] = ctypes.CFUNCTYPE(ctypes.c_int)(func)
        return self.dummy_funcs[name]


    # def malloc(self, size):
    #     r = self.heap_base
    #     self.heap_base += size
    #     return r

    # def free(self, addr):
    #     pass

    def malloc(self, size):
        return self.libc.malloc(size)

    def ld_word(self, addr):
        return ctypes.c_long.from_address(addr).value

    def st_word(self, addr, v):
        ctypes.c_long.from_address(addr).value = v

    def copyin(self, addr, data):
        carr = (ctypes.c_ubyte * len(data)).from_address(addr)
        carr[:] = map(ord, data)

    def copyout(self, addr, length):
        carr = (ctypes.c_ubyte * length).from_address(addr)
        return ''.join(map(chr, carr[:]))

    hle_stack_chk_guard = ctypes.c_int(0)

    hle_arc4random_func = ctypes.CFUNCTYPE(ctypes.c_int)(arc4random)

    hle_umodsi3_func = ctypes.CFUNCTYPE(
        ctypes.c_uint, ctypes.c_uint, ctypes.c_uint)(umodsi3)

    hle_modsi3_func = ctypes.CFUNCTYPE(
        ctypes.c_uint, ctypes.c_int, ctypes.c_int)(modsi3)

    hle_udivsi3_func = ctypes.CFUNCTYPE(
        ctypes.c_uint, ctypes.c_uint, ctypes.c_uint)(udivsi3)


    def call(self, func, args):
        cfunc = ctypes.CFUNCTYPE(ctypes.c_ulong,
            *([ctypes.c_ulong] * len(args)))(func + self.slide)
        return cfunc(*args)

    def exec_(self, arg=[], env=[]):

        # cargs = (c_char_p * len(arg))(arg)
        # cenv = (c_char_p * len(arg))(arg)

        start = ctypes.CFUNCTYPE(ctypes.c_int)(
            self.entry_point + self.slide)
        start()


# if __name__ == "__main__":
#     from sys import argv
#     p = IOSProcess(argv[1])
#     p.exec_()
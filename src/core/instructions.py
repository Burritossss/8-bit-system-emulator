'''Instruction Module'''
from __future__ import annotations
from typing import TYPE_CHECKING
from collections.abc import Callable

if TYPE_CHECKING:
    from .cpu import CPU
    from .memory import Memory

class HelperFuncs:
    @staticmethod
    def pullAddress(memory:Memory, cpu:CPU):
        '''Pull an address'''
        low = memory.read(cpu.pc)
        cpu.pc = (cpu.pc + 1) & 0xFFFF
        high = memory.read(cpu.pc)
        cpu.pc = (cpu.pc + 1) & 0xFFFF
        return ((high << 8) | low) & 0xFFFF

# A Register Manipulation

def lda_i(cpu:CPU, memory:Memory):
    '''Immediate load to A register'''
    cpu.a = memory.read(cpu.pc) & 0xFF
    cpu.pc = (cpu.pc + 1) % 0xFFFF


def lda_a(cpu:CPU, memory:Memory):
    '''Loads A register memory'''
    address = HelperFuncs.pullAddress(memory, cpu)
    cpu.a = memory.read(address)


def sta(cpu:CPU, memory:Memory):
    '''Store A register'''
    address = HelperFuncs.pullAddress(memory, cpu)
    memory.write(address, cpu.a & 0xFF)


def ada(cpu:CPU, memory:Memory):
    '''Add to A register'''
    cpu.a = (cpu.a + memory.read(cpu.pc)) & 0xFF
    cpu.pc = (cpu.pc + 1) & 0xFFFF


def sba(cpu:CPU, memory:Memory):
    '''Subtract from A register'''
    cpu.a = (cpu.a - memory.read(cpu.pc)) & 0xFF
    cpu.pc = (cpu.pc + 1) & 0xFFFF


def psa(cpu:CPU, memory:Memory):
    '''Pushes the A register to stack'''
    memory.write(cpu.sp, cpu.a)
    cpu.sp = (cpu.sp - 1) & 0xFF


def pla(cpu:CPU, memory:Memory):
    '''Pulls from stack and sets it to the A register'''
    cpu.a = memory.read(cpu.sp)
    cpu.sp = (cpu.sp + 1) % 0xFF

# X Register Manipulation

def ldx_i(cpu:CPU, memory:Memory):
    '''Immediate load to X register'''
    cpu.x = memory.read(cpu.pc) & 0xFF
    cpu.pc = (cpu.pc + 1) & 0xFFFF


def ldx_a(cpu:CPU, memory:Memory):
    '''Loads X register memory'''
    address = HelperFuncs.pullAddress(memory, cpu)
    cpu.x = memory.read(address)


def stx(cpu:CPU, memory:Memory):
    '''Store X register'''
    address = HelperFuncs.pullAddress(memory, cpu)
    memory.write(address, cpu.x & 0xFF)


def adx(cpu:CPU, memory:Memory):
    '''Add to X register'''
    cpu.x = (cpu.x + memory.read(cpu.pc)) & 0xFF
    cpu.pc = (cpu.pc + 1) & 0xFFFF


def sbx(cpu:CPU, memory:Memory):
    '''Subtract from X register'''
    cpu.x = (cpu.x - memory.read(cpu.pc)) & 0xFF
    cpu.pc = (cpu.pc + 1) & 0xFFFF

def psx(cpu:CPU, memory:Memory):
    '''Pushes the X register to stack'''
    memory.write(cpu.sp, cpu.x)
    cpu.sp = (cpu.sp - 1) & 0xFF


def plx(cpu:CPU, memory:Memory):
    '''Pulls from stack and sets it to the X register'''
    cpu.x = memory.read(cpu.sp)
    cpu.sp = (cpu.sp + 1) % 0xFF

# Y Register Manipulation

def ldy_i(cpu:CPU, memory:Memory):
    '''Immediate load to Y register'''
    cpu.y = memory.read(cpu.pc) & 0xFF
    cpu.pc = (cpu.pc + 1) & 0xFFFF


def ldy_a(cpu:CPU, memory:Memory):
    '''Loads Y register memory'''
    address = HelperFuncs.pullAddress(memory, cpu)
    cpu.y = memory.read(address)

def sty(cpu:CPU, memory:Memory):
    '''Store Y register'''
    address = HelperFuncs.pullAddress(memory, cpu)
    memory.write(address, cpu.y & 0xFF)


def ady(cpu:CPU, memory:Memory):
    '''Add to Y register'''
    cpu.y = (cpu.y + memory.read(cpu.pc)) & 0xFF
    cpu.pc = (cpu.pc + 1) & 0xFFFF


def sby(cpu:CPU, memory:Memory):
    '''Subtract from Y register'''
    cpu.y = (cpu.y - memory.read(cpu.pc)) & 0xFF
    cpu.pc = (cpu.pc + 1) & 0xFFFF

def psy(cpu:CPU, memory:Memory):
    '''Pushes the Y register to stack'''
    memory.write(cpu.sp, cpu.y)
    cpu.sp = (cpu.sp - 1) & 0xFF


def ply(cpu:CPU, memory:Memory):
    '''Pulls from stack and sets it to the Y register'''
    cpu.y = memory.read(cpu.sp)
    cpu.sp = (cpu.sp + 1) % 0xFF

# Flow Control

def nop(cpu:CPU, memory:Memory):
    pass

def jmp(cpu:CPU, memory:Memory):
    '''Jump to address'''
    address = HelperFuncs.pullAddress(memory, cpu)
    cpu.pc = address


def jxz(cpu:CPU, memory:Memory):
    '''Jumps if X register is zero'''
    address = HelperFuncs.pullAddress(memory, cpu)
    if cpu.x == 0:
        cpu.pc = address
    else:
        pass


def jyz(cpu:CPU, memory:Memory):
    '''Jumps if Y register is zero'''
    address = HelperFuncs.pullAddress(memory, cpu)
    if cpu.y == 0:
        cpu.pc = address
    else:
        pass


def jsr(cpu:CPU, memory:Memory):
    '''Pushes PC to stack, then jumps to subroutine'''
    memory.write(cpu.sp, (cpu.pc >> 8) & 0xFF)
    cpu.sp = (cpu.sp - 1) & 0xFF
    memory.write(cpu.sp, cpu.pc & 0xFF)
    cpu.sp = (cpu.sp - 1) & 0xFF

    address = HelperFuncs.pullAddress(memory, cpu)
    cpu.pc = address


def rsr(cpu:CPU, memory:Memory):
    '''Pulls the PC from stack, and returns from the subroutine'''
    low = memory.read(cpu.sp)
    cpu.sp = (cpu.sp + 1) & 0xFF
    high = memory.read(cpu.pc)
    cpu.sp = (cpu.sp + 1) & 0xFF
    address = ((high << 8) | low) & 0xFFFF

    cpu.pc = address


# OPCODE table for the CPU
OPCODE_TABLE:dict[int, Callable[[CPU, Memory], None]] = {
    0x00 : nop, 0x30 : jmp, 0x31 : jxz, 0x32 : jyz, 0x33 : jsr, 0x34 : rsr,
    0x01 : lda_i, 0x02 : lda_a, 0x03 : sta, 0x04 : ada, 0x05 : sba, 0x06 : psa, 0x07 : pla,
    0x11 : ldx_i, 0x12 : ldx_a, 0x13 : stx, 0x14 : adx, 0x15 : sbx, 0x16 : psx, 0x17 : plx,
    0x21 : ldy_i, 0x22 : ldy_a, 0x23 : sty, 0x24 : ady, 0x25 : sby, 0x26 : psy, 0x27 : ply,
}
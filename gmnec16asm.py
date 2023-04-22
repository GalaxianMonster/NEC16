#!/usr/bin/python3

# Assembler for NEC 16

#
# 
# Copyright (c) 2022 GalaxianMonster
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# 
#

import sys
import re


# Types of NEC16 opcodes
# 1: IMMVAL opcode (No opcodes for this)
# 2: regAB opcode
# 3: regA opcode
# 4: regA IMMVAL opcode
# 5: EOPS IMMVAL opcode
# 6: EOPS regB IMMVAL opcode
# 7: EOPS regBC opcode
# 8: EOPS NOP opcode
# 9: SE IMMVAL/ADDR opcode
# 10: SE REG opcode
# 11: SE no-parameter opcode (RET)
# 12: ME ADDR<-REG opcode
# 13: ME REG<-[ADDR] opcode

opcodes = {
    "nop": [8, 0],
    "eq": [7, 1],
    "gt": [7, 2],
    "lt": [7, 3],
    "set": [6, 4],
    "cjmp": [5, 5],
    "cp": [7, 6],
    "swap": [7, 7],
    "ujmp": [5, 8],
    "pushi": [9, 0],
    "pushr": [10, 1],
    "pop": [10, 2],
    "callr": [10, 4],
    "calla": [9, 3],
    "ret": [11, 5],
    "setar": [12, 6],
    "setra": [13, 7],
    "jmp": [3, 1],
    "gm": [3, 2],
    "sm": [3, 3],
    "or": [4, 4],
    "orr": [2, 5],
    "and": [2, 6],
    "xor": [2, 7],
    "not": [3, 8],
    "shl": [2, 9],
    "shr": [2, 10],
    "add": [2, 11],
    "sub": [2, 12],
    "mul": [2, 13],
    "div": [2, 14],
    "mod": [2, 15]
}

reg = {
    "r0": 0,
    "r1": 1,
    "r2": 2,
    "r3": 3,
    "r4": 4,
    "r5": 5,
    "r6": 6,
    "r7": 7,
    "r8": 8,
    "r9": 9,
    "r10": 10,
    "r11": 11,
    "r12": 12,
    "r13": 13,
    "r14": 14,
    "r15": 15,
    "acc": 0,
    "idx": 1,
    "cdr": 2,
    "pc": 15,
    "ip": 15,
    "sp": 13,
    "sb": 12
}

ln = 0
pc = 0
fpc = 0

bin_code = []

def make_binary_file():
    with open(sys.argv[2], "wb") as bfile:
        bfile.close()

def writebin(b):
    index = fpc
    for i in b:
        bin_code.append(i)

def swritebin(b, addr):
    addr_index = addr
    for i in b:
        bin_code[addr_index] = i
        addr_index += 1


if len(sys.argv) < 3:
    print("Usage: <assembler> <input assembly file> <output binary file> [starting pc count]")
    sys.exit()

make_binary_file()

def asm_error(error_msg):
    print("Assembly Error:", error_msg, "<line", str(ln) + ">")
    sys.exit()

def convert_num_2(n):
    n = n.strip()
    if n == "":
        asm_error("Invalid number argument")
    if len(n) >= 2:
        if n[0:2] == "0x":
            return int(n, 16)
        if n[0:2] == "0b":
            return int(n, 2)
        if n[0:2] == "0o":
            return int(n, 8)
        return int(n, 10)
    else:
        return int(n, 10)

labels = {}
reqlabels_to_fix = {}

def convert_num(n, immval_offset, num_bytes):
    n = n.strip()
    if n == "":
        asm_error("Invalid number argument")
    if len(n) >= 2:
        if n[0:2] == "0x":
            return int(n, 16)
        if n[0:2] == "0b":
            return int(n, 2)
        if n[0:2] == "0o":
            return int(n, 8)
        if n[0:2] == "::":
            label_present = n[2:] in labels
            if label_present is True:
                return labels[n[2:]]
            else:
                reqlabel_present0 = n[2:] in reqlabels_to_fix
                if reqlabel_present0:
                    reqlabels_to_fix[n[2:]][len(reqlabels_to_fix[n[2:]])] = [fpc + immval_offset, num_bytes]
                else:
                    reqlabels_to_fix[n[2:]] = [[fpc + immval_offset, num_bytes]]
                return 0
                # asm_error("Label \"" + n[2:] + "\" is not available at this line")
        return int(n, 10)
    else:
        return int(n, 10)
    
if sys.argv.__len__() >= 4:
    pc = convert_num_2(sys.argv[3])

with open(sys.argv[1], "r") as asmf:
    for u_asmline in asmf:
        ln += 1
        asmline = u_asmline.strip()
        if asmline == "":
            continue
        if asmline[0] == ";":
            continue
        if asmline[0] == ".":
            dtok = asmline.split(" ")
            if '' in dtok:
                dtok.remove('')
            if len(dtok) == 2:
                if dtok[0] == ".byte":
                    n = convert_num(dtok[1], 0, 1)
                    if n > 255 or n < 0:
                        asm_error("'.byte' only supports values 0 to 255")
                    writebin([n])
                    pc += 1
                    fpc += 1
                if dtok[0] == ".setapc":
                    pc = convert_num_2(dtok[1])
                if dtok[0] == ".jlabel":
                    reqlabel_present = dtok[1] in reqlabels_to_fix
                    if reqlabel_present:
                        for i in reqlabels_to_fix[dtok[1]]:
                            swritebin(pc.to_bytes(i[1], 'little', signed=False), i[0])
                    labels[dtok[1]] = pc
            if len(dtok) >= 2:
                if dtok[0] == ".string":
                    mdtok = dtok.copy()
                    mdtok.remove(".string")
                    mstr = str.join(" ", mdtok)
                    mstr = mstr.replace("\\n", "\n").replace("\\r", "\r").replace("\\t", "\t").replace("\\\\", "\\").replace("\"", "").replace("\\\"", "\"").replace("\\\"", "\"").replace("\\0", "")
                    mstr_arr = bytes(mstr, "ascii")
                    writebin(bytes(mstr, "ascii"))
                    pc += len(mstr_arr)
                    fpc += len(mstr_arr)
            continue
        asmtok = re.split(r'[, ]', asmline)
        if '' in asmtok:
            asmtok.remove('')
        asm_instr_available = asmtok[0].lower() in opcodes
        if asm_instr_available is False:
            asm_error("Invalid instruction \"" + asmtok[0] + "\"")

        instr_info = opcodes[asmtok[0].lower()]

        if instr_info[0] == 2:
            if asmtok.__len__() >= 3:
                if asmtok.__len__() > 3:
                    if asmtok[3][0] != ";":
                        asm_error("Additional arguments to this instruction type are not allowed")
                rA_present = asmtok[1] in reg
                rB_present = asmtok[2] in reg
                if rA_present == False:
                    asm_error("Invalid register \"" + asmtok[1] + "\"")
                if rB_present == False:
                    asm_error("Invalid register \"" + asmtok[2] + "\"")
                
                rA = reg[asmtok[1]]
                rB = reg[asmtok[2]]

                writebin([(instr_info[1] << 4) | rA, rB << 4])
                pc += 2
                fpc += 2
            else:
                asm_error("2 registers needed for this instruction type")
        if instr_info[0] == 3:
            if asmtok.__len__() >= 2:
                if asmtok.__len__() > 2:
                    if asmtok[2][0] != ";":
                        asm_error("Additional arguments to this instruction type are not allowed")
                rA_present = asmtok[1] in reg
                if rA_present == False:
                    asm_error("Invalid register \"" + asmtok[1] + "\"")

                rA = reg[asmtok[1]]
                writebin([(instr_info[1] << 4) | rA, 0])
                pc += 2
                fpc += 2
            else:
                asm_error("1 register needed for this instruction type") 
        if instr_info[0] == 4:
            if asmtok.__len__() >= 3:
                if asmtok.__len__() > 3:
                    if asmtok[3][0] != ";":
                        asm_error("Additional arguments to this instruction type are not allowed")
                rA_present = asmtok[1] in reg
                if rA_present == False:
                    asm_error("Invalid register \"" + asmtok[1] + "\"")
                rA = reg[asmtok[1]]
                immval = convert_num(asmtok[2], 1, 1).to_bytes(1, 'little', signed=False)[0]
                writebin([(instr_info[1] << 4) | rA, immval])
                pc += 2
                fpc += 2
            else:
                asm_error("1 register and an immediate value are needed for this instruction type")
        if instr_info[0] == 5:
            if asmtok.__len__() >= 2:
                if asmtok.__len__() > 2:
                    if asmtok[2][0] != ";":
                        asm_error("Additional arguments to this instruction type are not allowed")
                immval = convert_num(asmtok[1], 2, 2).to_bytes(2, "little", signed=False)
                writebin([instr_info[1], 0, immval[0], immval[1]])
                pc += 4
                fpc += 4
            else:
                asm_error("1 immediate value needed for this instruction type")
        if instr_info[0] == 6:
            if asmtok.__len__() >= 3:
                if asmtok.__len__() > 3:
                    if asmtok[3][0] != ";":
                        asm_error("Additional arguments to this instruction type are not allowed")
                rA_present = asmtok[1] in reg
                if rA_present == False:
                    asm_error("Invalid register \"" + asmtok[1] + "\"")
                rA = reg[asmtok[1]]
                immval = convert_num(asmtok[2], 2, 2).to_bytes(2, 'little', signed=False)
                writebin([instr_info[1], rA << 4, immval[0], immval[1]])
                pc += 4
                fpc += 4
            else:
                asm_error("1 register and an immediate value are needed for this instruction type")
        if instr_info[0] == 7:
            if asmtok.__len__() >= 3:
                if asmtok.__len__() > 3:
                    if asmtok[3][0] != ";":
                        asm_error("Additional arguments to this instruction type are not allowed")
                rA_present = asmtok[1] in reg
                rB_present = asmtok[2] in reg
                if rA_present == False:
                    asm_error("Invalid register \"" + asmtok[1] + "\"")
                if rB_present == False:
                    asm_error("Invalid register \"" + asmtok[2] + "\"")
                rA = reg[asmtok[1]]
                rB = reg[asmtok[2]]
                writebin([instr_info[1], (rA << 4) | rB])
                pc += 2
                fpc += 2
            else:
                asm_error("2 registers are needed for this instruction type")
        if instr_info[0] == 8:
            writebin([0, 0])
            pc += 2
            fpc += 2
        if instr_info[0] == 9:
            if asmtok.__len__() >= 2:
                if asmtok.__len__() > 2:
                    if asmtok[2][0] != ";":
                        asm_error("Additional arguments to this instruction type are not allowed")
                immval = convert_num(asmtok[1], 2, 2).to_bytes(2, 'little', signed=False)
                writebin([9, instr_info[1] << 4, immval[0], immval[1]])
                pc += 4
                fpc += 4
            else:
                asm_error("1 immediate value/address is needed for this instruction type")
        if instr_info[0] == 10:
            if asmtok.__len__() >= 2:
                if asmtok.__len__() > 2:
                    if asmtok[2][0] != ";":
                        asm_error("Additional arguments to this instruction type are not allowed")
                rA_present = asmtok[1] in reg
                if not rA_present:
                    asm_error("Invalid register \"" + asmtok[1] + "\"")
                rA = reg[asmtok[1]]
                writebin([9, (instr_info[1] << 4) | rA])
                pc += 2
                fpc += 2
            else:
                asm_error("1 register is needed for this instruction type")
        if instr_info[0] == 11:
            writebin([9, instr_info[1] << 4])
            pc += 2
            fpc += 2
        if instr_info[0] == 12:
            if asmtok.__len__() >= 3:
                if asmtok.__len__() > 3:
                    if asmtok[3][0] != ";":
                        asm_error("Additional arguments to this instruction type are not allowed")
                rA_present = asmtok[2] in reg
                if not rA_present:
                    asm_error("Invalid register \"" + asmtok[2] + "\"")
                rA = reg[asmtok[2]]
                immval = convert_num(asmtok[1], 2, 2).to_bytes(2, 'little', signed=False)
                writebin([9, (instr_info[1] << 4) | rA, immval[0], immval[1]])
                pc += 4
                fpc += 4
            else:
                asm_error("1 immediate value/address and 1 register are needed for this instruction type")
        if instr_info[0] == 13:
            if asmtok.__len__() >= 3:
                if asmtok.__len__() > 3:
                    if asmtok[3][0] != ";":
                        asm_error("Additional arguments to this instruction type are not allowed")
                rA_present = asmtok[1] in reg
                if not rA_present:
                    asm_error("Invalid register \"" + asmtok[1] + "\"")
                rA = reg[asmtok[1]]
                immval = convert_num(asmtok[2], 2, 2).to_bytes(2, 'little', signed=False)
                writebin([9, (instr_info[1] << 4) | rA, immval[0], immval[1]])
                pc += 4
                fpc += 4
            else:
                asm_error("1 immediate value/address are needed for this instruction type")

with open(sys.argv[2], "wb") as bin_file:
    bin_file.write(bytearray(bin_code))

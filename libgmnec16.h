/*

Copyright (c) 2022 GalaxianMonster

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

*/

#ifndef LIBGMNEC16_HEADER
#define LIBGMNEC16_HEADER

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdint.h>

/*
 * NEC 16 Specification
 *
 *    RAM: 64 KiB (fixed)
 *    Opcodes: 19
 *    Registers: 16
 *
 *
 */

#define GM_NEC16_ACCU 0
#define GM_NEC16_INDEX 1
#define GM_NEC16_CONDRES 2
#define GM_NEC16_PC 15

#define GM_NEC16_ADDRINVALID -3
#define GM_NEC16_UNKNOWN_ERROR -1

typedef int(*GM_NEC16_BusWriteFunc)(void*, uint16_t, uint8_t);
typedef int(*GM_NEC16_BusReadFunc)(void*, uint16_t, uint8_t*);

typedef struct __GM_NEC16
{
        GM_NEC16_BusWriteFunc bus_write;
        GM_NEC16_BusReadFunc bus_read;
        void* data;
        uint16_t regs[0x10]; /* 16 registers */
} GM_NEC16;

typedef struct __GM_NEC16_INSTR
{

        uint8_t opcode;
        uint8_t regA;
        uint8_t regB;
        uint16_t immval;
        uint8_t secondbyte;

} GM_NEC16_Instr;

int gmnec16_eops(GM_NEC16* nec, GM_NEC16_Instr instr)
{
        uint8_t realregB = instr.secondbyte & 0xf;
        switch(instr.regA)
        {
                case 0x0:
                        break;

                case 0x1:
                        if(nec->regs[instr.regB] == nec->regs[realregB])
                        {
                                nec->regs[GM_NEC16_CONDRES] = 0;
                        }
                        else
                        {
                                nec->regs[GM_NEC16_CONDRES] = 1;
                        }
                        break;

                case 0x2:
                        if(nec->regs[instr.regB] > nec->regs[realregB])
                        {
                                nec->regs[GM_NEC16_CONDRES] = 0;
                        }
                        else
                        {
                                nec->regs[GM_NEC16_CONDRES] = 1;
                        }
                        break;

                case 0x3:
                        if(nec->regs[instr.regB] < nec->regs[realregB])
                        {
                                nec->regs[GM_NEC16_CONDRES] = 0;
                        }
                        else
                        {
                                nec->regs[GM_NEC16_CONDRES] = 1;
                        }
                        break;

                default:
                        break;
        }
        return 0;
}

int gmnec16_jmp(GM_NEC16* nec, GM_NEC16_Instr instr)
{
        if(nec->regs[GM_NEC16_CONDRES] == 0)
        {
                nec->regs[GM_NEC16_PC] = nec->regs[instr.regA];
        }
        return 0;
}

int gmnec16_gm(GM_NEC16* nec, GM_NEC16_Instr instr)
{
        int bus_stat = 0;
        uint8_t bus_byte;
        bus_stat = nec->bus_read(nec->data, nec->regs[GM_NEC16_INDEX], &bus_byte);
        if(bus_stat < 0)
        {
                return bus_stat;
        }
        nec->regs[instr.regA] = bus_byte;
        return 0;
}

int gmnec16_sm(GM_NEC16* nec, GM_NEC16_Instr instr)
{
        int bus_stat = 0;
        uint8_t bus_byte = (uint8_t)(nec->regs[instr.regA] & 0xff);
        bus_stat = nec->bus_write(nec->data, nec->regs[GM_NEC16_INDEX], bus_byte);
        if(bus_stat < 0)
        {
                return bus_stat;
        }
        return 0;
}

int gmnec16_or(GM_NEC16* nec, GM_NEC16_Instr instr)
{
        nec->regs[instr.regA] |= instr.immval;
        return 0;
}

int gmnec16_orr(GM_NEC16* nec, GM_NEC16_Instr instr)
{
        nec->regs[instr.regA] |= nec->regs[instr.regB];
        return 0;
}

int gmnec16_and(GM_NEC16* nec, GM_NEC16_Instr instr)
{
        nec->regs[instr.regA] &= nec->regs[instr.regB];
        return 0;
}

int gmnec16_xor(GM_NEC16* nec, GM_NEC16_Instr instr)
{
        nec->regs[instr.regA] ^= nec->regs[instr.regB];
        return 0;
}

int gmnec16_not(GM_NEC16* nec, GM_NEC16_Instr instr)
{
        nec->regs[instr.regA] = ~(nec->regs[instr.regA]);
        return 0;
}

int gmnec16_shl(GM_NEC16* nec, GM_NEC16_Instr instr)
{
        nec->regs[instr.regA] <<= nec->regs[instr.regB];
        return 0;
}

int gmnec16_shr(GM_NEC16* nec, GM_NEC16_Instr instr)
{
        nec->regs[instr.regA] >>= nec->regs[instr.regB];
        return 0;
}

int gmnec16_add(GM_NEC16* nec, GM_NEC16_Instr instr)
{
        nec->regs[instr.regA] += nec->regs[instr.regB];
        return 0;
}

int gmnec16_sub(GM_NEC16* nec, GM_NEC16_Instr instr)
{
        nec->regs[instr.regA] -= nec->regs[instr.regB];
        return 0;
}

int gmnec16_mul(GM_NEC16* nec, GM_NEC16_Instr instr)
{
        nec->regs[instr.regA] *= nec->regs[instr.regB];
        return 0;
}

int gmnec16_div(GM_NEC16* nec, GM_NEC16_Instr instr)
{
        nec->regs[instr.regA] /= nec->regs[instr.regB];
        return 0;
}

int gmnec16_mod(GM_NEC16* nec, GM_NEC16_Instr instr)
{
        nec->regs[instr.regA] %= nec->regs[instr.regB];
        return 0;
}

typedef int(*gmnec16_opf)(GM_NEC16*, GM_NEC16_Instr);

int gmnec16_instr_step(GM_NEC16* nec)
{

        if(nec->regs[GM_NEC16_PC] == 0xffff)
        {
                return GM_NEC16_ADDRINVALID;
        }

        #define check(r) if((r) < 0) { return (r); }
        uint8_t instr0 = 0;
        uint8_t instr1 = 0;

        check(nec->bus_read(nec->data, nec->regs[GM_NEC16_PC], &instr0));
        check(nec->bus_read(nec->data, nec->regs[GM_NEC16_PC] + 1, &instr1));

        GM_NEC16_Instr instr;
        instr.opcode = (instr0 & 0xf0) >> 4;
        instr.regA = instr0 & 0xf;
        instr.regB = (instr1 & 0xf0) >> 4;
        instr.immval = (((uint16_t)instr0 & 0x0f) << 8) | (uint16_t)instr1;
        instr.secondbyte = instr1;

        gmnec16_opf opfs[] = {

                gmnec16_eops, // 0 (with 4 opcodes)
                gmnec16_jmp, // 1
                gmnec16_gm, // 2
                gmnec16_sm, // 3
                gmnec16_or, // 4
                gmnec16_orr, // 5
                gmnec16_and, // 6
                gmnec16_xor, // 7
                gmnec16_not, // 8
                gmnec16_shl, // 9
                gmnec16_shr, // 10
                gmnec16_add, // 11
                gmnec16_sub, // 12
                gmnec16_mul, // 13
                gmnec16_div, // 14
                gmnec16_mod, // 15

        };

        nec->regs[GM_NEC16_PC] += 2;

        return opfs[instr.opcode](nec, instr);

        #undef check
}

#ifdef __cplusplus
}
#endif

#endif

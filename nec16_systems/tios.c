/* TIOS, a simple I/O system for NEC16 */

#include <libgmnec16.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

/* addr 0 - exit, addr 1 - input, addr 2 - output */
/* 32 KiB ROM starts at addr 3 */
/* addr (32 * 1024 + 3) to addr (64 * 1024 - 1) are the address space for RAM */

int g_DEBUG_ENABLED = 0;
#define debugexec(f) if(g_DEBUG_ENABLED == 1) { f; }

typedef struct __COMPUTER
{
    GM_NEC16 cpu;
    uint8_t memory[0x10000 - 3];
    uint8_t exit_flag;
} computer_t;

int tios_mmu_read(void* data, uint16_t addr, uint8_t* ib)
{
    computer_t com = *(computer_t*)(data);

    debugexec(printf("\n[READ_REQ] >> addr:%04X\n", addr));
    switch(addr)
    {
        case 0: return GM_NEC16_ADDRINVALID;
        case 2: return GM_NEC16_ADDRINVALID;
        case 1:
            scanf("%c", (char*)ib);
            break;
        default:
            debugexec(printf("\n[READ_REQ] >> ib:%02X\n", com.memory[addr - 3]));
            *ib = com.memory[addr - 3];
            break;
    }
    return 0;
}

char* get_error_type(int errcode)
{

    switch(errcode)
    {
        case GM_NEC16_ADDRINVALID:
            return "Address invalid";
        case GM_NEC16_INSTRUCTIONINVALID:
            return "Instruction invalid";
        default:
            return "Unknown error";
    }

}

int tios_mmu_write(void* data, uint16_t addr, uint8_t ob)
{
    computer_t* comptr = (computer_t*)(data);

    debugexec(printf("\n[WRITE_REQ] >> addr:%04X ob:%02X\n", addr, ob));
    switch(addr)
    {
        case 0: comptr->exit_flag = 1; break;
        case 2: printf("%c", ob); break;
        case 1: return GM_NEC16_ADDRINVALID;
        default:
            comptr->memory[addr - 3] = ob;
            break;
    }
    return 0;
}

int loadrom(computer_t* com, const char* filename)
{
    FILE* fptr = fopen(filename, "rb");

    if(fptr == NULL)
    {
        printf("[ERROR] >> Error opening '%s'\n", filename);
        return -1;
    }
    fread(com->memory, 1, 32*1024, fptr);
    fclose(fptr);
    return 0;
}

int main(int args, char** argv)
{
    int instr_counts = 0;
    int instr_count = 0;
    int instr_lim_enabled = 0;
    computer_t com;
    com.exit_flag = 0;
    com.cpu.bus_read = tios_mmu_read;
    com.cpu.bus_write = tios_mmu_write;
    com.cpu.data = (void*)&com;
    com.cpu.regs[GM_NEC16_PC] = 3;

    if(args < 2)
    {
        printf("No file to execute.\n");
        return 0;
    }
    if(args >= 3)
    {
        if(strcmp("-d", argv[2]) == 0)
        {
            g_DEBUG_ENABLED = 1;
        }
    }
    if(args >= 4)
    {
        instr_counts = atoi(argv[3]);
        instr_lim_enabled = 1;
    }

    if(loadrom(&com, argv[1]) < 0)
    {

        return 1;

    }

    while(com.exit_flag != 1)
    {
        int inres;

        if(instr_lim_enabled)
        {
            instr_count += 1;
            if(instr_count >= instr_counts)
            {
                break;
            }
        }
        inres = gmnec16_instr_step(&(com.cpu));

        if(com.cpu.regs[GM_NEC16_PC] >= (32 * 1024 + 3))
        {
            printf("[ERROR] >> Attempted to execute code from RAM\n");
            com.exit_flag = 1;
        }
        if(inres < 0)
        {
            printf("[ERROR] >> Received error code %d, '%s'\n", inres, get_error_type(inres));
            com.exit_flag = 1;
        }
    }

    return 0;
}

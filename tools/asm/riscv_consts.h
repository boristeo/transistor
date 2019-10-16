#ifndef RISCV_RISCV_CONSTS_H
#define RISCV_RISCV_CONSTS_H

#include <stdint.h>


typedef uint8_t byte_t;
typedef uint16_t hword_t;
typedef uint32_t word_t;
typedef uint64_t dword_t;

typedef uint64_t reg_t;
typedef int64_t sreg_t;
#define REG_LEN 64
#define REG_MAX 0xffffffffffffffffllu
#define REG_MAXS 0x7fffffffffffffffllu
#define REG_MINS 0x8000000000000000llu
#define SREG_MAX 0xefffffffffffffffllu
typedef uint16_t regi_t;
typedef uint32_t instr_t;
#define INSTR_LEN 32
#define INSTR_LEN_B 4

#define VADDR_LEN 32
#define VADDR_LEN_B 4
#define VADDR_MAX 0xffffffffllu

#define PADDR_LEN 32
#define PADDR_LEN_B 4
#define PADDR_MAX 0xffffffffllu

/*(RISC-V V2.2)*/
/******* MASKS ********/
#define BYTE_MASK       0xffllu
#define BYTE_LEN        8
#define BYTE_LEN_B      1
#define HWORD_MASK      0xffffllu
#define HWORD_LEN       16
#define HWORD_LEN_B     2
#define WORD_MASK       0xffffffffllu
#define WORD_MAXS       0x7fffffffllu
#define WORD_MINS       0x80000000llu
#define WORD_LEN        32
#define WORD_LEN_B      4
#define DWORD_MASK      0xffffffffffffffffllu
#define DWORD_LEN       64
#define DWORD_LEN_B     8

#define OPCODE_MASK     0x7fu
#define OPCODE_OFFSET   0
#define OPCODE_LENGTH   7

#define RD_MASK         0xf80u
#define RD_OFFSET       7
#define RD_LENGTH       5

#define FUNCT3_MASK     0x7000u
#define FUNCT3_OFFSET   12
#define FUNCT3_LENGTH   3

#define RS1_MASK        0xf8000u
#define RS1_OFFSET      15
#define RS1_LENGTH      5

#define RS2_MASK        0x1f00000u
#define RS2_OFFSET      20
#define RS2_LENGTH      5

#define SHAMT_MASK      0x3f00000u
#define SHAMT_OFFSET    20
#define SHAMT_LENGTH    6

#define SHEAD_MASK      0xfc000000u
#define SHEAD_OFFSET    26
#define SHEAD_LENGTH    6

#define SHAMTW_MASK     0x1f00000u
#define SHAMTW_OFFSET   20
#define SHAMTW_LENGTH   5

#define SHEADW_MASK     0xfe000000u
#define SHEADW_OFFSET   25
#define SHEADW_LENGTH   7

/* R */
#define R_FUNCT7_MASK   0xfe000000u
#define R_FUNCT7_OFFSET 25
#define R_FUNCT7_LENGTH 7

/* I */
#define I_IMMB0_MASK    0xfff00000u
#define I_IMMB0_OFFSET  20
#define I_IMMB0_LENGTH  12


/* S */
#define S_IMM40_MASK    0xf80u
#define S_IMM40_OFFSET  7
#define S_IMM40_LENGTH  5

#define S_IMMB5_MASK    0xfe000000u
#define S_IMMB5_OFFSET  25
#define S_IMMB5_LENGTH  7

/* B */
#define B_IMMBB_MASK    0x80u
#define B_IMMBB_OFFSET  7
#define B_IMMBB_LENGTH  1

#define B_IMM41_MASK    0xf00u
#define B_IMM41_OFFSET  8
#define B_IMM41_LENGTH  4

#define B_IMMA5_MASK    0x7e000000u
#define B_IMMA5_OFFSET  25
#define B_IMMA5_LENGTH  6

#define B_IMMCC_MASK    0x80000000u
#define B_IMMCC_OFFSET  31
#define B_IMMCC_LENGTH  1

/* U */
#define U_IMMVC_MASK    0xfffff000u
/* DO NOT USE - IMMVC ALREADY ALIGNED
#define U_IMMVC_OFFSET  12
#define U_IMMVC_LENGTH  20
*/

/* J */
#define J_IMMJC_MASK    0xff000u
#define J_IMMJC_OFFSET  12
#define J_IMMJC_LENGTH  8

#define J_IMMBB_MASK    0x100000u
#define J_IMMBB_OFFSET  20
#define J_IMMBB_LENGTH  1

#define J_IMMA1_MASK    0x7fe00000u
#define J_IMMA1_OFFSET  21
#define F_IMMA1_LENGTH  10

#define J_IMMKK_MASK    0x80000000u
#define J_IMMKK_OFFSET  31
#define J_IMMKK_LENGTH   1


/*
   31 30 29 28|27 26 25 24|23 22 21 20|19 18 17 16|15 14 13 12|11 10 09 08|07 06 05 04|03 02 01 00
   -----------|-----------|-----------|-----------|-----------|-----------|-----------|-----------
R  f7 f7 f7 f7|f7 f7 f7 s2|s2 s2 s2 s2|s1 s1 s1 s1|s1 f3 f3 f3|rd rd rd rd|rd op op op|op op op op
I  B0 B0 B0 B0|B0 B0 B0 B0|B0 B0 B0 B0|s1 s1 s1 s1|s1 f3 f3 f3|rd rd rd rd|rd op op op|op op op op
S  B5 B5 B5 B5|B5 B5 B5 s2|s2 s2 s2 s2|s1 s1 s1 s1|s1 f3 f3 f3|40 40 40 40|40 op op op|op op op op
B  CC A5 A5 A5|A5 A5 A5 s2|s2 s2 s2 s2|s1 s1 s1 s1|s1 f3 f3 f3|41 41 41 41|BB op op op|op op op op
U  VC VC VC VC|VC VC VC VC|VC VC VC VC|VC VC VC VC|VC VC VC VC|rd rd rd rd|rd op op op|op op op op
J  KK A1 A1 A1|A1 A1 A1 A1|A1 A1 A1 BB|JC JC JC JC|JC JC JC JC|rd rd rd rd|rd op op op|op op op op

 */



#endif

#!/usr/bin/env python3
"""
assembler.py - Hack assembler (Nand to Tetris, ETCCNT301 capstone, Part B)
Name: Sujal Rana | Roll: 2501730343 | K = 41 | K mod 3 = 2

Usage:  python assembler.py InputFile.asm      ->  writes InputFile.hack

Pass 1: strip comments/whitespace, record (LABEL) -> ROM address.
Pass 2: translate A- and C-instructions to 16-bit binary; new variables get RAM 16, 17, ...
Extra feature (K mod 3 = 2): print a WARNING if the same label is declared more than once.
"""
import os
import sys

COMP = {
    "0": "0101010", "1": "0111111", "-1": "0111010",
    "D": "0001100", "A": "0110000", "!D": "0001101", "!A": "0110001",
    "-D": "0001111", "-A": "0110011", "D+1": "0011111", "A+1": "0110111",
    "D-1": "0001110", "A-1": "0110010", "D+A": "0000010", "D-A": "0010011",
    "A-D": "0000111", "D&A": "0000000", "D|A": "0010101",
    "M": "1110000", "!M": "1110001", "-M": "1110011", "M+1": "1110111",
    "M-1": "1110010", "D+M": "1000010", "D-M": "1010011", "M-D": "1000111",
    "D&M": "1000000", "D|M": "1010101",
}
# accept commutative spellings too (A+D, M+D, A&D, ...)
for _k, _v in list(COMP.items()):
    if len(_k) == 3 and _k[1] in "+&|" and _k[0] != _k[2]:
        COMP.setdefault(_k[2] + _k[1] + _k[0], _v)

JUMP = {"": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
        "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"}

SYMBOLS = {"SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
           "SCREEN": 16384, "KBD": 24576}
SYMBOLS.update({f"R{i}": i for i in range(16)})


def clean(line):
    """Remove comments and all whitespace."""
    return line.split("//", 1)[0].replace(" ", "").replace("\t", "").strip()


def dest_bits(d):
    return f"{int('A' in d)}{int('D' in d)}{int('M' in d)}"


def first_pass(lines):
    """Return (symbol table, list of (source_line_no, instruction))."""
    symbols = dict(SYMBOLS)
    labels_seen = {}          # label -> (source line, ROM address) of first declaration
    instructions = []
    for lineno, raw in enumerate(lines, start=1):
        line = clean(raw)
        if not line:
            continue
        if line.startswith("(") and line.endswith(")"):
            name = line[1:-1]
            if name in labels_seen:
                prev_line, prev_addr = labels_seen[name]
                print(f"WARNING: label '{name}' declared more than once "
                      f"(line {lineno}, ROM address {len(instructions)}; "
                      f"first declared on line {prev_line}, ROM address {prev_addr}). "
                      f"Keeping the first declaration.", file=sys.stderr)
            else:
                labels_seen[name] = (lineno, len(instructions))
                symbols[name] = len(instructions)
        else:
            instructions.append((lineno, line))
    return symbols, instructions


def second_pass(symbols, instructions):
    out = []
    next_var = 16
    for lineno, ins in instructions:
        if ins.startswith("@"):
            sym = ins[1:]
            if sym.isdigit():
                value = int(sym)
            else:
                if sym not in symbols:
                    symbols[sym] = next_var
                    next_var += 1
                value = symbols[sym]
            out.append(format(value, "016b"))
        else:
            dest, comp, jump = "", ins, ""
            if "=" in comp:
                dest, comp = comp.split("=", 1)
            if ";" in comp:
                comp, jump = comp.split(";", 1)
            if comp not in COMP or jump not in JUMP:
                sys.exit(f"Error on line {lineno}: cannot parse '{ins}'")
            out.append("111" + COMP[comp] + dest_bits(dest) + JUMP[jump])
    return out


def main():
    if len(sys.argv) != 2 or not sys.argv[1].endswith(".asm"):
        sys.exit("Usage: python assembler.py InputFile.asm")
    path = sys.argv[1]
    with open(path) as f:
        lines = f.read().splitlines()
    symbols, instructions = first_pass(lines)
    binary = second_pass(symbols, instructions)
    out_path = os.path.splitext(path)[0] + ".hack"
    with open(out_path, "w") as f:
        f.write("\n".join(binary) + "\n")
    print(f"Wrote {len(binary)} instructions to {out_path}")


if __name__ == "__main__":
    main()

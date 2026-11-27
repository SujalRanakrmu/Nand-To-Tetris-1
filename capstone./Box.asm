// Box.asm - Capstone "Make the Computer Draw a Box"
// Name: Sujal Rana | Roll: 2501730343 | K = 41
// Box: starts at row 41, height 20 rows (41..60), width 32 px = 2 words/row, left edge.
// Key pressed (KBD != 0) -> black (-1); no key -> white (0).
// Start address = SCREEN + 32*41 = 16384 + 1312 = 17696
//
// To change the box:  row  -> change 1312 (= 32 * startRow)
//                     height -> change @20      width -> change @2 (words)

(LOOP)
    @KBD
    D=M
    @BLACK
    D;JNE           // key pressed -> black
    @color
    M=0             // no key -> white
    @PAINT
    0;JMP
(BLACK)
    @color
    M=-1
(PAINT)
    @1312           // 32 * 41
    D=A
    @SCREEN
    D=D+A
    @addr           // addr = address of first word of current row
    M=D
    @20             // height in rows
    D=A
    @rows
    M=D
(ROW)
    @2              // width in words
    D=A
    @cols
    M=D
    @addr
    D=M
    @p              // p = pointer to current word
    M=D
(COL)
    @color
    D=M
    @p
    A=M
    M=D             // RAM[p] = color
    @p
    M=M+1
    @cols
    M=M-1
    D=M
    @COL
    D;JGT           // more words in this row?
    @32             // move to next screen row
    D=A
    @addr
    M=D+M
    @rows
    M=M-1
    D=M
    @ROW
    D;JGT           // more rows?
    @LOOP           // done painting; poll keyboard again
    0;JMP

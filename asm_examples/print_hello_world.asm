; Set jlabel starting pc to 3 (for TIOS)
.setapc 3

ujmp ::prog_main

.jlabel exit
set idx, 0
sm idx

.jlabel print
gm acc
set r14, 0
eq acc, r14
cjmp ::__print_end
cp r14, idx
set idx, 2
sm acc
cp idx, r14
set r14, 1
add idx, r14
ujmp ::print

.jlabel __print_end
ret

.jlabel mystring
.string "Hello, world!\n"
.byte 0

.jlabel prog_main
set sp, 0x9000
set idx, ::mystring
calla ::print
calla ::exit

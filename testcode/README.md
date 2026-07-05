# Lab 6 Official Test Code

These files were extracted from `CODExp.rar`.

## Files

- `rv32_sc_sim.dat` / `rv32_sc_sim.asm`: demo single-cycle CPU simulation test program.
- `rv32_pl_sim.dat` / `rv32_pl_sim.asm`: demo pipeline CPU simulation test program.
- `Test_30_Instr.dat` / `Test_30_Instr.asm`: 30-instruction target CPU test program.
- `riscv_sidascsorting_sim.dat` / `riscv_sidascsorting_sim.asm`: student-id ascending-sort simulation program.

## Mapping To Required Tests

- Test 1: target single-cycle CPU basic simulation test: use `rv32_sc_sim.dat` as the reference/demo program, or `Test_30_Instr.dat` if the requirement names the 30-instruction target test.
- Test 2: target pipeline CPU 30-instruction simulation test: use `Test_30_Instr.dat`.
- Test 3: target single-cycle CPU student-id sorting simulation test: use `riscv_sidascsorting_sim.dat`.
- Test 4: target pipeline CPU student-id sorting simulation test: use `riscv_sidascsorting_sim.dat`.

The original extracted paths are kept under `CODExp/testcode/` for traceability.

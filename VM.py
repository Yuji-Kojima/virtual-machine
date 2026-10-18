LOAD_A = 0x01
LOAD_B = 0x02
LOAD_C = 0x03
LOAD_D = 0x04
HALT = 0xFF



class main():
    def __init__(self,pg):
        self.program = bytes(pg)
        self.pc = 0
        self.registers = [0, 0, 0, 0]
        self.z = False
        self.c = False
        self.running = True

    def read(self):
        if self.pc >= len(self.program):
            self.running = False
            return 0
        value = self.program[self.pc]
        self.pc += 1
        return value

    def run(self,debug=False):
        while self.running:
            opcode = self.read()
            if debug:
                print(f"PC: {self.pc-1}, Opcode: {opcode}, Registers: {self.registers}, Z: {self.z}, C: {self.c}")

            if opcode == LOAD_A:
                self.registers[0] = self.read()

            elif opcode == LOAD_B:
                self.registers[1] = self.read()

            elif opcode == LOAD_C:
                self.registers[2] = self.read()

            elif opcode == LOAD_D:
                self.registers[3] = self.read()

            elif opcode == HALT:
                self.running = False

M=main([0x01,0x03,0x04,0x04,0xFF])
M.run(debug=True)

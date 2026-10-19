LOAD_A = 0x01
LOAD_B = 0x02
LOAD_C = 0x03
LOAD_D = 0x04
ADD_A = 0x05
ADD_B = 0x06
ADD_C = 0x07
ADD_D = 0x08
SUB_A = 0x09
SUB_B = 0x0A
SUB_C = 0x0B
SUB_D = 0x0C

HALT = 0xFF



class VM():
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
    
    def to_u8(self,value):
        if value > 0xFF or value < 0:
            self.c = True
        else:
            self.c = False
        new_value=value & 0xFF
        if new_value == 0:
            self.z = True
        else:
            self.z = False
        return new_value
    
    def run(self,debug=False):
        while self.running:
            opcode = self.read()
            if debug:
                print(f"PC: {self.pc-1}, Opcode: {opcode}, Registers: {self.registers}, Z: {self.z}, C: {self.c}")

            if opcode == LOAD_A:
                self.registers[0] = self.to_u8(self.read())

            elif opcode == LOAD_B:
                self.registers[1] = self.to_u8(self.read())

            elif opcode == LOAD_C:
                self.registers[2] = self.to_u8(self.read())

            elif opcode == LOAD_D:
                self.registers[3] = self.to_u8(self.read())

            elif opcode == ADD_A:
                self.registers[0] = self.to_u8(self.registers[0] + self.read())

            elif opcode == ADD_B:
                self.registers[1] = self.to_u8(self.registers[1] + self.read())

            elif opcode == ADD_C:
                self.registers[2] = self.to_u8(self.registers[2] + self.read())

            elif opcode == ADD_D:
                self.registers[3] = self.to_u8(self.registers[3] + self.read())

            elif opcode == SUB_A:
                self.registers[0] = self.to_u8(self.registers[0] - self.read())

            elif opcode == SUB_B:
                self.registers[1] = self.to_u8(self.registers[1] - self.read())

            elif opcode == SUB_C:
                self.registers[2] = self.to_u8(self.registers[2] - self.read())

            elif opcode == SUB_D:
                self.registers[3] = self.to_u8(self.registers[3] - self.read())

            elif opcode == HALT:
                self.running = False

vm=VM([0x01,0xFF,0x05,0xFF,0xFF])
vm.run(debug=True)


  
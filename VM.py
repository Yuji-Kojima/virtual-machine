NOP = 0x00
LOAD = 0x01
ADD = 0x02
SUB = 0x03


OUT = 0x0C
JMP = 0x0D
JZ = 0x0E
JNZ = 0x0F
JC = 0x10
JNC = 0x11
CMP = 0x12

HALT = 0xFF

def out_number(value):
    print(value)

def out_char(value):
    print(chr(value), end="")

class Error(Exception):
    pass
class VM():
    def __init__(self,pg):
        self.program = bytes(pg)
        self.pc = 0
        self.registers = [0, 0, 0, 0]
        self.z = False
        self.c = False
        self.running = True
        self.error = None
        self.ports={
            0 : out_number,
            1 : out_char
        }

    def read(self):
        if self.pc >= len(self.program):
            raise Error(f"プログラムの終わりを超えました (PC={self.pc})")

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
    def reg(self,r):
        if r < 0 or r >= len(self.registers):
            raise Error(f"レジスタ番号が不正です: {r} (PC={self.pc})")
        return r

    
    def run(self):
        while self.running:
            opcode = self.read()
            if opcode == LOAD:
                r = self.reg(self.read())
                n = self.read()
                self.registers[r] = self.to_u8(n)

            elif opcode == ADD:
                r = self.reg(self.read())
                n = self.read()
                self.registers[r] = self.to_u8(self.registers[r] + n)

            elif opcode == SUB:
                r = self.reg(self.read())
                n = self.read()
                self.registers[r] = self.to_u8(self.registers[r] - n)

            elif opcode == OUT:
                port = self.read()
                r = self.reg(self.read())
                if port not in self.ports:
                    raise Error(f"未定義のポートです: {port}")
                self.ports[port](self.registers[r])
                



            elif opcode == JMP:
                addr = self.read()
                self.pc = addr

            elif opcode == JZ:
                addr = self.read()
                if self.z:
                    self.pc = addr

            elif opcode == JNZ:
                addr = self.read()
                if not self.z:
                    self.pc = addr

            elif opcode == JC:
                addr = self.read()
                if self.c:
                    self.pc = addr

            elif opcode == JNC:
                addr = self.read()
                if not self.c:
                    self.pc = addr
            elif opcode == CMP:
                r = self.reg(self.read())
                n = self.read()
                self.to_u8(self.registers[r] - n)

            elif opcode == HALT:
                self.running = False

vm=VM([0x01,0,104,
       0x0C,1,0,
       0x01,0,101,
       0x0C,1,0,
       0x01,0,108,
       0x0C,1,0,
       0x01,0,108,
       0x0C,1,0,
       0x01,0,111,
       0x0C,1,0,
       0x01,0,119,
       0x0C,1,0,
       0x01,0,111,
       0x0C,1,0,
       0x01,0,114,
       0x0C,1,0,
       0x01,0,108,
       0x0C,1,0,
       0x01,0,100,
       0x0C,1,0,

       0xFF])
vm.run()


  
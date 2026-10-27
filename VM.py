from opcodes import * #opcodes.pyから命令集を持ってくるよ～～～
import devices


class VMError(Exception):
    pass
class VM():
    def __init__(self,pg, load=0, entry=0):
        
        self.memory = bytearray(0x10000)
        self.memory[load:load + len(pg)] = bytes(pg)

        self.sp = 0xFFFF 
        self.pc = entry
        self.registers = [0, 0, 0, 0]
        self.z = False
        self.c = False
        self.running = True
        self.ports = devices.ports
        self.d_update_count = 0

        devices.u.memory=self.memory
        
    
    def read(self):
        if self.pc >= 0x10000:
            raise VMError(f"プログラムの終わりを超えました (PC={self.pc})")

        value = self.memory[self.pc]
        self.pc += 1
        return value
    def read16(self):
        a=self.read()
        b=self.read()
        addr = b * 256 + a
        return addr
    
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
    def push(self,v):
        if self.sp < 0:
            raise VMError("スタックオーバーフロー")
        self.memory[self.sp] = v & 0xFF # 入れる値の方だからFF
        self.sp -= 1

    def pop(self):
        if self.sp >= 0xFFFF: # 番地の方だからFFFF
            raise VMError("スタックが空です")
        self.sp += 1
        return self.memory[self.sp]            

    def reg(self,r):
        if r < 0 or r >= len(self.registers):
            raise VMError(f"レジスタ番号が不正です: {r} (PC={self.pc})")
        return r

    
    def run(self,debug=False):
        while self.running:
            opcode = self.read()

            if debug:
                print(f"PC: {self.pc-1}, Opcode: {opcode}, Registers: {self.registers}, Z: {self.z}, C: {self.c}")

            if opcode == NOP: 
                pass

            elif opcode == LOAD:
                r = self.reg(self.read())
                n = self.read()
                self.registers[r] = n

            elif opcode == ADD:
                r = self.reg(self.read())
                n = self.read()
                self.registers[r] = self.to_u8(self.registers[r] + n)

            elif opcode == SUB:
                r = self.reg(self.read())
                n = self.read()
                self.registers[r] = self.to_u8(self.registers[r] - n)

            elif opcode == LOADM:
                r = self.reg(self.read())
                addr = self.read16()
                self.registers[r] = self.memory[addr]

            elif opcode == STOREM:
                r = self.reg(self.read())
                addr = self.read16()
                self.memory[addr] = self.registers[r]

            elif opcode == MOVM:
                addr_receive = self.read16()
                addr_send = self.read16()
                self.memory[addr_receive] = self.memory[addr_send]

            elif opcode == MOV:
                reg_receive = self.reg(self.read())
                reg_send = self.reg(self.read())
                self.registers[reg_receive] = self.registers[reg_send]

            elif opcode == INC:
                r = self.reg(self.read())
                self.registers[r] = self.to_u8(self.registers[r] + 1)

            elif opcode == DEC:
                r = self.reg(self.read())
                self.registers[r] = self.to_u8(self.registers[r] - 1)

            elif opcode == PUSH:
                r = self.reg(self.read())
                self.push(self.registers[r])

            elif opcode == POP:
                r = self.reg(self.read())
                self.registers[r] = self.pop()

            elif opcode == IN:
                port = self.read()
                r = self.reg(self.read())
                if port not in self.ports or self.ports[port][0] is None:
                    raise VMError(f"未定義のポートです: {port}")
                self.registers[r]  =self.ports[port][0]() & 0xFF

            elif opcode == OUT:
                port = self.read()
                r = self.reg(self.read())
                if port not in self.ports or self.ports[port][1] is None:
                    raise VMError(f"未定義のポートです: {port}")
                self.ports[port][1](self.registers[r])

            elif opcode == JMP:
                addr = self.read16()
                self.pc = addr

            elif opcode == JZ:
                addr = self.read16()
                if self.z:
                    self.pc = addr

            elif opcode == JNZ:
                addr = self.read16()
                if not self.z:
                    self.pc = addr

            elif opcode == JC:
                addr = self.read16()
                if self.c:
                    self.pc = addr

            elif opcode == JNC:
                addr = self.read16()
                if not self.c:
                    self.pc = addr

            elif opcode == CMP:
                r = self.reg(self.read())
                n = self.read()
                self.to_u8(self.registers[r] - n)

            elif opcode == CALL:
                addr = self.read16()
                self.push(self.pc >> 8)
                self.push(self.pc & 0xFF)
                self.pc = addr

            elif opcode == RET:
                lo = self.pop()
                hi = self.pop()
                self.pc = hi * 256 + lo

            elif opcode == LOADI:
                r = self.reg(self.read())
                r_lo = self.reg(self.read())
                r_hi = self.reg(self.read())
                addr = self.registers[r_hi] * 256 + self.registers[r_lo]
                self.registers[r] = self.memory[addr]

            elif opcode == STOREI:
                r = self.reg(self.read())
                r_lo = self.reg(self.read())
                r_hi = self.reg(self.read())
                addr = self.registers[r_hi] * 256 + self.registers[r_lo]
                self.memory[addr] = self.registers[r]

            elif opcode == JMPI:
                r_lo = self.reg(self.read())
                r_hi = self.reg(self.read())
                addr = self.registers[r_hi] * 256 + self.registers[r_lo]
                self.pc = addr

            elif opcode == ADDR:
                r = self.reg(self.read())
                r2 = self.reg(self.read())
                self.registers[r] = self.to_u8(self.registers[r] + self.registers[r2])

            elif opcode == SUBR:
                r = self.reg(self.read())
                r2 = self.reg(self.read())
                self.registers[r] = self.to_u8(self.registers[r] - self.registers[r2])

            elif opcode == CMPR:
                r = self.reg(self.read())
                r2 = self.reg(self.read())
                self.to_u8(self.registers[r] - self.registers[r2])

            elif opcode == AND:
                r = self.reg(self.read())
                n = self.read()
                self.registers[r] = self.to_u8(self.registers[r] & n)

            elif opcode == OR:
                r = self.reg(self.read())
                n = self.read()
                self.registers[r] = self.to_u8(self.registers[r] | n)

            elif opcode == XOR:
                r = self.reg(self.read())
                n = self.read()
                self.registers[r] = self.to_u8(self.registers[r] ^ n)

            elif opcode == NOT:
                r = self.reg(self.read())
                self.registers[r] = self.to_u8(~self.registers[r] & 0xFF)

            elif opcode == SHL:
                r = self.reg(self.read())
                self.registers[r] = self.to_u8(self.registers[r] << 1)

            elif opcode == SHR:
                r = self.reg(self.read())
                v = self.registers[r]
                self.registers[r] = self.to_u8(v >> 1)
                self.c = bool(v & 1)

            elif opcode == MIAO:
                print("M~I~😽~A~O~")
                print("Nyan🐈🌈Nyanyanyanyanyanyanya!")
                print("😸おお")
                print("/*喵喵喵喵😹喵喵喵喵*/")
                print("～にゃ🐈ゃに～")

            elif opcode == LOADLH:
                r_lo = self.reg(self.read())
                r_hi = self.reg(self.read())
                addr_hi = self.read()
                addr_lo = self.read()
                self.registers[r_lo] = addr_lo
                self.registers[r_hi] = addr_hi

            elif opcode == CALZ:
                addr = self.read16()
                if self.z:
                    self.push(self.pc >> 8)
                    self.push(self.pc & 0xFF)
                    self.pc = addr

            elif opcode == CALNZ:
                addr = self.read16()
                if not self.z:
                    self.push(self.pc >> 8)
                    self.push(self.pc & 0xFF)
                    self.pc = addr
                

            elif opcode == DUMP:
                addr_start = self.read16()
                addr_end = self.read16()
                for i in range(addr_start, addr_end):
                   print(f"{i:04X}: {self.memory[i]:02X}")

            elif opcode == HALT:
                self.running = False

            else: raise VMError("ないopcode")

            self.d_update_count += 1
            if self.d_update_count >= 1024:
                devices.u.update()
                self.d_update_count = 0



  
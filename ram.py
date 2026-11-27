memory = bytearray(0x10000)

try:
    with open("data/rom/bios.sema3","rb") as f:
        f.seek(13) 
        body = f.read()
        BIOS = body
        memory[0:len(BIOS)] = BIOS     # 0番地から BIOS をまるごと置く

        
except:
    print("BIOS_LOAD_ERROR")
    exit()


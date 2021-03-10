class CurrentStatus:
    def __init__(self):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @description Constructor initializes all the program status values.
        '''
        self.__pc=0
        self.__opc=0
        self.__ins=0
        self.__addr_mod=""
        self.__opr1="--"
        self.__opr2="--"
        self.__accum=0
        self.__xreg=0
        self.__yreg=0
        self.__sp=0
        self.__stat=0
    
    def set_operand_one(self, operand="--"):
        self.__opr1=operand
    
    def get_ins(self):
        return self.__ins
    
    def set_operand_two(self, operand="--"):
        self.__opr2=operand

    
    def set_PC(self, pc):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @param pc - the program counter
        @description Sets the program counter
        '''
        self.__pc=pc
    def set_OPC(self, opcode):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @param opcode - the current opcode
        @description Sets the opcode
        '''
        self.__opc=opcode
    def set_ins(self, instruction):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @param instruction - the assembler instruction
        @description Sets the instruction
        '''
        self.__ins=instruction
    def set_address_mode(self, address_mode):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @param address_mode - the addressing mode
        @description Sets the addressing mode
        '''
        self.__addr_mod=address_mode
    def set_accum(self, accum):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @param accum - the accumulator
        @description Sets the accumulator
        '''
        self.__accum=accum
    def set_xreg(self,xreg):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @param xreg - the x register
        @description Sets the x register
        '''
        self.__xreg=xreg
    def set_yreg(self,yreg):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @param yreg - the y register
        @description Sets the y register
        '''
        self.__yreg=yreg
    def set_sp(self, sp):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @param sp - the stack pointer
        @description Sets the stack pointer
        '''
        self.__sp=sp
    def set_stat(self, stat):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @param stat - the status register
        @description Sets the status register
        '''
        self.__stat=stat
    def build_info_str(self):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @description Creates a formatted status string for each instruction executed.
        '''
        fmt_string= "{0:>4}{1:>4}{2:>6}{3:>6}{4:>4}{5:>3}{6:>4}{7:>3}{8:>3}{9:>3} {10:0>8b}".format(
                    self.__pc, self.__opc, self.__ins, self.__addr_mod, self.__opr1, self.__opr2,
                    self.__accum, self.__xreg, self.__yreg, self.__sp, self.__stat)
        return fmt_string

    
    

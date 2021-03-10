import utils
from CurrentStatus import CurrentStatus
class system:

    def __init__ (self):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @description The constructor builds the core of the emulator.
        It initializes the registers and main memory, and sets the base
        address for the memory to be above the stack.
        '''
        self.registers=[]
        self.main_mem=bytearray(0x10000)
        self.instruction_operands=[]
        self.instructions=self.__create_ins_table()
        self.program_status=CurrentStatus()
        self.pc_offset=1

        for i in range(6):
            self.registers.append(0)
        
        self.registers[5]=0x1FF
    
    
    def parse_input(self, u_input):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @param u_input - the user input, as a string
        @description parse_input determines what the user wants to do
        based on their input. It also error checks the input, doing nothing if
        the user inputs something invalid.
        '''
        #remove any whitespace first
        u_input=u_input.strip()

        #If user input a clean hex string, they only want to display a memory address
        if(utils.is_hex(u_input)):
            try:
                hex_input=int(u_input,16)
                mem_val=self.main_mem[hex_input]
                self.print_mem_address(u_input,mem_val)
            except IndexError:
                print("Please input a number between 0x0 and 0xFFFF")
                
    
        #If there is a period, they want to see a range of addresses
        elif(u_input.find(".")!=-1 and len(u_input)-1>u_input.find('.')
            and u_input.find(':')==-1 and u_input.find('R')==-1):

            self.print_address_range(u_input)
        
        #If there is a colon, they want to edit some memory addresses
        elif(u_input.find(":")!=-1 and u_input.find('.')==-1
            and u_input.find('R')==-1):

            self.edit_mem_loc(u_input)

        #If there is an R, they want to run a program.
        elif(u_input.find("R")!=-1 and u_input.find(".")==-1
            and u_input.find(':')==-1):

            self.run_program(u_input)
        


    def init_mem_from_file(self,input_obj_file):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @param input_obj_file - the object file that the user wants to load in
        @description Loads in an Intel HEX file, parses it line-by-line,
        and then loads the values into the main memory
        '''
        line=" "
        while(line!=""):
            line=input_obj_file.readline()

            #line had a potential to be empty at end of file
            if(line!=""):
                data=utils.parse_hex_line(line)

                #Check for empty data string, then load it into memory
                if not("" in data):
                    byte_dat=bytearray.fromhex(data[2])
                    for i in range(len(byte_dat)):
                        self.main_mem[data[0]+i]=byte_dat[i]
    

    def print_address_range(self,u_input):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @param u_input - the user's input as a string
        @description Prints a range of memory addresses specified by
        the user
        '''

        index=None
        counter=0
        period_loc=u_input.find('.')

        #get the start and ending addresses
        first_addr=u_input[0:period_loc]
        second_addr=u_input[period_loc+1:]

        try:
            first_addr=int(first_addr,16)
            second_addr=int(second_addr,16)
        except ValueError:
            print ("Invalid input, please only input hex digits")
            return

        index=first_addr

        #print the initial line
        line_str=self.hex_to_fmt_string(first_addr)+"  "
        while(index<=second_addr):

            if (counter<8):

                #add an address to the string
                line_str=line_str+self.hex_to_fmt_string(self.main_mem[index])+" "
                counter=counter+1
                index=index+1
                
            else:
                print(line_str)
                line_str=self.hex_to_fmt_string(index)+"  "
                counter=0
        
        print(line_str)
            
        
    
    def edit_mem_loc(self, u_input):

        '''
        @author Woodlin Smith
        @param self - the emulator object
        @param u_input - the user's input as a string
        @description Overwrites memory starting at the specified address
        '''
        try:
            colon_loc=u_input.find(":")

            start_loc=u_input[0:colon_loc]
            new_addr=u_input[colon_loc+1:]

            start_addr=int(start_loc,16)
            #converts new_addr to bytes
            new_addr=bytearray.fromhex(new_addr)

            index=0
            end_loc=len(new_addr)

            while(index<end_loc):
                current_mem_loc=index+start_addr
                self.main_mem[current_mem_loc]=new_addr[index]
                index=index+1
        except ValueError:
            print ("Invalid input. Please only input hex digits")
    

    def run_program(self, u_input):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @param u_input - the user input as a string
        @description For now, all this function does is clear
        the registers, and then load the PC with the user's input
        '''
        break_reached=False
        #clear registers
        for i in range(6):
            self.registers[i]=0
        self.registers[5]=0x1ff

        #remove the R
        u_input=u_input[:len(u_input)-1]
        if(not utils.is_hex(u_input)):
            print("Invalid input. Please only input hex digits")
            return

        u_input=int(u_input,16)

        #set the program counter to the offset value and display information
        self.registers[0]=u_input
        self.print_run_table(u_input)

        while not break_reached:
            self.pc_offset=1
            curr_opcode=self.main_mem[self.registers[0]]
            self.program_status.set_PC(self.hex_to_fmt_string(self.registers[0]))
            self.program_status.set_OPC(self.hex_to_fmt_string(self.main_mem[self.registers[0]]))
            self.instruction_operands=self.__get_operands(self.main_mem[self.registers[0]])
            self.__execute_instruction(self.main_mem[self.registers[0]])
            self.program_status.set_accum(self.hex_to_fmt_string(self.registers[1]))
            self.program_status.set_xreg(self.hex_to_fmt_string(self.registers[2]))
            self.program_status.set_yreg(self.hex_to_fmt_string(self.registers[3]))
            self.program_status.set_sp(self.hex_to_fmt_string((self.registers[5]-0x100)))
            self.program_status.set_stat(self.registers[4])
            table_line=self.program_status.build_info_str()
            print(table_line)
            
            if curr_opcode==0:
                break_reached=True
            else:
                self.registers[0]=self.registers[0]+self.pc_offset
        
       

    def print_mem_address(self,u_input, str_val):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @param u_input - the user's input as a string
        @param str_val - the value stored at the address
        @description Prints the value stored at a specified
        memory address
        '''
        addr_string=self.hex_to_fmt_string(str_val)
        print(u_input+" "+addr_string)


    def hex_to_fmt_string(self,value):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @param value - the integer value to be formatted
        @description Takes a base 16 number and converts it to a formatted string
        for printing
        @return val_string - the formatted string
        '''
        val_string=hex(value)
        val_string=val_string[2:]
        val_string=val_string.upper()
        val_string=val_string.zfill(2)
        return val_string
    
    def print_run_table(self, u_input):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @param u_input - a parsed form of the user's input for running a program
        @description Prints a table of (mostly blank) information about registers
        and instructions.
        '''
        print("{0:>3}{1:>5} {2:>5}{3:>6} {4:>6}{5:>4}{6:>3}{7:>3}{8:>3} {9:>8}".format("PC","OPC","INS",
                "AMOD","OPRND","AC","XR","YR","SP","NV-BDIZC"))

    def __create_ins_table(self):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @description Creates the dictionary of instructions
        '''
        ins_table={ 0xA:  self.__accum_shift_left, 0x2A: self.__rotate_accum_left,
                    0x0:  self.__break, 0x18:self.__clear_carry, 0xD8: self.__clear_decimal_mode,
                    0x58: self.__clear_inter_disable, 0xB8: self.__clear_overflow,0xCA: self.__decr_X,
                    0x88: self.__decr_Y,0xE8: self.__incr_x, 0xC8: self.__incr_y, 0x4A: self.__shift_accum_right,
                    0xEA: self.__no_op, 0x48: self.__push_accum_stack, 0x08: self.__push_status_stack,
                    0x68: self.__pull_accum_stack, 0x28: self.__pull_status_stack, 0x6A: self.__rotate_accum_right,
                    0x38: self.__set_carry, 0xF8: self.__set_decimal, 0x78: self.__set_interr, 0xAA: self.__transfer_accum_x,
                    0xA8: self.__transfer_accum_y, 0xBA: self.__transfer_sp_x, 0x8A: self.__transfer_x_accum,
                    0x9A: self.__transfer_x_sp, 0x98: self.__transfer_y_accum, 0x69: self.__add_imm_accum,
                    0x29: self.__and_imm_accum, 0xC9: self.__cmp_imm_accum, 0xE0: self.__cmp_imm_x,
                    0xC0: self.__cmp_imm_y, 0x49: self.__xor_imm_accum, 0xA9: self.__load_imm_accum,
                    0xA2: self.__load_imm_x, 0xA0: self.__load_imm_y, 0x09: self.__or_imm_accum, 0x65: self.__add_zpg_accum,
                    0x25: self.__and_zpg_accum, 0x06: self.__shift_zpg_left,0x24: self.__test_mem_accum,
                    0xC5: self.__cmp_zpg_accum, 0xE4: self.__cmp_zpg_x, 0xC4: self.__cmp_zpg_y,
                    0xC6: self.__decr_mem_zpg, 0xE6: self.__incr_mem_zpg, 0x45: self.__xor_zpg_accum,
                    0xA5: self.__load_zpg_accum, 0xA6: self.__load_zpg_x, 0xA4: self.__load_zpg_y,
                    0x46: self.__shift_zpg_right, 0x05: self.__or_zpg_accum, 0x26: self.__rotate_zpg_left,
                    0x66: self.__rotate_zpg_right,0xE5: self.__sub_zpg_accum,0x85: self.__store_accum_zpg,
                    0x86: self.__store_x_zpg, 0x84: self.__store_y_zpg, 0x6D: self.__add_abs_accum, 0x2D: self.__and_abs_accum,
                    0x0E: self.__shift_abs_left, 0x2C: self.__test_abs_accum, 0xCD: self.__cmp_abs_accum, 0xEC: self.__cmp_abs_x,
                    0xCC: self.__cmp_abs_y, 0xCE: self.__decr_mem_abs, 0xEE: self.__incr_mem_abs,
                    0x4D: self.__xor_abs_accum, 0x4C: self.__jmp_abs, 0x20: self.__jump_save_return,
                    0xAD: self.__load_abs_accum, 0xAE: self.__load_abs_x, 0xAC: self.__load_abs_y,
                    0x4E: self.__shift_abs_left, 0x0D: self.__or_abs_accum, 0x2E: self.__rotate_abs_left,
                    0x6E: self.__rotate_abs_right, 0xED: self.__subtract_abs_accum, 0x8D: self.__store_accum_abs,
                    0x8E: self.__store_x_abs, 0x8C: self.__store_y_abs, 0x6C: self.__jmp_ind, 0x60: self.__return_from_subroutine,
                    0x90: self.__branch_carry_clear, 0xB0: self.__branch_carry_set, 0xF0: self.__branch_equal,
                    0xD0: self.__branch_not_zero, 0x30: self.__branch_neg, 0x10: self.__branch_positive,
                    0x50: self.__branch_overflow_clear, 0x70: self.__branch_overflow_set}
        return ins_table

    def __accum_shift_left(self):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @description Does a left shift on the Accumulator, updates flags
        '''

        #Update current status
        self.program_status.set_ins("ASL")
        self.program_status.set_address_mode("A")

        current_status=self.__get_current_status_reg()

        accum=self.registers[1]
        accum=accum<<1

        #wrap around if we go negative and update status
        if accum>127:
            current_status[7]=(accum&128)>>7
            current_status[0]=1<<7
            accum=accum-256

        # if this results in 0, update status
        elif accum == 0:
            current_status[5]=1<<1
        elif accum != 0:
            current_status[5]=0
        elif accum <= 127:
            current_status[7]=(accum&128)>>7
            current_status[0]=0
        
        
        self.registers[1]=accum
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])
        
    
    def __rotate_accum_left(self):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @description Performs a left rotation on the accumulator
        '''
        self.program_status.set_ins("ROL")
        self.program_status.set_address_mode("A")
        current_status=self.__get_current_status_reg()
        accum=self.registers[1]

        #get the current carry bit
        carryBit=(accum&128)

        #update the carry flag
        
        accum=accum<<1
        accum=accum|(carryBit>>7)

        if accum>255:
            accum=accum-256

        if accum>127:
            current_status[0]=1<<7
            
        elif accum == 0:
            current_status[5]=1<<1
        elif accum != 0:
            current_status[5]=0
        elif accum <= 127:
            current_status[0]=0

        current_status[7]=carryBit
        self.registers[1]=accum
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])


        
    
    def __break(self):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @description Essentially works as an interrupt. Pushes the PC and Status regs
        to the stack, and sets the interrupt flag
        '''
        self.program_status.set_ins("BRK")
        self.program_status.set_address_mode("impl")
        pc_lo_byte=self.registers[0]&255
        pc_hi_byte=(self.registers[0]&0xFF00)>>8
        #push the PC LoByte to stack
        self.main_mem[self.registers[5]]=pc_lo_byte
        self.registers[5]=self.registers[5]-1

        #push the PcHiByte to stack
        self.main_mem[self.registers[5]]=pc_hi_byte
        self.registers[5]=self.registers[5]-1
        self.main_mem[self.registers[5]]=self.registers[4]
        self.registers[5]=self.registers[5]-1

        #set break and interrupt flags
        self.registers[4]=self.registers[4]|4
        self.registers[4]=self.registers[4]|16
    
    def __clear_carry(self):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @description Clears the carry flag
        '''
        self.program_status.set_ins("CLC")
        self.program_status.set_address_mode("impl")
        self.registers[4]=self.registers[4]&254
    
    def __clear_decimal_mode(self):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @description Clears the decimal flag
        '''
        self.program_status.set_ins("CLD")
        self.program_status.set_address_mode("impl")
        self.registers[4]=self.registers[4]&247
    
    def __clear_inter_disable(self):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @description Clears the interrupt flag
        '''
        self.program_status.set_ins("CLI")
        self.program_status.set_address_mode("impl")
        self.registers[4]=self.registers[4]&251
    
    def __clear_overflow(self):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @description Clears the overflow flag
        '''
        self.program_status.set_ins("CLV")
        self.program_status.set_address_mode("impl")
        self.registers[4]=self.registers[4]&191
    
    def __decr_X(self):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @description Decrements the X register by 1 and updates flags
        '''
        #get current status
        self.program_status.set_ins("DEX")
        self.program_status.set_address_mode("impl")
        current_status=self.__get_current_status_reg()
        self.registers[2]=self.registers[2]-1

        if self.registers[2]>255:
            self.registers[2]=self.registers[2]-256
        
        if self.registers[2]<0:
            self.registers[2]=self.registers[2]+256
        #check to see how to update the flags and update them
        if self.registers[2]==0:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        if self.registers[2]>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        self.__update_status_reg(current_status[0],current_status[1],current_status[2],current_status[3],
                current_status[4],current_status[5], current_status[7])

    def __decr_Y(self):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @description Decrements the Y register by 1, updates flags accordingly
        '''
        #update current status accordingly
        self.program_status.set_ins("DEY")
        self.program_status.set_address_mode("impl")
        current_status=self.__get_current_status_reg()
        self.registers[3]=self.registers[3]-1

        if self.registers[3]>255:
            self.registers[3]=self.registers[3]-256
        
        if self.registers[3]<0:
            self.registers[3]=self.registers[3]+256

        #update the flag values
        if self.registers[3]==0:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        if self.registers[3]>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        self.__update_status_reg(current_status[0],current_status[1],current_status[2],current_status[3],
                current_status[4],current_status[5], current_status[7])
    
    def __incr_x(self):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @description Increments the X register by 1 and updates the flags
        '''
        self.program_status.set_ins("INX")
        self.program_status.set_address_mode("impl")
        current_status=self.__get_current_status_reg()
        self.registers[2]=self.registers[2]+1

        if self.registers[2]>255:
            self.registers[2]=self.registers[2]-256
        
        if self.registers[2]<0:
            self.registers[2]=self.registers[2]+256
        #update the flags
        if self.registers[2]==0:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        if self.registers[2]>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        self.__update_status_reg(current_status[0],current_status[1],current_status[2],current_status[3],
                current_status[4],current_status[5], current_status[7])
    
    def __incr_y(self):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @description Increments the Y register by 1, updates flags
        '''
        self.program_status.set_ins("INY")
        self.program_status.set_address_mode("impl")
        current_status=self.__get_current_status_reg()
        self.registers[3]=self.registers[3]+1

        if self.registers[3]>255:
            self.registers[3]=self.registers[3]-256
        
        if self.registers[3]<0:
            self.registers[3]=self.registers[3]+256

        #update the flags
        if self.registers[3]==0:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        if self.registers[3]>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        self.__update_status_reg(current_status[0],current_status[1],current_status[2],current_status[3],
                current_status[4],current_status[5], current_status[7])
    
    def __shift_accum_right(self):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @description Does a right shift and updates the flags
        '''
        self.program_status.set_ins("LSR")
        self.program_status.set_address_mode("A")
        curr_status=self.__get_current_status_reg()
        shift_dig=0
        carry=self.registers[1]&1
        self.registers[1]=self.registers[1]>>1
        self.registers[1]=self.registers[1] | (curr_status[7]<<7)

        if self.registers[1]==0:
            curr_status[5]=1<<1
        else:
            curr_status[5]=0
        
        if self.registers[1]>127:
            curr_status[0]=1<<7
        else:
            curr_status[0]=0
        curr_status[7]=carry

        self.__update_status_reg(curr_status[0],curr_status[1], curr_status[2], curr_status[3], curr_status[4], 
                                curr_status[5], curr_status[7])
        
        

        
    
    def __no_op(self):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @description No operation
        '''
        self.program_status.set_ins("NOP")
        self.program_status.set_address_mode("impl")
    
    def __push_accum_stack(self):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @description Pushes the accumulator onto the stack
        '''
        self.program_status.set_ins("PHA")
        self.program_status.set_address_mode("impl")

        self.main_mem[self.registers[5]]=self.registers[1]
        self.registers[5]=self.registers[5]-1
    
    def __push_status_stack(self):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @description Pushes the status register onto the stack
        '''
        self.program_status.set_ins("PHP")
        self.program_status.set_address_mode("impl")

        self.main_mem[self.registers[5]]=self.registers[4]
        self.registers[5]=self.registers[5]-1
    
    def __pull_accum_stack(self):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @description Pulls the accumulator off of the stack
        '''
        self.program_status.set_ins("PLA")
        self.program_status.set_address_mode("impl")
        self.registers[5]=self.registers[5]+1
        self.registers[1]=self.main_mem[self.registers[5]]

    
    def __pull_status_stack(self):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @description Pulls the status register off of the stack
        '''
        self.program_status.set_ins("PLP")
        self.program_status.set_address_mode("impl")
        self.registers[5]=self.registers[5]+1
        self.registers[4]=self.main_mem[self.registers[5]]

    
    def __rotate_accum_right(self):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @description Does a right rotate on the Accumulator, updates flags
        '''
        self.program_status.set_ins("ROR")
        self.program_status.set_address_mode("A")
        curr_status=self.__get_current_status_reg()
        #get the carry bit
        carry=self.registers[1]&1

        #do a right rotation
        self.registers[1]=self.registers[1]>>1
        self.registers[1]=self.registers[1] | (carry<<7)

        #update flags
        if self.registers[1]==0:
            curr_status[5]=1<<1
        else:
            curr_status[5]=0
        if self.registers[1]>127:
            curr_status[0]=1<<7
        else:
            curr_status[0]=0
            
        curr_status[7]=carry

        self.__update_status_reg(curr_status[0],curr_status[1], curr_status[2], curr_status[3], curr_status[4], 
                                curr_status[5], curr_status[7])
    
    def __set_carry(self):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @description Sets the carry flag
        '''
        self.program_status.set_ins("SEC")
        self.program_status.set_address_mode("impl")
        self.registers[4]=self.registers[4]|1
    
    def __set_decimal(self):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @description Sets the decimal flag
        '''
        self.program_status.set_ins("SED")
        self.program_status.set_address_mode("impl")
        self.registers[4]=self.registers[4]|8
    
    def __set_interr(self):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @description Sets the interrupt flag
        '''
        self.program_status.set_ins("SEI")
        self.program_status.set_address_mode("impl")
        self.registers[4]=self.registers[4]|4
    
    def __transfer_accum_x(self):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @description Transfers the accumulator into x and updates flags
        '''
        self.program_status.set_ins("TAX")
        self.program_status.set_address_mode("impl")
        current_status=self.__get_current_status_reg()
        self.registers[2]=self.registers[1]

        #updates 0 and negative flags
        if self.registers[2]==0:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        if self.registers[2]>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0

        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])
            
    def __transfer_accum_y(self):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @description Moves the accumulator into the Y register and updates the flags
        '''
        self.program_status.set_ins("TAY")
        self.program_status.set_address_mode("impl")
        current_status=self.__get_current_status_reg()
        self.registers[3]=self.registers[1]

        #Updates the 0 and negative flags
        if self.registers[3]==0:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        if self.registers[3]>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])
            
        
    
    def __transfer_sp_x(self):
        self.program_status.set_ins("TSX")
        self.program_status.set_address_mode("impl")
        current_status=self.__get_current_status_reg()
        curr_x=self.registers[2]
        self.registers[2]=self.registers[5]

        if self.registers[2]==0:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        if self.registers[2]>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])
            
    
    def __transfer_x_accum(self):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @description Moves the X register into the accumulator and updates the flags
        '''
        self.program_status.set_ins("TXA")
        self.program_status.set_address_mode("impl")
        current_status=self.__get_current_status_reg()
        self.registers[1]=self.registers[2]

        #Updates the negative and 0 flags
        if self.registers[1]==0:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        if self.registers[1]>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0

        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])
        
    
    def __transfer_x_sp(self):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @description moves x into the stack pointer
        '''
        self.program_status.set_ins("TXS")
        self.program_status.set_address_mode("impl")
        self.registers[5]=self.registers[2]
    
    def __transfer_y_accum(self):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @description Moves Y into the accumulator and updates the flags
        '''
        self.program_status.set_ins("TYA")
        self.program_status.set_address_mode("impl")
        current_status=self.__get_current_status_reg()
        self.registers[1]=self.registers[3]

        #updates the negative and 0 flags
        if self.registers[1]==0:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        if self.registers[1]>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
            
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])
        
    
    
    def __update_status_reg(self, neg, overflow, brk, decimal, 
                            interrupt, zero, carry):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @param neg - the value of the negative flag
        @param overflow - the value of the overflow flag
        @param brk - the value of the break flag
        @param decimal - the value of the decimal flag
        @param interrupt - the value of the interrupt flag
        @param zero - the value of the zero flag
        @param carry - the value of the carry flag
        @description ORs all the values together and updates the status register
        '''
        new_stat_reg=0
        new_stat_reg=new_stat_reg|carry
        new_stat_reg=new_stat_reg|zero
        new_stat_reg=new_stat_reg|interrupt
        new_stat_reg=new_stat_reg|decimal
        new_stat_reg=new_stat_reg|brk
        new_stat_reg=new_stat_reg|overflow
        new_stat_reg=new_stat_reg|neg

        if self.registers[4] != new_stat_reg:
            self.registers[4]=new_stat_reg

    def __get_current_status_reg(self):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @description Gets a list of the current flags
        '''
        status_flags=[]
        current_mask=128
        while current_mask >= 1:
            current_val=self.registers[4]&current_mask
            status_flags.append(current_val)
            current_mask=current_mask>>1 
        return status_flags
    
    def __execute_instruction(self, opcode):
        '''
        @author Woodlin Smith
        @param self - the emulator object
        @param opcode - the opcode of the instruction to be run
        @description Gets an instruction from the table and then executes it.
        '''
        ins=self.instructions[opcode]
        ins()
    
    def __add_imm_accum(self):
        self.program_status.set_ins("ADC")
        self.program_status.set_address_mode("#")
        current_status=self.__get_current_status_reg()
        accum=self.registers[1]
        
        #add with the carry
        self.registers[1]=self.registers[1]+self.instruction_operands[0]+current_status[7]

        #did we go over our range
        if self.registers[1]>255:
            self.registers[1]=self.registers[1]-256
        if self.registers[1]<0:
            self.registers[1]=self.registers[1]+256

        
        #check for overflow, negative, and carry flags
        if accum<=127 and self.instruction_operands[0]<=127 and self.registers[1]>127:
            current_status[1]=1<<6
        elif accum>127 and self.instruction_operands[0]>127 and self.registers[1]<=127:
            current_status[1]=1<<6
        
        else:
            current_status[1]=0
        
        if self.registers[1]>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        if accum&128!=0 and self.registers[1]&128==0:
           current_status[7]=1
        else:
            current_status[7]=0
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])
    

    def __and_imm_accum(self):
        self.program_status.set_ins("AND")
        self.program_status.set_address_mode("#")

        current_status=self.__get_current_status_reg()
        #do the and, check flags

        self.registers[1]=self.registers[1]&self.instruction_operands[0]
        
        if self.registers[1]>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        if self.registers[1]==0:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])

    def __cmp_imm_accum(self):
        self.program_status.set_ins("CMP")
        self.program_status.set_address_mode("#")

        current_status=self.__get_current_status_reg()
        inverse_op=utils.get_ones_comp(self.instruction_operands[0])
        accum=self.registers[1]

        result=accum+inverse_op-current_status[7]
        
        if result>255:
            result=result-256
        if result<0:
            result=result+256

        if accum==self.instruction_operands[0]:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        if result>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        if result&128 == 0 and self.registers[1]&128!=0:
            current_status[7]=1
        else:
            current_status[7]=0
        
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])

    def __cmp_imm_x(self):
        self.program_status.set_ins("CPX")
        self.program_status.set_address_mode("#")

        current_status=self.__get_current_status_reg()
        inverse_op=utils.get_ones_comp(self.instruction_operands[0])

        result=self.registers[2]+inverse_op-current_status[7]

        if result>255:
            result=result-256

        if self.registers[2]==self.instruction_operands[0]:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        if result>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        if result&128 == 0 and self.registers[2]&128!=0:
            current_status[7]=1
        else:
            current_status[7]=0
        
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])

    def __cmp_imm_y(self):
        self.program_status.set_ins("CPY")
        self.program_status.set_address_mode("#")

        current_status=self.__get_current_status_reg()
        inverse_op=utils.get_ones_comp(self.instruction_operands[0])

        result=self.registers[3]+inverse_op-current_status[7]

        if result>255:
            result=result-256
        if result<0:
            result=result+256

        if self.registers[3]==self.instruction_operands[0]:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        if result>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        if result&128 == 0 and self.registers[3]&128!=0:
            current_status[7]=1
        else:
            current_status[7]=0
        
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])


    def __xor_imm_accum(self):
        self.program_status.set_ins("EOR")
        self.program_status.set_address_mode("#")

        current_status=self.__get_current_status_reg()
        self.registers[1]=self.registers[1]^self.instruction_operands[0]

        if self.registers[1]==0:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        if self.registers[1]>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])

    def __load_imm_accum(self):
        self.program_status.set_ins("LDA")
        self.program_status.set_address_mode("#")

        current_status=self.__get_current_status_reg()
        self.registers[1]=self.instruction_operands[0]


        if self.registers[1]==0:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        if self.registers[1]>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])

    def __load_imm_x(self):
        self.program_status.set_ins("LDX")
        self.program_status.set_address_mode("#")

        current_status=self.__get_current_status_reg()
        self.registers[2]=self.instruction_operands[0]


        if self.registers[2]==0:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        if self.registers[2]>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])

    def __load_imm_y(self):
        self.program_status.set_ins("LDY")
        self.program_status.set_address_mode("#")

        current_status=self.__get_current_status_reg()
        self.registers[3]=self.instruction_operands[0]


        if self.registers[3]==0:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        if self.registers[3]>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])


    def __or_imm_accum(self):
        self.program_status.set_ins("ORA")
        self.program_status.set_address_mode("#")

        current_status=self.__get_current_status_reg()

        self.registers[1]=self.registers[1]|self.instruction_operands[0]
        
        if self.registers[1]>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        if self.registers[1]==0:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])
    
    def __sub_imm_accum(self):
        self.program_status.set_ins("SBC")
        self.program_status.set_address_mode("#")
        current_status=self.__get_current_status_reg()
        
        accum=self.registers[1]

        self.registers[1]=self.registers[1]-self.main_mem[self.instruction_operands[0]]-(1-current_status[7])
        
        if self.registers[1]>255:
            self.registers[1]=self.registers[1]-256
        if self.registers[1]<0:
            self.registers[1]=self.registers[1]+256

        if self.registers[1]<=127 and accum>127 and self.main_mem[self.instruction_operands[0]]>127:
            current_status[1]=1<<6
        elif self.registers[1]> 127 and accum <= 127 and self.main_mem[self.instruction_operands[0]]<=127:
            current_status[1]=1<<6
        
        else:
            current_status[1]=0
        
        if self.registers[1]>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        if self.registers[1]&128 == 0 and accum&128!=0:
            current_status[7]=1
        else:
            current_status[7]=0

        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])
    def __add_zpg_accum(self):
        self.program_status.set_ins("ADC")
        self.program_status.set_address_mode("zpg")
        current_status=self.__get_current_status_reg()
        operand=self.main_mem[self.instruction_operands[0]]
        accum=self.registers[1]        

        self.registers[1]=self.registers[1]+operand+current_status[7]
        
        if self.registers[1] > 127 and accum<=127 and operand<=127:
            current_status[1]=1<<6
        elif self.registers[1]<=127 and accum>127 and operand>127:
            current_status[1]=1<<6
        
        else:
            current_status[1]=0
        
        if self.registers[1]>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        if self.registers[1]&128 == 0 and accum&128!=0:
            current_status[7]=1
        else:
            current_status[7]=0

        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])
    
    def __and_zpg_accum(self):
        self.program_status.set_ins("AND")
        self.program_status.set_address_mode("zpg")

        current_status=self.__get_current_status_reg()
        operand=self.main_mem[self.instruction_operands[0]]

        self.registers[1]=self.registers[1]&operand
        
        if self.registers[1]>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        if self.registers[1]==0:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])

    def __shift_zpg_left(self):
        #Update current status
        self.program_status.set_ins("ASL")
        self.program_status.set_address_mode("zpg")

        current_status=self.__get_current_status_reg()
        operand=self.main_mem[self.instruction_operands[0]]

        curr_status[7]=(operand&128)>>7
       
        operand=operand<<1

        #wrap around if we go negative and update status
        if operand>127:
            current_status[0]=1<<7

        # if this results in 0, update status
        elif operand == 0:
            current_status[5]=1<<1
        elif operand != 0:
            current_status[5]=0
        elif operand <= 127:
            current_status[0]=0
        
        
        self.main_mem[self.instruction_operands[0]]=operand
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])
    
    def __test_mem_accum(self):
        self.program_status.set_ins("BIT")
        self.program_status.set_address_mode("zpg")

        current_status=self.__get_current_status_reg()
        operand=self.main_mem[self.instruction_operands[0]]

        current_status[0]=operand&128
        current_status[1]=operand&64

        result=self.registers[1]&operand

        if result==0:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])
    
    def __cmp_zpg_accum(self):
        self.program_status.set_ins("CMP")
        self.program_status.set_address_mode("zpg")

        current_status=self.__get_current_status_reg()
        inverse_op=utils.get_ones_comp(self.main_mem[self.instruction_operands[0]])
        accum=self.registers[1]

        result=accum+inverse_op-current_status[7]

        if result > 255:
            result=result-256
        if result<0:
            result=result+256
        
        if accum==self.main_mem[self.instruction_operands[0]]:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        if result>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        if result&128 == 0 and self.registers[1]&128!=0:
            current_status[7]=1
        else:
            current_status[7]=0
        
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])
    def __cmp_zpg_x(self):
        self.program_status.set_ins("CPX")
        self.program_status.set_address_mode("zpg")

        current_status=self.__get_current_status_reg()
        inverse_op=utils.get_ones_comp(self.main_mem[self.instruction_operands[0]])
        xreg=self.registers[2]

        result=xreg+inverse_op-current_status[7]

        if result > 255:
            result=result-256
        if result<0:
            result=result+256
        
        if xreg==self.main_mem[self.instruction_operands[0]]:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        if result>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        if result&128 == 0 and self.registers[2]&128!=0:
            current_status[7]=1
        else:
            current_status[7]=0
        
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])
    
    def __cmp_zpg_y(self):
        self.program_status.set_ins("CPY")
        self.program_status.set_address_mode("zpg")

        current_status=self.__get_current_status_reg()
        inverse_op=utils.get_ones_comp(self.main_mem[self.instruction_operands[0]])
        yreg=self.registers[3]

        result=yreg+inverse_op-current_status[7]

        if result > 255:
            result=result-256
        if result<0:
            result=result+256
        
        if yreg==self.main_mem[self.instruction_operands[0]]:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        if result>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        if result&128 == 0 and self.registers[3]&128!=0:
            current_status[7]=1
        else:
            current_status[7]=0
        
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])
    
    def __decr_mem_zpg(self):
        self.program_status.set_ins("DEC")
        self.program_status.set_address_mode("zpg")
        current_status=self.__get_current_status_reg()
        operand=self.main_mem[self.instruction_operands[0]]
        operand=operand-1

        if operand>255:
            operand=operand-256
        if operand<0:
            operand=operand+256
        #update the flag values
        if operand==0:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        if operand>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        self.main_mem[self.instruction_operands[0]]=operand
        self.__update_status_reg(current_status[0],current_status[1],current_status[2],current_status[3],
                current_status[4],current_status[5], current_status[7])
    
    def __incr_mem_zpg(self):
        self.program_status.set_ins("INC")
        self.program_status.set_address_mode("zpg")
        current_status=self.__get_current_status_reg()
        operand=self.main_mem[self.instruction_operands[0]]
        operand=operand+1

        if operand>255:
            operand=operand-256
        if operand<0:
            operand=operand+256
        #update the flag values
        if operand==0:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        if operand>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        self.main_mem[self.instruction_operands[0]]=operand
        self.__update_status_reg(current_status[0],current_status[1],current_status[2],current_status[3],
                current_status[4],current_status[5], current_status[7])
    
    def __xor_zpg_accum(self):
        self.program_status.set_ins("EOR")
        self.program_status.set_address_mode("zpg")

        current_status=self.__get_current_status_reg()
        self.registers[1]=self.registers[1]^self.main_mem[self.instruction_operands[0]]

        if self.registers[1]==0:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        if self.registers[1]>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])
    
    def __load_zpg_accum(self):
        self.program_status.set_ins("LDA")
        self.program_status.set_address_mode("zpg")
        current_status=self.__get_current_status_reg()
        self.registers[1]=self.main_mem[self.instruction_operands[0]]


        if self.registers[1]==0:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        if self.registers[1]>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])

    def __load_zpg_x(self):
        self.program_status.set_ins("LDX")
        self.program_status.set_address_mode("zpg")
        current_status=self.__get_current_status_reg()
        self.registers[2]=self.main_mem[self.instruction_operands[0]]


        if self.registers[2]==0:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        if self.registers[2]>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])
    
    def __load_zpg_y(self):
        self.program_status.set_ins("LDY")
        self.program_status.set_address_mode("zpg")
        current_status=self.__get_current_status_reg()
        self.registers[3]=self.main_mem[self.instruction_operands[0]]


        if self.registers[3]==0:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        if self.registers[3]>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])


    def __shift_zpg_right(self):
        self.program_status.set_ins("LSR")
        self.program_status.set_address_mode("zpg")
        curr_status=self.__get_current_status_reg()
        operand=self.main_mem[self.instruction_operands[0]]
        shift_dig=0
        carry=operand&1
        operand=operand>>1
        operand=operand | (curr_status[7]<<7)
        if operand==0:
            curr_status[5]=1<<1
        curr_status[7]=carry

        self.main_mem[self.instruction_operands[0]]=operand
        self.__update_status_reg(curr_status[0],curr_status[1], curr_status[2], curr_status[3], curr_status[4], 
                                curr_status[5], curr_status[7])


    def __or_zpg_accum(self):
        self.program_status.set_ins("ORA")
        self.program_status.set_address_mode("zpg")

        current_status=self.__get_current_status_reg()

        self.registers[1]=self.registers[1]|self.main_mem[self.instruction_operands[0]]
        
        if self.registers[1]>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        if self.registers[1]==0:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])
    
    def __rotate_zpg_left(self):
        self.program_status.set_ins("ROL")
        self.program_status.set_address_mode("zpg")
        current_status=self.__get_current_status_reg()
        operand=self.main_mem[self.instruction_operands[0]]

        #get the current carry bit
        carryBit=(operand&128)

        #update the carry flag
        
        operand=operand<<1
        operand=operand|(carryBit>>7)

        if operand>255:
            operand=operand-256

        if operand>127:
            current_status[0]=1<<7
            
        elif operand == 0:
            current_status[5]=1<<1
        elif operand != 0:
            current_status[5]=0
        elif operand <= 127:
            current_status[0]=0

        current_status[7]=carryBit

        self.main_mem[self.instruction_operands[0]]=operand
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7]) 
    
    def __rotate_zpg_right(self):
        self.program_status.set_ins("ROR")
        self.program_status.set_address_mode("zpg")
        curr_status=self.__get_current_status_reg()
        operand=self.main_mem[self.instruction_operands[0]]
        #get the carry bit
        carry=operand&1

        #do a right rotation
        operand=operand>>1
        operand=operand | (carry<<7)

        if operand>255:
            operand=operand-256
        if operand<0:
            operand=operand+256

        #update flags
        if operand==0:
            curr_status[5]=1<<1
        else:
            curr_status[5]=0
        if operand>127:
            curr_status[0]=1<<7
        else:
            curr_status[0]=0
            
        curr_status[7]=carry
        self.main_mem[self.instruction_operands[0]]=operand

        self.__update_status_reg(curr_status[0],curr_status[1], curr_status[2], curr_status[3], curr_status[4], 
                                curr_status[5], curr_status[7])


    def __sub_zpg_accum(self):
        self.program_status.set_ins("SBC")
        self.program_status.set_address_mode("zpg")
        current_status=self.__get_current_status_reg()
        accum=self.registers[1]

        self.registers[1]=self.registers[1]-self.main_mem[self.instruction_operands[0]]-(1-current_status[7])

        if self.registers[1]>255:
            self.registers[1]=self.registers[1]-256
        if self.registers[1]<0:
            self.registers[1]=self.registers[1]+256
           
        if self.registers[1]<=127 and accum >127 and self.main_mem[self.instruction_operands[0]] > 127:
            current_status[1]=1<<6
        elif self.registers[1]>127 and accum<=127 and self.main_mem[self.instruction_operands[0]]<=127:
            current_status[1]=1<<6
        
        else:
            current_status[1]=0
        
        if self.registers[1]>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        if accum&128!=0 and self.registers[1]&128==0:
            current_status[7]=1
        else:
            current_status[7]=0

        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])
        
    def __store_accum_zpg(self):
        self.program_status.set_ins("STA")
        self.program_status.set_address_mode("zpg")
        self.main_mem[self.instruction_operands[0]]=self.registers[1]
    
    def __store_x_zpg(self):
        self.program_status.set_ins("STX")
        self.program_status.set_address_mode("zpg")
        self.main_mem[self.instruction_operands[0]]=self.registers[2]
    
    def __store_y_zpg(self):
        self.program_status.set_ins("STY")
        self.program_status.set_address_mode("zpg")
        self.main_mem[self.instruction_operands[0]]=self.registers[3]
    
    def __add_abs_accum(self):
        self.program_status.set_ins("ADC")
        self.program_status.set_address_mode("abs")
        current_status=self.__get_current_status_reg()
        accum=self.registers[1]
        operand=self.main_mem[(self.instruction_operands[0]<<8)|self.instruction_operands[1]]
        

        self.registers[1]=self.registers[1]+operand+current_status[7]
        if self.registers[1]>255:
            self.registers[1]=self.registers[1]-256
        if self.registers[1]<0:
            self.registers[1]=self.registers[1]+256
        
        if accum<=127 and operand<=127 and self.registers[1]>127:
            current_status[1]=1<<6
        elif accum>127 and operand>127 and self.registers[1]<=127:
            current_status[1]=1<<6
        
        else:
            current_status[1]=0
        
        if self.registers[1]>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        if accum&128!=0 and self.registers[1]&128==0:
           current_status[7]=1
        else:
            current_status[7]=0
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])

                                
    def __and_abs_accum(self):
        self.program_status.set_ins("AND")
        self.program_status.set_address_mode("abs")
        operand=self.main_mem[(self.instruction_operands[0]<<8)|self.instruction_operands[1]]
        current_status=self.__get_current_status_reg()

        self.registers[1]=self.registers[1]&operand
        
        if self.registers[1]>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        if self.registers[1]==0:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])
    
    def __shift_abs_left(self):
        #Update current status
        self.program_status.set_ins("ASL")
        self.program_status.set_address_mode("abs")

        current_status=self.__get_current_status_reg()
        operand=self.main_mem[(self.instruction_operands[0]<<8)|self.instruction_operands[1]]

        if operand&128 != 0:
            current_status[7]=1
        else:
            current_status[7]=0
       
        operand=operand<<1
        if operand>255:
            operand=operand-256
        if operand<0:
            operand=operand+256

        #wrap around if we go negative and update status
        if operand>127:
            current_status[0]=1<<7

        # if this results in 0, update status
        elif operand == 0:
            current_status[5]=1<<1
        elif operand != 0:
            current_status[5]=0
        elif operand <= 127:
            current_status[0]=0
        
        
        self.main_mem[(self.instruction_operands[0]<<8)|self.instruction_operands[1]]=operand
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])
    
    def __test_abs_accum(self):
        self.program_status.set_ins("BIT")
        self.program_status.set_address_mode("abs")

        current_status=self.__get_current_status_reg()
        operand=self.main_mem[(self.instruction_operands[0]<<8)|self.instruction_operands[1]]

        current_status[0]=operand&128
        current_status[1]=operand&64

        result=self.registers[1]&operand

        if result==0:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])
    
    def __cmp_abs_accum(self):
        self.program_status.set_ins("CMP")
        self.program_status.set_address_mode("abs")

        current_status=self.__get_current_status_reg()
        inverse_op=utils.get_ones_comp(self.main_mem[(self.instruction_operands[0]<<8)|self.main_mem[self.instruction_operands[1]]])
        accum=self.registers[1]

        result=accum+inverse_op-current_status[7]

        if result > 255:
            result=result-256
        if result < 0:
            result=result+256
        
        if accum==self.main_mem[(self.instruction_operands[0]<<8)|self.instruction_operands[1]]:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        if result>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        if result&128 == 0 and self.registers[1]&128!=0:
            current_status[7]=1
        else:
            current_status[7]=0
        
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])

    def __cmp_abs_x(self):
        self.program_status.set_ins("CPX")
        self.program_status.set_address_mode("abs")

        current_status=self.__get_current_status_reg()
        inverse_op=utils.get_ones_comp(self.main_mem[(self.instruction_operands[0]<<8)|self.instruction_operands[1]])
        xreg=self.registers[2]

        result=xreg+inverse_op-current_status[7]

        if result > 255:
            result=result-256
        if result < 0:
            result = result + 256
        
        if xreg==self.main_mem[(self.instruction_operands[0]<<8)|self.instruction_operands[1]]:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        if result>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        if result&128 == 0 and self.registers[2]&128!=0:
            current_status[7]=1
        else:
            current_status[7]=0
        
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])

    def __cmp_abs_y(self):
        self.program_status.set_ins("CPY")
        self.program_status.set_address_mode("abs")

        current_status=self.__get_current_status_reg()
        inverse_op=utils.get_ones_comp(self.main_mem[(self.instruction_operands[0]<<8)|self.instruction_operands[1]])
        yreg=self.registers[3]

        result=yreg+inverse_op-current_status[7]

        if result > 255:
            result=result-256
        if result < 0:
            result = result + 256
        
        if yreg==self.main_mem[(self.instruction_operands[0]<<8)|self.instruction_operands[1]]:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        if result>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        if result&128 == 0 and self.registers[3]&128!=0:
            current_status[7]=1
        else:
            current_status[7]=0
        
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])
    def __decr_mem_abs(self):
        self.program_status.set_ins("DEC")
        self.program_status.set_address_mode("abs")
        current_status=self.__get_current_status_reg()
        operand=self.main_mem[(self.instruction_operands[0]<<8)|self.instruction_operands[1]]
        operand=operand-1
        if operand>255:
            operand=operand-256
        if operand<0:
            operand=operand+256
        #update the flag values
        if operand==0:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        if operand>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        self.main_mem[(self.instruction_operands[0]<<8)|self.instruction_operands[1]]=operand
        self.__update_status_reg(current_status[0],current_status[1],current_status[2],current_status[3],
                current_status[4],current_status[5], current_status[7])

    def __incr_mem_abs(self):
        self.program_status.set_ins("INC")
        self.program_status.set_address_mode("abs")
        current_status=self.__get_current_status_reg()
        operand=self.main_mem[(self.instruction_operands[0]<<8)|self.instruction_operands[1]]
        operand=operand+1

        if operand>255:
            operand=operand-256
        if operand<0:
            operand=operand+256
        #update the flag values
        if operand==0:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        if operand>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        self.main_mem[(self.instruction_operands[0]<<8)|self.instruction_operands[1]]=operand
        self.__update_status_reg(current_status[0],current_status[1],current_status[2],current_status[3],
                current_status[4],current_status[5], current_status[7])
    
    def __xor_abs_accum(self):
        self.program_status.set_ins("EOR")
        self.program_status.set_address_mode("abs")

        current_status=self.__get_current_status_reg()
        self.registers[1]=self.registers[1]^self.main_mem[(self.instruction_operands[0]<<8)|self.instruction_operands[1]]

        if self.registers[1]==0:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        if self.registers[1]>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])

    def __jmp_abs(self):
        self.program_status.set_ins("JMP")
        self.program_status.set_address_mode("abs")

        operand=(self.instruction_operands[0]<<8)|self.instruction_operands[1]
        self.registers[0]=operand

        #this might change
        self.pc_offset=0

        
    def __return_from_subroutine(self):
        self.program_status.set_ins("RTS")
        self.program_status.set_address_mode("impl")

        self.registers[5]=self.registers[5]+1 #fe
        pc_lo=self.main_mem[self.registers[5]] #fe


        self.registers[5]=self.registers[5]+1 #ff
        pc_high= self.main_mem[self.registers[5]]<<8 #ff

        self.pc_offset=1

        self.registers[0]=pc_high|pc_lo
    
    def __jump_save_return(self):
        self.program_status.set_ins("JSR")
        self.program_status.set_address_mode("abs")
        operand=(self.instruction_operands[0]<<8)|self.instruction_operands[1]
        return_address=self.registers[0]+2
        return_address_lo=return_address&255
        return_address_hi=(return_address&0xFF00)>>8

        
        self.main_mem[self.registers[5]]=return_address_hi#FF
        self.registers[5]=self.registers[5]-1#FE
        
        self.main_mem[self.registers[5]]=return_address_lo
        self.registers[5]=self.registers[5]-1
        self.pc_offset=0

        self.registers[0]=operand
    
    def __load_abs_accum(self):
        self.program_status.set_ins("LDA")
        self.program_status.set_address_mode("abs")
        current_status=self.__get_current_status_reg()
        self.registers[1]=self.main_mem[(self.instruction_operands[0]<<8)|self.instruction_operands[1]]


        if self.registers[1]==0:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        if self.registers[1]>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])
    
    def __load_abs_x(self):
        self.program_status.set_ins("LDX")
        self.program_status.set_address_mode("abs")
        current_status=self.__get_current_status_reg()
        self.registers[2]=self.main_mem[(self.instruction_operands[0]<<8)|self.instruction_operands[1]]


        if self.registers[2]==0:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        if self.registers[2]>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])
                            
    def __load_abs_y(self):
        self.program_status.set_ins("LDY")
        self.program_status.set_address_mode("zpg")
        current_status=self.__get_current_status_reg()
        self.registers[3]=self.main_mem[(self.instruction_operands[0]<<8)|self.instruction_operands[1]]


        if self.registers[3]==0:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        if self.registers[3]>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])
    
    def __shift_abs_right(self):
        self.program_status.set_ins("LSR")
        self.program_status.set_address_mode("abs")
        curr_status=self.__get_current_status_reg()
        operand=self.main_mem[(self.instruction_operands[0]<<8)|self.instruction_operands[1]]
        shift_dig=0
        carry=operand&1
        operand=operand>>1
        operand=operand | (curr_status[7]<<7)
        if operand==0:
            curr_status[5]=1<<1
        curr_status[7]=carry

        self.main_mem[(self.instruction_operands[0]<<8)|self.instruction_operands[1]]=operand
        self.__update_status_reg(curr_status[0],curr_status[1], curr_status[2], curr_status[3], curr_status[4], 
                                curr_status[5], curr_status[7])

    
    def __or_abs_accum(self):
        self.program_status.set_ins("ORA")
        self.program_status.set_address_mode("abs")

        current_status=self.__get_current_status_reg()

        self.registers[1]=self.registers[1]|self.main_mem[(self.instruction_operands[0]<<8)|self.instruction_operands[1]]
        
        if self.registers[1]>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        if self.registers[1]==0:
            current_status[5]=1<<1
        else:
            current_status[5]=0
        
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])
    
    def __rotate_abs_left(self):
        self.program_status.set_ins("ROL")
        self.program_status.set_address_mode("zpg")
        current_status=self.__get_current_status_reg()
        operand=self.main_mem[(self.instruction_operands[0]<<8)|self.instruction_operands[0]]

        #get the current carry bit
        carryBit=(operand&128)

        #update the carry flag
        
        operand=operand<<1
        operand=operand|(carryBit>>7)

        if operand>255:
            operand=operand-256
        if operand<0:
            operand=operand+256

        if operand>127:
            current_status[0]=1<<7
            
        elif operand == 0:
            current_status[5]=1<<1
        elif operand != 0:
            current_status[5]=0
        elif operand <= 127:
            current_status[0]=0

        current_status[7]=carryBit

        self.main_mem[(self.instruction_operands[0]<<8)|self.instruction_operands[1]]=operand
        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7]) 
    
    def __rotate_abs_right(self):
        self.program_status.set_ins("ROR")
        self.program_status.set_address_mode("abs")
        curr_status=self.__get_current_status_reg()
        operand=self.main_mem[(self.instruction_operands[0]<<8)|self.instruction_operands[1]]
        #get the carry bit
        carry=operand&1

        #do a right rotation
        operand=operand>>1
        operand=operand | (carry<<7)

        #update flags
        if operand==0:
            curr_status[5]=1<<1
        else:
            curr_status[5]=0
        if operand>127:
            curr_status[0]=1<<7
        else:
            curr_status[0]=0
            
        curr_status[7]=carry
        self.main_mem[(self.instruction_operands[0]<<8)|self.instruction_operands[1]]=operand

        self.__update_status_reg(curr_status[0],curr_status[1], curr_status[2], curr_status[3], curr_status[4], 
                                curr_status[5], curr_status[7])
    
    def __subtract_abs_accum(self):
        self.program_status.set_ins("SBC")
        self.program_status.set_address_mode("abs")
        current_status=self.__get_current_status_reg()
        accum=self.registers[1]

        self.registers[1]=self.registers[1]-self.main_mem[(self.instruction_operands[0]<<8)|self.instruction_operands[1]]\
                            -(1-current_status[7])

        if self.registers[1]>255:
            self.registers[1]=self.registers[1]-256
        if self.registers[1]<0:
            self.registers[1]=self.registers[1]+256
           
        if self.registers[1]<127 and accum >127 and \
            self.main_mem[(self.instruction_operands[0]<<8)|self.instruction_operands[1]] > 127:
            current_status[1]=1<<6

        elif self.registers[1]>127 and accum<127 and\
             self.main_mem[(self.instruction_operands[0]<<8)|self.instruction_operands[1]]<127:
            current_status[1]=1<<6
        
        else:
            current_status[1]=0
        
        if self.registers[1]>127:
            current_status[0]=1<<7
        else:
            current_status[0]=0
        
        if accum&128!=0 and self.registers[1]&128==0:
            current_status[7]=1
        else:
            current_status[7]=0

        self.__update_status_reg(current_status[0], current_status[1],current_status[2],
                                current_status[3], current_status[4], current_status[5],
                                current_status[7])
    
    def __store_accum_abs(self):
        self.program_status.set_ins("STA")
        self.program_status.set_address_mode("abs")
        self.main_mem[(self.instruction_operands[0]<<8)|self.instruction_operands[1]]=self.registers[1]
    
    def __store_x_abs(self):
        self.program_status.set_ins("STX")
        self.program_status.set_address_mode("abs")
        self.main_mem[(self.instruction_operands[0]<<8)|self.instruction_operands[1]]=self.registers[2]
    
    def __store_y_abs(self):
        self.program_status.set_ins("STY")
        self.program_status.set_address_mode("abs")
        self.main_mem[(self.instruction_operands[0]<<8)|self.instruction_operands[1]]=self.registers[3]


    def __jmp_ind(self):
        self.program_status.set_ins("JMP")
        self.program_status.set_address_mode("ind")

        operand_lo=self.main_mem[(self.instruction_operands[0]<<8)|self.instruction_operands[1]]
        operand_high=self.main_mem[((self.instruction_operands[0]<<8)|self.instruction_operands[1])+1]
        self.registers[0]=(operand_high<<8)|operand_lo

        #this might change
        self.pc_offset=0
    
    def __branch_carry_clear(self):
        self.program_status.set_ins("BCC")
        self.program_status.set_address_mode("rel")

        if self.registers[4]&1==0:

            #check if its negative
            if self.instruction_operands[0]>127:
                self.pc_offset=2+self.instruction_operands[0]-256
            else:
                self.pc_offset=2+self.instruction_operands[0]
            
    def __branch_carry_set(self):
        self.program_status.set_ins("BCS")
        self.program_status.set_address_mode("rel")
        if self.registers[4]&1!=0:
            #check if its negative
            if self.instruction_operands[0]>127:
                self.pc_offset=2+self.instruction_operands[0]-256
            else:
                self.pc_offset=2+self.instruction_operands[0]
    
    def __branch_equal(self):
        self.program_status.set_ins("BEQ")
        self.program_status.set_address_mode("rel")
        if self.registers[4]&2!=0:
            #check if its negative
            if self.instruction_operands[0]>127:
                self.pc_offset=2+self.instruction_operands[0]-256
            else:
                self.pc_offset=2+self.instruction_operands[0]

    def __branch_neg(self):
        self.program_status.set_ins("BMI")
        self.program_status.set_address_mode("rel")
        if self.registers[4]&128!=0:
            #check if its negative
            if self.instruction_operands[0]>127:
                self.pc_offset=2+self.instruction_operands[0]-256
            else:
                self.pc_offset=2+self.instruction_operands[0]
            
    def __branch_not_zero(self):
        self.program_status.set_ins("BNE")
        self.program_status.set_address_mode("rel")
        if self.registers[4]&2==0:
            #check if its negative
            if self.instruction_operands[0]>127:
                self.pc_offset=2+self.instruction_operands[0]-256
            else:
                self.pc_offset=2+self.instruction_operands[0]
    
    def __branch_positive(self):
        self.program_status.set_ins("BPL")
        self.program_status.set_address_mode("rel")
        if self.registers[4]&128==0:
            #check if its negative
            if self.instruction_operands[0]>127:
                self.pc_offset=2+self.instruction_operands[0]-256
            else:
                self.pc_offset=2+self.instruction_operands[0]
    
    def __branch_overflow_clear(self):
        self.program_status.set_ins("BVC")
        self.program_status.set_address_mode("rel")
        if self.registers[4]&64==0:
            #check if its negative
            if self.instruction_operands[0]>127:
                self.pc_offset=2+self.instruction_operands[0]-256
            else:
                self.pc_offset=2+self.instruction_operands[0]
    
    def __branch_overflow_set(self):
        self.program_status.set_ins("BVS")
        self.program_status.set_address_mode("rel")
        if self.registers[4]&64!=0:
            #check if its negative
            if self.instruction_operands[0]>127:
                self.pc_offset=2+self.instruction_operands[0]-256
            else:
                self.pc_offset=2+self.instruction_operands[0]


    def __get_operands(self, opcode):   
        operands=[]
        lo_nibble=opcode & 0xF
        hi_nibble=opcode & 0xF0
        if lo_nibble== 0x8 or lo_nibble == 0xA or opcode == 0x0 or opcode == 0x60:
            self.program_status.set_operand_one()
            self.program_status.set_operand_two()
            return operands
        if lo_nibble<10 and opcode !=0x20:
            operands.append(self.__get_one_operand())
            return operands
        else:
            operands=self.__get_two_operands()
            return operands
    


    def __get_one_operand(self):
        operand=self.main_mem[self.registers[0]+1]
        self.program_status.set_operand_one(self.hex_to_fmt_string(operand))
        self.program_status.set_operand_two()
        self.pc_offset=2
        return operand
    
    def __get_two_operands(self):
        operands=[]
        operands.append(self.main_mem[self.registers[0]+2])
        operands.append(self.main_mem[self.registers[0]+1])
        self.program_status.set_operand_one(self.hex_to_fmt_string(operands[0]))
        self.program_status.set_operand_two(self.hex_to_fmt_string(operands[1]))
        self.pc_offset=3
        return operands
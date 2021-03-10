import math
def handle_command_line_args(arguments):
    '''
    @author Woodlin Smith
    @parameter arguments - a list of command line arguments
    @description Checks the validity of command line arguments,
    prints a usage statement if they don't work. Also sets a flag
    to let the emulator know whether or not to load a file into memory
    @return -1 - invalid arguments
    @return 2 - load in a file
    @return 1 - normal operation
    '''
    if(len(arguments)<1 or len(arguments)>2):
        usage_statement()
        return -1
    
    elif(len(arguments)==2):
        return 2
    
    else:
        return 1
        



def usage_statement():
    '''
    @author Woodlin Smith
    @description Prints a usage statement
    '''
    print("USAGE: main.py objectfile.obj\nobjectfile is optional")




def parse_hex_line(in_line):
    
    '''
    @author Woodlin Smith
    @parameter in_line - the line we are reading in
    @description Parses a line of an Intel HEX file for its
    important elements, and packages them in a tuple
    @return info_tuple - the package of all the relevant data
    '''
    #remove colon
    in_line=in_line[1:]

    #Get the byte count and chop it off
    byte_count=get_byte_count(in_line)
    in_line=in_line[2:]

    #get the address and chop it off
    address=get_addr(in_line)
    in_line=in_line[4:]


    record_type=get_record_type(in_line)
    
    #check to see if we are at EOF
    if(record_type=="01"):
        info_tuple=(address,record_type,"")
        return info_tuple
    
    in_line=in_line[2:]

    #Get the data
    data=get_data(in_line,byte_count)
    info_tuple=(address,record_type,data)
    return info_tuple
    

def get_byte_count(in_line):
    '''
    @author Woodlin Smith
    @parameter in_line - the input line from the file
    @description gets how many bytes of data are in the line
    @return count - the byte count
    '''
    count=in_line[0:2]
    count=int(count,16)

    return count

def get_addr(in_line):
    '''
    @author Woodlin Smith
    @parameter in_line - the input line from the file
    @description Gets the offset from the base address to store the data
    @return addr - the address offset
    '''
    addr=in_line[0:4]
    addr=int(addr,16)
    return addr

def get_record_type(in_line):
    '''
    @author Woodlin Smith
    @parameter in_line - the input line from the file
    @description Gets the data record's type
    @return r_type the type
    '''
    r_type=in_line[0:2]
    return r_type

def get_data(in_line, byte_count):

    '''
    @author Woodlin Smith
    @parameter in_line - the input line from the file
    @parameter byte_count - the amount of bytes
    @description - gets the data from the line
    @return "" - no data to be retrieved
    @return dat - the data to be retrieved
    '''
    if(byte_count==0):
        return ""
    
    dat=in_line[0:(byte_count*2)]
    return dat

def is_hex(user_input):
    '''
    @source https://stackoverflow.com/questions/11592261/check-if-a-string-is-hexadecimal
    @parameter user_input - the user input as a string
    @description Checks if a string is a valid hex string
    @return true - the string is a hex string
    @return false - the string is not a hex string
    '''
    try:
        hex_val=int(user_input,16)
        return True
    except ValueError:
        return False


def get_ones_comp(number):
    if number==0:
        bit_no=1
    else: 
        bit_no=int(math.floor(math.log(number)/math.log(2))+1)
    return number^((1<<bit_no)-1)
        

import system
import utils
import sys


        
def main():
    '''
    @author Woodlin Smith
    @description Serves as the main processing loop for the program.
    '''
    #get the cmd line arguments
    arg_count=utils.handle_command_line_args(sys.argv)

    if(arg_count==-1):
        return -1
    
    user_input=""
    input_file=None


    #create the emulator, load in a file if required
    emulator=system.system()
    if(arg_count==2):
        input_file=open(sys.argv[1],"r")
        emulator.init_mem_from_file(input_file)
        input_file.close()

    #parse the user's input
    while user_input != "exit":
        try:
            user_input=input(">")
            emulator.parse_input(user_input)
        except EOFError:
            break
        except KeyboardInterrupt:
            break
    else:
        exit()


if __name__=="__main__":
    main()


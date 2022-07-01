import colorama
import time
file = ""
readfile = ""
overwrite = None
INFO = "[INFO]"
DEBUG = "[DEBUG]"
WARNING = "[WARNING]"
ERROR = "[ERROR]"
FATAL = "[FATAL]"
colorama.init(convert=True)



class InvalidWritefileError(BaseException):
    pass
# class InvalidReadfileError(BaseException):
#     pass

def config(filename:str, overwrite_param=False): #overwrite_param instead of overwrite to prefent conflicts.
    if not filename.endswith(".log"):
        raise InvalidWritefileError("Filename does not end with '.log'")
    else:
        global file
        global overwrite
        overwrite = overwrite_param
        file = filename
    if overwrite_param:
        with open(filename, "w") as fileobject:
            fileobject.write("{System} Overwritten this file, set overwrite_param to false to prevent this.\n")

# def readconfig(filename:str):
    # if not filename.endswith(".log"):
    #     raise InvalidReadfileError("Filename does not end with '.log'")
    # else:
    #     global readfile
    #     readfile = filename

def log(data:str, severity):
    if not file.endswith(".log"):
        raise InvalidWritefileError("Filename does not end with '.log'")
    else:
        with open(file, "a") as fileobject:
            fileobject.write(f"Time=[{time.asctime()}]|Severity={severity}|::  {data} \n")
            print(f"{colorama.Fore.YELLOW}Time=[{time.asctime()}]|Severity={severity}|{colorama.Fore.RESET}::  {data}")

if __name__ == "__main__":
    config("testlog.log")
    log("testlog hello world", DEBUG)
    log("System Exit Code 0", FATAL)
    exit(0)



from datetime import datetime

bcolors = {
    # 'HEADER' : '\033[95m',
    # 'NOTE': '\033[94m',
    # 'INFO': '\033[96m',
    # 'WAYPOINT': '\033[92m',
    # 'WARNING': '\033[93m',
    # 'ERROR': '\033[91m',
    # 'ENDC': '\033[0m',
    # 'BOLD': '\033[1m',
    # 'UNDERLINE': '\033[4m'
    }


def log(type, msg, src):
    
    lineLog = str(datetime.now()) + " - " + type + " - " + src + ": " + msg

    if type in bcolors:
        linePrint = str(datetime.now()) + " - " + src + " - " + f"{bcolors[type]}{type}: {bcolors['ENDC']}" + msg
    else:
        linePrint = lineLog

    print(linePrint)

    with open("log.txt", "a") as logFile:
        logFile.write(lineLog + '\n')


if __name__ == "__main__":
    log("ERROR", "ça marche pas!", "test")
    log("WARNING", "Attention!", "test")
    log("HEADER", "ça marche pas!", "test")
    log("NOTE", "Attention!", "test")
    log("INFO", "Attention!", "test")
    log("WAYPOINT", "Attention!", "test")

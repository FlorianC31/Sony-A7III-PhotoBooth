from multiprocessing import Process
from setproctitle import setproctitle
from PhotoBooth import run_photobooth


if __name__ == "__main__":

    # Configurer notre objet de Thread pour utiliser la fonction ci-dessus
    setproctitle("PhotoBooth-Master")  # set the name of the process visible by the system
    run = 1

    while run:
        process = Process(target=run_photobooth)
        process.name = "PhotoBooth-Run"  # not visible by the system, only by Python
        process.start()
        process.is_alive()
        # print(f"Photobooth lancé avec l'id {process.pid}")
        # Attendre la fin de l'exécution du thread.
        process.join()

        with open("run.txt", "r") as file:
            run = int(file.read())
        if run:
            print("")
            print("")
            print("######################################################################################################")
            print("#                                                                                                    #")
            print("#     OOPS, Il y a eu un petit souci, veuillez patienter le PhotoBooth va redémarrer tout seul !     #")
            print("#                                                                                                    #")
            print("######################################################################################################")
            print("")

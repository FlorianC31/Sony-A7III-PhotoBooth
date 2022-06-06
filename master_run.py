from multiprocessing import Process
from setproctitle import setproctitle
from PhotoBooth import run_photobooth
from logger import log


if __name__ == "__main__":

    # Configurer notre objet de Thread pour utiliser la fonction ci-dessus
    master_process_name = "PhotoBooth-Master"
    setproctitle(master_process_name)  # set the name of the process visible by the system
    run = 1

    while run:
        process = Process(target=run_photobooth)
        process.name = "PhotoBooth-Run"  # not visible by the system, only by Python
    
        log("WAYPOINT", "Lancement d'un nouveau processus " + process.name, master_process_name)
        process.start()
        process.is_alive()
        # print(f"Photobooth lancé avec l'id {process.pid}")
        # Attendre la fin de l'exécution du thread.
        process.join()

        with open("run.txt", "r") as file:
            run = int(file.read())
        if run:  # Si le photomaton est encore en mode "RUN" c'est qu'il n'était pas sencé se terminer
            # On affiche le message d'erreur et on repart au début du while avec run = 1
            log("ERROR", "Fermeture inopinee du processus " + process.name, master_process_name)
            print("")
            print("")
            print("######################################################################################################")
            print("#                                                                                                    #")
            print("#     OOPS, Il y a eu un petit souci, veuillez patienter le PhotoBooth va redémarrer tout seul !     #")
            print("#                                                                                                    #")
            print("######################################################################################################")
            print("")
        # Sinon, run = 0, on sort du while et on ferme normalement le programme
    
    log("WAYPOINT", "Fermeture Normale du PhotoBooth initiee par l'administrateur", master_process_name)

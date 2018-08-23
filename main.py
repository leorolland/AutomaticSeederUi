# Résolution 320 x 240

# Importations
from tkinter import *
from functools import partial
import time
import _thread
try:
    import RPi.GPIO as GPIO
    # On initialise l'interface GPIO en mode BCM
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(13, GPIO.OUT)     # Relié sur le PIN 4 Arduino
    GPIO.setup(11, GPIO.OUT)    # Relié sur le PIN 7 Arduino
    GPIO.output(13, GPIO.LOW)
    GPIO.output(11, GPIO.LOW)
except:
    pass

# Schéma représentatif :
#
# -------- CHAMP ----------
# |                       |
# |                       |
# |                       |
# |                       |
# |                       |
# |                       |
# | >                     |
# -------------------------
#
#       > = robot
#       - = largeur
#       | = longueur
#

## Dimensionnement du robot
longueurChamp = 10.0    # en m (profondeur, sur la gauche du robot)
largeurChamp = 10.0     # en m (devant robot)
largeurRobot = 0.30     # en m
vitesseRobot = 0.3      # en m/s
tempsDemiTour = 3       # en s

## Évolution dans le parcours
paused = False
timer = 0.0
avancement_x = 0 # en secondes
avancement_y = 0 # en largeurs

## Création de la fenêtre principale
win = Tk()
win.geometry('320x240')
win.attributes('-fullscreen', True)
frame = Frame(win, width=320, height=240)
frame.grid()
longLabel = None
largLabel = None
instructionFrame = Frame(win, width=300, height=240)
lancementFrame = Frame(win, width=320, height=240)

def lancement():
    """ Fonction qui lance le cycle du robot """
    global longueurChamp, largeurChamp, instructionFrame, largeurRobot, vitesseRobot, tempsDemiTour

    # Nombres de secondes pour faire une largeur de champ
    x = largeurChamp/vitesseRobot
    # Nombres de largeurs à faire
    y = longueurChamp/largeurRobot
    # Temps estimé
    eta = y * ( x + tempsDemiTour )

    # Variables
    playPauseButton = Button(lancementFrame, bg="LIGHTGREEN", text="Pause", font="Arial 13")
    progression = Label(lancementFrame, text="0%", font="Arial 50")
    progression.place(x=90,y=70)

    # Fonctions
    def commandeArduino(action):
        if action == 'gauche':
            # On envoie le signal GAUCHE
            try:
                GPIO.output(13, GPIO.HIGH)
                GPIO.output(11, GPIO.LOW)
            except:
                pass
            print("virage à gauche")
            # On attend que l'arduino récupère l'information
            time.sleep(tempsDemiTour)
            commandeArduino('avancer')
        elif action == 'droite':
            # On envoie le signal GAUCHE
            try:
                GPIO.output(13, GPIO.LOW)
                GPIO.output(11, GPIO.HIGH)
            except:
                pass
            print("virage à droite")
            # On attend que l'arduino récupère l'information
            time.sleep(tempsDemiTour)
            commandeArduino('avancer')
        elif action == 'avancer':
            try:
                GPIO.output(13, GPIO.HIGH)
                GPIO.output(11, GPIO.HIGH)
            except:
                pass
            print("avancer")
        elif action == 'arret':
            try:
                GPIO.output(13, GPIO.LOW)
                GPIO.output(11, GPIO.LOW)
            except:
                pass
            print("arret")


    def playPause():
        global paused, timer
        if paused:
            # Le processus est relancé
            paused = False
            playPauseButton.config(text="Pause")
        else:
            # Le processus est mis en pause
            GPIO.output(13, GPIO.LOW)
            GPIO.output(11, GPIO.LOW)
            paused = True
            playPauseButton.config(text="Reprendre")

    def fin():
        """ Éxécutée à la fin du cycle """
        exit()

    def seedingThread():
        """ Thread de gestion du robot """
        global timer, avancement_x, avancement_y
        while True:
            if not paused:
                timer+=1
                avancement_x+=1

                if avancement_y < y: # Si on a pas encore parcouru toutes les rangées
                
                    if avancement_x >= largeurChamp: # Si on arrive au bout de la largeur du champ
                        # Demi tour
                        # Si on est sur un avancement Y pair, demi tour à gauche
                        if avancement_y % 2 == 0:
                            commandeArduino('gauche')
                            print("Envoi de la commande gauche")
                        else:
                            commandeArduino('droite')
                            print("Envoi de la commande droite")
                        avancement_x =  0
                        avancement_y += 1

                    else:
                        commandeArduino('avancer')
                        print("Envoi de la cmde avancer")

                else:
                    commandeArduino('arret')
                    print("Envoi de la cmde arret")


                temps_restant = int(eta-timer) # secondes (arrondi)
                if temps_restant <= 60:
                    pText = "%s s"%(str())
                    progression.place(x=90,y=70)
                else:
                    pText = "%smin %ss"%(int(temps_restant/60),temps_restant%60)
                    progression.place(x=0,y=70)
                progression.config(text=pText)
                time.sleep(1)
            else:
                pass

    # Interface
    instructionFrame.grid_forget()
    lancementFrame.grid()
    longueurs = int(longueurChamp/largeurRobot)
    playPauseButton.config(command=playPause)
    Label(lancementFrame,text="Temps restant estimé :", font="Arial 17", height=3).place(x=10,y=5)
    playPauseButton.place(x=20,y=180)
    Button(lancementFrame, bg="LIGHTGREEN", text="Arrêt/Reser", font="Arial 13", command=fin).place(x=160,y=180)

    # Lancement du thread prinipal
    _thread.start_new_thread(seedingThread, ())

def finConfig():
    """ Fonction éxecutée quand tous les paramètres ont été définis. """
    global frame, win
    frame.grid_forget()
    instructionFrame.grid()
    Label(instructionFrame, text="Instructions", font='Arial 17').grid(columnspan=2,sticky=W)
    # Instruction 1
    Label(instructionFrame, text="1)", font='Arial 14').grid(row=1)
    Label(instructionFrame, justify=LEFT, text=" Vérifez que votre surface ne comporte pas de\n trop grosses pierres.").grid(row=1, column=1,sticky=W)
    # Instruction 2
    Label(instructionFrame, text="2)", font='Arial 14').grid(row=2)
    Label(instructionFrame, justify=LEFT, text=" Placez votre Automatic Seeder au début\n de la première rangée, avec\n la surface du champ sur sa gauche.\n Vérifiez l'alignement au bord.").grid(row=2, column=1,sticky=W)
    # Instruction 3
    Label(instructionFrame, text="3)", font='Arial 14').grid(row=3)
    Label(instructionFrame, justify=LEFT, text=" Assurez vous que la batterie soit pleine\n et que le réservoir de graines\n soit plein.\n").grid(row=3, column=1,sticky=W)
    # Bouton suivant
    Button(instructionFrame, bg='LIGHTGREEN', text="Prêt", font='Arial 17', command=lancement).grid(row=4,column=1, sticky=N)

def ajouterLongueur(x):
    """ Fonction de modification de la longueur du champ. """
    global longueurChamp, longLabel
    if longueurChamp+x > 4.5:
        longueurChamp+=x
        longLabel.config(text="%sm"%(longueurChamp))

def ajouterLargeur(x):
    """ Fonction de modification de la longueur du champ. """
    global largeurChamp, largLabel
    if largeurChamp+x > 4.5:
        largeurChamp+=x
        largLabel.config(text="%sm"%(largeurChamp))

# Positionnement des boutons de la page 1

# Ligne 0
Label(frame, text="Entrez les dimensions de votre surface :\n", font="Arial 12").grid(row=0, column=0, columnspan=300, sticky=N)

# Ligne 1 & 2
Label(frame, text="  Largeur (dist. devant robot) :", font="Arial 13").grid(row=1, column=0, columnspan=3)
largMoinsButton = Button(frame, text="-", bg="LIGHTGREY", font="Arial 16", width=3, command=partial(ajouterLargeur, -0.5))
largMoinsButton.grid(column=0, row=2)
largLabel = Label(frame, text="%sm"%(str(largeurChamp)), font="Arial 16", width=8)
largLabel.grid(column=1, row=2)
largPlusButton = Button(frame, text="+", bg="LIGHTGREY", font="Arial 16", width=3, command=partial(ajouterLargeur, 0.5))
largPlusButton.grid(column=2, row=2)
largPlusPlusButton = Button(frame, text="++", bg="LIGHTGREY", font="Arial 16", width=3, command=partial(ajouterLargeur, 3))
largPlusPlusButton.grid(column=3, row=2)

# Ligne 1 & 2
Label(frame, text="  Longueur :", font="Arial 13").grid(row=3, column=0, columnspan=3)
longMoinsButton = Button(frame, text="-", bg="LIGHTGREY", font="Arial 16", width=3, command=partial(ajouterLongueur, -0.5))
longMoinsButton.grid(column=0, row=4)
longLabel = Label(frame, text="%sm"%(str(longueurChamp)), font="Arial 16", width=8)
longLabel.grid(column=1, row=4)
longPlusButton = Button(frame, text="+", bg="LIGHTGREY", font="Arial 16", width=3, command=partial(ajouterLongueur, 0.5))
longPlusButton.grid(column=2, row=4)
longPlusPlusButton = Button(frame, text="++", bg="LIGHTGREY", font="Arial 16", width=3, command=partial(ajouterLongueur, 3))
longPlusPlusButton.grid(column=3, row=4)

# Ligne 5
suivantButton = Button(frame, text="Suivant", bg="LIGHTGREEN", font="Arial 14", command=finConfig)
suivantButton.grid(column=1, row=5, pady=5, sticky='S')

win.mainloop()

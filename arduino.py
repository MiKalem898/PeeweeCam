import serial
import time

class Arduino():
    def __init__(self):
        self.port = '/dev/ttyACM0'

        try:
            print("Connexion à l'arduino...")
            self.serial = serial.Serial(self.port, 9600, timeout=1) # lien avec l'arduino
            time.sleep(2)
            print('Arduino connecté')

        except Exception as e:
            print(f'Erreur lors de la connexion Arduino: {e}')
            self.serial = None

    def start(self, opening_time):
        if self.serial:
            self.serial.write(f'{opening_time}\n'.encode('utf-8')) # envoie le temps d'ouverture à l'arduino
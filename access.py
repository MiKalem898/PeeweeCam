import threading
from led import Led
from arduino import Arduino
from audio import Audio
from tinydb import TinyDB

db = TinyDB('database.json')
users = db.table('users')

class Access():
    def __init__(self, wtime, vision):
        self.led = Led()
        self.arduino = Arduino()
        self.audio = Audio()
        self.vision = vision
        self.time_for_unknown = 10

        self.waiting_time_for_next_scan = wtime

        self.have_got_unknown = False

        # self.known_users = [user for user in users]
        # self.known_embeddings = [user['vect'] for user in self.known_users]

    def recognized(self, fav_index): # si un visage est reconnu
        user = self.vision.known_users[fav_index]
        print(f'Visage reconnu: {user["name"]}')
        self.vision.app.edit_scan_label('Scan désactivé')

        if user['authorized']: #si autorisé
            c = "G"
            self.vision.app.edit_main_text(f'Visage reconnu: {user["name"]} - Autorisé')

            arduino_thread = threading.Thread(target=self.start_arduino, args=(self.waiting_time_for_next_scan, ))
            arduino_thread.start()

            self.audio.start_saying('authorized') #voix
                    
        else: #sinon
            c = "R"
            self.vision.app.edit_main_text(f'Visage reconnu: {user["name"]} - Refusé')

            self.audio.start_saying('unauthorized')

        led_thread = threading.Thread(target=self.start_led, args=c)
        led_thread.start()

    def unknown(self, face_crop, matrix): # si un visage est inconnu
        print('Visage inconnu')
        self.vision.app.edit_main_text('Visage inconnu')
        self.vision.app.edit_scan_label('Scan désactivé')

        if not self.have_got_unknown:
            self.vision.app.page_liste.create_add_btn()
            self.have_got_unknown = True

        self.current_matrix = matrix
        self.current_face_crop = face_crop
        self.vision.app.page_ajout.image_label.configure(image=self.vision.app.page_ajout.get_img_from_matrix(face_crop), text='')

        led_thread = threading.Thread(target=self.start_led, args='O')
        led_thread.start()

        self.audio.start_saying('unknown')

        self.vision.app.show_unknown_menue()
        self.vision.app.is_timer = True
        self.vision.app.timer(10)

        print('En attente de la réponse...')

        self.vision.is_waiting_for_unknown = True

    def start_led(self, c):
        self.led.change(c, self.waiting_time_for_next_scan)

    def start_arduino(self, op_time):
        self.arduino.start(op_time)

from ultralytics import YOLO
from facenet_pytorch import InceptionResnetV1
import threading
import torch
from tinydb import TinyDB
from PIL import Image
import cv2
import numpy as np
from scipy.spatial.distance import cdist
from access import Access


class Vision():
    def __init__(self, app):
        self.app = app
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') #choix de CUDA si possible pour PyTorch
        self.model = self.load_model() #YOLO
        self.recognizer = self.load_recognizer() #FaceNet
        self.cam = cv2.VideoCapture(0) #récupération de la cam - Windows
        # self.cam = cv2.VideoCapture(0, cv2.CAP_V4L2) #récupération de la cam - Linux
        self.cam.set(cv2.CAP_PROP_FPS, 30) #changement fps

        self.time_for_text = 0
        self.waiting_time_for_text = 45
        self.waiting_time_for_next_scan = 3 #en s
        self.faces_number_frames = 0
        self.distance_frames = 60
        self.time_between_faces_number_frames = 60 # ~2s
        self.time_between_distance_frames = 60
        self.scan_timer = 0
        self.scan_timer_needed = 60
        self.thread_ended_frames = 0
        self.faces = []
        self.is_threading = False
        self.thread_ended = False
        self.running = False
        self.is_waiting_for_next_scan = False
        self.delay = 0
        self.delay_between_each_face_frame = 6
        self.crop_w_face = 100
        self.crop_h_face = 100
        self.is_waiting_for_unknown = False
        self.is_on_another_page = False
        self.scan_active = True

        self.get_users_and_embeddings()

        self.access = Access(self.waiting_time_for_next_scan, self)

        #verif si la cam est ok
        if not self.cam.isOpened:
            print('Caméra non ouverte')

    def get_users_and_embeddings(self):
        self.db = TinyDB('database.json')
        self.users = self.db.table('users')
        self.known_users = [user for user in self.users]
        self.known_embeddings = [user['vect'] for user in self.known_users]

    def load_model(self): #chargement du model de YOLO
        print('Chargement du modèle YOLO...')
        try:
            model = YOLO('./models/yolov8n-face.pt')
            print('Lancé sur modèle yolov8n-face.pt')
        except:
            model = YOLO('./models/yolov8n.pt')
            print('Lancé sur modèle yolov8n.pt')

        return model

    def load_recognizer(self):
        print('Chargement du modèle FaceNet...')
        try:
            recognizer = InceptionResnetV1(pretrained='vggface2').eval().to(self.device) # chargement FaceNet avec jeu de données VggFace2
            print('FaceNet chargé avec succès')
        except Exception as e:
            print('Echec du chargement de FaceNet: ', e)

        return recognizer

    def warmup_model(self):
        print("Reconnaissance de test...")
        
        dummy_input = torch.randn(1, 3, 160, 160).to(self.device)
        
        with torch.no_grad():
            _ = self.recognizer(dummy_input)
            
        dummy_frame = torch.zeros(1, 3, 640, 640).to(self.device)
        _ = self.model(dummy_frame)

        print("Reconnaissance de test réussie.")

    def recognition(self, faces, threshold=0.52): #reconaissance de 5 visages
        print('Reconaissance...')

        try:
            processed_faces = [] # visages en matrices

            for face in faces: #transfo chaque image de l'input
                #redimensionnement
                img = cv2.resize(face, (160, 160))

                # changement vers RGB
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                #chnagement de HWC vers CHW
                img = np.transpose(img, (2, 0, 1))

                #normalisation
                img = (img - 127.5) / 128.0


                processed_faces.append(img)

            #conversion en de la liste en tensor (nombre, couleurs, w, h)
            batch_tensor = torch.tensor(np.array(processed_faces)).float().to(self.device)

            #inférence parrallèle (envoyer tous les visages d'un coup)
            with torch.no_grad():
                embeddings_batch = self.recognizer(batch_tensor)

            
            print('Reconaissance réussie !')
            input_face = np.mean(embeddings_batch.cpu().numpy(), axis=0) #moyenne des 5 matrices
            # print(input_face.tolist())

            if self.known_embeddings: #verif si la db est vide
                #comparaison avec la DB
                input_vect = input_face.reshape(1, -1) #trasnformation (512, ) en (1, 512)
                distances = cdist(input_vect, self.known_embeddings, metric='cosine') #comparaison des vecteurs connus avec le vecteur en input
                min_score = distances.min()
                fav_index = distances.argmin()

                if min_score <= threshold:
                    self.access.recognized(fav_index)

                else:
                    self.access.unknown(faces[1], input_face)

            else:
                self.access.unknown(faces[1], input_face)

            print(f'Score: {str(min_score)}')

        except Exception as e:
            print(f'Erreur lors de la reconaissance: {e}')

        finally:
            self.thread_ended = True
            self.is_threading = False


    def update(self):
        #récupération frames
        ret, frame = self.cam.read()
        frame = cv2.flip(frame, 1)

        results = self.model.track(frame, persist=True, tracker="bytetrack.yaml", conf=0.5, verbose=False)
        
        #récupération de la frame, avec le rectangle
        plotted_frame = results[0].plot()

        # cv2.imshow('Camera', plotted_frame) #retour cam temp
        # plotted_frame = cv2.resize(plotted_frame, (630, 470))
    
        frame_rgb = cv2.cvtColor(plotted_frame, cv2.COLOR_BGR2RGB) # conversion des couleurs
        self.app.last_img = Image.fromarray(frame_rgb) # retour cam final de l'image RGB avec le plot

        self.faces_number_frames += 1

        # attente entre 2 scans, si on est pas en l'attente de la réponse d'un inconnu
        if self.thread_ended and self.thread_ended_frames < self.waiting_time_for_next_scan**2 * 10 and not self.is_waiting_for_unknown and not self.is_on_another_page:
            self.app.edit_scan_label('Scan désactivé')

            if not self.is_waiting_for_next_scan: # si on n'attend pas le prochain scan
                self.time_for_text += 1

            else:
                self.thread_ended_frames += 1

            # message d'attente une seule fois, si le texte de résultat est là depuis 45 frames
            if not self.is_waiting_for_next_scan and self.time_for_text > self.waiting_time_for_text:
                self.is_waiting_for_next_scan = True
                self.time_for_text = 0
                print('Veuillez patienter...')
                self.app.edit_main_text('Veuillez patienter...')

            # attente entre 2 scans terminée
            elif self.thread_ended_frames >= self.waiting_time_for_next_scan**2 * 10:
                self.thread_ended_frames = 0
                self.thread_ended = False
                self.is_waiting_for_next_scan = False
                self.scan_timer = 0
                print('Scan activé')
                self.app.edit_scan_label('Scan désactivé')
                # self.app.edit_main_text('Scan activé')

        # on ne reconnait pas si > 1 visage (message ttes les ~2s)
        elif len(results[0].boxes) > 1 and not self.is_on_another_page and not self.is_waiting_for_unknown:
            self.app.edit_main_text('Identification possible avec un seul visage.')
            self.faces_number_frames = 0
            self.scan_timer = 0

            # délai pour les logs
            if self.faces_number_frames >= self.time_between_faces_number_frames:
                print('Identification possible avec un seul visage.')

            self.app.edit_scan_label('Scan activé')

        # reconnaissance si aucun scan deja en cours, ou si en attente, si pas sur une autre page, si timer écoulé
        elif len(results[0].boxes) == 1 and not self.is_threading and not self.thread_ended and not self.is_on_another_page:
            self.app.edit_scan_label('Scan activé')

            x1, y1, x2, y2 = map(int, results[0].boxes[0].xyxy[0])
            cropped_frame = frame[y1:y2, x1:x2] # crop pour envoyer uniquement le visage
            lx = x2 - x1 #largeur
            ly = y2 - y1 #longueur

            self.delay += 1
            self.distance_frames += 1

            # on recommence si le visage est trop loin, et on l'indique
            if lx < self.crop_w_face or ly < self.crop_h_face:
                self.faces = []
                self.scan_timer = 0

                # intervalle
                if self.distance_frames >= self.time_between_distance_frames:
                    print('Rapprochez votre visage.')
                    self.app.edit_main_text('Rapprochez votre visage.')
                    self.distance_frames = 0

            else:
                self.scan_timer += 1

                if self.scan_timer == 1:
                    print('Ne bougez plus...')
                    self.app.edit_main_text('Ne bougez plus...')

                # on laisse un delay de 6 frames entre chaque récupération de frame et un delai AVANT de commencer à recup les frames
                if self.scan_timer >= self.scan_timer_needed and self.delay >= self.delay_between_each_face_frame:
                    self.faces.append(cropped_frame)
                    self.delay = 0
                

            if len(self.faces) == 3: # on lance la reconaissance si on a 3 frames du visage
                self.is_threading = True

                thread = threading.Thread(target=self.recognition, args=(self.faces.copy(), ))
                thread.start()
                
                self.faces = []

        # si aucun visage + pas en train d'attendre, texte vide visages et timer de scan reset
        elif len(results[0].boxes) == 0 and not self.is_waiting_for_unknown and not self.is_waiting_for_next_scan and not self.is_on_another_page:
            self.app.edit_main_text('Aucun visage détecté')
            self.scan_timer = 0
            self.faces = []

        else:
            self.scan_timer = 0
            self.faces = []

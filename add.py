import customtkinter as ctk
from PIL import Image
from user import User
import cv2
from tinydb import TinyDB
import numpy as np

db = TinyDB('database.json')
users = db.table('users')

class Ajout(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        
        #Bouton retour vers la liste
        self.btn_retour = ctk.CTkButton(self, text="← ANNULER", 
                                         command=lambda: controller.afficher_page("PageListe"), 
                                         font=("Arial", 20))
        self.btn_retour.place(x=10, y=20)

        self.titre = ctk.CTkLabel(self, text="Nouveau Profil", font=("Arial", 35))
        self.titre.pack(pady=(60, 40))

        self.main = ctk.CTkFrame(self, width=950, height=500, border_width=2, border_color="white")
        self.main.pack(pady=(40, 20))

        self.current_img = None
        
######## Encadrer du haut pour representer la personne que l'on ajoute
        self.apercu = ctk.CTkFrame(self.main, width=900, height=150, border_width=2, border_color="green")
        self.apercu.pack(pady=(20, 10), padx=25)
        self.apercu.grid_propagate(False) # On utilise grid partout ici

        # Configuration des colonnes pour l'aperçu
        self.apercu.grid_columnconfigure((2, 3), weight=1)
        self.apercu.grid_rowconfigure((0, 1), weight=1)

        # Titre de l'aperçu (en grid pour ne pas casser le reste)
        ctk.CTkLabel(self.apercu, text="APERCU DE L'AJOUT", font=("Arial", 12, "bold"), text_color="blue").grid(row=0, column=0, columnspan=5, pady=5)
        
        # Image
        self.image_label = ctk.CTkLabel(self.apercu, image=self.current_img, text="PHOTO", width=100, height=100, fg_color="gray", corner_radius=8)
        self.image_label.grid(row=0, column=0, rowspan=2, padx=20, pady=10)

        # Trait de séparation
        ctk.CTkFrame(self.apercu, width=2, height=80, fg_color="white").grid(row=0, column=1, rowspan=2, pady=10)

        # Identité
        ctk.CTkLabel(self.apercu, text="Identité:", font=("Arial", 14), text_color="gray").grid(row=0, column=2, padx=20, sticky="sw")
        self.preview_name = ctk.CTkLabel(self.apercu, text="Nom Prénom", font=("Arial", 22, "bold"))
        self.preview_name.grid(row=1, column=2, padx=20, sticky="nw")

        # Statut
        ctk.CTkLabel(self.apercu, text="Statut:", font=("Arial", 14), text_color="gray").grid(row=0, column=3, padx=20, sticky="sw")
        self.preview_statut = ctk.CTkLabel(self.apercu, text="Statut", font=("Arial", 20))
        self.preview_statut.grid(row=1, column=3, padx=20, sticky="nw")

        # Indicateur d'acces
        self.status_indicator = ctk.CTkLabel(self.apercu, text="● ACCÈS OK", font=("Arial", 14, "bold"), text_color="green")
        self.status_indicator.grid(row=0, column=4, rowspan=2, padx=25)

######## Encadrer en bas pour modifier le dossier de la personne
        self.formulaire = ctk.CTkFrame(self.main, width=900, height=300, border_width=2, border_color="gray")
        self.formulaire.pack(pady=20, padx=25)
        self.formulaire.grid_propagate(False)

        self.formulaire.grid_columnconfigure(0, weight=1)
        self.formulaire.grid_columnconfigure(1, weight=1)
        self.formulaire.grid_rowconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkLabel(self.formulaire, text="MODIFIER LES INFORMATIONS", 
                     font=("Arial", 12, "bold"), text_color="gray").grid(row=0, column=0, columnspan=2, pady=(10, 0))

        # Identité
        ctk.CTkLabel(self.formulaire, text="Identité complète :", font=("Arial", 16)).grid(row=1, column=0, padx=20, sticky="e")
        self.entry_nom = ctk.CTkEntry(self.formulaire, width=350, height=40, placeholder_text="Ex: DUBOIS Vincent")
        self.entry_nom.grid(row=1, column=1, padx=20, sticky="w")
        self.entry_nom.bind("<KeyRelease>", self.update)

        # Statut
        ctk.CTkLabel(self.formulaire, text="Statut de l'utilisateur :", font=("Arial", 16)).grid(row=2, column=0, padx=20, sticky="e")
        self.entry_statut = ctk.CTkEntry(self.formulaire, width=350, height=40, placeholder_text="Ex: L2 INSSET")
        self.entry_statut.grid(row=2, column=1, padx=20, sticky="w")
        self.entry_statut.bind("<KeyRelease>", self.update)

        # Accès
        ctk.CTkLabel(self.formulaire, text="Droits d'accès :", font=("Arial", 16)).grid(row=3, column=0, padx=20, sticky="e")
        self.check_var = ctk.BooleanVar(value=True)
        self.check = ctk.CTkSwitch(self.formulaire, text="Autoriser l'entrée", 
                                   variable=self.check_var, command=self.update,
                                   progress_color="green")
        self.check.grid(row=3, column=1, padx=20, sticky="w")

        # Bouton Save (en dehors de formulaire, dans main ou self)
        self.btn_save = ctk.CTkButton(self, text="ENREGISTRER LE PROFIL", 
                                       font=("Arial", 18, "bold"), height=55, width=400, 
                                       fg_color="green", command=self.save)
        self.btn_save.pack(pady=20)

    def get_img_from_matrix(self, face):
        img = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        return ctk.CTkImage(light_image=img, size=(100, 100))

    def update(self, event=None):
        nom = self.entry_nom.get().strip()
        statut = self.entry_statut.get().strip()
        acces_autorise = self.check_var.get()

        self.preview_name.configure(text=nom.upper() if nom else "NOM PRÉNOM")
        self.preview_statut.configure(text=statut if statut else "STATUT")

        if acces_autorise:
            self.status_indicator.configure(text="● ACCÈS OK", text_color="green")
            self.apercu.configure(border_color="green")
        else:
            self.status_indicator.configure(text="○ REFUSÉ", text_color="red")
            self.apercu.configure(border_color="red")

    def save(self):
        nom = self.entry_nom.get().strip()
        statut = self.entry_statut.get().strip()
        acces = self.check_var.get()

        if nom and statut:
            # 1. On ajoute les données brutes dans le tableau global
            nouvel_user_data = [nom, statut, acces, 0] # 0 = index image par défaut

            matrix = self.controller.vision.access.current_matrix

            path = f'./images/{nom.replace(" ", "_").lower()}.jpg'
            success = cv2.imwrite(path, self.controller.vision.access.current_face_crop)

            if not success:
                print(f"Erreur lors de l'enregistrement de la photo: shape: {self.controller.vision.access.current_face_crop.shape}")

            new_user = {
                "vect": matrix.tolist(),
                "name": nom,
                "class": statut,
                "authorized": acces,
                "photo": path
            }

            users.insert(new_user) #ajout à la db

            #maj infos users de vision.py
            self.controller.vision.known_users.append(new_user)
            self.controller.vision.known_embeddings.append(new_user['vect'])

            print(f"{self.entry_nom.get()} ajouté")

            # 2. ON ACCÈDE À LA PAGE LISTE POUR AJOUTER LE COMPOSANT GRAPHIQUE
            # On récupère l'instance de la page "PageListe"
            page_liste = self.controller.pages["PageListe"]
            
            # On crée le nouveau badge User directement dans le scrolle de la page liste
            nouveau_badge = User(page_liste.scrolle,
                                 self.controller,
                                 id=nom, 
                                 statut=statut, 
                                 autoriser=acces,
                                 photo=path)
            
            # On l'affiche en bas de la liste
            nouveau_badge.pack(pady=5, padx=10, fill="x")
        self.controller.afficher_page("PageListe")
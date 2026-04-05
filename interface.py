import customtkinter as ctk
from PIL import Image
from users import Utilisateur
from add import Ajout
from guests import Visiteurs
from admin import Admin
from tinydb import TinyDB, Query

ctk.set_appearance_mode("Dark")

class Interface(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PeeweeCam")
        self.geometry("1000x850")
        self.resizable(False, False)

        self.get_users()
        self.User = Query()

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        self.pages = {}

        self.last_img = None

        # Initialisation des pages
        # 1. Accueil
        self.page_accueil = ctk.CTkFrame(self.container, fg_color="transparent")
        self.setup_accueil()
        self.pages["PageAccueil"] = self.page_accueil
        self.page_accueil.grid(row=0, column=0, sticky="nsew")

        # 2. Liste
        self.page_liste = Utilisateur(self.container, self.tab, self)
        self.pages["PageListe"] = self.page_liste
        self.page_liste.grid(row=0, column=0, sticky="nsew")

        # 3. Ajout
        self.page_ajout = Ajout(self.container, self)
        self.pages["pageAjout"] = self.page_ajout
        self.page_ajout.grid(row=0, column=0, sticky="nsew")

        #Visiteurs
        self.page_visiteurs = Visiteurs(self.container, self, self.tab)
        self.pages["pageVisiteurs"] = self.page_visiteurs
        self.page_visiteurs.grid(row=0, column=0, sticky="nsew")

        #Admin
        self.page_admin = Admin(self.container, self)
        self.pages["pageAdmin"] = self.page_admin
        self.page_admin.grid(row=0, column=0, sticky="nsew")


        self.afficher_page("PageAccueil")
        self.show_img()

        self.is_timer = False

        self.scan_status_label = ctk.CTkLabel(self.container, text="Scan activé")
        self.scan_status_label.grid(row=3, column=0, columnspan=1)

    def edit_scan_label(self, text):
        self.scan_status_label.configure(text=text)

    def get_users(self):
        self.db = TinyDB('database.json')
        self.tab = self.db.table('users')
        
    def timer(self, secondes):
        # label du timer
        if not hasattr(self, 'timer_label'):
            self.timer_label = ctk.CTkLabel(self.page_accueil, text="", font=("Arial", 20))
            self.timer_label.grid(row=3, column=1, columnspan=2, pady=20)

        if self.is_timer:
            # décompte
            if secondes > 1:
                self.timer_label.configure(text=f"{secondes} secondes restantes")
                self.after(1000, self.timer, secondes - 1)

            elif secondes == 1:
                self.timer_label.configure(text=f"{secondes} seconde restante")
                self.after(1000, self.timer, secondes - 1)

            else:
                # fin du chrono
                self.timer_label.configure(text="Terminé !")
                self.after(1000, self.vide)

   
    def vide(self): # enlever les 2 boutons et le timer
        # print("Fonctions utilisée")
        self.is_timer = False
        self.ajout_main_button.destroy()
        self.timer_label.destroy()
        self.visiter_main_button.destroy()

        self.vision.is_waiting_for_unknown = False

    def show_img(self):
        if self.last_img is not None:
            plotted_image_pil = ctk.CTkImage(light_image=self.last_img, size=(630, 470)) #conversion en image ctk
            self.video_cam.configure(image=plotted_image_pil, text='') # changement de l'image
            self.video_cam.image_reference = plotted_image_pil # garde en mémoire pour éviter le vide

        self.after(30, self.show_img) # refresh apres 30ms (environ 30 fps)


    def setup_accueil(self):
        # 1. Le switch (Position fixe en haut à gauche)
        self.switch = ctk.CTkSwitch(self.page_accueil, text="Mode Sombre/Clair", command=self.theme_changer)
        self.switch.grid(padx=10, pady=20, row=0, column=0, sticky="nw")

        # 2. Le bouton (Position fixe en haut à droite)
        # On met un gros padx à gauche pour le pousser vers la droite sans étirer la colonne
        self.user_button = ctk.CTkButton(self.page_accueil,
                                          text="utilisateurs →",
                                          font=("Arial", 20),
                                          height=40,
                                          command=lambda: self.afficher_page("PageListe"))
        self.user_button.grid(padx=20, pady=20, row=0, column=3, sticky="nw")

        # 3. Ton cadre vide (Taille strictement fixée)
        cadre_vide = ctk.CTkFrame(self.page_accueil,
                                   width=640,
                                   height=480,
                                   corner_radius=10,
                                   border_width=5,
                                   border_color="white")
        
        # On le place sur une ligne en dessous, centré sur les deux colonnes du haut
        cadre_vide.grid(row=1, column=1, columnspan=2, pady=25) 
        cadre_vide.grid_propagate(False)

        # 4. L'image à l'intérieur
        try:
            cam_img = ctk.CTkImage(light_image=Image.open("./IMAGE/images_fond.jpeg"), size=(630, 470))
            self.video_cam = ctk.CTkLabel(cadre_vide, image=cam_img, text="")
            self.video_cam.grid(padx=5, pady=5, sticky="nwes")
        except:
            # Si l'image n'est pas là, le texte permet de voir que le cadre est présent
            self.video_cam = ctk.CTkLabel(cadre_vide, text="Veuillez patienter...", font=("Arial", 20))
            self.video_cam.grid(padx=5, pady=5, sticky="nwes")

        self.main_text = ctk.CTkLabel(self.page_accueil, text=f"", font=("Arial", 25))
        self.main_text.grid(row=0, column=1, columnspan=2, pady=20)

    def edit_main_text(self, text):
        self.main_text.configure(text=text)

    def show_unknown_menue(self):
        # Bouton en fonction du visage reconnu
        #Bouton ajouter cette personne

        self.ajout_main_button = ctk.CTkButton(self.page_accueil,
                                          text="Ajouter cette personne",
                                          font=("Arial", 20),
                                          height=40,
                                          command=lambda: self.afficher_page("pageAdmin"))
        self.ajout_main_button.grid(row=2, column=1)

        #Bouton Entrer en tant que inviter
        self.visiter_main_button = ctk.CTkButton(self.page_accueil,
                                          text="Entrer en tant qu'invité",
                                          font=("Arial", 20),
                                          height=40,
                                          command=lambda: self.afficher_page("pageVisiteurs"))
        self.visiter_main_button.grid(row=2, column=2)

        #Timer
        time=10
        self.timer_label = ctk.CTkLabel(self.page_accueil, text=f"{time} secondes restantes", font=("Arial", 20))
        self.timer_label.grid(row=3, column=1, columnspan=2, pady=20)

    def afficher_page(self, nom_page):
        page = self.pages[nom_page]
        page.tkraise()

        if hasattr(self, 'vision'):
            if nom_page == 'PageAccueil':
                self.vision.is_on_another_page = False
                self.vision.scan_active = True

                print('Scan activé')
                self.edit_scan_label('Scan activé')

            else:
                self.vision.is_on_another_page = True

                if self.vision.scan_active:
                    print('Scan désactivé')
                    self.edit_scan_label('Scan désactivé')
                    self.vision.scan_active = False

                if nom_page == 'pageAdmin' or nom_page == 'pageVisiteurs':
                    self.timer(0)


    def theme_changer(self):
        mode = "light" if ctk.get_appearance_mode() == "Dark" else "dark"
        ctk.set_appearance_mode(mode)
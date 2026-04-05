import customtkinter as ctk
from tkinter import messagebox

class Visiteurs(ctk.CTkFrame):
    def __init__(self, master, controller, tab):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self.tab = tab
        
        #Bouton retour vers la liste
        self.btn_retour = ctk.CTkButton(self, text="← ANNULER", 
                                         command=lambda: controller.afficher_page("PageAccueil"), 
                                         font=("Arial", 20))
        self.btn_retour.place(x=10, y=20)

        self.titre = ctk.CTkLabel(self, text="Profil Visiteurs", font=("Arial", 35))
        self.titre.pack(pady=(60, 40))

        self.main = ctk.CTkFrame(self, width=950, height=500, border_width=2, border_color="white")
        self.main.pack(pady=(40, 20))
        
######## Encadrer du haut pour representer la personne que l'on ajoute
        self.apercu = ctk.CTkFrame(self.main, width=900, height=150, border_width=2, border_color="green")
        self.apercu.pack(pady=(20, 10), padx=25)
        self.apercu.grid_propagate(False) # On utilise grid partout ici

        # Configuration des colonnes pour l'aperçu
        self.apercu.grid_columnconfigure((2, 3), weight=1)
        self.apercu.grid_rowconfigure((0, 1), weight=1)

        # Titre de l'aperçu (en grid pour ne pas casser le reste)
        ctk.CTkLabel(self.apercu, text="APERCU DU VISITEURS", font=("Arial", 12, "bold"), text_color="blue").grid(row=0, column=0, columnspan=5, pady=5)
        
        # Image
        self.image_label = ctk.CTkLabel(self.apercu, text="PAS DE PHOTO", width=100, height=100, fg_color="gray", corner_radius=8)
        self.image_label.grid(row=0, column=0, rowspan=2, padx=20, pady=10)

        # Trait de séparation
        ctk.CTkFrame(self.apercu, width=2, height=80, fg_color="white").grid(row=0, column=1, rowspan=2, pady=10)

        # Identité
        ctk.CTkLabel(self.apercu, text="Identité:", font=("Arial", 14), text_color="gray").grid(row=0, column=2, padx=20, sticky="sw")
        self.name = ctk.CTkLabel(self.apercu, text="Visiteurs", font=("Arial", 22, "bold"))
        self.name.grid(row=1, column=2, padx=20, sticky="nw")

        # Statut
        ctk.CTkLabel(self.apercu, text="Garant:", font=("Arial", 14), text_color="gray").grid(row=0, column=3, padx=20, sticky="sw")
        self.preview_Garant = ctk.CTkLabel(self.apercu, text="Garant", font=("Arial", 20))
        self.preview_Garant.grid(row=1, column=3, padx=20, sticky="nw")

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
                     font=("Arial", 12, "bold"), text_color="blue").grid(row=0, column=0, columnspan=2, pady=(10, 0))

        # Identité
        ctk.CTkLabel(self.formulaire, text="Identité complète :", font=("Arial", 16)).grid(row=1, column=0, padx=20, sticky="e")
        self.nom = ctk.CTkLabel(self.formulaire, width=350, height=40, text="Visiteurs", font=("Arial", 20))
        self.nom.grid(row=1, column=1, padx=20, sticky="w")

        # Garant
        ctk.CTkLabel(self.formulaire, text="Votre garant :", font=("Arial", 16)).grid(row=2, column=0, padx=20, sticky="e")
        self.entry_garant = ctk.CTkEntry(self.formulaire, width=350, height=40, placeholder_text="Ex: DUBOIS Vincent")
        self.entry_garant.grid(row=2, column=1, padx=20, sticky="w")
        self.entry_garant.bind("<KeyRelease>", self.update)

        # Bouton Save (en dehors de formulaire, dans main ou self)
        self.btn_save = ctk.CTkButton(self, text="ENTRER",
                                       font=("Arial", 18, "bold"), height=55, width=400, 
                                       fg_color="green", command=self.save)
        self.btn_save.pack(pady=20)

    def update(self, event=None):
        garant = self.entry_garant.get().strip()
        
        self.autoriser = False
        for user in self.tab:
            if garant.lower() == str(user['name']).lower():
                self.autoriser = True
                break

        self.preview_Garant.configure(text=garant if garant else "GARANT")

        if self.autoriser:
            self.status_indicator.configure(text="● ACCÈS OK", text_color="green")
            self.apercu.configure(border_color="green")
            self.btn_save.configure(fg_color="green")
        else:
            self.status_indicator.configure(text="○ REFUSÉ", text_color="red")
            self.apercu.configure(border_color="red")
            self.btn_save.configure(fg_color="gray")

    def save(self):
        if self.entry_garant.get().strip() == '':
            print('Veuillez entrer un nom')
            messagebox.showerror("Erreur", "Veuillez entrer un nom")

        elif self.autoriser:
            print("Vous pouvez entrer")
            self.controller.edit_main_text('Accès autorisé')
            self.controller.afficher_page("PageAccueil")

            #logique d'ouverture
            self.controller.vision.access.start_arduino(self.controller.vision.waiting_time_for_next_scan)
            self.controller.vision.access.start_led('G')
            self.controller.vision.access.audio.start_saying('authorized')

        else:
            print("Personne non trouvée: orthographe incorrecte ou personne inexistante")
            messagebox.showerror("Erreur", "Personne non trouvée: orthographe incorrecte ou personne inexistante")

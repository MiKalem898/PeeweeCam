import customtkinter as ctk
from user import User

class Utilisateur(ctk.CTkFrame):
    def __init__(self, master, users, controller):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        
        # Bouton retour
        self.btn_retour = ctk.CTkButton(self, text="← RETOUR", 
                                         command=lambda: controller.afficher_page("PageAccueil"), 
                                         font=("Arial", 20))
        self.btn_retour.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        # Frame scrollable
        self.scrolle = ctk.CTkScrollableFrame(self, width=950, height=700, 
                                             border_width=5, border_color="white")
        self.scrolle.grid(row=1, column=0, columnspan=2, padx=5, pady=10)
        self.grid_columnconfigure((0, 1), weight=1)

        #Boucle pour faire les badges des utilisateurs connu dans la base de donnée
        self.users = []
        for user in users:
            # On passe l'index 3 pour l'image, 0 pour le nom, etc.
            u = User(self.scrolle, self.controller, photo=user['photo'], 
                     id=user['name'], statut=user['class'], autoriser=user['authorized'])
            u.pack(pady=5, padx=10, fill="x")
            self.users.append(u)

    def create_add_btn(self):
        # Bouton pour ajouter (Correction : Appel de la méthode de navigation)
        self.btn_add = ctk.CTkButton(self, text="Ajouter le dernier inconnu +", font=("Arial", 20), width=30,
                                         command=lambda: self.controller.afficher_page("pageAdmin"))
        self.btn_add.grid(row=0, column=1, padx=20, pady=20, sticky="e")

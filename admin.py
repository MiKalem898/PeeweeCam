import customtkinter as ctk
from tkinter import messagebox

class Admin(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")

        self.controller = controller
        self.mdp_correct = 'Peeweefamily_'  # On stocke le bon mot de passe

        # Bouton Retour
        self.btn_retour = ctk.CTkButton(self, text="← ANNULER", 
                                         command=lambda: controller.afficher_page("PageListe"), 
                                         font=("Arial", 20))
        self.btn_retour.place(x=10, y=20)

        self.titre_admin = ctk.CTkLabel(self, text="PANEL ADMIN", font=("Arial", 35))
        self.titre_admin.pack(pady=(60, 40))

        # Cadre principal
        self.main_mdp = ctk.CTkFrame(self, width=950, height=500, border_width=2, border_color="white")
        self.main_mdp.pack(pady=(40, 20))
        self.main_mdp.pack_propagate(False)

        self.titre_mdp = ctk.CTkLabel(self.main_mdp, text="MOT DE PASSE :", font=("Arial", 35))
        self.titre_mdp.pack(pady=(60, 20))

        # Champ de saisie
        self.entry_mdp = ctk.CTkEntry(self.main_mdp, width=350, height=40, 
                                      placeholder_text="Entrez le mot de passe", show="*")
        self.entry_mdp.pack(pady=(20, 40))

        # Bouton de confirmation avec la commande de vérification
        self.enter_button = ctk.CTkButton(self.main_mdp, text="Confirmer", 
                                          fg_color="gray20",
                                          command=self.verifier_mot_de_passe)
        self.enter_button.pack(pady=20)

    def verifier_mot_de_passe(self):
        # Récupération du texte tapé par l'utilisateur
        saisie = self.entry_mdp.get()

        if saisie == self.mdp_correct:
            # Si c'est correct, on change de page
            self.controller.afficher_page("pageAjout")
            self.entry_mdp.delete(0, 'end')
        else:
            # Si c'est faux, on affiche une petite alerte (ou on change la couleur de l'entry)
            self.entry_mdp.configure(border_color="red")
            #message d'erreur comme un alert en js
            messagebox.showerror("Erreur", "Mot de passe incorrect !")
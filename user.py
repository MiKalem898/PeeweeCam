import customtkinter as ctk
from PIL import Image

class User(ctk.CTkFrame):
    def __init__(self, master, controller, photo="./IMAGE/photo_user1.jpeg", id="Nom", statut="Statut", autoriser=True):
        super().__init__(master, fg_color="transparent")

        self.id = id
        self.controller = controller

        # Configuration du cadre principal
        self.user_frame = ctk.CTkFrame(self, width=900, height=110, corner_radius=10, border_width=2, border_color="white")
        self.user_frame.grid(row=0, column=0, padx=5)
        self.user_frame.grid_propagate(False)

        # --- FIXATION DE LA DISPOSITION ---
        # On force les colonnes d'infos (2 et 3) à avoir la même largeur et à être stables
        self.user_frame.grid_columnconfigure((2, 3), weight=1, uniform="group1")
        self.user_frame.grid_columnconfigure(0, weight=0) # Image
        self.user_frame.grid_columnconfigure(1, weight=0) # Séparateur
        self.user_frame.grid_columnconfigure(4, weight=0) # Checkbox
        self.user_frame.grid_columnconfigure(5, weight=0) # Bouton Edit

        self.check_var = ctk.BooleanVar(value=autoriser)

        def checkbox_event():
            try:
                photo_user = Image.open(photo)
                img_temp = photo_user if self.check_var.get() else photo_user.convert("L")
                self.mon_img = ctk.CTkImage(light_image=img_temp, size=(100, 100))
                
                if hasattr(self, 'image_label'):
                    self.image_label.configure(image=self.mon_img)
                else:
                    self.image_label = ctk.CTkLabel(self.user_frame, image=self.mon_img, text="")
                    self.image_label.grid(row=0, column=0, rowspan=2, padx=20, pady=5)
            except:
                self.image_label = ctk.CTkLabel(self.user_frame, text="Pas d'image", width=100)
                self.image_label.grid(row=0, column=0, rowspan=2, padx=20)

        # Séparateur
        ctk.CTkFrame(self.user_frame, width=2, height=80, fg_color="white").grid(row=0, rowspan=2, column=1, pady=10)

        # Identité (Label statique "Identité:")
        ctk.CTkLabel(self.user_frame, text="Identité:", font=("Arial", 16), text_color="gray").grid(row=0, column=2, padx=20, sticky="sw")
        
        # Nom (Valeur modifiable)
        self.nom_label = ctk.CTkLabel(self.user_frame, text=id, font=("Arial", 20, "bold"))
        self.nom_label.grid(row=1, column=2, padx=20, pady=(0, 15), sticky="nw")

        # Statut (Label statique "Statut:")
        ctk.CTkLabel(self.user_frame, text="Statut:", font=("Arial", 16), text_color="gray").grid(row=0, column=3, padx=20, sticky="sw")
        
        # Classe (Valeur modifiable)
        self.classe_label = ctk.CTkLabel(self.user_frame, text=statut, font=("Arial", 18))
        self.classe_label.grid(row=1, column=3, padx=20, pady=(0, 15), sticky="nw")

        # Checkbox
        self.right_checkbox = ctk.CTkCheckBox(self.user_frame, text="Accès", command=checkbox_event, variable=self.check_var)
        self.right_checkbox.grid(row=0, column=4, rowspan=2, padx=20)
        self.right_checkbox.configure(state="disabled")
        
        checkbox_event()
        
        def modifier():
            if self.edit_button.cget("text").strip() == "✏️":
                # MODE EDITION
                t1 = self.nom_label.cget("text")
                t2 = self.classe_label.cget("text")

                self.nom_label.grid_forget()
                self.classe_label.grid_forget()

                # On utilise exactement les mêmes coordonnées grid que les labels
                self.nom_entry = ctk.CTkEntry(self.user_frame, font=("arial", 18))
                self.nom_entry.insert(0, t1)
                self.nom_entry.grid(row=1, column=2, padx=20, pady=(0, 15), sticky="new") # sticky "new" pour remplir la largeur

                self.classe_entry = ctk.CTkEntry(self.user_frame, font=("arial", 16))
                self.classe_entry.insert(0, t2)
                self.classe_entry.grid(row=1, column=3, padx=20, pady=(0, 15), sticky="new")

                self.right_checkbox.configure(state="normal")
                self.edit_button.configure(text="✅")

            elif self.edit_button.cget("text").strip() == "✅":
                # RETOUR EN MODE NORMAL
                new_n = self.nom_entry.get()
                new_c = self.classe_entry.get()

                self.nom_entry.destroy()
                self.classe_entry.destroy()

                self.nom_label.configure(text=new_n)
                self.nom_label.grid(row=1, column=2, padx=20, pady=(0, 15), sticky="nw")

                self.classe_label.configure(text=new_c)
                self.classe_label.grid(row=1, column=3, padx=20, pady=(0, 15), sticky="nw")

                self.right_checkbox.configure(state="disabled")
                self.edit_button.configure(text="✏️")


                # maj de la db
                new_infos = {
                    'name': new_n,
                    'class': new_c,
                    'authorized': self.check_var.get()
                }

                controller.tab.update(new_infos, controller.User.name == self.id)
                controller.vision.get_users_and_embeddings()
                controller.get_users()
                self.id = new_n

        # Bouton Edit
        self.edit_button = ctk.CTkButton(self.user_frame, text="✏️", width=30, font=("arial", 16, "bold"), command=modifier)
        self.edit_button.grid(row=0, rowspan=2, column=5, padx=10, sticky="e")

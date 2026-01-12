import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from facture_seiko import FactureMouvementAbsolu, get_next_order_number
import webbrowser
import os

class FactureApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Facturation Seiko - Gestion des devis et factures")
        self.geometry("1000x700")
        self.minsize(900, 600)
        
        # Style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_style()
        
        # Variables
        self.numero_commande = get_next_order_number()
        self.articles = []
        
        # Configuration de la grille
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        self.create_widgets()
        
    def configure_style(self):
        """Configure le style de l'interface"""
        # Couleurs
        self.colors = {
            'primary': '#2c3e50',
            'secondary': '#34495e',
            'accent': '#3498db',
            'success': '#2ecc71',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'light': '#ecf0f1',
            'dark': '#2c3e50',
            'white': '#ffffff'
        }
        
        # Configuration des styles
        self.style.configure('TFrame', background=self.colors['light'])
        self.style.configure('TLabel', background=self.colors['light'], font=('Helvetica', 10))
        self.style.configure('TButton', font=('Helvetica', 10))
        self.style.configure('Header.TLabel', 
                           font=('Helvetica', 14, 'bold'), 
                           background=self.colors['primary'], 
                           foreground='white',
                           padding=10)
        self.style.configure('Accent.TButton', 
                           font=('Helvetica', 10, 'bold'), 
                           background=self.colors['accent'],
                           foreground='white')
        
    def create_widgets(self):
        # En-tête
        header_frame = ttk.Frame(self, style='Header.TFrame')
        header_frame.grid(row=0, column=0, sticky='ew', columnspan=2)
        
        ttk.Label(
            header_frame, 
            text=f"Facturation Seiko - Commande {self.numero_commande}",
            style='Header.TLabel'
        ).pack(expand=True, fill='x')
        
        # Conteneur principal
        main_frame = ttk.Frame(self)
        main_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Panneau de gauche - Informations client
        client_frame = ttk.LabelFrame(main_frame, text="Informations client", padding=10)
        client_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        # Champs client
        ttk.Label(client_frame, text="Nom du client :").grid(row=0, column=0, sticky='w', pady=2)
        self.nom_client = ttk.Entry(client_frame, width=30)
        self.nom_client.grid(row=0, column=1, sticky='ew', pady=2, padx=5)
        
        ttk.Label(client_frame, text="Adresse :").grid(row=1, column=0, sticky='w', pady=2)
        self.adresse = ttk.Entry(client_frame, width=30)
        self.adresse.grid(row=1, column=1, sticky='ew', pady=2, padx=5)
        
        ttk.Label(client_frame, text="Code postal :").grid(row=2, column=0, sticky='w', pady=2)
        self.code_postal = ttk.Entry(client_frame, width=15)
        self.code_postal.grid(row=2, column=1, sticky='w', pady=2, padx=5)
        
        ttk.Label(client_frame, text="Ville :").grid(row=3, column=0, sticky='w', pady=2)
        self.ville = ttk.Entry(client_frame, width=30)
        self.ville.grid(row=3, column=1, sticky='ew', pady=2, padx=5)
        
        # Panneau de droite - Articles
        articles_frame = ttk.LabelFrame(main_frame, text="Articles", padding=10)
        articles_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        
        # Boutons d'action
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, sticky='ew', pady=10)
        
        ttk.Button(
            button_frame, 
            text="Ajouter un article", 
            command=self.ajouter_article,
            style='Accent.TButton'
        ).pack(side='left', padx=5)
        
        ttk.Button(
            button_frame, 
            text="Générer la facture", 
            command=self.generer_facture,
            style='Accent.TButton'
        ).pack(side='left', padx=5)
        
        # Tableau des articles
        self.tree = ttk.Treeview(
            main_frame,
            columns=('description', 'reference', 'quantite', 'prix_unitaire', 'total'),
            show='headings',
            selectmode='browse'
        )
        
        # Configuration des colonnes
        self.tree.heading('description', text='Description')
        self.tree.heading('reference', text='Référence')
        self.tree.heading('quantite', text='Qté')
        self.tree.heading('prix_unitaire', text='Prix unitaire')
        self.tree.heading('total', text='Total HT')
        
        # Ajustement de la largeur des colonnes
        self.tree.column('description', width=200)
        self.tree.column('reference', width=100, anchor='center')
        self.tree.column('quantite', width=50, anchor='center')
        self.tree.column('prix_unitaire', width=100, anchor='e')
        self.tree.column('total', width=100, anchor='e')
        
        self.tree.grid(row=2, column=0, columnspan=2, sticky='nsew', pady=10)
        
        # Barre de défilement
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=2, column=2, sticky='ns')
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Panneau de statut
        status_frame = ttk.Frame(self)
        status_frame.grid(row=2, column=0, sticky='ew', padx=10, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Prêt")
        self.status_label.pack(side='left')
        
        # Configuration du redimensionnement
        self.rowconfigure(2, weight=1)
        
    def ajouter_article(self):
        """Ouvre une fenêtre pour ajouter un nouvel article"""
        dialog = AjoutArticleDialog(self)
        self.wait_window(dialog)
        
        if dialog.article_data:
            self.articles.append(dialog.article_data)
            self.maj_tableau_articles()
    
    def maj_tableau_articles(self):
        """Met à jour le tableau des articles"""
        # Vider le tableau
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Ajouter les articles
        for article in self.articles:
            total = article['quantite'] * article['prix_unitaire']
            self.tree.insert('', 'end', values=(
                article['description'],
                article['reference'],
                article['quantite'],
                f"{article['prix_unitaire']:.2f} €",
                f"{total:.2f} €"
            ))
    
    def generer_facture(self):
        """Génère la facture au format PDF"""
        # Vérifier les données
        if not self.articles:
            messagebox.showerror("Erreur", "Veuillez ajouter au moins un article.")
            return
            
        if not self.nom_client.get():
            messagebox.showerror("Erreur", "Veuillez renseigner le nom du client.")
            return
        
        # Préparer les données
        donnees = {
            'numero_commande': self.numero_commande,
            'date_commande': datetime.now().strftime("%d/%m/%Y"),
            'client': {
                'nom': self.nom_client.get(),
                'adresse': self.adresse.get(),
                'code_postal': self.code_postal.get(),
                'ville': self.ville.get()
            },
            'articles': self.articles
        }
        
        try:
            # Créer la facture
            facture = FactureMouvementAbsolu(donnees)
            
            # Ajouter les articles
            for article in self.articles:
                composants = [{
                    'nom': article['description'],
                    'reference': article['reference'],
                    'prix': article['prix_unitaire']
                }]
                
                facture.ajouter_article(
                    modele=article['description'],
                    reference=article['reference'],
                    composants=composants,
                    quantite=article['quantite']
                )
            
            # Générer le PDF
            nom_fichier = f"facture_{self.numero_commande}.pdf"
            facture.generer_facture(nom_fichier)
            
            # Afficher un message de succès
            messagebox.showinfo("Succès", f"La facture a été générée avec succès : {nom_fichier}")
            
            # Réinitialiser le formulaire
            self.reinitialiser_formulaire()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")
    
    def reinitialiser_formulaire(self):
        """Réinitialise le formulaire après génération de la facture"""
        # Réinitialiser les champs
        self.nom_client.delete(0, 'end')
        self.adresse.delete(0, 'end')
        self.code_postal.delete(0, 'end')
        self.ville.delete(0, 'end')
        
        # Vider les articles
        self.articles = []
        self.maj_tableau_articles()
        
        # Générer un nouveau numéro de commande
        self.numero_commande = get_next_order_number()
        self.title(f"Facturation Seiko - Commande {self.numero_commande}")
        
        self.status_label.config(text="Nouvelle facture prête")


class AjoutArticleDialog(tk.Toplevel):
    """Fenêtre de dialogue pour ajouter un nouvel article"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.article_data = None
        
        self.title("Ajouter un article")
        self.geometry("500x400")
        self.resizable(False, False)
        
        # Variables
        self.description = tk.StringVar()
        self.reference = tk.StringVar()
        self.quantite = tk.StringVar(value="1")
        self.prix_unitaire = tk.StringVar()
        
        # Configuration de la grille
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        
        # Widgets
        ttk.Label(self, text="Description :").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        ttk.Entry(self, textvariable=self.description, width=40).grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        ttk.Label(self, text="Référence :").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        ttk.Entry(self, textvariable=self.reference, width=20).grid(row=1, column=1, sticky='w', padx=5, pady=5)
        
        ttk.Label(self, text="Quantité :").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        ttk.Spinbox(self, from_=1, to=100, textvariable=self.quantite, width=5).grid(row=2, column=1, sticky='w', padx=5, pady=5)
        
        ttk.Label(self, text="Prix unitaire (€) :").grid(row=3, column=0, sticky='e', padx=5, pady=5)
        ttk.Entry(self, textvariable=self.prix_unitaire, width=10).grid(row=3, column=1, sticky='w', padx=5, pady=5)
        
        # Boutons
        button_frame = ttk.Frame(self)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(
            button_frame, 
            text="Annuler", 
            command=self.destroy
        ).pack(side='right', padx=5)
        
        ttk.Button(
            button_frame, 
            text="Ajouter", 
            command=self.valider_article,
            style='Accent.TButton'
        ).pack(side='right', padx=5)
        
        # Centrer la fenêtre
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
        # Mettre le focus sur le premier champ
        self.focus_force()
        self.grab_set()
        self.description.focus_set()
    
    def valider_article(self):
        """Valide l'ajout de l'article"""
        try:
            # Vérifier les champs obligatoires
            if not self.description.get():
                messagebox.showerror("Erreur", "Veuillez saisir une description pour l'article.")
                return
                
            if not self.prix_unitaire.get():
                messagebox.showerror("Erreur", "Veuillez saisir un prix unitaire.")
                return
                
            # Vérifier le format des nombres
            try:
                quantite = int(self.quantite.get())
                if quantite <= 0:
                    raise ValueError("La quantité doit être supérieure à zéro.")
                    
                prix = float(self.prix_unitaire.get().replace(',', '.'))
                if prix <= 0:
                    raise ValueError("Le prix doit être supérieur à zéro.")
                    
            except ValueError as e:
                messagebox.showerror("Erreur", f"Format invalide : {str(e)}")
                return
                
            # Enregistrer les données de l'article
            self.article_data = {
                'description': self.description.get(),
                'reference': self.reference.get(),
                'quantite': quantite,
                'prix_unitaire': prix
            }
            
            # Fermer la fenêtre
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")


if __name__ == "__main__":
    app = FactureApp()
    app.mainloop()

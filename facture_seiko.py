from fpdf import FPDF, XPos, YPos
from datetime import datetime
import os
import platform
from dateutil.relativedelta import relativedelta
from colorama import init, Fore, Style

# Initialisation de colorama
init()

class Color:
    # Couleurs de base
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    
    # Couleurs de texte
    BLACK = '\033[30m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    LIGHT_GRAY = '\033[37m'
    BLUE = '\033[34m'
    LIGHT_BLUE = '\033[94m'
    CYAN = '\033[36m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    ORANGE = '\033[38;5;208m'
    RED = '\033[31m'
    
    # Arrière-plans
    BG_WHITE = '\033[47m'
    BG_LIGHT_GRAY = '\033[47;1m'
    BG_BLUE = '\033[44m'
    BG_GRAY = '\033[100m'
    
    # Styles spéciaux
    SELECTED = '\033[48;5;153;38;5;0m'  # Fond bleu clair, texte noir
    HIGHLIGHT = '\033[48;5;153;38;5;0m'  # Surlignage bleu clir
    
    # Fonctions utilitaires
    @staticmethod
    def rgb(r, g, b):
        return f'\033[38;2;{r};{g};{b}m'
    
    @staticmethod
    def bg_rgb(r, g, b):
        return f'\033[48;2;{r};{g};{b}m'

def clear_screen():
    """Efface l'écran du terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Affiche l'en-tête stylisé de l'application"""
    clear_screen()
    
    # Définition des couleurs
    title_color = Color.rgb(0, 150, 255)  # Bleu clair
    subtitle_color = Color.rgb(100, 200, 255)  # Bleu très clair
    
    # Logo ASCII art stylisé
    logo = f"""
    {title_color}███████╗███████╗██╗██╗  ██╗ ██████╗     ███╗   ███╗ ██████╗ ██████╗ {Color.RESET}
    {title_color}██╔════╝██╔════╝██║██║ ██╔╝██╔═══██╗    ████╗ ████║██╔═══██╗██╔══██╗{Color.RESET}
    {title_color}███████╗█████╗  ██║█████╔╝ ██║   ██║    ██╔████╔██║██║   ██║██║  ██║{Color.RESET}
    {title_color}╚════██║██╔══╝  ██║██╔═██╗ ██║   ██║    ██║╚██╔╝██║██║   ██║██║  ██║{Color.RESET}
    {title_color}███████║███████╗██║██║  ██╗╚██████╔╝    ██║ ╚═╝ ██║╚██████╔╝██████╔╝{Color.RESET}
    {title_color}╚══════╝╚══════╝╚═╝╚═╝  ╚═╝ ╚═════╝     ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ {Color.RESET}
    
    {subtitle_color}         GÉNÉRATEUR DE FACTURES PROFESSIONNELLES{Color.RESET}
    {Color.GRAY}{'─' * 60}{Color.RESET}
    """
    
    # Affichage du logo
    print(logo)

def print_section(title):
    """Affiche un titre de section"""
    print(f"\n{Color.BOLD}{Color.BLUE}  {title.upper()}{Color.RESET}")
    print(f"{Color.GRAY}  {'─' * (len(title) + 1)}{Color.RESET}")

def input_style(prompt, default=""):
    """Style pour les champs de saisie"""
    prompt_text = f"{Color.BLUE}?{Color.RESET} {Color.BOLD}{prompt}{Color.RESET}"
    if default:
        prompt_text += f" {Color.GRAY}({default}){Color.RESET}"
    prompt_text += f" {Color.DIM}›{Color.RESET} "
    
    if default:
        user_input = input(prompt_text)
        return user_input if user_input.strip() else default
    return input(prompt_text)

def print_success(message):
    """Affiche un message de succès"""
    print(f"\n{Color.GREEN}✓ {message}{Color.RESET}")

def print_warning(message):
    """Affiche un message d'avertissement"""
    print(f"\n{Color.ORANGE}⚠ {message}{Color.RESET}")

def print_error(message):
    """Affiche un message d'erreur"""
    print(f"\n{Color.RED}✗ {message}{Color.RESET}")

def print_item(description, value, indent=0):
    """Affiche un élément avec mise en forme"""
    indent_str = " " * indent
    print(f"{indent_str}{Color.GRAY}•{Color.RESET} {Color.BOLD}{description}:{Color.RESET} {value}")

def get_next_order_number():
    """Génère un numéro de commande au format SM-AAAANN-NNNN"""
    COUNTER_FILE = 'last_order_number.txt'
    current_date = datetime.now()
    year_month = current_date.strftime("%Y%m")
    
    try:
        # Lire le dernier numéro
        with open(COUNTER_FILE, 'r') as f:
            last_date, last_number = f.read().strip().split('-')
            last_number = int(last_number)
            
            # Si c'est le même mois, on incrémente
            if last_date == year_month:
                new_number = last_number + 1
            else:  # Sinon on recommence à 1
                new_number = 1
    except (FileNotFoundError, ValueError):
        # Fichier inexistant ou corrompu, on commence à 1
        new_number = 1
    
    # Sauvegarder le nouveau numéro
    with open(COUNTER_FILE, 'w') as f:
        f.write(f"{year_month}-{new_number:04d}")
    
    # Retourner le numéro formaté
    return f"SM-{year_month}-{new_number:04d}"

class FactureSeiko:
    def __init__(self):
        self.pdf = FPDF()
        self.donnees = {}
        self.articles = []
        
    def clean_price_input(self, price_str):
        """Nettoie et convertit une chaîne de prix en nombre"""
        try:
            # Supprimer les espaces et le symbole €
            price_str = price_str.replace(' ', '').replace('€', '')
            # Remplacer la virgule par un point si nécessaire
            price_str = price_str.replace(',', '.')
            return float(price_str)
        except ValueError:
            return None

    def clean_quantity_input(self, qty_str):
        """Nettoie et convertit une quantité en nombre entier"""
        try:
            return int(qty_str.strip())
        except ValueError:
            return None

    def demander_articles(self):
        print_header()
        print_section("Saisie des articles")
        print("Appuyez sur Entrée pour terminer la saisie\n")
        
        while True:
            # En-tête de l'article avec coins arrondis
            print(f"\n{Color.GRAY}╭{'─'*56}╮{Color.RESET}")
            print(f"{Color.GRAY}│{Color.RESET} {Color.BOLD}NOUVEL ARTICLE{Color.RESET}{' '*(56-14)} {Color.GRAY}│{Color.RESET}")
            print(f"{Color.GRAY}╰{'─'*56}╯{Color.RESET}")
            
            # Modèle
            print(f"\n{Color.BOLD}Modèles courants :{Color.RESET}")
            print(f"  {Color.GRAY}•{Color.RESET} Dayjust")
            print(f"  {Color.GRAY}•{Color.RESET} Submariner")
            print(f"  {Color.GRAY}•{Color.RESET} GMT-Master")
            modele = input_style("Modèle de la montre").strip()
            
            # Vérifier si l'utilisateur veut arrêter
            if not modele:
                if self.articles:
                    break
                print_warning("Vous devez ajouter au moins un article.")
                continue
                
            # Référence
            print(f"\n{Color.BOLD}Exemples de référence pour {modele.upper()} :{Color.RESET}")
            print(f"  {Color.GRAY}•{Color.RESET} SNXS79, SNK809, SRPE55, etc.")
            reference = input_style("Référence de la montre").strip()
            if not reference:
                if self.articles:
                    break
                print_warning("La référence est obligatoire pour le premier article.")
                continue
            
            # Couleur
            print("\nCouleurs courantes: Bleu, Noir, Vert, Bleu Fumé, Noir Mat, Bleu Marin, Or, Argent, Bicolore")
            couleur_cadran = input("Couleur du cadran : ").strip()
            if not couleur_cadran:
                if self.articles:
                    break
                continue
            
            # Référence du mouvement
            print(f"\n{Color.BOLD}Référence du mouvement :{Color.RESET}")
            print(f"  {Color.GRAY}•{Color.RESET} NH35 (Miyota 8N24, mouvement automatique)")
            print(f"  {Color.GRAY}•{Color.RESET} 4R36 (Mouvement automatique avec réserve de marche)")
            print(f"  {Color.GRAY}•{Color.RESET} 7S26 (Mouvement automatique Seiko de base)")
            print(f"  {Color.GRAY}•{Color.RESET} VK64 (Mouvement chronographe à quartz)")
            mouvement = input_style("Référence du mouvement (ex: NH35)", "NH35").strip().upper() or "NH35"
            
            # Prix
            while True:
                try:
                    prix_str = input_style("Prix unitaire (en EUR)")
                    if not prix_str:
                        print_warning("Le prix est obligatoire.")
                        continue
                    prix = float(prix_str.replace(',', '.'))
                    if prix > 0:
                        break
                    print_error("Le prix doit être supérieur à 0.")
                except ValueError:
                    print_error("Veuillez entrer un nombre valide.")
            
            # Quantité
            while True:
                try:
                    quantite_str = input_style("Quantité", "1")
                    quantite = int(quantite_str or "1")
                    if quantite > 0:
                        break
                    print_error("La quantité doit être supérieure à 0.")
                except ValueError:
                    print_error("Veuillez entrer un nombre entier valide.")
            
            # Ajouter l'article à la liste
            article = {
                'modele': modele,
                'reference': reference,
                'mouvement': mouvement.capitalize(),
                'prix': prix,
                'quantite': quantite
            }
            self.articles.append(article)
            
            # Afficher le récapitulatif
            print_success("Article ajouté avec succès !")
            print(f"\n{Color.BOLD}Récapitulatif de l'article :{Color.RESET}")
            print(f"  {Color.GRAY}┌{'─'*54}┐{Color.RESET}")
            print_item("Modèle", modele, 4)
            print(f"  {Color.GRAY}│{Color.RESET}")
            print_item("Référence", reference, 4)
            print(f"  {Color.GRAY}│{Color.RESET}")
            print_item("Mouvement", mouvement.capitalize(), 4)
            print(f"  {Color.GRAY}│{Color.RESET}")
            print_item("Prix unitaire", f"{prix:.2f} EUR", 4)
            print(f"  {Color.GRAY}│{Color.RESET}")
            print_item("Quantité", quantite, 4)
            print(f"  {Color.GRAY}└{'─'*54}┘{Color.RESET}")
            print(f"\n  {Color.BOLD}Total pour cet article :{Color.RESET} {Color.GREEN}{prix * quantite:.2f} EUR{Color.RESET}")
            
            # Demander si on continue
            continuer = input("\nAppuyez sur Entrée pour ajouter un autre article, ou écrivez 'non' pour terminer : ").strip().lower()
            if continuer in ('n', 'non', 'fin', 'stop'):
                break
        
        # Si aucun article n'a été ajouté, on quitte
        if not self.articles:
            print("\nAucun article n'a été ajouté. Annulation de la facture.")
            exit()
            
        # Demander les informations du client
        print("\n" + "="*50)
        print("INFORMATIONS CLIENT")
        print("="*50)
        
        self.donnees['client_nom'] = input("\nNom complet du client : ").strip()
        self.donnees['client_prenom'] = ""  # Gardé pour la rétrocompatibilité
        self.donnees['client_adresse'] = input("Adresse : ").strip()
        self.donnees['client_cp'] = input("Code postal : ").strip()
        self.donnees['client_ville'] = input("Ville : ").strip()
        
        print("\n=== Détails de la commande ===")
        self.donnees['num_commande'] = get_next_order_number()
        print(f"Numéro de commande généré : {self.donnees['num_commande']}")
        self.donnees['date_facture'] = datetime.now().strftime("%d/%m/%Y")
    
    def generer_facture(self):
        # Palette de couleurs
        NOIR = (40, 40, 40)           # Noir doux
        GRIS_CLAIR = (245, 245, 245)  # Gris très clair pour les fonds
        GRIS_MOYEN = (200, 200, 200)  # Gris pour les séparateurs
        BLANC = (255, 255, 255)       # Blanc pur
        
        # Configuration de la police
        try:
            # Essayer d'utiliser Arial pour un rendu plus propre
            self.pdf.add_font('Arial', '', 'Arial.ttf', uni=True)
            self.pdf.add_font('Arial', 'B', 'Arial Bold.ttf', uni=True)
            font_family = 'Arial'
        except:
            # Fallback sur Helvetica si Arial n'est pas disponible
            font_family = 'Helvetica'
        
        # Configuration de la page
        self.pdf.add_page()
        self.pdf.set_auto_page_break(auto=True, margin=30)
        self.pdf.set_margins(25, 25, 25)
        
        # Fond de page en gris très clair
        self.pdf.set_fill_color(*GRIS_CLAIR)
        self.pdf.rect(0, 0, 210, 297, 'F')  # A4: 210x297mm
        
        # Zone de contenu blanche avec bordure grise
        self.pdf.set_fill_color(*BLANC)
        self.pdf.rect(10, 10, 190, 277, 'F')
        
        # En-tête avec logo et informations
        self.pdf.rect(10, 10, 190, 40, 'F')  # Hauteur réduite pour l'en-tête
        
        # Cadre gris autour de la zone de contenu
        self.pdf.set_draw_color(200, 200, 200)
        self.pdf.rect(10, 10, 190, 277)
        
        # Titre principal
        self.pdf.set_font(font_family, 'B', 24)
        self.pdf.set_text_color(40, 40, 40)  # Noir doux
        self.pdf.set_xy(15, 15)
        self.pdf.cell(0, 10, 'SEIKO MOD', 0, 1, 'L')
        
        # Sous-titre
        self.pdf.set_font(font_family, '', 10)
        self.pdf.set_text_color(100, 100, 100)  # Gris foncé
        self.pdf.set_xy(15, 25)
        self.pdf.cell(0, 6, 'Modifications et personnalisations horlogères', 0, 1, 'L')
        
        # Ligne de séparation sous l'en-tête
        self.pdf.set_draw_color(*GRIS_MOYEN)
        self.pdf.line(15, 38, 195, 38)
        
        # Titre FACTURE à droite
        self.pdf.set_font(font_family, 'B', 20)
        self.pdf.set_text_color(*NOIR)
        self.pdf.set_xy(120, 15)
        self.pdf.cell(0, 10, 'FACTURE', 0, 1, 'R')
        
        # Numéro de facture et date
        self.pdf.set_font(font_family, '', 10)
        self.pdf.set_xy(15, 50)  # Position ajustée
        self.pdf.set_text_color(100, 100, 100)  # Gris foncé
        self.pdf.cell(0, 6, f'FACTURE N°{self.donnees["num_commande"]}', 0, 1, 'L')
        self.pdf.set_x(15)
        self.pdf.cell(0, 6, f'Date : {self.donnees["date_facture"]}', 0, 1, 'L')
        
        # Section client - Positionnement précis
        self.pdf.set_xy(15, 70)  # Position remontée
        self.pdf.set_font(font_family, '', 9)
        self.pdf.set_text_color(150, 150, 150)  # Gris moyen
        self.pdf.cell(0, 6, 'FACTURÉ À', 0, 1, 'L')
        
        # Informations client
        self.pdf.set_font(font_family, '', 10)
        y_client = self.pdf.get_y()
        self.pdf.set_xy(25, y_client)
        self.pdf.set_text_color(*NOIR)
        self.pdf.multi_cell(0, 6, f"{self.donnees['client_nom']}\n{self.donnees['client_adresse']}\n{self.donnees['client_cp']} {self.donnees['client_ville']}")
        
        # Position de départ du tableau (après la section client)
        y_tableau = max(y_client + 30, 140)
        
        # Largeurs des colonnes ajustées
        w_qte = 15          # Colonne quantité
        w_designation = 80  # Colonne désignation
        w_mouvement = 28    # Légèrement réduit
        w_prix = 30         # Colonne prix unitaire
        w_total = 30        # Réduit pour s'adapter au cadre
        
        # Position X de départ du tableau (aligné à gauche avec la marge)
        start_x = 10  # Marge gauche de 10mm
        
        # En-tête du tableau
        self.pdf.set_xy(start_x, y_tableau)
        self.pdf.set_font(font_family, 'B', 9)
        self.pdf.set_text_color(100, 100, 100)  # Gris foncé
        
        # En-têtes de colonnes
        self.pdf.cell(w_qte, 10, 'QTÉ', 0, 0, 'C')
        self.pdf.cell(5)  # Petit espace
        self.pdf.cell(w_designation, 10, 'DÉSIGNATION', 0, 0, 'L')
        self.pdf.cell(w_mouvement, 10, 'MOUVEMENT', 0, 0, 'C')
        self.pdf.cell(w_prix, 10, 'PRIX UNIT.', 0, 0, 'R')
        self.pdf.cell(w_total, 10, 'TOTAL', 0, 1, 'R')
        
        # Ligne de séparation sous l'en-tête
        self.pdf.set_draw_color(*GRIS_MOYEN)
        y_line = self.pdf.get_y()
        total_width = w_qte + 5 + w_designation + w_mouvement + w_prix + w_total
        self.pdf.line(start_x, y_line, start_x + total_width, y_line)
        self.pdf.ln(5)
        
        # Détail des articles
        self.pdf.set_font(font_family, '', 10)
        y_article = self.pdf.get_y()
        
        for i, article in enumerate(self.articles):
            if y_article > 250:  # Vérifier l'espace restant
                self.pdf.add_page()
                y_article = 30
            
            # Calcul du total de la ligne
            total_ligne = article['prix'] * article['quantite']
            hauteur = 8  # Hauteur réduite pour un look plus aéré
            
            # Couleur du texte
            self.pdf.set_text_color(*NOIR)
            
            # Position X de départ pour les articles
            x_pos = start_x
            
            # Quantité
            self.pdf.set_xy(x_pos, y_article)
            self.pdf.cell(w_qte, hauteur, str(article['quantite']), 0, 0, 'C')
            x_pos += w_qte + 5  # Ajout d'un espace après la quantité
            
            # Désignation avec gestion du texte trop long
            designation = f"{article['modele']} - {article['reference']}"
            if len(designation) > 30:
                designation = designation[:27] + '...'
            
            self.pdf.set_xy(x_pos, y_article)
            self.pdf.cell(w_designation, hauteur, designation, 0, 0, 'L')
            x_pos += w_designation
            
            # Mouvement
            self.pdf.set_xy(x_pos, y_article)
            self.pdf.cell(w_mouvement, hauteur, article['mouvement'], 0, 0, 'C')
            x_pos += w_mouvement
            
            # Prix unitaire
            self.pdf.set_xy(x_pos, y_article)
            self.pdf.cell(w_prix, hauteur, f"{article['prix']:,.2f} EUR".replace(',', ' '), 0, 0, 'R')
            x_pos += w_prix
            
            # Total ligne
            self.pdf.set_xy(x_pos, y_article)
            self.pdf.cell(w_total, hauteur, f"{total_ligne:,.2f} EUR".replace(',', ' '), 0, 1, 'R')
            
            # Ligne de séparation fine
            if i < len(self.articles) - 1:  # Pas de ligne après le dernier article
                self.pdf.set_draw_color(*GRIS_MOYEN)
                self.pdf.set_line_width(0.1)
                self.pdf.line(start_x, y_article + hauteur + 3, 
                            start_x + total_width, 
                            y_article + hauteur + 3)
            
            # Préparer la position Y pour la prochaine ligne
            y_article += hauteur + 5
        
        # Section des totaux (positionnement dynamique)
        y_totals = max(y_article + 20, self.pdf.get_y() + 20)
        
        # Vérifier si on a assez d'espace, sinon nouvelle page
        if y_totals > 250:
            self.pdf.add_page()
            y_totals = 30
        
        # Ligne de séparation avant les totaux
        self.pdf.set_draw_color(*GRIS_MOYEN)
        self.pdf.line(25, y_totals - 10, 185, y_totals - 10)
        
        # Détail des totaux
        total_ht = sum(article['prix'] * article['quantite'] for article in self.articles)
        
        # Total
        self.pdf.set_xy(25, y_totals)
        self.pdf.set_font(font_family, 'B', 12)
        self.pdf.set_text_color(*NOIR)
        self.pdf.cell(50, 10, 'TOTAL', 0, 0, 'L')
        self.pdf.set_x(155)
        self.pdf.cell(30, 10, f"{total_ht:.2f} EUR", 0, 1, 'R')
        
        # Ligne de séparation sous le total
        self.pdf.set_draw_color(*NOIR)
        self.pdf.set_line_width(0.5)
        self.pdf.line(155, y_totals + 12, 185, y_totals + 12)
        
        # Message de remerciement
        y_thanks = y_totals + 30
        if y_thanks > 250:
            self.pdf.add_page()
            y_thanks = 30
            
        self.pdf.set_xy(25, y_thanks)
        self.pdf.set_font(font_family, '', 9)
        self.pdf.set_text_color(100, 100, 100)
        self.pdf.multi_cell(160, 5, "Merci pour votre confiance.")
        
        # Pied de page
        self.pdf.set_y(-15)
        self.pdf.set_font(font_family, '', 7)
        self.pdf.set_text_color(150, 150, 150)
        self.pdf.cell(0, 10, f'Facture générée le {datetime.now().strftime("%d/%m/%Y à %H:%M")}', 0, 0, 'C')
        
        # Création du dossier factures s'il n'existe pas
        os.makedirs('factures', exist_ok=True)
        
        # Nom du fichier
        nom_client = ''.join(c if c.isalnum() else '_' for c in self.donnees['client_nom'])
        nom_fichier = f"factures/Facture_{self.donnees['num_commande']}_{nom_client}.pdf"
        
        # Sauvegarde du PDF
        self.pdf.output(nom_fichier)
        
        return nom_fichier
        
    def ouvrir_facture(self, nom_fichier):
        chemin_absolu = os.path.abspath(nom_fichier)
        print(f"\nFacture générée avec succès : {chemin_absolu}")
        
        # Ouvrir le fichier automatiquement
        if platform.system() == 'Darwin':  # macOS
            os.system(f'open "{chemin_absolu}"')
        elif platform.system() == 'Windows':  # Windows
            os.startfile(chemin_absolu)
        else:  # Linux
            os.system(f'xdg-open "{chemin_absolu}"')

def main():
    print_header()
    print(f"  {Color.BLUE}Créez des factures professionnelles pour vos montres Seiko{Color.RESET}\n")
    print(f"  {Color.GRAY}Ce programme vous guide pas à pas pour créer une facture détaillée.{Color.RESET}\n")
    
    # Délai d'attente pour l'effet de démarrage
    import time
    print(f"  {Color.GRAY}Chargement...{Color.RESET}", end="\r")
    time.sleep(0.5)
    
    facture = FactureSeiko()
    
    # Démarrer la saisie des articles
    facture.demander_articles()
    
    # Vérifier si des articles ont été ajoutés
    if not facture.articles:
        print_error("Aucun article n'a été ajouté. La facture n'a pas été créée.")
        return
    
    # Générer le PDF
    try:
        print_section("Génération de la facture")
        
        # Animation de chargement
        print(f"  {Color.GRAY}Génération en cours ", end="", flush=True)
        for _ in range(3):
            time.sleep(0.3)
            print(f"{Color.GRAY}.{Color.RESET}", end="", flush=True)
        print("\r", end="")
        
        # Génération de la facture
        nom_fichier = facture.generer_facture()
        
        # Affichage du succès
        print(f"  {Color.GREEN}✓ Facture générée avec succès{Color.RESET}\n")
        print(f"  {Color.BOLD}Emplacement :{Color.RESET}")
        print(f"  {Color.CYAN}→{Color.RESET} {os.path.abspath(nom_fichier)}\n")
        
        # Demander si on veut ouvrir le PDF
        if input_style("\nOuvrir la facture ? (o/n)").lower() in ('o', 'oui'):
            facture.ouvrir_facture(nom_fichier)
            
    except Exception as e:
        print_error(f"Une erreur est survenue : {str(e)}")

if __name__ == "__main__":
    main()

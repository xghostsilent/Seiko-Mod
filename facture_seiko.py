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

    def ajouter_article(self, modele, reference, mouvement, couleur, prix, quantite=1):
        """Ajoute un article directement à la facture
        
        Args:
            modele (str): Modèle de la montre (ex: 'Seiko 5 Sports')
            reference (str): Référence du modèle (ex: 'SRPD55K1')
            mouvement (str): Référence du mouvement (ex: '4R36')
            couleur (str): Couleur du cadran
            prix (float): Prix unitaire
            quantite (int, optional): Quantité. Par défaut à 1.
        """
        self.articles.append({
            'modele': modele,
            'reference': reference,
            'mouvement': mouvement,
            'couleur': couleur,
            'prix': float(prix),
            'quantite': int(quantite)
        })

    def generer_facture(self):
        # Palette de couleurs raffinée
        NOIR = (30, 30, 30)           # Noir profond
        GRIS_FONCE = (100, 100, 100)  # Gris foncé pour le texte secondaire
        GRIS_CLAIR = (245, 245, 245)  # Gris très clair pour les fonds
        BLEU_SEIKO = (0, 85, 150)     # Bleu Seiko officiel
        BLEU_CLAIR = (200, 225, 245)  # Bleu clair pour les en-têtes
        BLANC = (255, 255, 255)       # Blanc pur
        
        # Configuration des polices
        try:
            # Essayer d'utiliser des polices professionnelles
            self.pdf.add_font('Helvetica', '', 'Helvetica.ttf', uni=True)
            self.pdf.add_font('Helvetica', 'B', 'Helvetica-Bold.ttf', uni=True)
            self.pdf.set_font('Helvetica', '', 10)
        except:
            # Fallback sur Arial si Helvetica n'est pas disponible
            try:
                self.pdf.add_font('Arial', '', 'Arial.ttf', uni=True)
                self.pdf.add_font('Arial', 'B', 'Arial Bold.ttf', uni=True)
                self.pdf.set_font('Arial', '', 10)
            except:
                # Fallback final sur la police par défaut
                self.pdf.set_font('Arial', '', 10)
        
        # Création du dossier factures s'il n'existe pas
        if not os.path.exists('factures'):
            os.makedirs('factures')
        
        # Nom du fichier basé sur la référence de commande
        nom_fichier = f"factures/facture_{self.donnees['num_commande']}.pdf"
        
        # Création d'une nouvelle instance FPDF avec des marges personnalisées
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=20)
        self.pdf.add_page()
        
        # Définition des marges
        margin_left = 15
        margin_right = 15
        margin_top = 15
        page_width = self.pdf.w - 2 * margin_left
        
        # En-tête de la facture
        self.pdf.set_fill_color(*BLEU_SEIKO)
        self.pdf.set_text_color(*BLANC)
        self.pdf.set_font('Helvetica', 'B', 24)
        self.pdf.cell(0, 15, 'SEIKO MOD', 0, 1, 'R', fill=True)
        
        # Ligne de séparation sous l'en-tête
        self.pdf.set_draw_color(*BLEU_SEIKO)
        self.pdf.set_line_width(0.5)
        self.pdf.line(margin_left, 30, self.pdf.w - margin_right, 30)
        
        # Position Y courante
        y = 40
        
        # Titre de la facture
        self.pdf.set_xy(margin_left, y)
        self.pdf.set_font('Helvetica', 'B', 20)
        self.pdf.set_text_color(*NOIR)
        self.pdf.cell(0, 10, 'FACTURE', 0, 1, 'L')
        y += 15
        
        # Informations de la facture
        self.pdf.set_xy(margin_left, y)
        self.pdf.set_font('Helvetica', '', 10)
        self.pdf.set_text_color(*GRIS_FONCE)
        self.pdf.cell(30, 6, 'N° de facture :', 0, 0, 'L')
        self.pdf.set_text_color(*NOIR)
        self.pdf.cell(0, 6, self.donnees['num_commande'], 0, 1, 'L')
        y += 7
        
        self.pdf.set_xy(margin_left, y)
        self.pdf.set_text_color(*GRIS_FONCE)
        self.pdf.cell(30, 6, 'Date :', 0, 0, 'L')
        self.pdf.set_text_color(*NOIR)
        self.pdf.cell(0, 6, self.donnees['date_facture'], 0, 1, 'L')
        y += 15
        
        # Section client
        self.pdf.set_fill_color(*BLEU_CLAIR)
        self.pdf.set_text_color(*NOIR)
        self.pdf.set_font('Helvetica', 'B', 12)
        self.pdf.set_xy(margin_left, y)
        self.pdf.cell(0, 8, 'CLIENT', 0, 1, 'L', fill=True)
        y += 10
        
        # Coordonnées du client
        self.pdf.set_fill_color(*GRIS_CLAIR)
        self.pdf.rect(margin_left, y, page_width - 20, 25, 'F')
        
        self.pdf.set_xy(margin_left + 5, y + 5)
        self.pdf.set_font('Helvetica', 'B', 11)
        self.pdf.cell(0, 6, self.donnees['client_nom'], 0, 1, 'L')
        
        self.pdf.set_xy(margin_left + 5, y + 13)
        self.pdf.set_font('Helvetica', '', 10)
        self.pdf.multi_cell(0, 5, f"{self.donnees['client_adresse']}\n{self.donnees['client_cp']} {self.donnees['client_ville']}", 0, 'L')
        
        y += 35  # Espacement après la section client
        
        # En-tête du tableau des articles
        y_table_start = y
        
        # Vérifier s'il y a assez d'espace pour l'en-tête du tableau
        if y > 220:  # Si on est trop bas sur la page
            self.pdf.add_page()
            y = 20  # Réinitialiser la position Y après un saut de page
            y_table_start = y
        
        # En-tête du tableau
        self.pdf.set_xy(margin_left, y)
        self.pdf.set_fill_color(*BLEU_SEIKO)
        self.pdf.set_text_color(*BLANC)
        self.pdf.set_font('Helvetica', 'B', 10)
        
        # Largeurs des colonnes (ajustées pour une meilleure répartition)
        w_quantite = 15
        w_designation = 75  # Légèrement réduite pour laisser plus d'espace
        w_reference = 30
        w_prix = 35  # Légèrement augmentée pour les prix
        w_total = 35  # Légèrement augmentée pour les totaux
        
        # Hauteur de ligne de base
        line_height = 8
        
        # En-têtes de colonnes
        self.pdf.set_xy(margin_left, y)
        self.pdf.set_fill_color(*BLEU_SEIKO)
        self.pdf.set_text_color(*BLANC)
        self.pdf.set_font('Helvetica', 'B', 10)
        
        # Dessiner le fond de l'en-tête
        self.pdf.rect(margin_left, y, w_quantite + w_designation + w_reference + w_prix + w_total, line_height, 'F')
        
        # Dessiner les bordures des cellules d'en-tête
        self.pdf.rect(margin_left, y, w_quantite, line_height, 'D')
        self.pdf.rect(margin_left + w_quantite, y, w_designation, line_height, 'D')
        self.pdf.rect(margin_left + w_quantite + w_designation, y, w_reference, line_height, 'D')
        self.pdf.rect(margin_left + w_quantite + w_designation + w_reference, y, w_prix, line_height, 'D')
        self.pdf.rect(margin_left + w_quantite + w_designation + w_reference + w_prix, y, w_total, line_height, 'D')
        
        # Texte des en-têtes
        self.pdf.set_xy(margin_left, y + 2)
        self.pdf.cell(w_quantite, line_height, 'Qté', 0, 0, 'C')
        self.pdf.cell(w_designation, line_height, 'Désignation', 0, 0, 'L')
        self.pdf.cell(w_reference, line_height, 'Référence', 0, 0, 'L')
        self.pdf.cell(w_prix, line_height, 'Prix unitaire', 0, 0, 'R')
        self.pdf.cell(w_total, line_height, 'Total', 0, 1, 'R')
        
        y += line_height  # Hauteur de l'en-tête
        
        # Lignes des articles
        self.pdf.set_font('Helvetica', '', 10)
        total_ht = 0
        
        for i, article in enumerate(self.articles):
            # Vérifier l'espace restant avant d'ajouter une nouvelle ligne
            if y > 250:  # Si on est trop bas sur la page
                self.pdf.add_page()
                y = 30  # Réinitialiser la position Y après un saut de page
                
                # Redessiner l'en-tête du tableau sur la nouvelle page
                self.pdf.set_fill_color(*BLEU_SEIKO)
                self.pdf.set_text_color(*BLANC)
                self.pdf.set_font('Helvetica', 'B', 10)
                self.pdf.rect(margin_left, y, w_quantite + w_designation + w_reference + w_prix + w_total, line_height, 'F')
                self.pdf.set_xy(margin_left, y + 2)
                self.pdf.cell(w_quantite, line_height, 'Qté', 0, 0, 'C')
                self.pdf.cell(w_designation, line_height, 'Désignation', 0, 0, 'L')
                self.pdf.cell(w_reference, line_height, 'Référence', 0, 0, 'L')
                self.pdf.cell(w_prix, line_height, 'Prix unitaire', 0, 0, 'R')
                self.pdf.cell(w_total, line_height, 'Total', 0, 1, 'R')
                y += line_height
                
                # Réinitialisation des styles pour le contenu
                self.pdf.set_font('Helvetica', '', 10)
                self.pdf.set_text_color(*NOIR)  # Réinitialisation de la couleur du texte
                
                # Réinitialisation de la couleur de fond pour la première ligne
                if i % 2 == 0:
                    self.pdf.set_fill_color(*BLANC)
                else:
                    self.pdf.set_fill_color(*GRIS_CLAIR)
            
            # Préparation du contenu
            quantite = str(article['quantite'])
            designation = f"{article['modele']}\nMouvement: {article['mouvement']} | Couleur: {article['couleur']}"
            reference = article['reference']
            prix_unitaire = f"{article['prix']:.2f} EUR"
            total_ligne = article['prix'] * article['quantite']
            total_ht += total_ligne
            
            # Calculer la hauteur nécessaire pour cette ligne
            nb_lignes_designation = max(1, len(designation) // 40 + 1)
            hauteur_ligne = max(8, 6 * nb_lignes_designation)  # Hauteur minimale de 8mm
            
            # Couleur de fond alternée pour les lignes
            if i % 2 == 0:
                self.pdf.set_fill_color(*BLANC)
            else:
                self.pdf.set_fill_color(*GRIS_CLAIR)
            
            # Dessiner le fond de la ligne
            self.pdf.rect(margin_left, y, w_quantite + w_designation + w_reference + w_prix + w_total, hauteur_ligne, 'F')
            
            # Bordures des cellules
            self.pdf.rect(margin_left, y, w_quantite, hauteur_ligne, 'D')
            self.pdf.rect(margin_left + w_quantite, y, w_designation, hauteur_ligne, 'D')
            self.pdf.rect(margin_left + w_quantite + w_designation, y, w_reference, hauteur_ligne, 'D')
            self.pdf.rect(margin_left + w_quantite + w_designation + w_reference, y, w_prix, hauteur_ligne, 'D')
            self.pdf.rect(margin_left + w_quantite + w_designation + w_reference + w_prix, y, w_total, hauteur_ligne, 'D')
            
            # Réinitialiser les couleurs et la police
            self.pdf.set_text_color(*NOIR)
            self.pdf.set_font('Helvetica', '', 10)
            
            # Calculer la hauteur nécessaire pour la cellule de désignation
            # On ajoute une marge supplémentaire de 2 unités pour éviter toute coupure
            nb_lignes = len(designation) // 35 + 1  # Estimation du nombre de lignes
            hauteur_designation = 6 * nb_lignes + 4  # 4 unités de marge supplémentaire
            hauteur_ligne = max(10, hauteur_designation)  # Hauteur minimale de 10
            
            # Dessiner le fond de la ligne entière
            self.pdf.set_fill_color(*BLANC if i % 2 == 0 else GRIS_CLAIR)
            self.pdf.rect(margin_left, y, w_quantite + w_designation + w_reference + w_prix + w_total, hauteur_ligne, 'F')
            
            # Bordures des cellules
            self.pdf.rect(margin_left, y, w_quantite, hauteur_ligne, 'D')
            self.pdf.rect(margin_left + w_quantite, y, w_designation, hauteur_ligne, 'D')
            self.pdf.rect(margin_left + w_quantite + w_designation, y, w_reference, hauteur_ligne, 'D')
            self.pdf.rect(margin_left + w_quantite + w_designation + w_reference, y, w_prix, hauteur_ligne, 'D')
            self.pdf.rect(margin_left + w_quantite + w_designation + w_reference + w_prix, y, w_total, hauteur_ligne, 'D')
            
            # Afficher la quantité (centrée)
            self.pdf.set_xy(margin_left, y + (hauteur_ligne - 6) / 2)
            self.pdf.cell(w_quantite, 6, quantite, 0, 0, 'C')
            
            # Afficher la désignation (avec multi-lignes si nécessaire)
            self.pdf.set_xy(margin_left + w_quantite + 2, y + 2)  # Petite marge à gauche
            self.pdf.multi_cell(w_designation - 4, 6, designation, 0, 'L')
            
            # Afficher la référence
            self.pdf.set_xy(margin_left + w_quantite + w_designation, y + (hauteur_ligne - 6) / 2)
            self.pdf.cell(w_reference, 6, reference, 0, 0, 'L')
            
            # Afficher le prix unitaire
            self.pdf.set_xy(margin_left + w_quantite + w_designation + w_reference, y + (hauteur_ligne - 6) / 2)
            self.pdf.set_text_color(*GRIS_FONCE)
            self.pdf.cell(w_prix - 2, 6, prix_unitaire, 0, 0, 'R')
            
            # Afficher le total de la ligne
            self.pdf.set_xy(margin_left + w_quantite + w_designation + w_reference + w_prix, y + (hauteur_ligne - 6) / 2)
            self.pdf.set_text_color(*NOIR)
            self.pdf.set_font('Helvetica', 'B', 10)
            self.pdf.cell(w_total - 2, 6, f"{total_ligne:.2f} EUR", 0, 0, 'R')
            self.pdf.set_font('Helvetica', '', 10)  # Réinitialiser la police
            
            # Mise à jour de la position Y pour la prochaine ligne
            y += hauteur_ligne
        
        # Section des totaux
        y_totals = max(y + 10, 200)  # Position minimale pour les totaux
        
        # Vérifier s'il y a assez d'espace pour les totaux
        if y_totals > 240:  # Si on est trop bas sur la page
            self.pdf.add_page()
            y_totals = 20
        
        # Ligne de séparation avant les totaux
        self.pdf.set_draw_color(*GRIS_FONCE)
        self.pdf.line(margin_left, y_totals - 5, margin_left + w_quantite + w_designation + w_reference + w_prix + w_total, y_totals - 5)
        
        # Calcul des totaux
        taux_tva = 0.20  # 20% de TVA
        montant_tva = total_ht * taux_tva
        total_ttc = total_ht + montant_tva
        
        # Affichage des totaux
        self.pdf.set_font('Helvetica', '', 10)
        
        # Positionnement des totaux à droite
        x_totals = margin_left + w_quantite + w_designation + w_reference - 20
        
        # Total HT
        self.pdf.set_xy(x_totals, y_totals)
        self.pdf.cell(60, 8, 'Total HT:', 0, 0, 'R')
        self.pdf.cell(30, 8, f"{total_ht:.2f} EUR", 0, 1, 'R')
        
        # TVA
        self.pdf.set_xy(x_totals, y_totals + 8)
        self.pdf.cell(60, 8, f'TVA {int(taux_tva*100)}%:', 0, 0, 'R')
        self.pdf.cell(30, 8, f"{montant_tva:.2f} EUR", 0, 1, 'R')
        
        # Total TTC
        self.pdf.set_xy(x_totals, y_totals + 16)
        self.pdf.set_font('Helvetica', 'B', 11)
        self.pdf.set_fill_color(*BLEU_CLAIR)
        self.pdf.cell(60, 10, 'Total TTC:', 'T', 0, 'R', 1)
        self.pdf.cell(30, 10, f"{total_ttc:.2f} EUR", 'T', 1, 'R', 1)
        
        # Conditions de paiement
        y_paiement = y_totals + 35
        
        # Vérifier s'il y a assez d'espace pour les conditions de paiement
        if y_paiement > 250:  # Si on est trop bas sur la page
            self.pdf.add_page()
            y_paiement = 20
            
        self.pdf.set_xy(margin_left, y_paiement)
        self.pdf.set_font('Helvetica', 'B', 10)
        self.pdf.cell(0, 6, 'Conditions de paiement :', 0, 1, 'L')
        
        self.pdf.set_xy(margin_left, y_paiement + 5)
        self.pdf.set_font('Helvetica', '', 9)
        self.pdf.multi_cell(0, 5, 
            'Paiement à réception de la facture par virement bancaire.\n'
            'Les pénalités de retard sont de 1,5 fois le taux d\'intérêt légal.\n'
            'En cas de retard de paiement, une indemnité forfaitaire de 40 EUR pour frais de recouvrement sera appliquée.', 
            0, 'L')
        
        # Pied de page
        self.pdf.set_y(-20)  # 20mm du bas
        self.pdf.set_font('Helvetica', 'I', 8)
        self.pdf.set_text_color(*GRIS_FONCE)
        self.pdf.cell(0, 4, 'SEIKO MOD - Spécialiste des montres Seiko modifiées', 0, 1, 'C')
        self.pdf.cell(0, 4, 'SIRET: 123 456 789 00012 - TVA non applicable, art. 293 B du CGI', 0, 1, 'C')
        self.pdf.cell(0, 4, 'Contact: contact@seikomod.fr - Tél: +33 1 23 45 67 89', 0, 1, 'C')
        
        # Enregistrement du fichier
        self.pdf.output(nom_fichier)
        return nom_fichier

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

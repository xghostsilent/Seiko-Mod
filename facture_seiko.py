from fpdf import FPDF, XPos, YPos
from datetime import datetime
import os
import platform
import math
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
    HIGHLIGHT = '\033[48;5;153;38;5;0m'  # Surlignage bleu clair
        
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
    print()


def print_section(title):
    """Affiche un titre de section"""
    print(f"\n{Color.BOLD}{Color.UNDERLINE}{title.upper()}{Color.RESET}\n")
    print(f"{Color.GRAY}  {'─' * (len(title) + 1)}{Color.RESET}")


def input_style(prompt, default=""):
    """Style pour les champs de saisie"""
    prompt_text = f"{Color.BLUE}{prompt}{Color.RESET}"
    if default:
        prompt_text += f" {Color.GRAY}({default}){Color.RESET}"
    prompt_text += f" {Color.DIM}›{Color.RESET} "
    
    user_input = input(prompt_text)
    return user_input if user_input.strip() else default


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


class PDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajout de la police DejaVu pour supporter les caractères Unicode
        self.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
        self.add_font('DejaVu', 'B', 'DejaVuSans-Bold.ttf', uni=True)
        self.add_font('DejaVu', 'I', 'DejaVuSans-Oblique.ttf', uni=True)
        self.add_font('DejaVu', 'BI', 'DejaVuSans-BoldOblique.ttf', uni=True)
        self.set_font('DejaVu', '', 10)
        self.set_auto_page_break(auto=True, margin=30)
        self.add_page()
    
    def header(self):
        # En-tête avec dégradé de bleu
        self.set_fill_color(0, 85, 150)  # Bleu foncé
        self.rect(0, 0, self.w, 25, 'F')
        
        # Logo et titre
        self.set_font('DejaVu', 'B', 24)
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, 'ATELIER S-MOD', 0, 1, 'R')
        
        # Ligne de séparation
        self.set_draw_color(255, 255, 255)
        self.set_line_width(0.5)
        self.line(15, 25, self.w - 15, 25)
        
        # Sous-titre
        self.set_font('DejaVu', 'I', 10)
        self.cell(0, 5, 'L\'excellence horlogère à son apogée', 0, 1, 'R')
    
    def rounded_rect(self, x, y, w, h, r, style='', corners='1234'):
        """Dessine un rectangle avec des coins arrondis
        'style' peut être 'F' (fill), 'D' (draw), 'DF' (draw and fill), etc.
        'corners' est une chaîne contenant les coins à arrondir (1=top-left, 2=top-right, 3=bottom-right, 4=bottom-left)
        """
        k = self.k
        hp = self.h
        op = 'S'
        if style == 'F':
            op = 'f'
        elif style == 'FD' or style == 'DF':
            op = 'B'
        
        # Sauvegarder la couleur de remplissage actuelle
        if style == 'F' or style == 'FD' or style == 'DF':
            self._out('q ' + self.fill_color.serialize() + ' RG ' + self.fill_color.serialize() + ' rg')
        
        # Dessiner le rectangle arrondi
        self._out(f'{x*k:.2f} {(hp-(y+h))*k:.2f} m')
        
        # Coin supérieur gauche
        if '1' in corners:
            self._out(f'{(x+r)*k:.2f} {(hp-y)*k:.2f} l')
            self._arc(x+r, y+r, r, 180, 270, 1, 's')
        else:
            self._out(f'{x*k:.2f} {(hp-y)*k:.2f} l')
        
        # Coin supérieur droit
        if '2' in corners:
            self._out(f'{(x+w-r)*k:.2f} {(hp-y)*k:.2f} l')
            self._arc(x+w-r, y+r, r, 270, 360, 1, 's')
        else:
            self._out(f'{(x+w)*k:.2f} {(hp-y)*k:.2f} l')
        
        # Coin inférieur droit
        if '3' in corners:
            self._out(f'{(x+w)*k:.2f} {(hp-(y+h-r))*k:.2f} l')
            self._arc(x+w-r, y+h-r, r, 0, 90, 1, 's')
        else:
            self._out(f'{(x+w)*k:.2f} {(hp-(y+h))*k:.2f} l')
        
        # Coin inférieur gauche
        if '4' in corners:
            self._out(f'{(x+r)*k:.2f} {(hp-(y+h))*k:.2f} l')
            self._arc(x+r, y+h-r, r, 90, 180, 1, 's')
        else:
            self._out(f'{x*k:.2f} {(hp-(y+h))*k:.2f} l')
        
        # Fermer le chemin et appliquer le style
        self._out(f' {op}')
        
        # Restaurer la couleur si nécessaire
        if style == 'F' or style == 'FD' or style == 'DF':
            self._out(' Q')
    
    def _arc(self, x, y, r, a0, a1, direction=1, style=''):
        """Dessine un arc de cercle pour les coins arrondis"""
        a0 = (a0-90) * 0.017453292519943295  # deg to rad
        a1 = (a1-90) * 0.017453292519943295
        arc = self._arc_bezier(x, y, r, a0, a1, direction)
        self._out(arc + ' ' + style)
    
    def _arc_bezier(self, x, y, r, a0, a1, direction=1):
        """Génère une courbe de Bézier pour un arc de cercle"""
        k = self.k
        hp = self.h
        x0 = x + r * math.cos(a0)
        y0 = y + r * math.sin(a0)
        x1 = x + r * math.cos(a1)
        y1 = y + r * math.sin(a1)
        
        # Points de contrôle pour l'approximation de l'arc par une courbe de Bézier
        t = 4/3 * math.tan((a1 - a0) / 4)
        x2 = x0 - t * (y0 - y)
        y2 = y0 + t * (x0 - x)
        x3 = x1 + t * (y1 - y)
        y3 = y1 - t * (x1 - x)
        
        if direction == 1:  # Sens horaire
            return f'{x0*k:.2f} {(hp-y0)*k:.2f} {x2*k:.2f} {(hp-y2)*k:.2f} {x3*k:.2f} {(hp-y3)*k:.2f} {x1*k:.2f} {(hp-y1)*k:.2f} c'
        else:  # Sens anti-horaire
            return f'{x1*k:.2f} {(hp-y1)*k:.2f} {x3*k:.2f} {(hp-y3)*k:.2f} {x2*k:.2f} {(hp-y2)*k:.2f} {x0*k:.2f} {(hp-y0)*k:.2f} c'
    
    def footer(self):
        self.set_y(-20)
        self.set_font('DejaVu', 'I', 8)
        self.set_text_color(100, 100, 100)
        
        # Ligne de séparation
        self.set_draw_color(200, 200, 200)
        self.line(15, self.h - 25, self.w - 15, self.h - 25)
        
        # Contenu du pied de page
        self.set_y(-18)
        self.cell(0, 4, "Atelier S-MOD - L'excellence horlogère à son apogée", 0, 1, 'C')
        self.cell(0, 4, "SIRET: 123 456 789 00012 - TVA non applicable, art. 293 B du CGI", 0, 1, 'C')
        self.cell(0, 4, "Contact: contact@atelier-s-mod.fr - Tél: +33 1 23 45 67 89", 0, 1, 'C')
        
        # Numéro de page
        self.set_y(-10)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')


class FactureMouvementAbsolu:
    # Marges et espacement optimisés pour une page
    MARGIN_LEFT = 10
    MARGIN_RIGHT = 10
    MARGIN_TOP = 10
    MARGIN_BOTTOM = 10
    LINE_HEIGHT = 5  # Réduit de 6 à 5
    SECTION_SPACING = 5  # Réduit de 10 à 5
    
    # Couleurs (R, G, B)
    BLEU_MAIN = (0, 51, 102)      # Bleu foncé
    BLEU_CLAIR = (200, 220, 240)  # Bleu clair pour les fonds
    GRIS_FONCE = (100, 100, 100)  # Gris pour le texte secondaire
    GRIS_CLAIR = (200, 200, 200)  # Gris clair pour les séparateurs
    NOIR = (0, 0, 0)              # Noir pour le texte principal
    BLANC = (255, 255, 255)       # Blanc pour les fonds
    
    def __init__(self, donnees):
        self.donnees = donnees
        self.articles = []
        self.pdf = PDF()
        self.total_ht = 0
        self.tva = 0.20  # Taux de TVA à 20%
        
    def _draw_info_field_compact(self, x, y, label, value):
        """Dessine un champ d'information plus compact"""
        self.pdf.set_xy(x, y)
        self.pdf.set_font('DejaVu', 'B', 8)  # Taille réduite
        self.pdf.cell(25, 4, label, 0, 0, 'R')  # Largeur et hauteur réduites
        self.pdf.set_font('DejaVu', '', 8)  # Taille réduite
        self.pdf.cell(0, 4, str(value), 0, 1, 'L')  # Hauteur réduite
        
        self.pdf.set_font('DejaVu', '', 9)
        self.pdf.set_text_color(30, 30, 30)  # Noir
        self.pdf.cell(0, 6, str(value), 0, 1, 'L')

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
        print_section("Saisie des montres")
        print("Appuyez sur Entrée sans modèle pour terminer.\n")

        while True:
            modele = input_style("Modèle de la montre").strip()
            if not modele:
                if self.articles:
                    break
                print_warning("Vous devez ajouter au moins une montre.")
                continue

            reference = input_style("Référence du modèle").strip()
            if not reference:
                print_warning("La référence est obligatoire.")
                continue

            print_section("Détails & composants")

            composants = []

            def ask_component(nom, ref_label):
                ref = input_style(f"{ref_label}")
                prix = None
                while prix is None:
                    prix_str = input_style(f"Prix {nom} (EUR)")
                    prix = self.clean_price_input(prix_str)
                    if prix is None or prix <= 0:
                        print_error("Prix invalide.")
                        prix = None
                    else:
                        composants.append({
                            'nom': nom,
                            'reference': ref,
                            'prix': prix
                        })

            ask_component("Mouvement", "Référence du mouvement (ex: NH35)")
            ask_component("Cadran", "Description du cadran (ex: Noir soleil)")
            ask_component("Boîtier", "Boîtier (ex: Acier 316L 40mm)")
            ask_component("Bracelet", "Bracelet (ex: Oyster acier)")
            ask_component("Main d'œuvre", "Type de main d'œuvre (montage, réglage…)")

            quantite = 1
            try:
                quantite = int(input_style("Quantité", "1"))
            except ValueError:
                quantite = 1

            prix_total = sum(c['prix'] for c in composants)

            self.articles.append({
                'modele': modele,
                'reference': reference,
                'composants': composants,
                'prix_total': prix_total,
                'quantite': quantite
            })

            print_success("Montre ajoutée")
            print(f"Total unitaire calculé : {prix_total:.2f} EUR")

            if input("\nAjouter une autre montre ? (Entrée = oui / n = non) ").lower() in ('n', 'non'):
                break

            print_section("Informations client")
            self.donnees['client_nom'] = input("Nom complet : ").strip()
            self.donnees['client_adresse'] = input("Adresse : ").strip()
            self.donnees['client_cp'] = input("Code postal : ").strip()
            self.donnees['client_ville'] = input("Ville : ").strip()

            self.donnees['num_commande'] = get_next_order_number()
            self.donnees['date_facture'] = datetime.now().strftime("%d/%m/%Y")

    def ajouter_article(self, modele, reference, composants, quantite=1):
        """Ajoute une montre avec ses composants détaillés à la facture
        
        Args:
            modele (str): Modèle de la montre (ex: 'Chronographe Classique')
            reference (str): Référence du modèle (ex: 'CC-2024-01')
            composants (list): Liste des composants avec leur prix
                Exemple: [
                    {'nom': 'Mouvement', 'reference': 'Valjoux 7750', 'prix': 400.00},
                    {'nom': 'Cadran', 'description': 'Noir émaillé', 'prix': 150.00},
                    {'nom': 'Boîtier', 'description': 'Acier 316L 40mm', 'prix': 250.00},
                    {'nom': 'Bracelet', 'description': 'Cuir véritable', 'prix': 120.00},
                    {'nom': 'Main d\'œuvre', 'description': 'Montage et réglage', 'prix': 200.00}
                ]
            quantite (int, optional): Quantité. Par défaut à 1.
        """
        # Calcul du prix total
        prix_total = sum(comp['prix'] for comp in composants)
        
        self.articles.append({
            'modele': modele,
            'reference': reference,
            'composants': composants,
            'prix_total': prix_total,
            'quantite': int(quantite)
        })

    def ouvrir_facture(self, chemin_fichier):
        """Ouvre le fichier PDF avec l'application par défaut du système"""
        try:
            if platform.system() == 'Darwin':  # macOS
                os.system(f'open "{chemin_fichier}"')
            elif platform.system() == 'Windows':
                os.startfile(chemin_fichier)
            else:  # Linux et autres
                os.system(f'xdg-open "{chemin_fichier}"')
        except Exception as e:
            print_error(f"Impossible d'ouvrir le fichier : {e}")

    def generer_facture(self):
        """Génère le fichier PDF de la facture sur une seule page"""
        # Palette de couleurs raffinée
        self.NOIR = (30, 30, 30)           # Noir profond
        self.GRIS_FONCE = (100, 100, 100)  # Gris foncé pour le texte secondaire
        self.GRIS_CLAIR = (245, 245, 245)  # Gris très clair pour les fonds
        self.BLEU_MAIN = (0, 85, 150)      # Bleu officiel Atelier S-MOD
        self.BLEU_CLAIR = (200, 225, 245)  # Bleu clair pour les en-têtes
        self.BLANC = (255, 255, 255)       # Blanc pur
        
        # Constantes de mise en page
        self.MARGIN_LEFT = 15
        self.MARGIN_RIGHT = 15
        self.MARGIN_TOP = 15
        self.MARGIN_BOTTOM = 20
        self.LINE_HEIGHT = 5
        self.SECTION_SPACING = 5
        
        # Création du PDF sans ajout de page automatique
        self.pdf = PDF()
        # Désactiver la création automatique de page
        self.pdf.set_auto_page_break(False, margin=0)
        
        # Réinitialisation des totaux
        self.total_ht = 0
        
        # Ajout des sections dans l'ordre
        self._ajouter_entete()
        self._ajouter_infos_client()
        self._ajouter_tableau_articles()
        self._ajouter_totaux()
        
        # Création du dossier de destination si nécessaire
        if not os.path.exists('factures'):
            os.makedirs('factures')
            
        # Sauvegarde du fichier
        nom_fichier = f"factures/facture_{self.donnees.get('num_commande', '')}.pdf"
        self.pdf.output(nom_fichier)
        return nom_fichier
            
    def _ajouter_entete(self):
        """Ajoute l'en-tête de la facture avec une hiérarchie visuelle améliorée"""
        # Couleurs
        BLEU_FONCE = (0, 51, 102)  # Bleu plus foncé pour le titre
        
        # Titre de la facture - Plus grand et plus visible
        self.pdf.set_xy(15, 10)
        self.pdf.set_font('DejaVu', 'B', 22)  # Taille augmentée
        self.pdf.set_text_color(*BLEU_FONCE)
        self.pdf.cell(0, 12, 'FACTURE', 0, 1, 'L')
        
        # Ligne de séparation sous le titre
        self.pdf.set_line_width(0.5)
        self.pdf.set_draw_color(*self.BLEU_MAIN)
        self.pdf.line(15, 24, 100, 24)  # Ligne plus épaisse et plus longue
        
        # Bloc entreprise - Mise en valeur avec un fond légèrement coloré
        self.pdf.set_fill_color(*self.BLEU_CLAIR)
        self.pdf.rect(15, 30, 90, 25, 'F')  # Fond pour le bloc entreprise
        
        # Nom de l'entreprise
        self.pdf.set_xy(20, 32)
        self.pdf.set_font('DejaVu', 'B', 12)
        self.pdf.set_text_color(*self.BLEU_MAIN)
        self.pdf.cell(0, 6, 'Atelier S-MOD', 0, 1, 'L')
        
        # Coordonnées de l'entreprise
        self.pdf.set_xy(20, 39)
        self.pdf.set_font('DejaVu', '', 8)
        self.pdf.set_text_color(*self.NOIR)
        self.pdf.cell(0, 4, '123 Rue de l\'Horloge', 0, 1, 'L')
        
        self.pdf.set_xy(20, 43)
        self.pdf.cell(0, 4, '75001 PARIS', 0, 1, 'L')
        
        self.pdf.set_xy(20, 49)
        self.pdf.cell(0, 4, 'Tél: 01 23 45 67 89', 0, 1, 'L')
        self.pdf.set_xy(20, 53)
        self.pdf.cell(0, 4, 'contact@atelier-smod.com', 0, 1, 'L')
        
        # Bloc numéro de facture et date - Encadré pour le mettre en valeur
        self.pdf.set_xy(-75, 32)
        self.pdf.set_fill_color(250, 250, 250)  # Fond très légèrement grisé
        self.pdf.rounded_rect(self.pdf.w - 80, 30, 65, 25, 3, 'DF', corners='1234')
        
        # Numéro de facture
        self.pdf.set_xy(-75, 32)
        self.pdf.set_font('DejaVu', 'B', 10)
        self.pdf.set_text_color(*self.BLEU_MAIN)
        self.pdf.cell(0, 6, 'FACTURE N°', 0, 1, 'L')
        
        self.pdf.set_xy(-75, 38)
        self.pdf.set_font('DejaVu', 'B', 12)
        self.pdf.cell(0, 6, self.donnees.get('num_commande', ''), 0, 1, 'L')
        
        # Date de facturation
        self.pdf.set_xy(-75, 46)
        self.pdf.set_font('DejaVu', '', 8)
        self.pdf.cell(0, 4, f"Date: {self.donnees.get('date_facture', '')}", 0, 1, 'L')
        
        # Légère séparation avant la section suivante
        self.pdf.set_draw_color(220, 220, 220)
        self.pdf.line(15, 62, self.pdf.w - 15, 62)
            
    def _ajouter_infos_client(self):
        """Ajoute les informations client avec une meilleure mise en forme"""
        # Position après l'en-tête
        y = 70  # Ajusté pour la nouvelle mise en page
        
        # En-tête de section avec icône
        self.pdf.set_xy(15, y)
        self.pdf.set_fill_color(*self.BLEU_MAIN)
        self.pdf.set_text_color(255, 255, 255)  # Texte blanc
        self.pdf.set_font('DejaVu', 'B', 10)
        self.pdf.cell(0, 6, '  INFORMATIONS CLIENT', 0, 1, 'L', 1)
        
        # Icône utilisateur (simulée avec un caractère)
        self.pdf.set_xy(18, y + 2)
        self.pdf.set_font('DejaVu', 'B', 8)
        self.pdf.cell(0, 0, '👤', 0, 0, 'L')
        
        # Cadre des informations client avec coins arrondis
        self.pdf.set_fill_color(250, 250, 250)  # Fond légèrement grisé
        self.pdf.rounded_rect(15, y + 8, self.pdf.w - 30, 28, 3, 'DF', corners='1234')
        self.pdf.set_draw_color(220, 220, 220)
        self.pdf.rounded_rect(15, y + 8, self.pdf.w - 30, 28, 3, 'D', corners='1234')
        
        # Nom du client en plus grand et en gras
        self.pdf.set_xy(20, y + 12)
        self.pdf.set_font('DejaVu', 'B', 10)
        self.pdf.set_text_color(*self.BLEU_MAIN)
        self.pdf.cell(0, 5, self.donnees.get('client_nom', '').upper(), 0, 1)
            
        # Adresse
        self.pdf.set_xy(20, y + 18)
        self.pdf.set_font('DejaVu', '', 9)
        self.pdf.set_text_color(*self.NOIR)
        self.pdf.cell(0, 4, self.donnees.get('client_adresse', ''), 0, 1)
        
        # Code postal et ville
        self.pdf.set_xy(20, y + 24)
        self.pdf.cell(0, 4, f"{self.donnees.get('client_cp', '')} {self.donnees.get('client_ville', '').upper()}", 0, 1)
        
        # Ligne de séparation avant la section suivante
        self.pdf.set_draw_color(220, 220, 220)
        self.pdf.line(15, y + 38, self.pdf.w - 15, y + 38)
        
        # Retourne la position Y pour la suite
        return y + 40
            
    def _ajouter_tableau_articles(self, y, page_width):
        """Ajoute le tableau des articles avec les composants détaillés
        
        Args:
            y (int): Position Y de départ pour le tableau
            page_width (float): Largeur de la page moins les marges
            
        Returns:
            int: Nouvelle position Y après l'ajout du tableau
        """
        # Dessiner l'en-tête du tableau
        self._dessiner_en_tete_tableau(y)
        y += 8  # Réduit l'espace après l'en-tête de 12 à 8
        
        # Réinitialisation du total HT
        self.total_ht = 0
        
        # Pour chaque article
        for i, article in enumerate(self.articles):
            # Calculer la hauteur nécessaire pour cet article
            hauteur_article = self._calculer_hauteur_article(article)
            
            # Vérifier l'espace restant avant d'ajouter un nouvel article
            if hauteur_article is None or y + hauteur_article > 220:  # Vérification de None ajoutée
                break
                
            # Dessiner l'article avec ses composants
            total_ligne = self._dessiner_article_compact(
                article, y, hauteur_article, i % 2 == 0
            )
            
            # Mettre à jour la position Y et le total
            y += hauteur_article + 3  # Petit espace entre les articles
            self.total_ht += total_ligne
    
    def _calculer_hauteur_article(self, article):
        """Calcule la hauteur nécessaire pour afficher un article"""
        if not article or not isinstance(article, dict):
            return 15  # Hauteur minimale par défaut
            
        nb_lignes = 1  # Au moins une ligne pour le modèle
        if 'composants' in article and article['composants']:
            # Une ligne par composant, maximum 3 affichés
            nb_lignes += min(3, len(article['composants']))
        return max(15, nb_lignes * 5)  # Hauteur minimale de 15 unités
    
    def _dessiner_en_tete_tableau(self, y):
        """Dessine l'en-tête du tableau des articles avec un style moderne et lisible"""
        HAUTEUR = 10  # Hauteur légèrement augmentée
        
        # Définition des largeurs de colonnes optimisées
        self.col_design = 90     # Colonne désignation élargie
        self.col_ref = 25        # Colonne référence réduite
        self.col_qte = 20        # Colonne quantité légèrement élargie
        self.col_prix = 35       # Colonne prix unitaire
        
        # Positions X de chaque colonne
        self.x_design = 18
        self.x_ref = self.x_design + self.col_design + 5
        self.x_qte = self.x_ref + self.col_ref
        self.x_prix = self.x_qte + self.col_qte
        self.x_total = self.x_prix + self.col_prix
        
        # Style de l'en-tête avec dégradé (simulé par des bandes)
        self.pdf.set_line_width(0.3)
        
        # Fond avec coins arrondis en haut
        self.pdf.set_fill_color(*self.BLEU_MAIN)
        self.pdf.rounded_rect(15, y, self.pdf.w - 30, HAUTEUR, 3, 'F', corners='12')
        
        # Bordure inférieure plus fine
        self.pdf.set_draw_color(200, 200, 220)
        self.pdf.line(15, y + HAUTEUR, self.pdf.w - 15, y + HAUTEUR)
        
        # Texte en blanc
        self.pdf.set_text_color(255, 255, 255)
        self.pdf.set_font('DejaVu', 'B', 9)  # Police légèrement plus grande
        
        # Icônes pour les en-têtes (simulées avec des caractères)
        icons = {
            'design': '📋',
            'ref': '🔖',
            'qte': '🔢',
            'prix': '💰',
            'total': '💶'
        }
        
        # Positionnement précis des en-têtes avec icônes
        # Désignation
        self.pdf.set_xy(self.x_design, y + 3)
        self.pdf.cell(12, 4, icons['design'] + ' ', 0, 0, 'L')
        self.pdf.cell(0, 4, 'DÉSIGNATION', 0, 0, 'L')
        
        # Référence
        self.pdf.set_xy(self.x_ref, y + 3)
        self.pdf.cell(10, 4, icons['ref'] + ' ', 0, 0, 'L')
        self.pdf.cell(0, 4, 'RÉF.', 0, 0, 'L')
        
        # Quantité
        self.pdf.set_xy(self.x_qte, y + 3)
        self.pdf.cell(10, 4, icons['qte'], 0, 0, 'C')
        
        # Prix unitaire
        self.pdf.set_xy(self.x_prix, y + 3)
        self.pdf.cell(self.col_prix, 4, f"{icons['prix']} PRIX U.", 0, 0, 'R')
        
        # Total
        self.pdf.set_xy(self.x_total - 5, y + 3)
        self.pdf.cell(0, 4, f"{icons['total']} TOTAL", 0, 0, 'R')
        
        # Légende explicative en petit en dessous (optionnel)
        self.pdf.set_font('DejaVu', 'I', 6)
        self.pdf.set_text_color(150, 150, 150)
        self.pdf.set_xy(15, y + HAUTEUR + 2)
        self.pdf.cell(0, 3, "* Les prix sont indiqués en euros (€) toutes taxes comprises", 0, 1, 'L')
        
    def _dessiner_article_compact(self, article, y, hauteur, pair):
        """Dessine un article avec ses composants détaillés"""
        # Couleur de fond alternée pour une meilleure lisibilité
        if pair:
            self.pdf.set_fill_color(245, 245, 245)  # Gris très clair
        else:
            self.pdf.set_fill_color(255, 255, 255)  # Blanc
        
        # Fond pour toute la hauteur de l'article
        self.pdf.rect(15, y, self.pdf.w - 30, hauteur, 'F')
        
        # Bordures légères
        self.pdf.set_draw_color(220, 220, 220)
        self.pdf.line(15, y, self.pdf.w - 15, y)  # Ligne du haut
        
        # Couleur du texte
        self.pdf.set_text_color(0, 0, 0)
        
        # Hauteur de la première ligne
        hauteur_ligne = 6
        
        # Désignation du modèle (colonne 1) - avec troncature si trop longue
        modele = article['modele']
        if len(modele) > 30:  # Tronquer les modèles trop longs
            modele = modele[:27] + '...'
        
        self.pdf.set_font('DejaVu', 'B', 8)  # Police réduite
        self.pdf.set_xy(self.x_design, y + 4)
        self.pdf.cell(self.col_design, hauteur_ligne, modele, 0, 0, 'L')
        
        # Référence (colonne 2)
        ref = article['reference']
        if len(ref) > 10:  # Tronquer les références trop longues
            ref = ref[:7] + '...'
        
        self.pdf.set_xy(self.x_ref, y + 4)
        self.pdf.set_font('DejaVu', '', 7)  # Police réduite
        self.pdf.cell(self.col_ref, hauteur_ligne, ref, 0, 0, 'L')
        
        # Quantité (colonne 3)
        self.pdf.set_font('DejaVu', '', 8)
        self.pdf.set_xy(self.x_qte, y + 4)
        self.pdf.cell(self.col_qte, hauteur_ligne, f"x{article['quantite']}", 0, 0, 'C')
        
        # Prix unitaire (colonne 4)
        self.pdf.set_xy(self.x_prix, y + 4)
        self.pdf.cell(self.col_prix, hauteur_ligne, f"{article['prix_total']:.2f} €", 0, 0, 'R')
        
        # Total ligne (colonne 5)
        total_ligne = article['prix_total'] * article['quantite']
        self.pdf.set_xy(self.x_total, y + 4)
        self.pdf.set_font('DejaVu', 'B', 8)  # Police réduite
        self.pdf.cell(0, hauteur_ligne, f"{total_ligne:.2f} €", 0, 0, 'R')
        
        # Affichage des composants sous la première ligne
        self.pdf.set_font('DejaVu', '', 7)  # Police réduite pour les composants
        for i, composant in enumerate(article['composants']):
            if i >= 2:  # Limiter à 2 composants max pour l'affichage
                break
                
            y_composant = y + 12 + (i * 5)  # Espacement entre les lignes
            
            # Libellé du composant (décalé à droite)
            self.pdf.set_xy(self.x_design + 5, y_composant)
            nom_composant = f"• {composant['nom']}"
            if len(nom_composant) > 30:  # Tronquer les noms trop longs
                nom_composant = nom_composant[:27] + '...'
            self.pdf.cell(0, 4, nom_composant, 0, 1)
            
            # Prix du composant (aligné à droite)
            self.pdf.set_xy(self.x_prix, y_composant)
            self.pdf.cell(self.col_prix, 4, f"{composant['prix']:.2f} €", 0, 0, 'R')
        
        # Ligne de séparation sous l'article
        self.pdf.line(15, y + hauteur - 1, self.pdf.w - 15, y + hauteur - 1)
        
        return total_ligne
    
    def _ajouter_mentions_legales(self, y, page_width):
        """Ajoute les mentions légales en bas de la facture
        
        Args:
            y (int): Position Y de départ pour les mentions légales
            page_width (float): Largeur de la page moins les marges
            
        Returns:
            int: Nouvelle position Y après l'ajout des mentions légales
        """
        # Positionnement dynamique en fonction de la position actuelle
        y = max(y + 20, self.pdf.h - 30)  # Ajusté pour être plus compact
        
        # Police plus petite pour les mentions légales
        self.pdf.set_font('DejaVu', '', 6)  # Réduit de 7 à 6
        self.pdf.set_text_color(120, 120, 120)  # Gris un peu plus clair
        
        # Texte des mentions légales
        mentions = (
            "SARL au capital de 10 000 € - RCS Paris 123 456 789 - TVA intracommunautaire FR 12 34567891234\n"
            "Siège social : 123 Rue de l'Horlogerie, 75001 Paris - Tél : 01 23 45 67 89 - contact@atelier-s-mod.fr\n"
            "En cas de litige, les tribunaux de Paris sont seuls compétents."
        )
        
        # Affichage des mentions légales
        self.pdf.set_xy(15, y)
        self.pdf.multi_cell(0, 3, mentions, 0, 'C')
        
        return y + 20
        
    def _ajouter_totaux(self, y, page_width):
        """Ajoute les totaux en bas de la page avec un espacement optimisé
        
        Args:
            y (int): Position Y de départ pour les totaux
            page_width (float): Largeur de la page moins les marges
            
        Returns:
            int: Nouvelle position Y après l'ajout des totaux
        """
        # Calcul de la TVA et du TTC
        montant_tva = self.total_ht * self.tva
        total_ttc = self.total_ht + montant_tva
        
        # Positionnement dynamique plus haut sur la page
        y = max(y, 180)  # Ajusté pour être plus haut sur la page
        
        # Largeur des colonnes
        largeur_col1 = 35  # Libellés légèrement plus larges
        largeur_col2 = 35  # Valeurs légèrement plus larges
        marge_droite = 25  # Marge droite augmentée
        
        # Position X de départ (aligné à droite)
        x_start = self.pdf.w - marge_droite - largeur_col1 - largeur_col2 - 5
        
        # Ligne de séparation
        self.pdf.set_draw_color(200, 200, 200)
        self.pdf.line(x_start, y, self.pdf.w - marge_droite, y)
        y += 6  # Espacement réduit après la ligne
        
        # Style des libellés
        self.pdf.set_font('DejaVu', 'B', 9)
        self.pdf.set_text_color(80, 80, 80)
        
        # Style des valeurs
        self.pdf.set_font('DejaVu', '', 9)
        
        # Total HT
        self.pdf.set_xy(x_start, y)
        self.pdf.cell(largeur_col1, 6, 'Total HT:', 0, 0, 'R')
        self.pdf.set_x(x_start + largeur_col1 + 5)
        self.pdf.cell(largeur_col2, 6, f"{self.total_ht:.2f} €", 0, 1, 'R')
        y += 5  # Espacement réduit entre les lignes
        
        # TVA
        self.pdf.set_xy(x_start, y)
        self.pdf.cell(largeur_col1, 6, f'TVA {int(self.tva * 100)}%:', 0, 0, 'R')
        self.pdf.set_x(x_start + largeur_col1 + 5)
        self.pdf.cell(largeur_col2, 6, f"{montant_tva:.2f} €", 0, 1, 'R')
        y += 6  # Espacement réduit avant la ligne de séparation
        
        # Ligne de séparation
        self.pdf.line(x_start, y, self.pdf.w - marge_droite, y)
        y += 4  # Espacement réduit après la ligne
        
        # Total TTC
        self.pdf.set_font('DejaVu', 'B', 10)  # Taille légèrement réduite
        self.pdf.set_text_color(*self.BLEU_MAIN)
        self.pdf.set_xy(x_start, y)
        self.pdf.cell(largeur_col1, 8, 'TOTAL TTC:', 0, 0, 'R')
        self.pdf.set_x(x_start + largeur_col1 + 5)
        self.pdf.cell(largeur_col2, 8, f"{total_ttc:.2f} €", 0, 1, 'R')
        y += 10  # Espacement avant les mentions légales
        
        # Mentions légales
        self.pdf.set_font('DejaVu', 'I', 6)
        self.pdf.set_text_color(100, 100, 100)
        self.pdf.set_xy(15, 280)
        self.pdf.cell(0, 3, "TVA non applicable, article 293 B du CGI", 0, 1, 'L')
        self.pdf.set_x(15)
        self.pdf.cell(0, 3, "Paiement à réception de facture par virement bancaire", 0, 1, 'L')
        
        # Mention légale en tout petit en bas
        self.pdf.set_xy(15, 285)
        self.pdf.set_font('DejaVu', 'I', 5)
        self.pdf.set_text_color(150, 150, 150)
        self.pdf.cell(0, 3, 
            "TVA non applicable, article 293 B du CGI - RCS Paris 123 456 789 - "
            "N° TVA: FR00123456789 - SIRET: 123 456 789 00012",
            0, 1, 'C')
    
    def ouvrir_facture(self, nom_fichier):
        """Ouvre la facture avec le visualiseur par défaut"""
        try:
            if platform.system() == 'Darwin':  # macOS
                os.system(f'open "{nom_fichier}"')
            elif platform.system() == 'Windows':
                os.startfile(nom_fichier)
            else:  # Linux et autres
                os.system(f'xdg-open "{nom_fichier}"')
        except Exception as e:
            print(f"Impossible d'ouvrir le fichier : {e}")
    
    def _format_prix(self, montant):
        """Formate un montant avec le symbole € et deux décimales"""
        return f"{montant:,.2f} €".replace(',', ' ')
    
    def _ajouter_en_tete(self, y):
        """Ajoute l'en-tête de la facture avec le logo et les informations de l'entreprise"""
        # Titre de la facture
        self.pdf.set_xy(self.MARGIN_LEFT, y)
        self.pdf.set_font('DejaVu', 'B', 18)  # Réduit de 20 à 18
        self.pdf.set_text_color(*self.BLEU_MAIN)
        self.pdf.cell(0, 12, 'FACTURE', 0, 1, 'L')  # Réduit la hauteur de 15 à 12
        
        # Ligne de séparation
        self.pdf.set_draw_color(*self.BLEU_MAIN)
        self.pdf.set_line_width(0.8)
        self.pdf.line(self.MARGIN_LEFT, y + 18, self.MARGIN_LEFT + 60, y + 18)
        
        # Informations de l'entreprise (taille de police réduite et espacement)
        self.pdf.set_font('DejaVu', 'B', 9)  # Réduit de 10 à 9
        self.pdf.set_text_color(*self.NOIR)
        self.pdf.set_xy(self.MARGIN_LEFT, y + 22)  # Ajusté de 25 à 22
        self.pdf.cell(0, 4, 'Atelier S-MOD', 0, 1, 'L')  # Réduit de 5 à 4
        self.pdf.set_x(self.MARGIN_LEFT)
        self.pdf.cell(0, 4, '123 Rue de l\'Horlogerie', 0, 1, 'L')
        self.pdf.set_x(self.MARGIN_LEFT)
        self.pdf.cell(0, 4, '75001 Paris, France', 0, 1, 'L')
        self.pdf.ln(3)  # Réduit de 5 à 3
        
        # Informations de contact (taille de police réduite et espacement)
        self.pdf.set_font('DejaVu', '', 8)  # Réduit de 9 à 8
        self.pdf.set_text_color(*self.GRIS_FONCE)
        self.pdf.set_x(self.MARGIN_LEFT)
        self.pdf.cell(0, 3, 'Tél: +33 1 23 45 67 89', 0, 1, 'L')  # Réduit de 4 à 3
        self.pdf.set_x(self.MARGIN_LEFT)
        self.pdf.cell(0, 3, 'Email: contact@atelier-s-mod.fr', 0, 1, 'L')
        self.pdf.set_x(self.MARGIN_LEFT)
        self.pdf.cell(0, 3, 'SIRET: 123 456 789 00012', 0, 1, 'L')
        
        return y + 80  # Retourne la nouvelle position Y
    
    def _ajouter_infos_facture(self, x, y, largeur):
        """Ajoute les informations de facturation (n° de facture, date, etc.)"""
        # Cadre autour des informations (hauteur réduite)
        self.pdf.set_draw_color(*self.GRIS_CLAIR)
        self.pdf.set_fill_color(*self.BLEU_CLAIR)
        self.pdf.rect(x, y, largeur, 35, 'DF')  # Hauteur réduite de 40 à 35
        
        # Titre de la section (taille de police réduite)
        self.pdf.set_font('DejaVu', 'B', 9)  # Réduit de 10 à 9
        self.pdf.set_text_color(*self.BLEU_MAIN)
        self.pdf.set_xy(x + 5, y + 3)  # Ajustement vertical
        self.pdf.cell(0, 4, 'FACTURE N°', 0, 1, 'L')  # Hauteur réduite de 5 à 4
        
        # Numéro de facture (taille de police réduite)
        self.pdf.set_font('DejaVu', 'B', 11)  # Réduit de 12 à 11
        self.pdf.set_text_color(*self.NOIR)
        self.pdf.set_xy(x + 5, y + 9)  # Ajustement vertical
        self.pdf.cell(0, 5, self.donnees['num_commande'], 0, 1, 'L')  # Hauteur réduite de 7 à 5
        
        # Date de facturation (taille de police réduite)
        self.pdf.set_font('DejaVu', '', 8)  # Réduit de 9 à 8
        self.pdf.set_text_color(*self.GRIS_FONCE)
        self.pdf.set_xy(x + 5, y + 20)  # Ajustement vertical (25 -> 20)
        self.pdf.cell(0, 4, f'Date: {self.donnees["date_facture"]}', 0, 1, 'L')  # Hauteur réduite de 5 à 4
        
        return y + 45  # Retourne la nouvelle position Y
    
    def _ajouter_infos_client(self, x, y, largeur):
        """Ajoute les informations du client"""
        # Cadre autour des informations client (hauteur réduite)
        self.pdf.set_draw_color(*self.GRIS_CLAIR)
        self.pdf.set_fill_color(*self.BLEU_CLAIR)
        self.pdf.rect(x, y, largeur, 50, 'DF')  # Hauteur réduite de 60 à 50
        
        # Titre de la section (taille de police réduite)
        self.pdf.set_font('DejaVu', 'B', 9)  # Réduit de 10 à 9
        self.pdf.set_text_color(*self.BLEU_MAIN)
        self.pdf.set_xy(x + 5, y + 3)  # Ajustement vertical
        self.pdf.cell(0, 4, 'FACTURER À', 0, 1, 'L')  # Hauteur réduite de 5 à 4
        
        # Informations du client (taille de police réduite)
        self.pdf.set_font('DejaVu', 'B', 9)  # Réduit de 10 à 9
        self.pdf.set_text_color(*self.NOIR)
        self.pdf.set_xy(x + 5, y + 12)  # Ajustement vertical
        self.pdf.cell(0, 4, self.donnees['client_nom'], 0, 1, 'L')  # Hauteur réduite
        
        # Adresse sur plusieurs lignes si nécessaire (taille de police réduite)
        self.pdf.set_font('DejaVu', '', 8)  # Réduit de 9 à 8
        self.pdf.set_xy(x + 5, y + 18)  # Ajustement vertical
        adresse = self.donnees.get('client_adresse', '')
        if adresse is not None:
            self.pdf.multi_cell(largeur - 10, 3.5, adresse, 0, 'L')  # Interligne réduit
        
        # Code postal et ville
        adresse_y = y + 18
        if 'client_adresse' in self.donnees and self.donnees['client_adresse'] is not None:
            adresse_y += len(str(self.donnees['client_adresse']).split('\n')) * 3.5
            
        self.pdf.set_xy(x + 5, adresse_y)
        cp = self.donnees.get('client_cp', '')
        ville = self.donnees.get('client_ville', '')
        self.pdf.cell(0, 4, f"{cp} {ville}".strip(), 0, 1, 'L')  # Hauteur réduite
        
        # Complément d'adresse si présent
        if 'client_complement' in self.donnees and self.donnees['client_complement']:
            self.pdf.set_xy(x + 5, adresse_y + 5)  # Ajustement vertical
            self.pdf.cell(0, 4, self.donnees['client_complement'], 0, 1, 'L')  # Hauteur réduite
        
        return y + 55  # Retourne la nouvelle position Y (65 -> 55)
    
    def generer_facture(self):
        """Génère la facture au format PDF"""
        # Création du dossier factures s'il n'existe pas
        if not os.path.exists('factures'):
            os.makedirs('factures')
        
        # Nom du fichier basé sur la référence de commande
        nom_fichier = f"factures/facture_{self.donnees['num_commande']}.pdf"
        
        # Initialisation du PDF
        self.pdf = PDF()
        self.pdf.add_page()
        
        # Définition des marges et largeur de page
        page_width = self.pdf.w - self.MARGIN_LEFT - self.MARGIN_RIGHT
        y = self.MARGIN_TOP
        
        # En-tête de la facture
        y = self._ajouter_en_tete(y)
        
        # Largeurs des colonnes pour la mise en page
        largeur_col = (page_width - 20) / 2  # Moins l'espacement entre les colonnes
        
        # Section informations de facturation (à gauche)
        y = max(y, self._ajouter_infos_facture(
            self.MARGIN_LEFT, y, largeur_col
        ))
        
        # Section client (à droite)
        y = max(y, self._ajouter_infos_client(
            self.MARGIN_LEFT + largeur_col + 20, 
            self.MARGIN_TOP + 20, 
            largeur_col
        ))
        
        # Ajout du tableau des articles
        y = self._ajouter_tableau_articles(y, page_width)
        
        # Ajout des totaux
        y = self._ajouter_totaux(y, page_width)
        
        # Ajout des mentions légales
        self._ajouter_mentions_legales(y, page_width)
        
        # Enregistrement du fichier
        self.pdf.output(nom_fichier)
        return nom_fichier

    def main():
        print_header()
        print(f"  {Color.BLUE}Créez des factures professionnelles pour vos montres{Color.RESET}\n")
        print(f"  {Color.GRAY}Ce programme vous guide pas à pas pour créer une facture détaillée.{Color.RESET}\n")
        
        # Délai d'attente pour l'effet de démarrage
        import time
        print(f"  {Color.GRAY}Chargement...{Color.RESET}", end="\r")
        time.sleep(0.5)
            
        facture = FactureMouvementAbsolu()
        
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

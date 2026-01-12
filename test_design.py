from facture_seiko import FactureMouvementAbsolu, get_next_order_number, Color, print_success
from datetime import datetime
import os
import sys

def generer_facture_test():
    """Génère une facture de test avec des données d'exemple"""
    # Désactiver l'affichage des entrées/sorties pendant le test
    original_input = __builtins__.input
    def mock_input(prompt=''):
        return ""
    __builtins__.input = mock_input
    
    try:
        # Configuration des informations client de test
        donnees = {
            'client_nom': 'DUPONT Jean',
            'client_adresse': '123 Rue des Montres',
            'client_cp': '75000',
            'client_ville': 'PARIS',
            'num_commande': get_next_order_number(),
            'date_facture': datetime.now().strftime('%d/%m/%Y')
        }
        
        # Création d'une instance de FactureMouvementAbsolu avec les données
        facture = FactureMouvementAbsolu(donnees)
        
        # Article de test 1
        article1 = {
            'modele': 'Chronographe Classique',
            'reference': 'CC-2024-01',
            'composants': [
                {'nom': 'Mouvement', 'reference': 'Valjoux 7750', 'prix': 650.00},
                {'nom': 'Cadran', 'reference': 'Noir mat', 'prix': 120.00},
                {'nom': 'Boîtier', 'reference': 'Acier 316L 42mm', 'prix': 280.00},
                {'nom': 'Bracelet', 'reference': 'Cuir noir', 'prix': 90.00},
                {'nom': 'Main d\'œuvre', 'reference': 'Assemblage', 'prix': 210.00},
            ],
            'prix_total': 1350.00,
            'quantite': 1
        }
        
        # Article de test 2 (plus simple)
        article2 = {
            'modele': 'Dress Watch Élégante',
            'reference': 'DE-2024-02',
            'composants': [
                {'nom': 'Mouvement', 'reference': 'Miyota 9015', 'prix': 280.00},
                {'nom': 'Cadran', 'reference': 'Blanc émaillé', 'prix': 150.00},
                {'nom': 'Boîtier', 'reference': 'Acier poli 38mm', 'prix': 220.00},
                {'nom': 'Bracelet', 'reference': 'Cuir croco noir', 'prix': 180.00},
                {'nom': 'Main d\'œuvre', 'reference': 'Montage', 'prix': 150.00},
            ],
            'prix_total': 980.00,
            'quantite': 2
        }

        # Ajout des articles à la facture
        facture.articles = [article1, article2]
        
        # Calcul du total HT
        facture.total_ht = sum(art['prix_total'] * art['quantite'] for art in facture.articles)
        
        # Génération de la facture
        print(f"{Color.BLUE}Génération de la facture de test...{Color.RESET}")
        nom_fichier = facture.generer_facture()
        
        # Afficher le chemin du fichier généré
        print_success(f"Facture générée avec succès : {os.path.abspath(nom_fichier)}")
        
        # Demander si on veut ouvrir le PDF
        response = input(f"\n{Color.BLUE}Voulez-vous ouvrir la facture ? (O/n){Color.RESET} ").strip().lower()
        if not response or response == 'o' or response == 'oui':
            facture.ouvrir_facture(nom_fichier)
            
    except Exception as e:
        print(f"{Color.RED}Erreur lors de la génération de la facture : {e}{Color.RESET}")
    finally:
        # Restaurer la fonction input originale
        __builtins__.input = original_input

if __name__ == "__main__":
    generer_facture_test()
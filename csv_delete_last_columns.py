import pandas as pd
import sys
import os

# Vérifier qu'un fichier a été fourni en argument
if len(sys.argv) < 2:
    print("Usage: python perfcheck_converter.py <fichier.csv>")
    sys.exit(1)

input_file = sys.argv[1]

# Vérifier que le fichier existe
if not os.path.exists(input_file):
    print(f"Erreur: Le fichier {input_file} n'existe pas.")
    sys.exit(1)

try:
    # Lire le fichier CSV
    df = pd.read_csv(input_file)
    
    # Vérifier que le fichier n'est pas vide
    if df.empty:
        print("Erreur: Le fichier CSV est vide.")
        sys.exit(1)
    
    # Vérifier qu'il y a au moins une colonne à supprimer
    if df.shape[1] < 1:
        print("Erreur: Le fichier n'a pas de colonnes.")
        sys.exit(1)
    
    print(f"Fichier original: {df.shape[0]} lignes, {df.shape[1]} colonnes")
    
    # Supprimer la dernière colonne
    df = df.iloc[:, :-1]
    
    # Sauvegarder
    output_file = input_file.replace('.csv', '_clean.csv')
    df.to_csv(output_file, index=False)
    
    print(f"Dernière colonne supprimée ! Fichier sauvé: {output_file}")
    print(f"Nouveau fichier: {df.shape[0]} lignes, {df.shape[1]} colonnes")

except pd.errors.EmptyDataError:
    print("Erreur: Le fichier CSV est vide ou mal formaté.")
except Exception as e:
    print(f"Erreur lors du traitement: {str(e)}")

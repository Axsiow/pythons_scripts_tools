import pandas as pd
import sys
import os

# check files
if len(sys.argv) < 2:
    print("Usage: python csv_delete_last_columns.py <fichier.csv>")
    sys.exit(1)

input_file = sys.argv[1]

# check if file exist
if not os.path.exists(input_file):
    print(f"Erreur: Le fichier {input_file} n'existe pas.")
    sys.exit(1)

try:
    # read csv file
    df = pd.read_csv(input_file)
    
    # check if file is empty
    if df.empty:
        print("Erreur: Le fichier CSV est vide.")
        sys.exit(1)
    
    # check if file have column
    if df.shape[1] < 1:
        print("Erreur: Le fichier n'a pas de colonnes.")
        sys.exit(1)
    
    print(f"Fichier original: {df.shape[0]} lignes, {df.shape[1]} colonnes")
    print("\nColonnes disponibles:")
    
    # Display all columns with index
    for i, column in enumerate(df.columns):
        print(f"{i}: {column}")
    
    # Ask user which column to delete
    while True:
        try:
            choice = input(f"\nQuelle colonne voulez-vous supprimer ? (0-{len(df.columns)-1}) ou 'q' pour quitter: ")
            
            if choice.lower() == 'q':
                print("Annulé.")
                sys.exit(0)
            
            column_index = int(choice)
            
            if 0 <= column_index < len(df.columns):
                column_to_delete = df.columns[column_index]
                print(f"Vous allez supprimer la colonne: '{column_to_delete}'")
                
                confirm = input("Confirmer ? (y/n): ")
                if confirm.lower() in ['y', 'yes', 'o', 'oui']:
                    # Delete selected column
                    df = df.drop(columns=[column_to_delete])
                    break
                else:
                    print("Suppression annulée.")
                    continue
            else:
                print(f"Erreur: Veuillez entrer un nombre entre 0 et {len(df.columns)-1}")
        except ValueError:
            print("Erreur: Veuillez entrer un nombre valide ou 'q' pour quitter")
    
    # save
    output_file = input_file.replace('.csv', '_clean.csv')
    df.to_csv(output_file, index=False)
    
    print(f"\nColonne '{column_to_delete}' supprimée ! Fichier sauvé: {output_file}")
    print(f"Nouveau fichier: {df.shape[0]} lignes, {df.shape[1]} colonnes")

except pd.errors.EmptyDataError:
    print("Erreur: Le fichier CSV est vide ou mal formaté.")
except KeyboardInterrupt:
    print("\nOpération annulée par l'utilisateur.")
except Exception as e:
    print(f"Erreur lors du traitement: {str(e)}")

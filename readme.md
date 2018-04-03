# link to API

https://gissmo-test.u-strasbg.fr/api/v2/
# Config
  dans config.py ajouté vos accés puis faites:

  source config.sh

# Insérer une station 
 Pour inserer une station, les informations doit etre renseigné dans un fichier Json ( voir exemple de StationA202A.json)

 Avant d'inserer la station, Il faut vérifier que le modele d'equipement et son owner existe dans l'API( je le ferai aprés dans le script)

 Puis vous lancez le script : addStation.py avec le chemin en argument 

 Exemple :
    ./addStation.py  -f  StationA202A.json 



# Récupérer une station 
    ./addStation.py  -f  A202A

    resultat dans  ResultGet_StationA202A.json


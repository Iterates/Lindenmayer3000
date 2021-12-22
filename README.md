
# LINDENMAYER 3000

## Sommaire

Génération de Systèmes de Lindenmayer via une interface graphique développée en Qt. Utilisation d'un algorithme  
génétique afin de générer un système via des fitness prédéfinies.  

### Installation

L'application utilise le langage Python ainsi qu'une base de données _SQLite3_. Les librairies _Numpy_ et _PySide6_ sont  
également utilisées. Les IDE suggérés sont _PyCharm_ ou _Visual Studio Code_.  

### Utilisation

L'application s'exécute à partir du fichier main.py. Il est import que le dossier courant soit /dev pour se connecter  
correctement à la base de données. L'application est composée de trois panneaux. Le panneau  
central affiche l'image qui est générée soit par le panneaux de gauche soit celui de droite. Le panneau de gauche  
génère un système soit à partir d'un item choisi dans la liste déroulante, soit en remplissant les champs et en choisissant  
les paramètres correspondant. Suite au remplissage des champs, il est possible de sauvegarder la forme dans une base de données  
locale afin de pouvoir l'afficher dans le futur. Le panneau de droite génère également une forme, mais à l'aide d'un  
algorithme génétique. Trois paramètres sont disponibles : la taille de la population de départ, le taux d'élitisme (qui  
représente le nombre d'individus qui vont perdurer dans la génération suivante) et le nombre de génération qui limite  
la boucle de l'algorithme. Un bouton permet également de sauver sous format png les images générées.  
Un bouton arrêter permet d'arrêter le fil d'exécution. Il n'est pas possible de démarrer une seconde simulation  
si une première est toujours en cours d'exécution.  

### Références

* Przemyslaw Prusinkiewicz et Aristid Lindenmayer (1990). _The Algorithmic Beauty of Plants_. New York : Springer-Verlag  
* Gabriela Ochoa. _On Genetic Algorithms and Lindenmayer Systems_  
* James Hanan et Przemyslaw Prusinkiewicz. (1988). _Lecture Notes in Biomathematics_  
* Melanie Mitchell. (1999). _An Introduction to Genetic Algorithms_. Cambridge : MIT Press  
* [www.jobtalle.com](www.jobtalle.com)  
* [www.thenatureofcode.com](www.thenatureofcode.com)  
* Christian Jacob. (1996). _Genetic L-System Programming_  
* John R. Koza. (1990). _Genetic Programming: A Paradigm for Genetically Breeding Populations of Computer Programs to Solve Problems_  
* John R. Koza. (1998). _Genetic Programming On the Programming of Computers by Means of Natural Selection_. Cambridge : MIT Press  
* Riccardo Poli, William B. Langdon, Nicholas F. Mcphee. (2008). _A Field Guide to Genetic Programming_. [http://www.gp-field-guide.org.uk](http://www.gp-field-guide.org.uk)  

### Contact

ariel.hotz@hotmail.com  

### Remerciements

Je tiens à remercier mes professeurs : Pierre-Paul pour ses judicieux conseils et Jean-Cristophe pour ses conseils,  
ses orientations et recommendations.
Merci à Maude, son support continu, sa patience et sa suggestion de rajouter la possibilité de sauvegarder les images  
générées.

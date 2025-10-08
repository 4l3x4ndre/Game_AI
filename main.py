from src.api import * 
from src.utils import grid_list_to_grid_tuple, grid_tuple_to_grid_list, afficher_plateau, afficher_plateau_graph
from src.strategies_dodo import strategy_aleatoire, player_a_jouer, jouer, strategy_alphabeta_intelligente
from src.strategies_gopher import strategy_aleatoire_gopher, strategy_alpha_beta_gopher, strategy_alpha_beta_gopher_actions
from random import randint
from typing import Callable
from math import inf
from tabulate import tabulate
import copy # deepcopy pour player_a_jouer
import time

import ast
import argparse
from typing import Dict, Any
from gndclient import start, Action, Score, Player, State, Time, DODO_STR, GOPHER_STR


# -------------------------  Constantes de grille --------------------------
# Constantes utilisées pour commencer le jeu à partir d'une grille ou d'autres variantes.
# liste de grilles = liste de listes de tuple (pour l'instant qu'une seule grille, celle de la démo du serveur)
GRID_POSSIBLE_DODO = {5:[[((-1, -1), 1), ((-1, -2), 1), ((-1, -3), 1), ((-1, -4), 1), ((-1, 0), 0), ((-1, 1), 0), ((-1, 2), 0), ((-1, 3), 0), ((-2, -1), 1), ((-2, -2), 1), ((-2, -3), 1), ((-2, -4), 1), ((-2, 0), 1), ((-2, 1), 0), ((-2, 2), 0), ((-3, -1), 1), ((-3, -2), 1), ((-3, -3), 1), ((-3, -4), 1), ((-3, 0), 1), ((-3, 1), 0), ((-4, -1), 1), ((-4, -2), 1), ((-4, -3), 1), ((-4, -4), 1), ((-4, 0), 1), ((0, -1), 0), ((0, -2), 1), ((0, -3), 1), ((0, -4), 0), ((0, 0), 0), ((0, 1), 0), ((0, 2), 2), ((0, 3), 2), ((0, 4), 2), ((1, -1), 0), ((1, -2), 0), ((1, -3), 1), ((1, 0), 0), ((1, 1), 2), ((1, 2), 2), ((1, 3), 2), ((1, 4), 2), ((2, -1), 0), ((2, -2), 0), ((2, 0), 2), ((2, 1), 2), ((2, 2), 2), ((2, 3), 2), ((2, 4), 2), ((3, -1), 0), ((3, 0), 2), ((3, 1), 2), ((3, 2), 2), ((3, 3), 2), ((3, 4), 2), ((4, 0), 2), ((4, 1), 2), ((4, 2), 2), ((4, 3), 2), ((4, 4), 2)]]}

# liste de grilles = liste de listes de tuple (pour l'instant qu'une seule grille pour chaque taille)
GRID_POSSIBLE_GOPHER = {4:[[((-3, -3), 0), ((-3, -2), 0), ((-3, -1), 0), ((-3, 0), 0), ((-2, -3), 0), ((-2, -2), 0), ((-2, -1), 0), ((-2, 0), 0), ((-2, 1), 0), ((-1, -3), 0), ((-1, -2), 0), ((-1, -1), 0), ((-1, 0), 0), ((-1, 1), 0), ((-1, 2), 0), ((0, -3), 0), ((0, -2), 0), ((0, -1), 0), ((0, 0), 0), ((0, 1), 0), ((0, 2), 0), ((0, 3), 0), ((3, 3), 0), ((3, 2), 0), ((3, 1), 0), ((3, 0), 0), ((2, 3), 0), ((2, 2), 0), ((2, 1), 0), ((2, 0), 0), ((2, -1), 0), ((1, 3), 0), ((1, 2), 0), ((1, 1), 0), ((1, 0), 0), ((1, -1), 0), ((1, -2), 0)]], 
                        5:[[((-4, -4), 0), ((-4, -3), 0), ((-4, -2), 0), ((-4, -1), 0), ((-4, 0), 0), ((-3, -4), 0), ((-3, -3), 0), ((-3, -2), 0), ((-3, -1), 0), ((-3, 0), 0), ((-3, 1), 0), ((-2, -4), 0), ((-2, -3), 0), ((-2, -2), 0), ((-2, -1), 0), ((-2, 0), 0), ((-2, 1), 0), ((-2, 2), 0), ((-1, -4), 0), ((-1, -3), 0), ((-1, -2), 0), ((-1, -1), 0), ((-1, 0), 0), ((-1, 1), 0), ((-1, 2), 0), ((-1, 3), 0), ((0, -4), 0), ((0, -3), 0), ((0, -2), 0), ((0, -1), 0), ((0, 0), 0), ((0, 1), 0), ((0, 2), 0), ((0, 3), 0), ((0, 4), 0), ((4, 4), 0), ((4, 3), 0), ((4, 2), 0), ((4, 1), 0), ((4, 0), 0), ((3, 4), 0), ((3, 3), 0), ((3, 2), 0), ((3, 1), 0), ((3, 0), 0), ((3, -1), 0), ((2, 4), 0), ((2, 3), 0), ((2, 2), 0), ((2, 1), 0), ((2, 0), 0), ((2, -1), 0), ((2, -2), 0), ((1, 4), 0), ((1, 3), 0), ((1, 2), 0), ((1, 1), 0), ((1, 0), 0), ((1, -1), 0), ((1, -2), 0), ((1, -3), 0)]],
                        6:[[((-5, -5), 0), ((-5, -4), 0), ((-5, -3), 0), ((-5, -2), 0), ((-5, -1), 0), ((-5, 0), 0), ((-4, -5), 0), ((-4, -4), 0), ((-4, -3), 0), ((-4, -2), 0), ((-4, -1), 0), ((-4, 0), 0), ((-4, 1), 0), ((-3, -5), 0), ((-3, -4), 0), ((-3, -3), 0), ((-3, -2), 0), ((-3, -1), 0), ((-3, 0), 0), ((-3, 1), 0), ((-3, 2), 0), ((-2, -5), 0), ((-2, -4), 0), ((-2, -3), 0), ((-2, -2), 0), ((-2, -1), 0), ((-2, 0), 0), ((-2, 1), 0), ((-2, 2), 0), ((-2, 3), 0), ((-1, -5), 0), ((-1, -4), 0), ((-1, -3), 0), ((-1, -2), 0), ((-1, -1), 0), ((-1, 0), 0), ((-1, 1), 0), ((-1, 2), 0), ((-1, 3), 0), ((-1, 4), 0), ((0, -5), 0), ((0, -4), 0), ((0, -3), 0), ((0, -2), 0), ((0, -1), 0), ((0, 0), 0), ((0, 1), 0), ((0, 2), 0), ((0, 3), 0), ((0, 4), 0), ((0, 5), 0), ((5, 5), 0), ((5, 4), 0), ((5, 3), 0), ((5, 2), 0), ((5, 1), 0), ((5, 0), 0), ((4, 5), 0), ((4, 4), 0), ((4, 3), 0), ((4, 2), 0), ((4, 1), 0), ((4, 0), 0), ((4, -1), 0), ((3, 5), 0), ((3, 4), 0), ((3, 3), 0), ((3, 2), 0), ((3, 1), 0), ((3, 0), 0), ((3, -1), 0), ((3, -2), 0), ((2, 5), 0), ((2, 4), 0), ((2, 3), 0), ((2, 2), 0), ((2, 1), 0), ((2, 0), 0), ((2, -1), 0), ((2, -2), 0), ((2, -3), 0), ((1, 5), 0), ((1, 4), 0), ((1, 3), 0), ((1, 2), 0), ((1, 1), 0), ((1, 0), 0), ((1, -1), 0), ((1, -2), 0), ((1, -3), 0), ((1, -4), 0)]]}
# --------------------------------------------------------------------------




def initialize(game: str, state: State, player: Player, 
               hex_size: int, total_time: Time) -> Environment:
    """
    Cette fonction est lancée au début du jeu. Elle dit à quel jeu on joue, 
    le joueur que l'on est et renvoie l'environnement.

    Pour créer le state (s'il n'est pas donné par un serveur),
    décommenter la partie centrale.
    """

    # Variable construisant la grille si elle n'est pas fournie par le serveur.
    _state = []
    doit_renvoyer_state = len(state) == 0 #state est vide = il faut le créer et le renvoyer

    # Cache de l'environnement
    cache = {}

    # Pions de bordure = la première ligne à l'init (suivant les règles)
    bordure = {}

    # Le code de génération de grillefontionne en [0, hex_size[.
    # Il faut donc adapter le hex_size que l'on envoie en paramètres (serveur alpha&beta).
    # Dans l'environnement c'est bien le hex_size passé
    # en paramètre qui est stocké.
    hex_size -= 1;


   
    if game.lower() == 'dodo':
        # ----------------------------- INIT DES PIONS ------------------------------------
        if len(state) == 0: # state est vide = il faut le générer
            for _player in [-1, 1]:
                _player_game = 1 # respecte l'API
                if _player == 1:
                        _player_game = 2

                # -------------------Première colonne (6, ...) ou (-6, ...)-------------------
                for y in range(0, hex_size*_player + _player, _player):
                    _state.append(((hex_size * _player, y), _player_game))


                # -------------------Les autres colonnes -------------------
                y_init = 0
                for x in range(_player * hex_size - _player, -_player, -_player):
                    # x varie de 5 à 0 ou -5 à 0 (donc un pas de -1 ou +1)

                    # À partir de la troisième colonne, on décale la première ligne de 1 vers le bas (P-1)
                    # ou 1 vers le haut (P1) à chaque nouvelle colonne
                    if _player == 1 and x  <  hex_size- 1:
                        y_init += _player
                    elif _player == -1 and x > -hex_size + 1:
                        y_init += _player
                    
                    pions_de_bordure = 2
                    pions_de_bordure_adverse = 2
                    for y in range(y_init, hex_size * _player + _player, _player):
                        _state.append(((x, y), _player_game))
                        if player == _player_game and pions_de_bordure > 0:
                            bordure[(x, y)] =  _player_game
                            pions_de_bordure -=1;
                        if player != _player_game and pions_de_bordure_adverse > 0:
                            bordure[(x, y)] =  _player_game
                            pions_de_bordure_adverse -=1;

                
                # les cases du bord sont aussi des bordures :
                # (pour la case (-6, 0) qui n'est pas prise en compte ci-dessus :
                if player == _player_game:
                    #bordure.append(((hex_size*_player, 0), player))
                    bordure[(hex_size*_player, 0)] = player

                else: # adverse
                    #bordure_adverse.append(((hex_size*_player, 0), _player_game))
                    bordure[(hex_size*_player, 0)] =  _player_game

            


            # ------------------faire le reste avec les cases vides (=sans joueur) -------------------------
            # ailes gauche et droite du papillon
            for x in range(-1, -hex_size, -1):
                for y in range(hex_size + x, 0, -1):
                    _state.append(((x, y), 0))
                    _state.append(((-x, -y), 0))


            # ailes haut et bas
            for x in range(-hex_size + 2, 0, 1):
                for y in range(0, -hex_size+2 -x-1, -1):
                    _state.append(((x, y), 0))
                    _state.append(((-x, -y), 0))

            # diagonale haut-gauche -> bas-droite
            for y in range(hex_size - 2, 0, -1):
                _state.append( ((0, y), 0) )
                _state.append( ((0, -y), 0) )


            _state.append( ((0, 0), 0) )

            state=_state

        # Représentation de l'environnement en dictionnaire
        cells = {}
        for cell_player in state:
            cells[cell_player[0]] = cell_player[1]
               
        # Création des pions de bordure.
        for cell, _player in state:

            if _player == 0:continue
            _p = -1
            if _player == 2:
                _p = 1

            # Calcul des trois coups possibles pour chaque pion
            possible1 = tuple(map(lambda i, j: i + j, cell , (-_p,0)))
            possible2 = tuple(map(lambda i, j: i + j, cell , (-_p,-_p)))
            possible3 = tuple(map(lambda i, j: i + j, cell , (0,-_p)))

            # On ajoute ces coups à "actions"... s'il n'y a pas déjà de pions à cet endroit :

            actuel_est_bordure = False 
            # Pour savoir si le pion actuel n'est pas en bordure : 
            # parce que par défaut il y est (issu d'un déplacement),
            # mais peut être que ça nouvelle position est bloquée.
            # Si on peut le bouger => ça devient une bordure. Si on ne peut pas, ça ne l'est pas.

            if possible1 in cells and cells[possible1] == 0: #case inoccupée
                actuel_est_bordure = True
            elif possible2 in cells and cells[possible2] == 0: #case inoccupée
                actuel_est_bordure = True
            elif possible3 in cells and cells[possible3] == 0: #case inoccupée
                actuel_est_bordure = True
            
            if actuel_est_bordure:
                bordure[cell] = _player
        

        player_adverse = 1
        if player == 1:
            player_adverse = 2

        _env= {'cache':{'bordure':bordure}, 'player':player, 'cells':cells, 'jeu':game, 'tour':0, 
                'hex_size':hex_size+1, # remise de la valeur correcte de taille de plateau
                'reset_cache_eval':1 # En début de partie : reset des caches de mémoïsation
                }
        if doit_renvoyer_state:
            return _env, state
        else:
            return _env


    # fin si dodo
    else:
        #jeu = gopher
        # partie basse
        for x in range(-hex_size, 1, 1):
            for y in range(-hex_size, x + hex_size + 1, 1):
                cell = (x, y)
                _state.append((cell, 0))

        # partie haute
        for x in range(hex_size, 0, -1):
            for y in range(hex_size, x - hex_size - 1, -1):
                cell = (x, y)
                _state.append((cell, 0))

        _env = {'jeu':game, 'taille': hex_size, 'nb_pions': 0, 'reset_cache':1,
                'cells_impossibles1':[], # liste des cellules où l'on sait que l'on ne peut pas jouer (nb_ennemie > 1)
                'cells_impossibles2':[]  # une liste par joueur
                }
        if doit_renvoyer_state:
            return _env, _state
        else:
            return _env



    

def final_result(state: State, score: Score, player: Player):
    """
    Cette fonction est appelée à la fin du jeu et reçoit le joueur gagnant, l'état final et le score.
    """
    print(f"\n\nFin,  {player} a gagné avec un score de {score}\n\n")



def vérification_env(env:Environment):
    """
    Vérification locale pour Dodo en attendant le serveur : 

    Peut être que notre init n'est pas bon ; peut être que nos strats effacent/ajoutent des pions.
    Vérification que le nombre de cases pour j1, j2, non occupée soit le bon.
    
    Ne vérifie que les tailles 4 ou 6 suivant les règles.
    Cette fonction n'est plus appelée. Gardée si besoin.
    """

    if env['jeu'].lower() != 'dodo':return
    nb1 = 0
    nb2 = 0
    nb_vide = 0
    for cell, player in env['cells'].items():
        if player == 1:
            nb1 += 1
        elif player == 2:
            nb2 += 1
        else:
            nb_vide += 1
    print(nb1, nb2, nb_vide)
    if env['hex_size'] == 6:
        if nb1 != 34 or nb2 != 34 or nb_vide != 59:
            raise Exception(f"Problème environnement : {env}")
    if env['hex_size'] == 4:
        if nb1 != 13 or nb2 != 13 or nb_vide != 11:
            raise Exception(f"Problème environnement {nb1}, {nb2}, {nb_vide}: {env}")
    
 

def play(strategy_1: Callable, strategy_2: Callable, hex_size:int, 
         jeu:str='dodo', debug: bool = False, save_img:bool=False,
         regenerate_state:bool=False) -> tuple[Player, Player]:
    """
    Boucle de jeu.

    Parameters:
    regenerate_state : recréer un état de jeu, ou utiliser ceux sauvegarder
    save_img : si les états initial et final du plateau doivent être enregistrer en png.
    
    Returns:
    (joueur qui à commencé, joueur qui a gagné)
    """

    # Un timer par joueur.
    if jeu == 'gopher':
        total_time = 150
    else:
        total_time = 300

    time_j1 = total_time
    time_j2 = total_time

    # Initiatlisation des grilles de départs et des joueurs
    if jeu.lower() == "dodo":
        joueurDebut = randint(1, 2)
    else:
        joueurDebut = 2

    if not regenerate_state:
        if jeu.lower() == "dodo":
            state = GRID_POSSIBLE_DODO[hex_size][0]
        else:
            state = GRID_POSSIBLE_GOPHER[hex_size][0]
        # Initialisation des environnements en fonction de l'état initiale.
        envj1 = initialize(game=jeu, state=state, player=1, hex_size=hex_size, total_time=total_time)
        envj2 = initialize(game=jeu, state=state, player=2, hex_size=hex_size, total_time=total_time)
    else:
        # Initialisation des environnements et génération du plateau
        envj1,state = initialize(game=jeu, state=[], player=1, hex_size=hex_size, total_time=total_time)
        envj2 = initialize(game=jeu, state=state, player=2, hex_size=hex_size, total_time=total_time)


    print(f"Joueur {joueurDebut} commence.")

    # On compte pour vérifier à la fin
    # que des pions n'aient pas été supprimés/ajoutés.
    # (stockage pour l'instant, puis affichage à la fin pour comparaison).
    nb1, nb2, nb0 = 0, 0, 0
    for cell, p in state:
        if p == 1:
            nb1 += 1
        elif p == 2:
            nb2 += 1
        else:
            nb0 += 1



    # Impression de l'image en png.
    if save_img:afficher_plateau_graph(state, hex_size, f"init")


    if debug: print(f"Il y a {len(state)} cases dans tout le plateau") # vérifier que 3n(n−1)+1 = len(state)
    if debug:afficher_plateau(state)
    

   
    # ------------------------------------- Boucle principale : -----------------------------------------

    nb_tour = 1
    joueur = joueurDebut
    while True:       

        # Le joueur choisit son action.
        if joueur == 1:
            start = time.time()
            envj1, action = strategy_1(envj1, state, 1, time_left=time_j1)
            time_j1 -= time.time() - start
        if joueur == 2:
            start = time.time()
            envj2, action = strategy_2(envj2, state, 2, time_left=time_j2)
            time_j2 -= time.time() - start


        if debug: print(f"L'action choisie est : {action}")

        # Appliquer l'action choisie au jeu.
        state = jouer(state=state, action=action, joueur=joueur, jeu=jeu, debug=debug)


        if debug:afficher_plateau(state)

        if jeu.lower() == "dodo":
            # notifier l'autre joueur de l'action choisie par son adversaire
            # /!\ On ne le fait plus. Chaque joueur est chargé, avant de joueur, de détecter
            # le coup joué par l'autre. C'est fait au début des fonctions strategy().
            """
            if joueur == 1:
                envj2 = player_a_jouer(1, action, copy.deepcopy(envj2))
            else:
                envj1 = player_a_jouer(2, action, copy.deepcopy(envj1))
            """
                
            
            # Coup décisif ? (fin de partie ?) 
            if final(state):

                # Désignation du vainqueur
                if nb_coups(state, 1) == 0:
                    joueur_gagnant = 1
                else:
                    joueur_gagnant = 2

                # Impression du plateau final en sortie
                if save_img:afficher_plateau_graph(state, hex_size, f"{joueur_gagnant} a gagné")

                # Vérification (voir dans la console) de si on a rajouté/supprimé
                # des jetons (cad est-ce que nos coups légaux sont faux).
                _nb1, _nb2, _nb0 = 0, 0, 0
                for cell, p in state:
                    if p == 1:
                        _nb1 += 1
                    elif p == 2:
                        _nb2 += 1
                    else:
                        _nb0 += 1
                

                if debug:afficher_plateau(state)

                return joueurDebut, joueur_gagnant      

        else:
            # Cas jeu=gopher.
            if action is None: # Fin du jeu
                if joueur == 1:
                    joueur_gagnant = 2
                else:
                    joueur_gagnant = 1
                if save_img:afficher_plateau_graph(state, hex_size, f"{joueur_gagnant} a gagné")
                return joueurDebut, joueur_gagnant
    
        print(f"Tour {nb_tour} fini, {joueur} a joué {action}. Tour suivant...") 

        # joueur suivant
        if joueur == 1:
            joueur = 2
        else:
            joueur = 1
        nb_tour += 1


def final(grid: State) -> bool:
    """
    Fonction verifiant si la partie est terminé
    """
    return nb_coups(grid, 1) == 0 or nb_coups(grid, 2) == 0


# Ma version pour calculer les possibilités (ne marche que si les 1 en bas a gauche et les 2 en haut a droite)
def nb_coups(state: State, player: Player) -> int:
    """
    Renvoie le nombre de coups du joueur spécifié dans l'etat donné
    """
    nb_coup_joueur = 0
    if player == 1:
        for cell_player in state:
            cell = cell_player[0]
            if cell_player[1] == 1:  # On cherche le nombre de coups possible du joueur 1
                if ((cell[0] + 1, cell[1]), 0) in state:
                    nb_coup_joueur += 1
                if ((cell[0], cell[1] + 1), 0) in state:
                    nb_coup_joueur += 1
                if ((cell[0] + 1, cell[1] + 1), 0) in state:
                    nb_coup_joueur += 1
    else:
        for cell_player in state:
            cell = cell_player[0]
            if cell_player[1] == 2: # On cherche le nombre de coups possible du joueur 2
                if ((cell[0] - 1, cell[1]), 0) in state:
                    nb_coup_joueur += 1
                if ((cell[0], cell[1] - 1), 0) in state:
                    nb_coup_joueur += 1
                if ((cell[0] - 1, cell[1] - 1), 0) in state:
                    nb_coup_joueur += 1

    return nb_coup_joueur


def main():
    nb_commence_gagne = 0
    nb_j1_commence = 0
    nb_j1_gagne = 0
    nb_j1_commence_gagne = 0
    nb_partie_sup_temps = 0 # nb fois que la partie a débordé du temps max.
    n = 200
    durations = []
    game = 'dodo'
    if game == 'dodo':
        max_time = 300*2
    else:
        max_time = 150*2
    
    # Simulation des parties
    for i in range(n):
        start_time = time.time()

        # joueur qui commence ; joueur qui gagne
        joueurDebut, joueur = play(
            strategy_1=decideur_de_strategy,
            strategy_2=decideur_de_strategy,
            #decideur_de_strategy,
            hex_size=6, jeu=game, debug=False, save_img=False,
            regenerate_state=True
        )
        durations.append(time.time()-start_time)

        # Mise à jour des compteurs :
        nb_commence_gagne += joueurDebut == joueur
        nb_j1_commence += joueurDebut == 1
        nb_j1_gagne += joueur == 1
        nb_j1_commence_gagne += joueurDebut == 1 and joueur == 1
        nb_partie_sup_temps += durations[-1] > max_time

        # Calcul des statistiques
        stats = [
            ["Statistique", "Valeur", "Pourcentage"],
            ["Commence et gagne", nb_commence_gagne, f"{nb_commence_gagne/(i+1)*100:.2f}%"],
            ["J1 commence", nb_j1_commence, f"{nb_j1_commence/(i+1)*100:.2f}%"],
            ["J1 gagne", nb_j1_gagne, f"{nb_j1_gagne/(i+1)*100:.2f}%"],
            ["J1 commence et gagne", nb_j1_commence_gagne, f"{nb_j1_commence_gagne/(i+1)*100:.2f}%"],
            ["Temps moyen", f"{sum(durations)/len(durations):.2f}", ''],
            [f"Partie > {max_time}s", f"{nb_partie_sup_temps}",f"{nb_partie_sup_temps/(i+1)*100:.2f}%"],
        ]
        
        # Affichage des statistiques après chaque partie
        print(f"Partie finie en {durations[-1]:.2f}s")
        print(f"Statistiques après {i + 1} parties:")
        print(tabulate(stats, headers="firstrow", tablefmt="grid"))
        print("\n")  


def decideur_de_strategy(env:Environment, state:State, player:Player, time_left:Time) -> tuple[Environment, Action]:
    """
    Applique la stratégie appropriée en fonction du jeu.
    """
    if env['jeu'].lower() == 'gopher':
        return strategy_alpha_beta_gopher_actions(env, state, player, time_left)

    return strategy_alphabeta_intelligente(env, state, player, time_left)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog="Client", description="IA02 python client. Whether -l or all other args."
    )
    parser.add_argument('-ll', '--local-loop', action='store_true')
    parser.add_argument("group_id", nargs='?')
    parser.add_argument("members", nargs='?')
    parser.add_argument("password", nargs='?')
    parser.add_argument("-s", "--server-url", default="http://localhost:8080/")
    #parser.add_argument("-s", "--server-url", default="http://lagrue.ninja/")
    parser.add_argument("-d", "--disable-dodo", action="store_false")
    parser.add_argument("-g", "--disable-gopher", action="store_false")
    args = parser.parse_args()



    if args.local_loop:
        print("Executing main() function...")
        main()
    else:    
        available_games = [DODO_STR, GOPHER_STR]
        if args.disable_dodo:
            available_games.remove(DODO_STR)
        if args.disable_gopher:
            available_games.remove(GOPHER_STR)

        start(
            args.server_url,
            args.group_id,
            args.members,
            args.password,
            available_games,
            initialize,
            decideur_de_strategy,
            final_result,
            gui=True,
        )
                        

    
        
    


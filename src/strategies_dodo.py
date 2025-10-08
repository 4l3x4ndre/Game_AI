################################################################

# Ce fichier contient les strategies pour DODO et les utilitaires
# liés aux strategies et aux actions.
# Les fonction de strategy sont à la fin.

###############################################################




from .api import *
from .utils import grid_tuple_to_grid_list, grid_list_to_grid_tuple,afficher_plateau_graph

from random import randint
from math import inf
import copy
import time





def jouer(state:State, action:Action, joueur:Player, jeu:str, debug:bool=False) -> State:
    """
    A partir d'un état, joue l'action du joueur sur le plateau et renvoie le nouvel état résultant.
    Fonction utilisée dans la boucle de jeu principale.
    """

    # mutable
    state_mut = grid_tuple_to_grid_list(state)

    if jeu.lower() == 'dodo':

        # Il y a deux étapes par tour : 
        # 1. créer un pion sur la nouvelle case
        # 2. retirer le pion de l'ancienne case
        # On peut d'abord faire le 1 puis le 2 ou l'inverse
        # en fonction de la case qu'on croise en premier
        nouvelle_case_affectée = False
        ancienne_case_retirée = False

        # pour afficher seulement
        id = 0 # permet de suivre l'id de la case courante dans state
        id_ = 0 # permet de sauvegarder l'id de la case d'arrivée dans state

        # Parcourt toutes les cases et réalise les deux étapes
        for cell_player in state_mut:
            cell, player = cell_player
            if tuple(cell) == action[0] and not ancienne_case_retirée: # libère la case départ
                state_mut[id][1] = 0
                ancienne_case_retirée = True
            elif tuple(cell) == action[1] and not nouvelle_case_affectée: # place le pion sur la case d'arrivée
                if debug: print(cell_player, end= "devient => ")
                state_mut[id][1] = joueur
                nouvelle_case_affectée = True
                id_= id
            
            id += 1
            if nouvelle_case_affectée and ancienne_case_retirée:
                break

        if debug: print(state_mut[id_])
    
    else:
        # Jeu : gopher
        for cell_player in state_mut:
            if tuple(cell_player[0]) == action:
                cell_player[1] = joueur
                break
                
    # Reprise en tuple du plateau
    state = grid_list_to_grid_tuple(state_mut)

    return state # état deu jeu mis à jour

def evaluation_intelligente(env:Environment, player_principal:Player, player:Player) -> Score:
    """
    idée de l'évaluation :
    Il vaut mieux avoir des pions bloqués par ses propres pions que par ceux de l'adversaire.
    Car on contrôle leur déplacement, alors que si l'adervsaire bouge un pion, 
    il peut nous libérer plein de pions <=> nous donner beaucoup d'actions. 
    On compte donc le nombre, parmi les trois actions possibles pour chaque pions, de 
    fois où l'action est bloquée par un de mes pions, et un autre compteur pour bloqué
    par un des siens.
    """
    player_vs = 1
    _p = 1            # 2 API (bleu, en haut)
    if player == 1:
        player_vs = 2
        _p = -1       # 1 API (rouge, en bas)

    nb_bloqués_par_moi = 0 
    nb_bloqués_par_lui = 0
    for cell, _player in env['cells'].items():
        # Il faut calculer que sur ses actions = départ de ses pions.
        if _player == player:

            # Calcul des trois coups possibles pour chaque pion
            possible1 = tuple(map(lambda i, j: i + j, cell , (-_p,0)))
            possible2 = tuple(map(lambda i, j: i + j, cell , (-_p,-_p)))
            possible3 = tuple(map(lambda i, j: i + j, cell , (0,-_p)))

            if possible1 in env['cells']:
                if env['cells'][possible1] == player:
                    nb_bloqués_par_moi += 1
                elif env['cells'][possible1] == player_vs:
                    nb_bloqués_par_lui += 1

            if possible2 in env['cells']:
                if env['cells'][possible2] == player:
                    nb_bloqués_par_moi += 1
                elif env['cells'][possible2] == player_vs:
                    nb_bloqués_par_lui += 1   

            if possible3 in env['cells']:
                if env['cells'][possible3] == player:
                    nb_bloqués_par_moi += 1
                elif env['cells'][possible3] == player_vs:
                    nb_bloqués_par_lui += 1
            
            x, y = cell
            dist = (abs(x) + abs(x + y) + abs(y)) /2

    if player == 1:
        if nb_bloqués_par_moi > nb_bloqués_par_lui:
            return nb_bloqués_par_moi
        elif nb_bloqués_par_moi == nb_bloqués_par_lui:
            return 0
        else:
            return -nb_bloqués_par_lui
    else:
        if nb_bloqués_par_moi > nb_bloqués_par_lui:
            return nb_bloqués_par_moi
        elif nb_bloqués_par_moi == nb_bloqués_par_lui:
            return 0
        else:
            return -nb_bloqués_par_lui


def evaluation_nb_actions(env:Environment, player_principal:Player, player:Player) -> Score:
    """
    Idée de l'évaluation : 
    Plus l'adervaire à de coups par rapport à nous, mieux c'est.
    """
    player_adverse = 1
    if player_principal == 1: player_adverse = 2

    coups_pp = legals(player_principal, env)
    coups_vs = legals(player_adverse, env)
    
    return len(coups_vs) - len(coups_pp)


def legals(player:Player, env:Environment, urgent:bool=False) -> list[Action]:
    """
    legals est une fonction qui étant donné un état et joueur, 
    renvoie l'ensemble des actions légales pour ce joueur ainsi que son env mis à jour

    ATTENTION : l'environnement (notamment bordure et cells) doit être à jour avec le plateau.

    Params:
    urgent: Si True, renvoie une réponse dès que possible (la première trouvée)

    Returns:
    list[Action] : toutes les actions légales pour cet état de jeu pour ce joueur
    """
    
    # Coefficient pour les déplacements
    _p = -1 # rouge = joueur 1 de l'api
    if player == 2:
        _p = 1
    
  
    actions = []
    liste_cell_player = list(env['cache']['bordure'].items())
    for cell, _player in liste_cell_player:

        # Bordure contient aussi les pions déplaçables adverses.
        # Il faut calculer legals que sur les siens.
        if _player == player:

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

            if possible1 in env['cells'] and env['cells'][possible1] == 0: #case inoccupée
                actions.append((cell, possible1))
                actuel_est_bordure = True
            if possible2 in env['cells'] and env['cells'][possible2] == 0: #case inoccupée
                actions.append((cell, possible2))
                actuel_est_bordure = True
            if possible3 in env['cells'] and env['cells'][possible3] == 0: #case inoccupée
                actions.append((cell, possible3))
                actuel_est_bordure = True
            if actuel_est_bordure and urgent:
                return actions # On a trouvé une possibilité => il faut la renvoyer de suite.

    return actions


def detecter_autre_coup_et_jouer(player:Player, env:Environment, state:State)-> Environment:
    """
    C'est à player de jouer.
    Avant d'appliquer sa stratégie, il faut qu'il mette à jour son environnement en fonction 
    du coup que l'autre joueur vient de faire.
    Cette fonction détecte l'action de l'autre joueur et renvoie un environnement mis à jour 
    pour tenir compte de cette action.
    Fonctionne même si aucun coup n'a été joué avant.
    """

    action_jouée = None
    adv = 1
    if player == 1:
        adv = 2

    if env['jeu'] == 'dodo':

        action_départ = None
        action_arrivée = None
        for cell, _p in state:
            if env['cells'][cell] != _p: 
                # Une cell de l'environnement n'est plus à jour
                # avec le plateau.

                if _p == 0: # La nouvelle case est vide => c'est la case de départ
                    action_départ = cell
                else: # Sinon, c'est l'arrivée
                    action_arrivée = cell
        action_jouée = (action_départ, action_arrivée)
        if action_jouée == (None, None):
            return env

    else:
        # N'est utilisée que pour la stratégie DODO
        print("NO GOPHER.")
        return env


    return player_a_jouer(adv, action_jouée, copy.deepcopy(env))



def player_a_jouer(player:Player, action:Action, env:Environment) -> Environment:
    """
    Modifie l'environnement suite à l'action du jouer "player".

    Params:
    player = joueur adverse
    env = environnement du joueur principal (pas de l'adverse)
    """

    player_vs = 1
    p = 1            # valeur pour calcul. Le joueur qui a joué est le 2 API (bleu, en haut)
    if player == 1:
        player_vs = 2
        p = -1       # valeur pour calcul. Le joueur qui a joué est le 1 API (rouge, en bas)

    if env['jeu'] == 'dodo':

        # ---------------- Mise à jour du plateau -----------------
        # ("plateau" = représentation du plateau sous forme de dictionnaire)
        try:
            env['cells'][action[1]] = player
            env['cells'][action[0]] = 0
        except:
            raise Exception(f"Erreur pour l'action de {player} qui est : {action}")
        
        env['cells'][action[1]] = player
        env['cells'][action[0]] = 0
        try:
            del env['cache']['bordure'][action[0]]
        except:
            # Si action[0] n'est pas une clé de bordure, 
            # Alors le plateau représenté n'est pas le bon. 
            # Erreur critique.
            raise Exception(f"Erreur de joueur {player} pour action {action} {env['cache']['bordure']}")

        # ----------Mise à jour des pions déplaçables (miens + siens) -----------
        coord = action[0] # coord = départ

        # Les cases autour du départ avec les pions adverses sont peut être libérés = déplaçables :
        # Les pions adverses autour du pion joué devient une bordure ?
        # Partie 1 (ceinture haute pour player = rouge)
        liste_pions = [
            (coord[0] -p, coord[1]),
            (coord[0] -p, coord[1] -p),
            (coord[0], coord[1] -p)
        ]
        try:
            liste_pions.remove(action[1])
        except:
            # Si action[1] n'est pas dans les pions,
            # alors l'action semble illégale.
            # Erreur critique.
            raise Exception(f"Can't remove from action={action}")

        for pion in liste_pions:
            # Si le joueur rouge avance un pion, il libère peut être un de mes (bleus) pions
            # qui peut alors aller sur la case de départ. On l'ajoute à la liste 
            # des pions déplaçables :
            if pion in env['cells'] and env['cells'][pion] == player_vs:
                env['cache']['bordure'][pion] = player_vs

        # Mes pions sous / derrière la case d'arrivée sont peut être aussi libérés
        # Partie 2 (ceinture basse pour player = rouge)
        liste_pions = [
            (coord[0] +p, coord[1]),
            (coord[0] +p, coord[1] +p),
            (coord[0], coord[1] +p)
        ]
        for pion in liste_pions:
            if pion in env['cells'] and env['cells'][pion] == player:
                env['cache']['bordure'][pion] = player

            
        # Est-ce que le nouvel emplacement est déplaçable ?
        # Partie 3 (ceinture haute autour d'arrivée pour player = rouge)
        coord = action[1] # coord = arrivée
        liste_cases_devant_pions = [
            (coord[0] -p, coord[1]),
            (coord[0] -p, coord[1] -p),
            (coord[0], coord[1] -p)
        ]
        for case in liste_cases_devant_pions:
            if case in env['cells']:
                if env['cells'][case] == 0:
                    env['cache']['bordure'][coord] = player # case devant vide = arrivé déplaçable

                # est-ce que le nouvelle emplacement ferme la ceinture autour
                # d'un des pions adverses et donc le bloque ?
                # Partie 4 (ceinture basse autour des pions adverses en face
                # de l'arrivée pour player = rouge)
                elif env['cells'][case] == player_vs and case in env['cache']['bordure']:
                    # on a check si dans bordure car on ne s'intéresse qu'aux déplaçables
                    # pour savoir s'ils ne sont plus déplaçables

                    bordure = ((case[0] + p, case[1]) in env['cells'] and env['cells'][(case[0] + p, case[1])] == 0) or \
                       ((case[0] + p, case[1]+p) in env['cells'] and  env['cells'][(case[0] + p, case[1] + p)] == 0) or \
                       ((case[0], case[1]+p) in env['cells'] and  env['cells'][(case[0], case[1] + p)] == 0)
                    if not bordure:
                        del env['cache']['bordure'][case]
                    else:
                        env['cache']['bordure'][case] = player_vs


    # Environment avec bordures et cells mises à jour.
    return env 


def rotate_60(state:State)->State:
    """
    Tourne les coordonnées des cellules de 60° dans le sens horaire.
    Utile pour éviter de calculer 𝛂𝛃 sur une rotation de 120° (inversion de pov).

    Returns:
    Le plateau tournée de 60%.
    """
    rotated_state = []
    for (x, y), player in state:
        new_x = -y
        new_y = x + y
        rotated_state.append(((new_x, new_y), player))
    return rotated_state


def cache_alpha_beta(f:Callable) -> Callable:
    """
    Mémoïsation pour αβ.
    Stockage du plateau, du joueur qui à la main (par récursivité) et 
    du joueur qui a appelé alphabeta initiallement.
    """
    cache = {}
    
    def wrapper(env:Environment, player_principal:Player, player:Player, alpha:float, beta:float, depth:int):
        nonlocal cache
        if env['reset_cache_eval']:
            # La toute première fois que l'on joue, il faut reset le cache de mémoisation
            # pour éviter de biaiser les parties suivante.
            cache = {}
            env['reset_cache_eval'] = 0

        # clé du cache
        v_tuple1 = tuple(grid_list_to_grid_tuple(list(env['cells'].items())) + [player, player_principal])

        if v_tuple1 in cache and cache[v_tuple1][1] is not None:
            return cache[v_tuple1]
        
        # Si il n'y a pas cette configuration dans le cache, peut être qu'il y a l'inverse !
        # Donc le plateau est tournée de 120 degrée, puis re-vérification de la présence dans le cache

        # Inversion du joueur et du plateau :
        adv = 1
        if player == 1:
            adv = 2
        env_inverse =rotate_60(rotate_60(list(env['cells'].items()))) 

        v_tuple2 = tuple(env_inverse + [adv, player_principal])
        if v_tuple2 in cache and cache[v_tuple2][1] is not None:
            return cache[v_tuple1]

        # Si aucune configuration correspondante dans le cache : calcul αβ 
        val = f(env, player_principal, player, alpha, beta, depth)
        cache[v_tuple1] = val
        return val
    return wrapper
       

@cache_alpha_beta
def alphabeta(env:Environment, player_principal:Player, player:Player, alpha:float, beta:float, depth:int) -> tuple[Score, Action]:
    """La meilleure action est sélectionnée au hasard parmis toutes celles qui mène au même meilleur score"""


    player_adverse = 1
    if player_principal == 1: player_adverse = 2

    # Liste des coups pour joueur 1 et joueur 2 : 
    coups_1 = legals(player_principal, env)
    coups_2 = legals(player_adverse, env)

    # Cas de base : profondeur max atteinte ou fin de partie.
    if depth == 0 or len(coups_1) == 0 or len(coups_2) == 0:
        return evaluation_intelligente(env, player_principal, player), None
        #return evaluation_nb_actions(env, player_principal, player), None
       

    if player == player_principal:
        value = -inf
        bestAction = [] # initialisation

        # - parcours des coups possibles,
        # - calcul du score
        # - mise à jour de alpha et beta.
        for action in coups_1:
            _sous_env = player_a_jouer(player, action, copy.deepcopy(env))
            _sous_val, _ = alphabeta(_sous_env, player_principal, player_adverse, alpha, beta, depth-1)

            # value = max(value, sous_value) : 
            if value < _sous_val:
                value = _sous_val
                bestAction = [action]
            elif value == _sous_val:
                bestAction.append(action)

            alpha = max(alpha, value)
            if alpha >=beta:
                break

        result = (value, bestAction[randint(0, len(bestAction)-1)])

        return result
    else:
        value = inf
        bestAction = [] # initialisation

        # - parcours des coups possibles,
        # - calcul du score
        # - mise à jour de alpha et beta.
        for action in coups_2:
            _sous_env = player_a_jouer(player, action, copy.deepcopy(env))
            _sous_val, _ = alphabeta(_sous_env, player_principal, player_principal, alpha, beta, depth-1)

            # value = min(value, sous_value) : 
            if value == _sous_val:
                bestAction.append(action)
            elif value > _sous_val:
                value = _sous_val
                bestAction = [action]

            beta = min(beta, value)
            if alpha >=beta:
                break
        
        result = (value, bestAction[randint(0, len(bestAction)-1)])

        return result



def strategy_alphabeta_intelligente(env:Environment, state: State, player: Player,
             time_left: Time) -> tuple[Environment, Action]:
    """
    Cette fonction est la strategie que vous utilisez pour jouer. 
    Cette fonction est lancée à chaque fois que c'est à votre joueur de jouer.

    Strategie principale pour DODO.

    """
    
    # Mise à jour de l'environnement en fonction du coup qui vient d'être fait
    # (fonctionne même si aucun coup n'a été fait avant)
    env = detecter_autre_coup_et_jouer(player, env, state)
    env['tour'] += 2

    # n = nombre de pions que l'on peut déplacer.
    # Plus il y en a, plus le calule de αβ sera compliqué.
    n = len(env['cache']['bordure'])

    _start = time.time() # Pour savoir le temps pris pour ce calcul.

    # Adaptation de la profondeur en fonction du nombre de pions déplaçable.
    if env['hex_size'] == 4:
        if env['tour'] == 2: # Première fois que l'on joue:
            depth=7;
        elif n > 20:
            depth = 5
        elif 17 <= n <= 20:
            depth = 7
        elif 15 <= n < 17:
            depth = 9
        elif 13 <= n < 15:
            depth = 10
        elif 10 <= n < 13:
            depth = 11
        elif 5 <= n < 10:
            depth = 12
        else:
            depth = 15
    
    elif env['hex_size'] == 5:
        depth = 3
        if n < 5:
            depth = 10
        elif n < 10:
            depth=8
        elif n < 20:
           depth = 5
        elif n < 25:
            depth= 5
        elif n < 30:
            depth=4

    elif env['hex_size'] == 6:
        depth = 3
        if n < 10:
            depth=10
        elif n < 20:
           depth = 7
        elif n < 30:
            depth=5

    else: # Si la taille est ni 4x4, ni 6x6, ni 5x5
        depth = 2
        if n < 10:
            depth=6
        elif n < 20:
           depth = 4
        elif n < 30:
            depth=4

        
    # si le temps est < 5s, la situation est critique, legals retourne alors la première position qu'il trouve    
    if time_left <= 5:
        action = legals(player, env, urgent=True)[-1]

    # si le temps restant est inférieur a 10 secondes, on ignore toutes les strategies et on fait des mouvement aléatoire
    elif time_left <= 20:
        actions = legals(player, env)
        action = actions[randint(0, len(actions) - 1)]

    else:
        score, action = alphabeta(env, player, player, alpha=-inf, beta=inf, depth=depth)



    
    if action == None:
        # Si le programme entre ici, c'est que c'est une fin de partie,
        # on peut renvoyer n'importe quel action (légale) pour le serveur.
        action = legals(player, env, urgent=True)[-1]
        return env, action


    env = player_a_jouer(player, action,  copy.deepcopy(env))
    return env, action



def strategy_aleatoire(env:Environment, state: State, player: Player,
             time_left: Time) -> tuple[Environment, Action]:
    """
    Cette fonction est la strategie que vous utilisez pour jouer. 
    Cette fonction est lancée à chaque fois que c'est à votre joueur de jouer.

    Stratégie alétaoire pour DODO.

    """

    # Mise à jour de l'environnement en fonction du coup qui vient d'être fait
    # (fonctionne même si aucun coup n'a été fait avant)
    env = detecter_autre_coup_et_jouer(player, env, state)

    env['tour'] += 2
    
    actions = legals(player, env)

    if len(actions) == 0:
        return env, None # fin de partie

    action = actions[randint(0, len(actions)-1)]

    env = player_a_jouer(player, action, copy.deepcopy(env))
    return env, action


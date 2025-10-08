from src.api import *
from src.utils import afficher_plateau_graph, grid_tuple_to_dict, grid_dict_to_tuple, grid_list_to_grid_tuple
from random import randint
import math
import copy


def legals_gopher(state: State, joueur: Player, urgent:bool=False) -> list[ActionGopher]:
    """
    Renvoit la liste des coups possible pour un joueur sur un plateau donné.

    Si urgent, alors la fonction renvoit le premier résultat trouvé.
    """
    dict_state = grid_tuple_to_dict(state)
    if joueur == 1:
        adversaire = 2
    else:
        adversaire = 1
    coups = []
    for cell, player in dict_state.items():
        if player == adversaire:
            cell_to_check = [
                (cell[0] + 1, cell[1]),
                (cell[0] - 1, cell[1]),
                (cell[0], cell[1] + 1),
                (cell[0], cell[1] -1),
                (cell[0] + 1, cell[1] + 1),
                (cell[0] - 1, cell[1] - 1)]

            for cell_temp in cell_to_check:
                if cell_temp not in dict_state:  # si la case n'est pas dans le plateau on l'abandonne
                    continue
                if dict_state[cell_temp] != 0:  # si la case est deja occupé on l'abandonne
                    continue
                # on teste les cases adjacentes pour verifier qu'il n'y a aucun allié a coté
                # si c'est le cas alors pas besoin de continuer a tester car la position n'est pas legal
                adjacentes = [(cell_temp[0] + 1, cell_temp[1]),
                             (cell_temp[0], cell_temp[1] + 1),
                             (cell_temp[0] - 1, cell_temp[1]),
                             (cell_temp[0], cell_temp[1] - 1),
                             (cell_temp[0] + 1, cell_temp[1] + 1),
                             (cell_temp[0] - 1, cell_temp[1] - 1)]
                est_possible = True
                nb_ennemi = 0
                for adjacent in adjacentes:
                    if adjacent not in dict_state:
                        continue
                    if dict_state[adjacent] == joueur:
                        est_possible = False
                        break
                    if dict_state[adjacent] == adversaire:
                        nb_ennemi += 1
                        if nb_ennemi > 1:
                            est_possible = False
                            break
                if est_possible:
                    coups.append(cell_temp)
                    if urgent:
                        return [cell_temp]
    return coups

def legals_gopher_env(env:Environment, state: State, joueur: Player, urgent:bool=False) -> list[ActionGopher]:
    """
    Renvoit la liste des coups possible pour un joueur sur un plateau donné.

    Si urgent, alors la fonction renvoit le premier résultat trouvé.
    """
    dict_state = grid_tuple_to_dict(state)
    if joueur == 1:
        adversaire = 2
    else:
        adversaire = 1
    coups = []
    nom_liste_env = 'cells_impossibles' + str(adversaire) # éviter de multiplier l'opération dans la boucle
    for cell, player in dict_state.items():
        if player == adversaire:
            cell_to_check = [
                (cell[0] + 1, cell[1]),
                (cell[0] - 1, cell[1]),
                (cell[0], cell[1] + 1),
                (cell[0], cell[1] -1),
                (cell[0] + 1, cell[1] + 1),
                (cell[0] - 1, cell[1] - 1)]

            for cell_temp in cell_to_check:
                if cell_temp not in dict_state or cell_temp in env[nom_liste_env]:
                    # si la case n'est pas dans le plateau 
                    # ou que l'on sait qu'elle est injouable (nb_ennemi > 1)
                    # on l'abandonne
                    continue

                if dict_state[cell_temp] != 0:  # si la case est deja occupé on l'abandonne
                    continue
                # on teste les cases adjacentes pour verifier qu'il n'y a aucun allié a coté
                # si c'est le cas alors pas besoin de continuer a tester car la position n'est pas legal
                adjacentes = [(cell_temp[0] + 1, cell_temp[1]),
                             (cell_temp[0], cell_temp[1] + 1),
                             (cell_temp[0] - 1, cell_temp[1]),
                             (cell_temp[0], cell_temp[1] - 1),
                             (cell_temp[0] + 1, cell_temp[1] + 1),
                             (cell_temp[0] - 1, cell_temp[1] - 1)]
                est_possible = True
                nb_ennemi = 0
                for adjacent in adjacentes:
                    if adjacent not in dict_state:
                        continue
                    if dict_state[adjacent] == joueur:
                        est_possible = False
                        break
                    if dict_state[adjacent] == adversaire:
                        nb_ennemi += 1
                        if nb_ennemi > 1:
                            est_possible = False
                            env[nom_liste_env].append(cell_temp)
                            break
                if est_possible:
                    coups.append(cell_temp)
                    if urgent:
                        return [cell_temp]
    return coups


def is_premier_coup(state: State) -> bool:
    """
    Verifie si un coup a déjà été joué sur le plateau
    """
    for cell_player in state:
        if cell_player[1] != 0:
            return False
    return True


def evaluation_gopher(state: State, player: Player) -> int:
    """
    Fonction renvoyant un score représentant l'etat du plateau selon le joueur
    """
    # approche simple pour le moment: on compare le nombre de coups possible
    if player == 1:
        adversaire = 2
    else:
        adversaire = 1

    nb_coups_j1 = len(legals_gopher(state, player))
    nb_coups_j2 = len(legals_gopher(state, adversaire))

    # prise en compte de la victoire ou de la defaite
    offset = 0
    # si l'on ne peut plus jouer mais que l'adversaire si alors on perd
    if nb_coups_j1 == 0 and nb_coups_j2 > 0:
        offset = -100
    # si on peut jouer mais que l'adversaire non alors on gagne
    if nb_coups_j1 > 0 and nb_coups_j2 == 0:
        offset = 100

    return (nb_coups_j1 - nb_coups_j2) + offset

def evaluation_gopher_env(env:Environment, state: State, player: Player) -> int:
    """
    Fonction renvoyant un score représentant l'etat du plateau selon le joueur
    """
    # approche simple pour le moment: on compare le nombre de coups possible
    if player == 1:
        adversaire = 2
    else:
        adversaire = 1

    nb_coups_j1 = len(legals_gopher_env(env, state, player))
    nb_coups_j2 = len(legals_gopher_env(env, state, adversaire))

    # prise en compte de la victoire ou de la defaite
    offset = 0
    # si l'on ne peut plus jouer mais que l'adversaire si alors on perd
    if nb_coups_j1 == 0 and nb_coups_j2 > 0:
        offset = -100
    # si on peut jouer mais que l'adversaire non alors on gagne
    if nb_coups_j1 > 0 and nb_coups_j2 == 0:
        offset = 100

    return (nb_coups_j1 - nb_coups_j2) + offset

def play_gopher(state: State, action: ActionGopher, joueur: Player) -> State:
    """
    Fonction renvoyant un nouveau plateau avec le coup joué
    """
    state = grid_tuple_to_dict(state)
    state[action] = joueur
    return grid_dict_to_tuple(state)


def undo_gopher(state: State, action: ActionGopher, joueur: Player) -> State:
    """
    Fonction renvoyant un nouveau plateau avec le coup annulé
    """
    state = grid_tuple_to_dict(state)
    state[action] = 0
    return grid_dict_to_tuple(state)

def final_gopher(state: State) -> bool:
    return len(legals_gopher(state, 1)) == 0 or len(legals_gopher(state, 2)) == 0


def cache_ab_gopher(func:Callable):
    cache = {}
    def wrapper(env:Environment, state: State, actual_player: Player, player: Player, alpha: float, beta: float, depth: int) -> int:
        nonlocal cache
        if env['reset_cache'] == 1:
            env['reset_cache'] = 0
            cache={}
        

        _state_tuple = tuple(grid_list_to_grid_tuple(state) + [actual_player, player])
        if _state_tuple in cache:
            if cache[_state_tuple][1] is None:
                if final_gopher_player(env, state, actual_player):
                    return cache[_state_tuple]
            else:
                return cache[_state_tuple]

        val = func(env, state, actual_player, player, alpha, beta, depth)
        cache[_state_tuple] = val
        return val
    return wrapper

def alpha_beta(env:Environment,state: State, actual_player: Player, player: Player, alpha: float, beta: float, depth: int) -> int:
    """
    Renvoit le score du coup ayant le plus élevé
    """
    if final_gopher(state) or depth <= 0:
        return evaluation_gopher(state, player)

    if actual_player == player:
        bestvalue = float("-inf")
        for coup in legals_gopher(state, actual_player):
            # On applique le coup pour l'evaluer
            state = play_gopher(state, coup, actual_player)

            # on evalue la nouvele configuration obtenue
            if actual_player == 1:
                value = alpha_beta(env, state, 2, player, alpha, beta, depth - 1)
            else:
                value = alpha_beta(env, state, 1, player, alpha, beta, depth - 1)

            # On inverse le coup pour retrouver l'état de base
            state = undo_gopher(state, coup, actual_player)

            bestvalue = max(bestvalue, value)
            alpha = max(alpha, bestvalue)
            if alpha >= beta:
                break

        return bestvalue

    else:
        bestvalue = float("inf")
        for coup in legals_gopher(state, actual_player):
            # On applique le coup pour l'evaluer
            state = play_gopher(state, coup, actual_player)

            # on evalue la nouvele configuration obtenue
            if actual_player == 1:
                value = alpha_beta(env, state, 2, player, alpha, beta, depth - 1)
            else:
                value = alpha_beta(env, state, 1, player, alpha, beta, depth - 1)

            # On inverse le coup pour retrouver l'état de base
            state = undo_gopher(state, coup, actual_player)

            bestvalue = min(bestvalue, value)
            beta = min(beta, bestvalue)
            if alpha >= beta:
                break
        return bestvalue

def final_gopher_player(env:Environment,state: State, player:Player) -> bool:
    """
    C'est à player de jouer. S'il ne peut pas, alors c'est la fin du jeu.
    """
    return len(legals_gopher_env(env, state, player, True)) == 0

@cache_ab_gopher
def alpha_beta_gopher_actions(env:Environment,state: State, actual_player: Player, player: Player, 
                              alpha: float, beta: float, depth: int) -> tuple[int, Action]:
    """
    Renvoie une action aléatoire parmis celles renvoyant au meilleur score.
    """
    if final_gopher_player(env, state, player) or depth == 0:
        if depth == 0:
            return evaluation_gopher_env(env, state, player), None
        if actual_player == player:
            # C'est à X de jouer et X n'a plus de coup
            # => Il perd
            return -1, None
        else:
            return 1, None

    if actual_player == player:
        bestvalue = -math.inf
        bestActions = []
        for coup in legals_gopher_env(env, state, actual_player):
            # On applique le coup pour l'evaluer
            state = play_gopher(state, coup, actual_player)

            # on evalue la nouvele configuration obtenue
            _env = copy.deepcopy(env)
            if actual_player == 1:
                value, _ = alpha_beta_gopher_actions(_env, state, actual_player,2, alpha, beta, depth - 1)
            else:
                value, _ = alpha_beta_gopher_actions(_env, state, actual_player,1, alpha, beta, depth - 1)

            # On inverse le coup pour retrouver l'état de base
            state = undo_gopher(state, coup, actual_player)

            #  --------- Comparaison du score du coup --------
            # bestvalue = max(bestvalue, value)
            # Si c'est mieux, on reset et on ne garde que ce coup
            if value > bestvalue:
                bestvalue = value
                bestActions = [coup]
            # Si c'est aussi bien, on l'ajoute à la liste des coups intéressants
            elif value == bestvalue:
                bestActions.append(coup)

            # --------------- Élagage ----------------
            alpha = max(alpha, bestvalue)
            if alpha >= beta:
                break
       
        return bestvalue, bestActions[randint(0, len(bestActions)-1)]

    else:
        bestvalue = math.inf
        bestActions = []
        for coup in legals_gopher_env(env,state, player):
            # On applique le coup pour l'evaluer
            state = play_gopher(state, coup, player)

            # on evalue la nouvele configuration obtenue
            _env = copy.deepcopy(env)
            value, _ = alpha_beta_gopher_actions(_env, state, actual_player,actual_player, alpha, beta, depth - 1)

            # On inverse le coup pour retrouver l'état de base
            state = undo_gopher(state, coup, player)
            
            #  --------- Comparaison du score du coup --------
            #bestvalue = min(bestvalue, value)
            # Si c'est mieux, on reset et on ne garde que ce coup
            if value < bestvalue:
                bestvalue = value
                bestActions = [coup]
            # Si c'est aussi bien, on l'ajoute à la liste des coups intéressants
            elif value == bestvalue:
                bestActions.append(coup)

            beta = min(beta, bestvalue)
            if alpha >= beta:
                break
        
        return bestvalue, bestActions[randint(0, len(bestActions)-1)]


def strategy_alpha_beta_gopher(env: Environment, state: State, player: Player, time_left: Time) -> tuple[Environment, Action]:
    """
    Renvoie le coups le plus interessant ainsi que son score pour un état donné
    """
    if is_premier_coup(state):
        # On commence dans le coin du plateau
        return env, (-env["taille"], -env["taille"])

    # ajustement de la profondeur en fonction du nombre de pions
    depth: int
    if env["nb_pions"] < 4:
        depth = 10
    elif env["nb_pions"] < 20:
        depth = 6
    else:
        depth = 5

    meilleur_coup = None
    if time_left <= 5:
        # Cas urgent : legals renvoit le premier coup trouvé dans une liste.
        coup_unique = legals_gopher(state, player, True)
        # Donc une liste de 1 coup. Mais parfois 0 coups (partir finie) :
        if len(coup_unique) > 0: meilleur_coup = coup_unique[0]

    elif time_left > 10:
        best_score = float('-inf')
        for coup in legals_gopher(state, player):
            score_coup = alpha_beta(env,state, player, player, float('-inf'), float('inf'), depth)
            if score_coup > best_score:
                best_score = score_coup
                meilleur_coup = coup
    else:
        coups = legals_gopher(state, player)
        if len(coups) != 0:
            meilleur_coup = coups[randint(0, len(coups) - 1)]

    env["nb_pions"] += 1
    return env, meilleur_coup

def strategy_alpha_beta_gopher_actions(env: Environment, state: State, player: Player, time_left: Time) -> tuple[Environment, Action]:
    """
    Renvoie le coups le plus interessant ainsi que son score pour un état donné
    """
    if is_premier_coup(state):
        # On commence dans le coin du plateau
        return env, (-env["taille"], -env["taille"])

    # ajustement de la profondeur en fonction du nombre de pions
    depth: int
    n = len(env['cells_impossibles' + str(player)])
    if env["nb_pions"] < 4:
        depth = 11
    elif env["nb_pions"] < 15:
        depth = 9
    elif env["nb_pions"] < 20:
        depth = 8
    else:
        depth = 7

    meilleur_coup = None
    if time_left <= 5:
        # Cas urgent : legals renvoit le premier coup trouvé dans une liste.
        coup_unique = legals_gopher_env(env, state, player, True)
        # Donc une liste de 1 coup. Mais parfois 0 coups (partie finie) :
        if len(coup_unique) > 0: meilleur_coup = coup_unique[0]

    elif time_left > 10:
        score, meilleur_coup = alpha_beta_gopher_actions(env,state, player, player, float('-inf'), float('inf'), depth)
    else:
        coups = legals_gopher_env(env,state, player)
        if len(coups) != 0:
            meilleur_coup = coups[randint(0, len(coups) - 1)]

    env["nb_pions"] += 1
    return env, meilleur_coup



def strategy_aleatoire_gopher(env: Environment, state: State, player: Player,time_left: Time) -> tuple[Environment, Action]:
    """
    Fonction renvoyant un coup aléatoire parmis ceux possibles et None si aucun n'est possible
    """
    if is_premier_coup(state):
        # On commence dans le coin du plateau
        return env, (-env["taille"], -env["taille"])

    coups = legals_gopher(state, player)
    if len(coups) != 0:
        return env, coups[randint(0, len(coups) - 1)]
    else:
        return env, None


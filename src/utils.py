#########################################################
#
# Fichier d'utilitaires pour manipulation de State et
# affichage des plateaux consoles/png.
# 
#########################################################



from src.api import * 
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os


def grid_tuple_to_grid_list(state: State) -> list[list[list[int, int], Player]]:
    """changements entre représentations mutables et non mutables de la grille

    Params:
    state: list[tuple[tuple[int, int], Player]]
    """
    return [ 
        [[cell_player[0][0], cell_player[0][1]], cell_player[1]]
        for cell_player in state
    ]


def grid_list_to_grid_tuple(grid: list[list[list[int, int], Player]]) -> State:
    """changements entre représentations mutables et non mutables de la grille

    Returns:
    state: list[tuple[tuple[int, int], Player]]
    """

    state = [] 
    for cell_player in grid:
        t = tuple([tuple([cell_player[0][0], cell_player[0][1]]), cell_player[1]])
        state.append(t)


    return state   


def afficher_plateau(data, taille=4):
    """affichage console (un peu de travers)"""
    # Création d'un dictionnaire pour stocker les valeurs à chaque coordonnée
    coord_dict = {}
    x_values = []
    y_values = []
    for coord, value in data:
        coord_dict[coord] = value
        x_values.append(coord[0])
        y_values.append(coord[1])
    # Définition des limites de la grille en fonction des coordonnées fournies
    x_min, x_max = min(x_values), max(x_values)
    y_min, y_max = min(y_values), max(y_values)
    # Affichage des valeurs pour chaque coordonnée dans la grille
    for y in range(y_max, y_min - 1, -1):
        row = []
        for x in range(x_min, x_max + 1):
            value = coord_dict.get((x, y), "None")
            row.append(str(value).rjust(5))
        print(" ".join(row))  



def grid_tuple_to_dict(state: State) -> dict[Cell, Player]:
    dic = {}
    for cell_player in state:
        dic[cell_player[0]] = cell_player[1]
    return dic


def grid_dict_to_tuple(state: dict[Cell, Player]) -> State:
    temp = []
    for cell, player in state.items():
        temp.append((cell, player))
    return temp


def afficher_plateau_graph(grid, taille, title):
    """
    Sauvegarde du plateau en png.
    """ 
    size = 1  # outer circle
    height = math.sqrt(3) * size
    width = 2 * size
    horizontal_spacing = (3 / 2) * size
    vertical_spacing = height/2

    fig, ax = plt.subplots()

    # Set equal scaling, aspect ratio
    ax.set_aspect('equal')

    # Define the centers and size of the hexagons
    hex_centers = []
    start_pos = [0, 0]
    pos = [0, 0]
    coord_center = {}
    x = -taille + 1
    y = -taille + 1
    grid_dict = grid_tuple_to_dict(grid)
    # premiere partie qui s'élargie depuis le bas
    for i in range(taille):
        for j in range(i + (i + 1)):
            hex_centers.append(tuple(pos))
            coord_center[tuple(pos)] = (x, y)
            if j < i:
                pos[1] += vertical_spacing
                x += 1
            else:
                pos[1] -= vertical_spacing
                y -= 1
            pos[0] += horizontal_spacing

        # on elargie depuis le bas
        if i < taille - 1:
            start_pos[0] -= horizontal_spacing
            x = -taille + 1
            y = -taille + 1 + (i + 1)
        # dans tous les cas on monte
        start_pos[1] += vertical_spacing
        pos = start_pos.copy()

    # ajustement start_pos entre les deux parties
    start_pos[1] += vertical_spacing
    pos = start_pos.copy()
    x = -taille + 2
    y = 1
    coord_center[tuple(pos)] = (x, y)

    # deuxième partie qui reste droite
    for i in range(taille - 1):
        for j in range(2 * taille - 1):
            hex_centers.append(tuple(pos))
            coord_center[tuple(pos)] = (x, y)
            # pyramide
            if j < taille - 1:
                pos[1] += vertical_spacing
                x += 1
            else:
                pos[1] -= vertical_spacing
                y -= 1
            pos[0] += horizontal_spacing
        # dans tous les cas on monte
        start_pos[1] += height
        pos = start_pos.copy()
        x = y + 2
        y = x + taille - 1

    hex_size = size  # Radius of the hexagons

    # Draw hexagons
    for center in hex_centers:
        if center in coord_center:
            if coord_center[center] in grid_dict:
                cell_state = grid_dict[coord_center[center]]
                if cell_state == 1:
                    draw_hexagon(ax, center, hex_size, edgecolor='black', facecolor='red')
                elif cell_state == 2:
                    draw_hexagon(ax, center, hex_size, edgecolor='black', facecolor='blue')
                else:
                    draw_hexagon(ax, center, hex_size, edgecolor='black', facecolor='beige')
            else:
                draw_hexagon(ax, center, hex_size, edgecolor='black', facecolor='beige')
            #debug (affichage des coordonnées dans les hexagones)
            #ax.text(center[0], center[1], f'({coord_center[center][0]}, {coord_center[center][1]})', ha='center', va='center', fontsize=5)

    # Set limits and grid
    ax.set_xlim(-width * taille, width * taille)
    ax.set_ylim(-height, height * (2 * taille))

    ax.set_title(title)

    #plt.show()
    # Calcul du prochain nom de fichier à donner à cette image.
    saved_graphs_number = [int(f.split('graph')[1].split('.png')[0]) for f in os.listdir('.') if os.path.isfile(f) and 'graph' in f]
    if len(saved_graphs_number) == 0:
        saved_graphs_number = [-1] # Pour que la première img ait le nom "0"
    plt.savefig(f'./graph{max(saved_graphs_number) + 1}.png')
    plt.close()


def draw_hexagon(ax, center, size, **kwargs):
    hexagon = patches.RegularPolygon(center, numVertices=6, radius=size, orientation=np.radians(30), **kwargs)
    ax.add_patch(hexagon)


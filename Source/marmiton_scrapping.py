#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 21:04:24 2019

@author: pierre
"""
from keep import *
from function_marmiton import *
# =============================================================================
# Variables pour la requete
# =============================================================================
search_str_list=["croque madame","pizza carbonara","pate carbonara","Gateaux Chocolat","salade césar","tomates moza"]
search_str_list=[search_str.replace(" ", "-") for search_str in search_str_list]
root_url="https://www.marmiton.org/"
url=root_url+'recettes/recherche.aspx'

a=[scrap_url(url,{"aqt":search_str}) for search_str in search_str_list]
b=[data_scraping(root_url+url[0][0]) for url in a]

n_per=[3,2,2,8,2,1]
if len(n_per)==len(search_str_list):
    liste_finale=liste_ingredient(b,n_per)
    create_doc_list(liste_finale)
    create_doc_json(liste_finale)
else:
    liste_finale='Erreur de taille'

export(liste_finale)


# =============================================================================
# Explication Algo :
#     0- Etablir les paramètres de la recherche
#     1- Rechercher les differentes recette se rapportant à la recherche
#     2- Conserver les urls des recettes les plus proche de la recherche
#     3- Etablir la liste des ingrédients
# ============================================================================
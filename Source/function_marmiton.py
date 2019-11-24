#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 17 14:27:07 2019

@author: pierre
"""
import requests
from bs4 import BeautifulSoup
import re
import json
from fuzzywuzzy import fuzz
from unidecode import unidecode
from fractions import Fraction
import copy
from math import ceil

CONSTANTE_CS=1.5
STRING_CS='cuilleres a soupe'
CONSTANTE_CC=0.5
STRING_CC='cuillere a cafe'
CONSTANTE_PINCEE=3

def scrap_url(url,param):
    try:
        requete = requests.get(url,params=param)
        html_file  = requete.content
        soup = BeautifulSoup(html_file,'lxml')
    except :
        print("Erreur")
    if (requete.status_code == requests.codes.ok):
        hrefs=[]
        noms=[]
        div_content=soup.find_all('a',class_="recipe-card-link")
        noms_spans=soup.find_all('span',class_="recipe-card__add-to-notebook")
#        print(div_content)
        for a_s in div_content:
#            print('sucess')
            hrefs.append(a_s.get('href'))
        for nom in noms_spans:
            noms.append(nom.get('data-recipe-title'))
        return (hrefs,noms)
    
def data_scraping(url_string):
    try:
        requete = requests.get(url_string)
        html_file  = requete.content
        soup = BeautifulSoup(html_file,'lxml')
    except :
        print("Erreur")
    finally: 
        nom=soup.find(class_="main-title").text
        div_content=soup.find('div',class_="recipe-infos")
        spans=div_content.find_all('span')
        attributs_spans=[span.text for span in spans]
        attributs={'tps':attributs_spans[1],
                   'nb_pers':int(attributs_spans[3]),
                   'dif':attributs_spans[4],
                   'exp':attributs_spans[5]}
        
        ingredient_list=soup.find_all("li",class_="recipe-ingredients__list__item")
        ingredient=[ing.find_all('span') for ing in ingredient_list]
        ingredient_list_detail=[[item.text for item in ing] for ing in ingredient]
       
        ustensils_list=soup.find_all("span", class_="recipe-utensil__name")
        ustensils_list=[re.sub('[^\w ]','',item.text) for item in ustensils_list]
    
        ustensils={}
        for item in ustensils_list:
            ustensils[re.sub('[0-9 ]','',item)]=re.sub('[^0-9]','',item)
            
        recette = {'nom':nom,
                   'attr': attributs,
                   'ingredients': ingredient_list_detail,
                   'ustensils': ustensils}
    return recette

def collect_menus(search_str,NB_pagemax):
    root_url="https://www.marmiton.org/"
    pageurl=root_url+'/recettes/?page='
    links=set()
    data ={}
    if NB_pagemax!=0 : root_urls=set([root_url_string+str(i+1) for i in range(NB_pagemax)])
    else:
        url_search=root_url+"/recettes/recherche.aspx?aqt="+search_str
        urls=[url_search]
        
    for url in urls:
        print('url=',url)
        links.update(scrap_url(url)) 
    
    for link in links:
        print(link)
        key=re.sub('[^0-9]','',link)
    #    data[key]=data_scraping(link)
     
    with open('marmiton.json', 'w', encoding='utf-8') as f:
         json.dump(data, f, ensure_ascii=False, indent=3)

def create_doc_list(dico_final):
    with open('../Output/Listeingredient.txt', 'w', encoding='utf-8') as f:
        f.write("--Liste des Ingrédients--\r\n") 
        for nom_ing,qt in dico_final.items():
             f.write("{} {}\r\n".format(qt,nom_ing))

def create_doc_json(dico_final):
    with open('../Output/liste_ingredient.json', 'w', encoding='utf-8') as f:
              json.dump(dico_final, f)

    
def liste_ingredient(menus,nb_p):
    liste_ingredient=[]
    normalize_qt(menus,nb_p)
#    Création des listes de la liste des ingrédients
    for menu in menus:
        for liste in menu["ingredients"]:
            liste_ingredient.append(liste)

#    Gestion des types de la liste d'ingrédients
    liste_ingredient=handle_types(liste_ingredient)
#    print('Liste in 1=\n',liste_ingredient)
#    Transformation des qt 'CUILLERE A SOUPE/CAFE'
    
    for item in liste_ingredient:
        if(STRING_CS in item[1]):
            item[0]=item[0]*CONSTANTE_CS
#            print(item[1])
            item[1]=item[1].replace(STRING_CS,'cl')
        elif (STRING_CC in item[1]):
            item[0]=item[0]*CONSTANTE_CC
            item[1]=item[1].replace(STRING_CC,'cl')
            
#    Extraction noms ingrédients
    extracted_ing_1=[item[1] for item in liste_ingredient]        
    indices=[key for key,ing in enumerate(extracted_ing_1) if 'g de ' in ing]
    print(indices)
    l1=[re.sub('g de ', '',ing).strip() for ing in extracted_ing_1]
    indices=[l1[idx] for idx in indices]
##    Remplacement des noms par fréquence
    Substitution=freqOrthog(l1)
    l1_joined='//'.join(l1)
    l1=replace(l1_joined,Substitution).split('//')
    f=count_freq(l1)
    add_string(indices,f)
    qt=[item[0] for item in liste_ingredient]
    
#    Création de la liste finale
    dico_ing_final={}
    for key,item in f.items():
        qt_final=0.0
        for idx in item :
            qt_final=qt_final+qt[idx]
        dico_ing_final[key]=ceil(qt_final)
    
    print('\n\n')
    print(dico_ing_final)
    
    return dico_ing_final

def add_string(indices,freq):
    for item in indices:
        if item in freq.keys():
            freq['g de '+item]=freq.pop(item)
      
def handle_types(liste_ingredient):
    for item in liste_ingredient:
        item[1]=unidecode(item[1].lower())
        item[2]=unidecode(item[2].lower())
        if(item[0]!=''): 
            temp=Fraction(item[0])
            item[0]=float(temp)
        else: item[0]=CONSTANTE_PINCEE
    return(liste_ingredient) 
    
def freqOrthog(data) :
    res=copy.deepcopy(data)
    comparelen=lambda x,y: mot if len(x) > len(y) else y 
    simili={}
    for mot_test in data:
        for item in data:
            condition = fuzz.partial_ratio(mot_test,item)
            if(condition>87):
                simili[item]=mot_test
    return simili

def replace(string, substitutions):
    substrings = sorted(substitutions, key=len, reverse=True)
    regex = re.compile('|'.join(map(re.escape, substrings)))
    return regex.sub(lambda match: substitutions[match.group(0)], string)

def extract(datas,col):
    res=[]
    for data in datas:
        if (not(data[col] in res)):
            res.append(data[col])
        else: continue
    return res

def count_freq(liste):
    #Création d'un dict vide
    freq = {} 
    for elem in liste: 
        indices=[key for key,ing in enumerate(liste) if elem in ing]
        freq[elem] = indices
    return freq

def normalize_qt(list_dico_menus,nb_p):
    for idx,item in enumerate(list_dico_menus):
        coef_normalisation=nb_p[idx]/(item["attr"]["nb_pers"])
        print(coef_normalisation)
        list_temp=item["ingredients"]
        handle_types(item["ingredients"])
        for item in list_temp:
            item[0]=int(item[0])*coef_normalisation           
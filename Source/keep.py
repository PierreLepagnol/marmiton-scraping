#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 17 19:13:28 2019

@author: pierre
"""
import gkeepapi

def export(liste):
    user = 'Nom d\'utilisateur compte google'
    password= 'Mot de passe compte google'
    keep = gkeepapi.Keep()
    keep.login(user,password)
    liste_export=[(str(item)+" "+key,False) for key,item in liste.items()]
    keep.createList('liste course',liste_export)
    keep.sync()

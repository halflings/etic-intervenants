#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import lxml.html
import pymongo

# URL du fichier XML où se trouvent les études proposées par ETIC
ETUDES_XML_URL = 'https://doletic.etic-insa.com/services/etudes.php'

# Initialisation de la BdDs
db = pymongo.MongoClient().etic
db_etudes = db.etudes

class Etude(object):

    def __init__(self, numero, titre, domaine, statut, description=""):
        self.numero = int(numero)
        self.titre = titre
        self.domaine = domaine
        self.statut = int(statut)
        self.description = description

    @staticmethod
    def by_domaine(domaine):
        etudes = list()
        etudes_result = db_etudes.find({'domaine' : domaine})
        for etude in etudes_result:
            params = [etude[param] for param in ['numero', 'titre', 'domaine', 'statut', 'description']]
            etudes.append(Etude(*params))
        return etudes

    @staticmethod
    def fromxml(node):
        attributs = list()
        for attr in ['numero', 'titre', 'domaine', 'statut', 'description']:
            attributs.append(node.xpath('@' + attr)[0].encode('utf-8'))
        return Etude(*attributs)

    @staticmethod
    def update_db(xml_url=ETUDES_XML_URL):
        """ Met à jour la BdD des études """

        # On purge la base de donnée d'études
        db_etudes.drop()

        # On récupère le fichier XML contenant les études et on extrait ces dernières
        etudes_content = requests.get(xml_url, verify=False).content
        etudes_xml = lxml.html.fromstring(etudes_content)
        etudes_nodes = etudes_xml.xpath('//etude')
        
        # Pour chaque étude...
        for node in etudes_nodes:
            # On crée un object 'Etude' à partir des données XML
            etude = Etude.fromxml(node)
            # On insert l'objet Etude dans la BdD
            db_etudes.insert(etude.__dict__)

    def __str__(self):
        """ String representation, mostly for debugging """
        res = str()
        res += "Étude n°{}:\n".format(self.numero)
        res += "  - Domaine: '{}'\n".format(self.domaine)
        res += "  - Titre: '{}'\n".format(self.titre.encode('utf-8'))
        res += "  - Statut: '{}'\n".format(self.statut)
        if self.description:
            res += "  - Description: '{}'\n".format(self.description)
        return res
if __name__ == '__main__':
    # # Mise à jour des études depuis le fichier XML
    # Etude.update_db()

    # # Affichage des études
    # etudes = list(db_etudes.find())

    for etude in Etude.by_domaine('Informatique'):
        print etude
        print '-'*60

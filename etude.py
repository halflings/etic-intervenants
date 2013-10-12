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

    # Méthodes pour importer une méthode soit depuis un noeud XML (fourni par le service doletic), soit depuis le format JSON (MongoDB)
    @staticmethod
    def from_xml(node):
        attributs = list()
        for attr in ['numero', 'titre', 'domaine', 'statut', 'description']:
            attributs.append(node.xpath('@' + attr)[0].encode('utf-8'))
        return Etude(*attributs)

    @staticmethod
    def from_json(etude_json):
        params = [etude_json[param] for param in ['numero', 'titre', 'domaine', 'statut', 'description']]
        return Etude(*params)

    # Méthodes pour retrouver des études depuis la base de donnée selon plusieurs critères
    @staticmethod
    def all():
        return [Etude.from_json(etude_json) for etude_json in db_etudes.find()]

    @staticmethod
    def by_domaine(domaine):
        return [Etude.from_json(etude_json) for etude_json in db_etudes.find({'domaine': domaine})]

    @staticmethod
    def by_numero(numero):
        result = db_etudes.find({'numero': numero})
        return Etude.from_json(result[0]) if result else None

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
            etude = Etude.from_xml(node)
            # On insert l'objet Etude dans la BdD
            db_etudes.insert(etude.__dict__)

    def __str__(self):
        """ Résumé d'une étude. Seulement pour faire du debugging. """
        res = str()
        res += "Étude n°{}:\n".format(self.numero)
        res += "  - Domaine: '{}'\n".format(self.domaine)
        res += "  - Titre: '{}'\n".format(self.titre.encode('utf-8'))
        res += "  - Statut: '{}'".format(self.statut)
        if self.description:
            res += "\n  - Description: '{}'".format(self.description)
        return res

if __name__ == '__main__':
    # # Mise à jour des études depuis le fichier XML
    # Etude.update_db()

    # # Affichage des études
    # etudes = list(db_etudes.find())

    for etude in Etude.by_domaine('Informatique'):
        print etude
        print '-'*60

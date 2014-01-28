#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import lxml.html
import mongoengine

import config

# URL du fichier XML où se trouvent les études proposées par ETIC

# Initialisation de la BdDs
db = mongoengine.connect(config.db_name)

def fetch_etudes(xml_url=config.etudes_xml_url):
    """ Met à jour la BdD des études """

    # On purge la base de donnée d'études
    db.drop_database(config.db_name)

    # On récupère le fichier XML contenant les études et on extrait ces dernières
    etudes_content = requests.get(xml_url, verify=False).content
    etudes_xml = lxml.html.fromstring(etudes_content)
    etudes_nodes = etudes_xml.xpath('//etude')

    # Pour chaque étude...
    for node in etudes_nodes:
        # On crée un object 'Etude' à partir des données XML
        etude = Etude.from_xml(node)

        # On sauvegarde l'étude dans la BdD
        etude.save()


class Etude(mongoengine.Document):

    numero = mongoengine.fields.IntField(required=True)
    titre = mongoengine.fields.StringField(required=True)
    domaine = mongoengine.fields.StringField(required=True)
    description = mongoengine.fields.StringField()
    statut = mongoengine.fields.IntField()

    # Méthodes pour importer une méthode soit depuis un noeud XML (fourni par le service doletic), soit depuis le format JSON (MongoDB)
    @staticmethod
    def from_xml(node):
        attributs = dict()
        for attr in ['numero', 'titre', 'domaine', 'statut', 'description']:
            attributs[attr] = node.xpath('@' + attr)[0].encode('utf-8')
        return Etude(**attributs)

    def __str__(self):
        """ Résumé d'une étude. Seulement pour faire du debugging. """
        res = str()
        res += "Étude n°{}:\n".format(self.numero)
        res += "  - Domaine: '{}'\n".format(self.domaine.encode('utf-8'))
        res += "  - Titre: '{}'\n".format(self.titre.encode('utf-8'))
        res += "  - Statut: '{}'".format(self.statut)
        if self.description:
            res += "\n  - Description: '{}'".format(self.description)
        return res

if __name__ == '__main__':
    # Mise à jour des études depuis le fichier XML
    fetch_etudes()

    # Affichage des études
    for etude in Etude.objects():
        print etude
        print '-'*60

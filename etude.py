#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import lxml.html
import mongoengine

import config

# Initialisation de la BdDs
db = mongoengine.connect(config.db_name)

def fetch_etudes(xml_url=config.etudes_xml_url):
    """ Met à jour la BdD des études """

    # On purge la base de donnée d'études
    Etude.drop_collection()

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
    number = mongoengine.fields.IntField(required=True, primary_key=True)
    title = mongoengine.fields.StringField(required=True)
    domain = mongoengine.fields.StringField(required=True)
    description = mongoengine.fields.StringField()
    status = mongoengine.fields.IntField()

    # Méthodes pour importer une méthode soit depuis un noeud XML (fourni par le service doletic), soit depuis le format JSON (MongoDB)
    attr_map = {'numero':'number', 'titre':'title', 'domaine':'domain', 'statut':'status'}

    @staticmethod
    def from_xml(node):
        attributes = dict()
        for xml_attr, attr in Etude.attr_map.iteritems():
            attributes[attr] = node.xpath('@' + xml_attr)[0].encode('utf-8')
        return Etude(**attributes)

    def __str__(self):
        """ Résumé d'une étude. Seulement pour faire du debugging. """
        res = str()
        res += "Étude n°{}:\n".format(self.number)
        res += "  - Domaine: '{}'\n".format(self.domain.encode('utf-8'))
        res += "  - Titre: '{}'\n".format(self.title.encode('utf-8'))
        res += "  - Statut: '{}'".format(self.status)
        if self.description:
            res += "\n  - Description: '{}'".format(self.description)
        return res

if __name__ == '__main__':
    # Mise à jour des études depuis le fichier XML
    #fetch_etudes()

    # Affichage des études
    for etude in Etude.objects():
        print etude
        print '-'*60

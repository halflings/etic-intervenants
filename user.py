#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mongoengine
import config

from etude import Etude

DEPARTEMENTS = {'IF' : 'Informatique',
                'TC' : 'Telecommunications, Services et Usages',
                'GI' : 'Génie Industriel',
                'GE' : 'Génie Electrique',
                'GEN' : 'Génie Energétique et Environnement',
                'SGM' : 'Science et Génie des Matériaux',
                'GCU' : 'Génie Civil et Urbanisme',
                'GMD' : 'Génie Mécanique Developpement',
                'GMC' : 'Génie Mécanique Conception',
                'GMPP': 'Génie Mécanique Procédés Plasturgie',
                'BIM' : 'BioInformatique et Modélisation',
                'BB' : 'Biochimie et Biotechnologies'}

# Initialisation de la BdD
db = mongoengine.connect(config.db_name)

class User(mongoengine.Document):

    email = mongoengine.fields.StringField(required=True, unique=True)
    password = mongoengine.fields.StringField(required=True)
    nom = mongoengine.fields.StringField(required=True)
    departement = mongoengine.fields.StringField(required=True)

    actif = mongoengine.fields.BooleanField(default=False)

    etudes = mongoengine.fields.ListField(mongoengine.fields.ReferenceField(Etude))
    abonnements = mongoengine.fields.ListField(mongoengine.fields.StringField())

    def save(self, *args, **kwargs):
        """ Surcharge de la méthode save pour valider les données """

        # Vérification de l'email
        if not self.email.endswith('@insa-lyon.fr'):
            raise ValueError("Impossible de créer un utilisateur avec un email non-INSA : {}".format(self.email))

        # Vérification du département
        if not self.departement in DEPARTEMENTS:
            raise ValueError("Département introuvable dans la base de données : {}".format(self.departement))

        # Appel à la méthode save de la classe mère
        super(User, self).save(*args, **kwargs)

    def subscribe_etude(self, num_etude):
        etude = Etude.objects.get(numero=num_etude)
        # S'il existe une étude avec ce numéro, on la rajoute à la liste d'études suivies
        if etude is None:
            raise ValueError("Aucune étude ne porte le numéro '{}'".format(num_etude))

        self.etudes.append(etude)
        self.save()

    def unsubscribe_etude(self, num_etude):
        etude = Etude.objects.get(numero=num_etude)
        # S'il existe une étude avec ce numéro, on la rajoute à la liste d'études suivies
        if etude is None:
            raise ValueError("Aucune étude ne porte le numéro '{}'".format(num_etude))

        if not etude in self.etudes:
            raise ValueError("Cette étude n'est pas suivie par l'utilisateur")

        self.etudes.remove(etude)
        self.save()


    def subscribe_departement(self, departement):
        if not departement in DEPARTEMENTS:
            raise ValueError("Département inconnu: '{}'".format(departement))

        self.abonnements.append(departement)
        self.save()

    def unsubscribe_departement(self, departement):
        if not departement in self.abonnements:
            raise ValueError("Impossible de se désabonner d'un département auquel l'utilisateur n'est pas abonné: '{}'".format(departement))

        self.abonnements.remove(departement)
        self.save()

    def __str__(self):
        return "Utilisateur {}. email = {}".format(self.nom, self.email)

if __name__ == '__main__':

    db = mongoengine.connect(config.test_db)
    User.drop_collection()

    # Tests unitaires de la classe User et de sa base de données
    print ". Création d'un object User"
    u = User(nom='Ahmed Kachkach', password='mypassword', email='test@insa-lyon.fr', departement='IF')
    u.save()

    assert User.objects.get(email='test@insa-lyon.fr').nom == 'Ahmed Kachkach'


    print ". Changement du nom de l'utilisateur de 'Ahmed Kachkach' à 'Dwight Schrute'"
    u.nom = 'Dwight Shrute'
    u.save()

    assert User.objects.get(email='test@insa-lyon.fr').nom == 'Dwight Shrute'


    print ". Abonnement de l'utilisateur à toutes les offres GI"
    u.subscribe_departement('GI')
    u.save()

    assert 'GI' in User.objects.get(email='test@insa-lyon.fr').abonnements


    print '-' * 80
    print "Fin des tests et suppression de l'utilisateur de test"
    u.delete()

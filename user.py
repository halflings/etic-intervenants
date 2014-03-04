#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import hashlib

import mongoengine

import config

from etude import Etude

DEPARTMENTS = { 'IF'  : u'Informatique',
                'TC'  : u'Telecommunications, Services et Usages',
                'GI'  : u'Génie Industriel',
                'GE'  : u'Génie Electrique',
                'GEN' : u'Génie Energétique et Environnement',
                'SGM' : u'Science et Génie des Matériaux',
                'GCU' : u'Génie Civil et Urbanisme',
                'GMD' : u'Génie Mécanique Developpement',
                'GMC' : u'Génie Mécanique Conception',
                'GMPP': u'Génie Mécanique Procédés Plasturgie',
                'BIM' : u'BioInformatique et Modélisation',
                'BB'  : u'Biochimie et Biotechnologies'}

# Initialisation de la BdD
db = mongoengine.connect(config.db_name)

def generate_salt():
    return os.urandom(16).encode('base_64')

def hash_password(password, salt):
    return hashlib.sha512(salt + password).hexdigest()

class User(mongoengine.Document):

    email = mongoengine.StringField(required=True, unique=True)

    secret_hash = mongoengine.StringField(required=True)
    salt = mongoengine.StringField(required=True)

    name = mongoengine.StringField(required=True)
    department = mongoengine.StringField(required=True)

    activated = mongoengine.BooleanField(default=False)

    etudes = mongoengine.ListField(mongoengine.ReferenceField(Etude))
    following = mongoengine.ListField(mongoengine.StringField())

    @staticmethod
    def new_user(email, password, name, department, activated=False):
        user = User(email=email, name=name, department=department, activated=activated)

        user.salt = generate_salt()
        user.secret_hash = hash_password(password, user.salt)

        return user

    def valid_password(self, password):
        return hash_password(password, self.salt) == self.secret_hash

    def clean(self):
        """ Validation des données """

        # Vérification de l'email
        if not self.email.endswith('@insa-lyon.fr'):
            raise mongoengine.ValidationError(u"Impossible de créer un utilisateur avec un email non-INSA : {}".format(self.email))

        # Vérification du département
        if not self.department in DEPARTMENTS:
            raise mongoengine.ValidationError(u"Département introuvable dans la base de données : {}".format(self.department))

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


    def subscribe_department(self, department):
        if not department in DEPARTMENTS:
            raise ValueError("Département inconnu: '{}'".format(department))

        self.following.append(department)
        self.save()

    def unsubscribe_department(self, department):
        if not department in self.following:
            raise ValueError("Impossible de se désabonner d'un département auquel l'utilisateur n'est pas abonné: '{}'".format(department))

        self.following.remove(department)
        self.save()

    def __str__(self):
        return "Utilisateur {}. email = {}".format(self.name, self.email)

if __name__ == '__main__':

    db = mongoengine.connect(config.test_db)
    User.drop_collection()

    # Tests unitaires de la classe User et de sa base de données
    print ". Création d'un object User"
    u = User.new_user(email='test@insa-lyon.fr',name='Ahmed Kachkach', password='mypassword', department='IF')
    u.save()

    assert User.objects.get(email='test@insa-lyon.fr').name == 'Ahmed Kachkach'


    print ". Changement du name de l'utilisateur de 'Ahmed Kachkach' à 'Dwight Schrute'"
    u.name = 'Dwight Shrute'
    u.save()

    assert User.objects.get(email='test@insa-lyon.fr').name == 'Dwight Shrute'


    print ". Abonnement de l'utilisateur à toutes les offres GI"
    u.subscribe_department('GI')
    u.save()

    assert 'GI' in User.objects.get(email='test@insa-lyon.fr').following


    print '-' * 80
    print "Fin des tests et suppression de l'utilisateur de test"
    u.delete()

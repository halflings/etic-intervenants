#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymongo

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
db = pymongo.MongoClient().etic
users_db = db.users
db_etudes = db.etudes

class User(object):

    def __init__(self, nom, password, email, departement, etudes=[], departements=[]):
        self.nom = nom
        self.password = password

        # Vérification de l'email
        if not email.endswith('@insa-lyon.fr'):
            raise ValueError("Impossible de créer un utilisateur avec un email non-INSA : {}".format(email))
        self.email = email

        # Vérification du département
        if not departement in DEPARTEMENTS.keys():
            raise ValueError("Département introuvable dans la base de données : {}".format(departement))
        
        self.departement = departement

        # Les études et départements suivis par l'utilisateur:
        self.etudes = etudes
        self.departements = departements

    def subscribe_etude(self, num_etude):
        etude = list(db_etudes.find({'numero' : num_etude}))
        # S'il existe une étude avec ce numéro, on la rajoute à la liste d'études suivies
        if etude:
            self.etudes.append(num_etude)
            self.merge()

    def unsubscribe_etude(self, num_etude):
        if num_etude in self.etudes:
            self.etudes.remove(num_etude)
            self.merge()


    def subscribe_departement(self, departement):
        if departement in DEPARTEMENTS.keys():
            self.departements.append(departement)
            self.merge()

    def unsubscribe_departement(self, departement):
        if unsubscribe_departement in self.departements:
            self.etudes.remove(departement)
            self.merge()

    @staticmethod
    def by_email(email):
        user = list(users_db.find({'email' : email}))
        if user:
            attributes = [user[0][attr] for attr in ['nom', 'password', 'email', 'departement', 'etudes', 'departements']]
            return User(*attributes)
        else:
            return None

    def merge(self):
        """ Met à jour la BdD avec les données actuelles de l'objet """
        user_in_db = list(users_db.find({'email' : self.email}))

        # Si l'utilisateur est déjà dans la base de données, on le met à jour
        if user_in_db:
            users_db.update(dict(_id=user_in_db[0]['_id']), self.__dict__)
        # S'il n y est pas, on le crée
        else:
            users_db.insert(self.__dict__)

    def update(self):
        """ Met à jour les données de l'objet avec celles présentes dans la BdD """
        user_in_db = list(users_db.find({'email' : self.email}))
        if not user_in_db:
            raise ValueError("Tentative de mise à jour d'un objet User qui n'existe pas dans la base de données")
        
        self.__dict__ = user_in_db[0]

    def remove(self):
        """ Suppression de l'utilisateur """
        users_db.remove({'email' : self.email})

if __name__ == '__main__':
    
    # Tests unitaires de la classe User et de sa base de données

    print "Création d'un object User avec..."
    print "nom='Ahmed Kachkach', password='mypassword', email='test@insa-lyon.fr', departement='IF'"
    u = User(nom='Ahmed Kachkach', password='mypassword', email='test@insa-lyon.fr', departement='IF')
    print "... et synchronisation de l'objet avec la base de données"
    u.merge()

    print ""
    print "Dans la BdD:"
    print User.by_email('test@insa-lyon.fr').__dict__

    print '-' *80
    print "Changement du nom de l'utilisateur de 'Ahmed Kachkach' à 'Dwight Schrute'"
    u.nom = 'Dwight Shrute'
    u.merge()


    print ""
    print "Dans la BdD:"
    print User.by_email('test@insa-lyon.fr').__dict__


    print '-' *80
    print "Abonnement de l'utilisateur à toutes les offres GI"
    u.subscribe_departement('GI')
    u.merge()

    print ""
    print "Dans la BdD:"
    print User.by_email('test@insa-lyon.fr').__dict__


    print '-'*80
    print "Fin des tests et suppression de l'utilisateur de test"
    u.remove()
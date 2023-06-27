from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for, flash
# from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import check_password_hash, generate_password_hash,Bcrypt
from flask_login import UserMixin
from enum import Enum
from sqlalchemy import Enum as SQLAlchemyEnum
import random
from sqlalchemy import event,DDL
from sqlalchemy.orm import mapper
from sqlalchemy.orm.attributes import get_history
from datetime import datetime

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://babou:passer@localhost/yeswecan'
app.secret_key = 'your_secret_key'
db = SQLAlchemy(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    matricule = db.Column(db.String(10), nullable=False)
    login = db.Column(db.String(30), nullable=False, unique=True)
    prenom = db.Column(db.String(30), nullable=False)
    nom = db.Column(db.String(30), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    sigle_service = db.Column(db.String(30))
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    state = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(60), nullable=False)
    nom_abrege = db.Column(db.String(30))
    date_debut = db.Column(db.DateTime, nullable=False)
    date_fin = db.Column(db.DateTime)
    password = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    role_user = db.relationship('Role', backref='users', lazy=True)

    def __init__(self, matricule, login, prenom, nom, role, sigle_service, service_id, state, email, nom_abrege, date_debut, date_fin=None, password=None):
        self.matricule = matricule
        self.login = login
        self.prenom = prenom
        self.nom = nom
        self.role = role
        self.sigle_service = sigle_service
        self.service_id = service_id
        self.state = state
        self.email = email
        self.nom_abrege = nom_abrege
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.password = password

    #     if password:
    #         self.set_password(password)

    # def set_password(self, password):
    #     self.password_hash = generate_password_hash(password)

    # def check_password(self, password):
    #     return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)


    @staticmethod
    def get(id):
        return User(id)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(30), nullable=False)
    sigle = db.Column(db.String(30), nullable=False)
    utilisateurs = db.relationship('User', backref='service')

    def __init__(self, nom,sigle):
        self.nom = nom
        # self.chef_service = chef_service
        self.sigle = sigle


    @staticmethod
    def get(id):
        return Service(id)



class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(30), unique=True)
    users_role = db.relationship('User', backref='role', lazy=True)


    # def __init__(self,role,users_role):
    #     self.role = role


class TypeDefaut(db.Model):
    __tablename__ = 'type_defauts'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False,default=f'{random.getrandbits(14)}_code_{random.randint(112,666)}')
    type_defaut = db.Column(db.String(20), nullable=False)
    description_defaut = db.Column(db.String(800), nullable=False)
    confirm = db.Column(db.String(20))
    date_debut = db.Column(db.Date, nullable=False)
    date_fin = db.Column(db.Date)
    user_email = db.Column(db.String(200), nullable=False)
    commentaires=db.Column(db.TEXT)
    commentaires_evaluer = db.Column(db.String(255))
    commentaires_n1 = db.Column(db.String(255))
    validation = db.Column(db.String(20), nullable=False)
    service = db.Column(db.String(100),nullable=False)
    date_dernier_rappel = db.Column(db.Date)

    @staticmethod
    def get_defauts_to_remind():
        today = datetime.now().date()
        return TypeDefaut.query.filter(TypeDefaut.confirm == 'NON', TypeDefaut.date_dernier_rappel < today).all()

    def set_last_reminder_date(self, date):
        self.date_dernier_rappel = date
        db.session.commit()

    @staticmethod
    def get_next_code():
        code = random.getrandbits(14)+random.randint(112,666)
        if code:
            code = random.getrandbits(14)+random.randint(112,666)+1
        return 'code_'+str(code)
    
    @staticmethod
    def get_defauts_by_user_email(email):
        return TypeDefaut.query.filter_by(user_email=email).all()

    
    def __init__(self,code, type_defaut, description_defaut,confirm, date_debut, date_fin=None,user_email=None,commentaires="",commentaires_evaluer="",commentaires_n1="",validation="Invalide",service=None,date_dernier_rappel=datetime.now()):
        self.code = code
        self.type_defaut = type_defaut
        self.description_defaut = description_defaut
        self.confirm=confirm
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.user_email=user_email,
        self.commentaires = commentaires
        self.commentaires_evaluer=commentaires_evaluer
        self.commentaires_n1=commentaires_n1
        self.validation = validation
        self.service=service
        self.date_dernier_rappel=date_dernier_rappel


# Définir la classe modèle pour la table Ticket
class Ticket(db.Model):
    __tablename__ = 'tickets'

    id = db.Column(db.Integer, primary_key=True)
    numero_demande = db.Column(db.String(20))
    enregistre_le = db.Column(db.DateTime)
    date_resolution = db.Column(db.DateTime)
    libelle_service = db.Column(db.String(200))
    demandeur = db.Column(db.String(60))
    statut_demande = db.Column(db.String(50))
    resolu_par = db.Column(db.String(60))
    origine_demande = db.Column(db.String(30))
    date_resolution_max = db.Column(db.DateTime)
    description = db.Column(db.TEXT)
    resolution = db.Column(db.TEXT)
    sla = db.Column(db.String(10))
    nom_abrege_agent = db.Column(db.String(300))
    type_echant = db.Column(db.String(30))
    defaut = db.Column(db.String(10))
    type_defaut = db.Column(db.TEXT)
    description_defaut = db.Column(db.String(800))
    commentaires_defaut = db.Column(db.String(400))
    periode = db.Column(db.String(100))
    evaluateur = db.Column(db.String(30))


class Fichier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero_demande = db.Column(db.String(20))
    enregistre_le = db.Column(db.Date)
    date_resolution = db.Column(db.Date)
    libelle_service = db.Column(db.String(200))
    saisi_par = db.Column(db.String(50))
    demandeur = db.Column(db.String(50))
    demandeur_entite = db.Column(db.String(200))
    localisation = db.Column(db.String(200))
    urgence_utilisateur = db.Column(db.String(100))
    impact = db.Column(db.String(100))
    priorite = db.Column(db.String(100))
    statut_demande = db.Column(db.String(100))
    delai_resolution_hhmm = db.Column(db.String(10))
    delai_resolution_min = db.Column(db.Integer)
    resolution_immediate = db.Column(db.String(10))
    resolu_par_groupe = db.Column(db.String(50))
    origine_demande = db.Column(db.String(100))
    date_resolution_maximum = db.Column(db.String(1000))
    description = db.Column(db.String(500))
    resolu_par_intervenant = db.Column(db.String(50))
    service_retard_hhmm = db.Column(db.String(10))
    service_retard_min = db.Column(db.Integer)
    group_fr = db.Column(db.String(100))
    resolution = db.Column(db.String(255))
    sla = db.Column(db.String(100))
    beneficiaire_courriel = db.Column(db.String(200))
    xa_date_fin_de_mois = db.Column(db.String(255))
    xb_periode = db.Column(db.String(7))
    xc_statut_trait = db.Column(db.String(100))
    xx_num_sequence = db.Column(db.Integer)
    xx_agent_transfert_dsi = db.Column(db.String(200))
    xx_agent_responsable = db.Column(db.String(200))
    xx_service = db.Column(db.String(200))
    xx_intervalle_delai_res = db.Column(db.String(200))
    xx_delai30min = db.Column(db.String(3))
    xx_delai1h = db.Column(db.String(3))
    xx_delai2h = db.Column(db.String(3))
    xx_delai1j = db.Column(db.String(3))
    xx_delai2j = db.Column(db.String(3))
    xx_respect_delais = db.Column(db.String(100))
    xx_retard_en_jours = db.Column(db.String(255))
    xx_activite = db.Column(db.String(200))
    xx_a_comptabiliser = db.Column(db.String(100))
    xx_application = db.Column(db.String(200))
    xx_dep_traitant = db.Column(db.String(200))
    xx_direction = db.Column(db.String(200))
    xx_agent_refus = db.Column(db.String(200))
    numero = db.Column(db.String(100))
    type_echant = db.Column(db.String(200))
    defaut = db.Column(db.String(200))
    type_description_defaut = db.Column(db.String(100))
    description_du_defaut = db.Column(db.String(200))
    commentaires = db.Column(db.String(2000))
    note_defaut = db.Column(db.String(10))
    agent_escalade = db.Column(db.String(200))
    pertinence_escalade = db.Column(db.String(100))
    type_erreur_escalade = db.Column(db.String(200))
    actions_correctives_preventives = db.Column(db.String(500))



    def to_dict(self):
        return {
            'numero_demande': self.numero_demande,
            'enregistre_le': self.enregistre_le,
            'date_resolution': self.date_resolution,
            'libelle_service':self.libelle_service, 
            'statut_demande': self.statut_demande,
            'defaut':self.defaut
        }

class Fichier_charger(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_user = db.relationship('User', backref='users', lazy=True) 

    def __init__(self,nom, user_id):
        self.nom = nom
        self.user_id = user_id


    
class Corbeille(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    matricule = db.Column(db.String(10), nullable=False)
    login = db.Column(db.String(30), nullable=False, unique=True)
    prenom = db.Column(db.String(30), nullable=False)
    nom = db.Column(db.String(30), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    sigle_service = db.Column(db.String(30))
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    state = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(60), nullable=False)
    nom_abrege = db.Column(db.String(30))
    date_debut = db.Column(db.DateTime, nullable=False)
    date_fin = db.Column(db.DateTime)
    password = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    corbeille_role = db.relationship('Role', backref='corbeilles', lazy=True)



    def __init__(self, matricule, login, prenom, nom, role, sigle_service, service_id,role_id, state, email, nom_abrege, date_debut, date_fin=None, password=None):
        self.matricule = matricule
        self.login = login
        self.prenom = prenom
        self.nom = nom
        self.role = role
        self.sigle_service = sigle_service
        self.service_id = service_id
        self.role_id = role_id
        self.state = state
        self.email = email
        self.nom_abrege = nom_abrege
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.password = password

    #     if password:
    #         self.set_password(password)

    # def set_password(self, password):
    #     self.password_hash = generate_password_hash(password)

    # def check_password(self, password):
    #     return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)


    @staticmethod
    def get(id):
        return Corbeille(id)



class UserServiceHistory(db.Model):
    __tablename__ = 'user_service_history'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    old_service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    new_service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    transition_date = db.Column(db.DateTime, nullable=False)

    user = db.relationship("User", backref="service_history")
    old_service = db.relationship("Service", foreign_keys=[old_service_id])
    new_service = db.relationship("Service", foreign_keys=[new_service_id])
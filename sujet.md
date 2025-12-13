# TP3 : Ansible et Passerelle

## Contexte

Une petite société commence à grossir et le gérant voudrait simplifier la gestion des utilisateurs qui consiste pour le moment à cliquer des dizaines de fois dans chaques logiciels internes afin d’ajouter ses employés. Il demande à une connaissance personnelle (le gérant a su garder le sens des économies).
Vous devez déployer et remplir un serveur LDAP, puis mettre en place une passerelle HTTP permettant d’authentifier les employés. Afin de reproduire facilement le déploiement, vous devrez utiliser Ansible et téléverser votre travail sur un projet git.


# Création d’un projet git

Rendez-vous sur https://git.unistra.fr afin de créer votre projet, vous pouvez utiliser cette arborescence : 

```
.
├── inventory.yaml
├── playbook_tp1.yaml
├── requirements.txt
└── roles
    ├── openldap
    ├── traefik
    └── whoami

4 directories, 5 files
```

Vous devrez ensuite installer ansible et quelques dépendances python (vous pouvez utiliser la commande `pip install -r requirements.txt`).
Ce TP se fera sur votre poste, vous pouvez donc créer un groupe `test` et y ajouter votre poste.
Vous pouvez enfin créer un playbook `playbook_tp1.yaml` qui déploira votre pile.

Vous répondrez aux questions dans un fichier nommé `questions.md`

## Création d’un serveur LDAP

Créer un rôle Ansible `openldap`, à l'aide d'une image de conteneur existante (https://hub.docker.com/r/bitnamilegacy/openldap) et du role ansible docker-compose(https://docs.ansible.com/projects/ansible/latest/collections/community/docker/docker_compose_v2_module.html).
Vous devrez également utilise le moteur de template d'Ansible et définir/utiliser les variables suivantes:

```
openldap_home: "define me"
openldap_admin_username: "admin"
openldap_admin_password: "define me"
openldap_root: "dc=ansible,dc=fr"
```

Vous pouvez vérifier l'état de l'instance avec la commande `ldapvi -h ldap://localhost:1389 -D 'cn=admin,dc=ansible,dc=fr' -b 'dc=ansible,dc=fr'`

Attention, l'instance doit être persistente, la femme de ménage débranche régulièrement le serveur. 

Pourquoi est-il pertinent d'attacher des conteneurs à plusieurs réseaux ?

Pourquoi certains ports ne sont pas ouvrable depuis votre utilisateur ?

# Import des utilisateurs

Pous pouvez 
À partir du fichier "usr.csv", créer un fichier LDIF (LDAP Directory Interchange Format) puis l'importer dans l'annuaire du serveur dans la branche "ou=People,..."

Chaque utilisateur sera dans un groupe "primaire" dédié. 
Ce groupe devra aussi être créé dans l'annuaire (branche "ou=Group,"...) et il portera comme nom le login de l'utilisateur.
Pour les uid/gid unix, générer des numéros uniques pour chaque utilisateur, dans l’ordre du fichier,, en commençant à 1000

Suggestions :
    • utiliser un language de votre choix en vous aidant de modules (càd. "ne pas réinventer la roue")
    • commande d'import : 
      ldapadd -H ldap://nom_ou_adresse_du_serveur -D dn_de_l'admin -x -w mot_de_passe_de_l'admin -f fichier.ldif

Exemple:

dn: cn=jdoe,ou=Group,...
cn: jdoe
objectclass: posixGroup
objectclass: top
gidnumber: 1000

dn: uid=jdoe,ou=People,...
objectclass: top
objectclass: inetOrgPerson
objectclass: person
objectclass: organizationalPerson
objectclass: posixAccount
objectclass: shadowAccount
cn: John Doe
sn: Doe
uid: jdoe
givenName: John
userpassword: {SSHA}H/YPhEO5YT/REoiFFsoCCT6q34c+fBJp
loginshell: /bin/bash
gidnumber: 1000
uidnumber: 1000
homeDirectory: /home/jdoe

Vous pouvez utiliser ce module python: https://www.python-ldap.org/en/latest/reference/ldif.html

# Creation d'une passerelle HTTP

Le gérant a lu que [Traefik](https://traefik.io/traefik/) est la solution à ses problèmes, vous devez donc créer un role Ansible **traefik** qui permetra à l'aide du module ansible `community.docker.docker_compose`.

Vous pouvez utiliser le port **8000** comme port d'entrée HTTP et le port **8080** comme port de gestion (port qui est très utilise pour voir la configuration de Traefik).

# Creation d'un application WEB

Le gérant voudrait déployer un service pour tester le bon fonctionnement de Traefik, vous devez déployer le conteneur `traefik/whoami` sur le domaine `whoami.localhost`.


Sur quel couches du modèle OSI peut agir Traefik ?

Qu'est qu'une ingress (vous pouvez faire le lien avec une ingress Kubernetes), un middleware et un plugin Traefik ?

Quelles expressions d'ingress permettent de capter:
* mondomaine.com/api/* et mondomaine2.fr/api/*
* tondomaine.com/api/* 
?

Quel peut être l'interet d'utiliser une passerelle HTTP/HTTPS ?

## Utilisation des groupes

Déclarez votre poste dans 3 groupes d'hotes ansible puis modifiez votre `playbook` afin de de jouer le role whoami sur les 3 groupes.

Vous pouvez utiliser le groupe `all` pour définir des variables par défaut (plus d'informations sur https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html#variable-precedence-where-should-i-put-a-variable)

Vous devez maintenant déployer 3 conteneurs:
* un conteneur whoami sur le domaine `whoami.localhost`
* un conteneur Apache sur le domaine `mon-site.localhost` et sur le chemin /front/*
* un conteneur Nginx sur le domaine `mon-site.localhost` et sur le chemin /api/* 

Vous devez utiliser un `middleware` afin de supprimer le prefix du front et de l'API.

# Sécurisation du site de test

Vous allez maintenant devoir en place de l'authentification basique (https://www.rfc-editor.org/rfc/rfc7617.html).

A l'aide de ce plugin Traefik (https://plugins.traefik.io/plugins/628c9eb7ffc0cd18356a979c/ldap-auth), n'autoriser que les employés à accéder à l'ingress `whoami.localhost`.

Quel élément peut utiliser une application WEB derrière cette passerelle pour déterminer quel employé à envoyer la requête HTTP ?

Comment ajouterez-vous le fameux cadenas vert à ce domaine (Vous pouvez expliquer plusieurs solutions) ?

Combien de réseaux docker utilisez-vous et pourquoi ?

Le projet git sera évalué, envoyez le lien de votre projet par email.

# Plugin Traefik

Dans de nombreux cas, il est pertinent de développer quelques lignes afin de résoudre un problème spécifique.

Afin de simuler le comportement d'une solution très complexe, créez un plugin Traefik qui redirigera les requetes non authentifiées vers une page d'authentification.
On utilisera la présence du cookie 'authtoken' à cet effet.

Exemple:

GET http://monApp.localhost/monApp-front/* **sans** le cookie `authtoken` de défini --> code HTTP 302 vers http://monApp.localhost/monApp-api/Login*
GET http://monApp.localhost/monApp-front/* **avec** le cookie `authtoken` de défini --> code HTTP 200

Vous devrez créer un projet git supplémentaire.


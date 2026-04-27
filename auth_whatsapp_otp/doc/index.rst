WhatsApp OTP Authentication
===========================

Présentation
------------

Ce module ajoute une option de connexion via OTP (mot de passe à usage unique) envoyé sur WhatsApp.
Il s'intègre au formulaire de connexion de l'interface web d'Odoo et utilise l'API UltraMsg pour l'envoi du code.

Fonctionnalités
---------------

- Bouton "Login by WhatsApp" sur la page de connexion.
- Saisie du numéro WhatsApp et envoi d'un code OTP.
- Validation du code OTP côté client et redirection vers l'interface Odoo.
- Page de vérification 2FA si nécessaire.

Installation
------------

1. Copier le module `auth_whatsapp_otp` dans le répertoire des modules Odoo.
2. Mettre à jour la liste des modules dans Odoo.
3. Installer le module depuis l'interface d'administration.

Configuration
-------------

- Assurez-vous que le module `web` est installé.
- Configurez les paramètres UltraMsg dans le menu de configuration si cette option est disponible.
- Vérifiez que le serveur peut accéder à l'API UltraMsg pour envoyer des messages WhatsApp.

Utilisation
-----------

- Accédez à la page de connexion Odoo.
- Cliquez sur le bouton "Login by WhatsApp".
- Entrez votre numéro WhatsApp au format international (`+212...`).
- Recevez le code sur WhatsApp et saisissez-le pour vous connecter.

Notes
-----

- Le code OTP expire après 2 minutes.
- En cas d'échec, un message d'erreur s'affiche sur le formulaire.

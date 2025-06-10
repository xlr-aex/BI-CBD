# 🌿 BI Pro CBD Shops – Outil d'Analyse des Flux RSS

---

## 🚀 Vue d'ensemble

"BI Pro CBD Shops" est une application Streamlit puissante conçue pour analyser les flux RSS de boutiques en ligne spécialisées dans le CBD. Cet outil permet aux professionnels de la Business Intelligence, aux analystes de marché ou aux propriétaires de boutiques de surveiller et d'analyser les tendances des produits, les nouveautés, les catégories populaires et les taux de cannabinoïdes (CBD, THC, etc.) à travers différentes plateformes.

Grâce à une interface intuitive, vous pouvez importer des listes de flux RSS (format OPML), filtrer les données par période, par boutique ou par catégorie, et visualiser des rapports dynamiques pour obtenir des insights précieux sur le marché du CBD.

## ✨ Fonctionnalités

* **Import OPML** : Chargez facilement vos listes de flux RSS via un fichier OPML.
* **Analyse de Flux** : Récupération et parsing automatique des données de produits depuis les flux RSS.
* **Extraction de Cannabinoïdes** : Détection et extraction des taux de CBD, THC, CBG, CBN, THCV directement depuis les noms de produits.
* **Catégorisation Intelligente** : Classement automatique des produits en catégories prédéfinies (Huiles, Fleurs, Vapes, Comestibles, Cosmétiques, etc.).
* **Filtrage Avancé** : Filtrez les données par date, boutique et catégorie pour des analyses ciblées.
* **Tableaux de bord Interactifs** :
    * **Vue générale** : Statistiques clés, top boutiques, répartition par catégorie, évolution temporelle et carte des boutiques par pays.
    * **Comparaison** : Comparez l'activité de différentes boutiques ou l'évolution des catégories sur la période sélectionnée.
    * **Analyse par Boutique** : Plongez dans les détails d'une boutique spécifique (nombre d'articles, taux moyens, répartition par catégorie).
    * **Explorateur de Données** : Visualisez et téléchargez toutes les données brutes analysées.
* **Export Excel** : Téléchargez vos données filtrées au format `.xlsx` pour des analyses plus approfondies.

## 🛠️ Installation

Pour faire fonctionner cette application en local, suivez ces étapes :

1.  **Clonez le dépôt (ou téléchargez les fichiers) :**
    Si vous utilisez Git :
    ```bash
    git clone <URL_DU_DÉPÔT> # Remplacez <URL_DU_DÉPÔT> par l'URL de votre dépôt Git
    cd bi-pro-cbd-shops # Ou le nom de votre dossier de projet
    ```

2.  **Créez un environnement virtuel (recommandé) :**
    ```bash
    python -m venv venv
    # Sur Windows :
    venv\Scripts\activate
    # Sur macOS/Linux :
    source venv/bin/activate
    ```

3.  **Installez les dépendances :**
    Assurez-vous d'avoir le fichier `requirements.txt` dans le même dossier que votre script principal.
    ```bash
    pip install -r requirements.txt
    ```
    *(Note : L'application nécessite soit `openpyxl` soit `xlsxwriter` pour l'export Excel. Le `requirements.txt` inclut les deux, mais Python installera ceux qui lui sont nécessaires.)*

## 🚀 Utilisation

1.  **Lancez l'application Streamlit :**
    Depuis le répertoire de votre projet, exécutez :
    ```bash
    streamlit run votre_script_principal.py # Remplacez 'votre_script_principal.py' par le nom de votre fichier Python
    ```
    Votre navigateur web devrait s'ouvrir automatiquement à l'adresse de l'application (généralement `http://localhost:8501`).

2.  **Importez votre fichier OPML :**
    Dans la barre latérale gauche de l'application, utilisez le bouton "1️⃣ OPML des flux RSS" pour téléverser votre fichier OPML contenant les URL des flux RSS à analyser.

3.  **Configurez la période et la granularité :**
    Utilisez les sélecteurs de date et le bouton de granularité ("Jour", "Semaine", "Mois") pour définir la période d'analyse et l'agrégation des données.

4.  **Lancez l'analyse :**
    Cliquez sur le bouton "🚀 Analyser les flux" pour récupérer et traiter les données des flux.

5.  **Explorez les données :**
    Utilisez les onglets principaux ("Vue générale", "Comparaison", "Analyse par Boutique", "Explorateur de Données") et les filtres avancés dans la barre latérale pour naviguer et analyser les informations.

6.  **Exportez vos données (si besoin) :**
    Dans l'onglet "Explorateur de Données", un bouton "📥 Télécharger Excel" est disponible pour exporter l'ensemble des données filtrées.





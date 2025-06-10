# 🌿 BI Pro CBD Shops – v3.4.1

---

## Description

Ce script, `rss_kilo.py`, est un **outil de Business Intelligence (BI)** conçu spécifiquement pour l'analyse des données provenant des boutiques en ligne de produits CBD. Il offre une gamme d'outils de comparaison et de visualisations interactives pour vous aider à comprendre la **diversité des produits**, les **volumes de publication**, la **distribution des prix** et les **profils de cannabinoïdes** à travers différentes boutiques.

## ✨ Fonctionnalités Clés (Mises à jour v3.4.1)

Cette version introduit des améliorations significatives pour une meilleure fiabilité et expérience utilisateur :

* **Radar Multi-Boutiques Fiable** : Utilisation de `px.line_polar` pour des graphiques radar multi-boutiques précis et pertinents.
* **Calcul Robuste des Taux Moyens** : Assure que la variable `avg_rates` est toujours définie et que le code associé ne s'exécute que si les colonnes de taux (`*_rate`) sont présentes, prévenant ainsi les erreurs.
* **Thème Sombre Cohérent** : Implémentation du modèle `plotly_dark` par défaut pour une lisibilité améliorée sur les arrière-plans sombres, avec des axes toujours clairs.
* **Correction des Erreurs `NameError`** : Toutes les occurrences résiduelles d'erreurs `NameError` ont été identifiées et corrigées pour une stabilité accrue.

---

## 🛠️ Configuration

### Prérequis

Avant de lancer l'application, assurez-vous d'avoir :

* **Python 3** installé sur votre système.
* Tous les **packages Python requis** listés dans le fichier `requirements.txt`.

### Installation

Suivez ces étapes pour installer et préparer l'environnement :

1.  **Clonez ce dépôt**
2.  **Installez les packages Python nécessaires** en utilisant `pip` :

    ```bash
    pip install -r requirements.txt
    ```

---

## 🚀 Utilisation

Ce script est conçu pour être exécuté en tant qu'**application Streamlit**.

Pour démarrer l'application :

```bash
streamlit run rss_kilo.py
```

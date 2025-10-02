# GPT Genius

Un framework d'IA avancé pour la génération et l'amélioration de code automatisées, basé sur des modèles de langage de grande taille.

## Fonctionnalités

- 🚀 **Génération de code automatique** : Créez des applications complètes à partir de descriptions en langage naturel
- 🔧 **Amélioration de code intelligente** : Modifiez et améliorez du code existant avec l'IA
- 📊 **Système de benchmarking** : Évaluez les performances sur des tâches de programmation
- 🎯 **Interface CLI intuitive** : Ligne de commande simple et puissante
- 🧠 **Support multi-modèles** : OpenAI GPT-4, Claude, et plus
- 🔄 **Gestion de versions** : Suivi des modifications et snapshots
- 🛠️ **Auto-réparation** : Détection et correction automatique des erreurs

## Installation

```bash
pip install gpt-genius
```

Ou depuis les sources :

```bash
git clone https://github.com/AI-Advenced/GPT_Genius/
cd gpt-genius
pip install -e .
```

## Usage rapide

### Génération d'une nouvelle application

```bash
gpt-genius init "Créer une API REST pour la gestion des tâches avec FastAPI et SQLite"
```

### Amélioration de code existant

```bash
gpt-genius improve "Ajouter la validation des données et la gestion d'erreurs"
```

### Configuration des clés API

```bash
export OPENAI_API_KEY="votre_clé_openai"
export ANTHROPIC_API_KEY="votre_clé_anthropic"  # optionnel
```

## Structure du projet

```
gpt_genius/
├── core/                    # Modules principaux
│   ├── ai.py               # Interface IA
│   ├── files_dict.py       # Gestion des fichiers
│   ├── prompt.py           # Système de prompts
│   └── default/            # Implémentations par défaut
├── applications/
│   └── cli/                # Interface en ligne de commande
├── benchmark/              # Système de benchmarking
├── tools/                  # Outils et utilitaires
└── preprompts/            # Templates de prompts
```

## Configuration

Créez un fichier `.env` ou `gpt-genius.toml` :

```toml
[model]
name = "gpt-4"
temperature = 0.1

[paths]
workspace = "./workspace"
```

## Exemples avancés

### Mode clarification

```bash
gpt-genius --clarify "Application de chat en temps réel"
```

### Mode lite (génération rapide)

```bash
gpt-genius --lite "Script de backup automatique"
```

### Auto-réparation

```bash
gpt-genius --self-heal "API avec tests unitaires"
```

## Benchmarks

Évaluez les performances :

```bash
gpt-genius benchmark --suite mbpp
```

## Contribution

Les contributions sont les bienvenues ! Consultez [CONTRIBUTING.md](CONTRIBUTING.md) pour plus d'informations.

## Licence

MIT License - voir [LICENSE](LICENSE) pour plus de détails.

## Support

- 📖 [Documentation complète](https://docs.gpt-genius.com)
- 💬 [Discussions GitHub](https://github.com/gpt-genius/AI-Advenced/GPT_Genius/discussions)
- 🐛 [Signaler un bug](https://github.com/AI-Advenced/GPT_Genius/issues)

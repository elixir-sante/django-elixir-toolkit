#!/bin/bash
# Usage : ./release.sh tag=x.x.x
# Crée un tag annoté vx.x.x et le pousse sur origin.
# Le workflow GitHub Actions publish-release se déclenche sur les tags v*.

set -euo pipefail

# Parse l'argument tag=x.x.x
TAG_VERSION=""
for arg in "$@"; do
    case "$arg" in
        tag=*) TAG_VERSION="${arg#tag=}" ;;
        *) echo "Argument inconnu : $arg"; exit 1 ;;
    esac
done

if [ -z "$TAG_VERSION" ]; then
    echo "Usage : ./release.sh tag=x.x.x"
    exit 1
fi

# Supprime un éventuel préfixe v
TAG_VERSION="${TAG_VERSION#v}"

# Valide le format x.x.x (semver)
if ! echo "$TAG_VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
    echo "Version invalide : $TAG_VERSION (format attendu x.x.x, ex. 0.31.0)"
    exit 1
fi

TAG="v$TAG_VERSION"

# Refuse si le tag existe déjà localement ou sur origin
if git rev-parse -q --verify "refs/tags/$TAG" >/dev/null; then
    echo "Le tag $TAG existe déjà localement."
    exit 1
fi
if git ls-remote --exit-code --tags origin "refs/tags/$TAG" >/dev/null 2>&1; then
    echo "Le tag $TAG existe déjà sur origin."
    exit 1
fi

# Refuse si l'arbre de travail n'est pas propre
if [ -n "$(git status --porcelain)" ]; then
    echo "Arbre de travail non propre, committez ou stash avant de taguer."
    exit 1
fi

# Refuse si on n'est pas à jour avec origin/main
git fetch origin main
if [ "$(git rev-parse HEAD)" != "$(git rev-parse origin/main)" ]; then
    echo "HEAD n'est pas synchronisé avec origin/main."
    exit 1
fi

echo "Création du tag $TAG sur $(git rev-parse --short HEAD)"
git tag -a "$TAG" -m "Release $TAG"

echo "Envoi du tag $TAG sur origin"
git push origin "$TAG"

echo "Release $TAG publiée. Suivi : https://github.com/elixir-sante/django-elixir-toolkit/actions"

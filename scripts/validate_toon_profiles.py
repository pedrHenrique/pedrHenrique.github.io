"""Valida versão e conteúdo dos perfis JSON e TOON."""

import json
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

try:
    from toon_format import decode
except ImportError:
    print(
        "Erro: toon-python não está instalado. Execute primeiro "
        "scripts/convert_profiles_to_toon.py.",
        file=sys.stderr,
    )
    raise SystemExit(1)


ROOT_FOLDER = Path(__file__).resolve().parent.parent
PROFILE_NAMES = ("profile-en", "profile-pt-BR")


def read_json(path: Path):
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def read_toon(path: Path):
    return decode(path.read_text(encoding="utf-8"))


def version_of(data, path: Path):
    try:
        return data["meta"]["version"]
    except (KeyError, TypeError):
        raise ValueError(f"{path.name}: campo meta.version ausente") from None


def first_key_difference(expected, actual, path="$"):
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return f"{path}: estrutura diferente (objeto esperado)"

        missing = expected.keys() - actual.keys()
        extra = actual.keys() - expected.keys()
        if missing or extra:
            details = []
            if missing:
                details.append(f"ausentes no TOON: {sorted(missing)}")
            if extra:
                details.append(f"extras no TOON: {sorted(extra)}")
            return f"{path}: chaves diferentes ({'; '.join(details)})"

        for key in expected:
            difference = first_key_difference(expected[key], actual[key], f"{path}.{key}")
            if difference:
                return difference

    elif isinstance(expected, list):
        if not isinstance(actual, list):
            return f"{path}: estrutura diferente (lista esperada)"
        if len(expected) != len(actual):
            return f"{path}: tamanho da lista diferente (JSON {len(expected)}, TOON {len(actual)})"
        for index, (left, right) in enumerate(zip(expected, actual)):
            difference = first_key_difference(left, right, f"{path}[{index}]")
            if difference:
                return difference

    elif isinstance(actual, (dict, list)):
        return f"{path}: estrutura diferente (valor escalar esperado)"

    return None


def values_match(expected, actual):
    if expected == actual:
        return True

    # toon-python decodes an unquoted +N string as the number N.
    if isinstance(expected, str) and expected.startswith("+") and isinstance(actual, (int, float)):
        try:
            return Decimal(expected) == Decimal(str(actual))
        except InvalidOperation:
            pass

    return False


def first_value_difference(expected, actual, path="$"):
    if isinstance(expected, dict):
        for key in expected:
            difference = first_value_difference(expected[key], actual[key], f"{path}.{key}")
            if difference:
                return difference
    elif isinstance(expected, list):
        for index, (left, right) in enumerate(zip(expected, actual)):
            difference = first_value_difference(left, right, f"{path}[{index}]")
            if difference:
                return difference
    elif not values_match(expected, actual):
        return f"{path}: valores diferentes (JSON {expected!r}, TOON {actual!r})"

    return None


def main() -> None:
    profiles = {}
    versions = {}

    for name in PROFILE_NAMES:
        json_path = ROOT_FOLDER / "public" / f"{name}.json"
        toon_path = ROOT_FOLDER / "public" / f"{name}.toon"
        profiles[name] = (read_json(json_path), read_toon(toon_path))
        versions[json_path.name] = version_of(profiles[name][0], json_path)
        versions[toon_path.name] = version_of(profiles[name][1], toon_path)

    if len(set(versions.values())) != 1:
        details = ", ".join(f"{name}={version}" for name, version in versions.items())
        raise ValueError(f"Versões diferentes: {details}")

    for name, (json_data, toon_data) in profiles.items():
        difference = first_key_difference(json_data, toon_data)
        if difference:
            raise ValueError(f"{name}: {difference}")

    for name, (json_data, toon_data) in profiles.items():
        difference = first_value_difference(json_data, toon_data)
        if difference:
            raise ValueError(f"{name}: {difference}")

    version = next(iter(versions.values()))
    print(f"Perfis JSON e TOON coerentes (versão {version}).")


if __name__ == "__main__":
    try:
        main()
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"Erro de validação: {error}", file=sys.stderr)
        raise SystemExit(1) from error

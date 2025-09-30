"""Example test file.

Ce fichier montre comment écrire des tests avec pytest.
"""


def test_example_always_passes() -> None:
    """Test d'exemple qui passe toujours."""
    assert 1 + 1 == 2


def test_example_with_fixture(tmp_path):
    """Test d'exemple utilisant une fixture pytest."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello World")

    assert test_file.read_text() == "Hello World"


# TODO: Écrire des tests pour DataLoader
# TODO: Écrire des tests pour DataAnalyzer
# TODO: Utiliser des fixtures pour créer des données de test
# TODO: Tester les cas d'erreur (avec pytest.raises)


class TestDataLoader:
    """Tests pour la classe DataLoader."""

    pass


class TestDataAnalyzer:
    """Tests pour la classe DataAnalyzer."""

    pass

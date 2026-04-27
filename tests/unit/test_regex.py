# tests/test_atom_00.py
import pytest

def test_import_models():
    """Vérifie que les modèles de données sont importables sans erreur."""
    try:
        from ace.models.chat import Role, ContentType, MessagePart, Turn, ChatSession
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")

def test_role_enum():
    from ace.models.chat import Role
    assert Role.USER.value == "user"
    assert Role.MODEL.value == "model"
    assert Role.SYSTEM.value == "system"

def test_create_turn():
    from ace.models.chat import Turn, Role
    turn = Turn(index=0, role=Role.USER, content=[], confidence=0.9)
    assert turn.index == 0
    assert turn.role == Role.USER

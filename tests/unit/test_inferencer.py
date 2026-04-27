# tests/test_atom_03.py
from bs4 import BeautifulSoup
from ace.engine.inferencer import RoleInferrer
from ace.models.chat import Role

def test_infer_user_role():
    html = '<div class="user-message">Bonjour, comment ça va ?</div>'
    soup = BeautifulSoup(html, 'html.parser')
    tag = soup.find('div')
    inferrer = RoleInferrer()
    role, conf = inferrer.infer(tag, context=[])
    assert role == Role.USER
    assert conf > 0.5

def test_infer_model_role_with_code():
    html = '<div class="assistant"><pre><code>print("hello")</code></pre></div>'
    soup = BeautifulSoup(html, 'html.parser')
    tag = soup.find('div')
    inferrer = RoleInferrer()
    role, _ = inferrer.infer(tag, context=[])
    # La présence de code favorise fortement MODEL
    assert role == Role.MODEL

def test_alternance_fallback():
    """Si aucun signal fort, doit alterner par rapport au tour précédent."""
    inferrer = RoleInferrer()
    context = [type('Turn', (), {'role': Role.USER})()]
    html = '<div>Réponse neutre</div>'
    tag = BeautifulSoup(html, 'html.parser').find('div')
    role, _ = inferrer.infer(tag, context)
    assert role == Role.MODEL

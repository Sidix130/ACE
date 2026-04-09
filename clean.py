"""
clean.py v3 — Architecture universelle, zéro préset

Dépendances : beautifulsoup4 (déjà installé)

Logique :
1. Nettoyage du DOM (bruit UI)
2. Détection des blocs répétés (scoring par fréquence + densité)
3. Inférence des rôles par vote multi-signal
4. Conversion HTML → Markdown (stdlib Python)
5. Validation et écriture du fichier de sortie

Usage : python clean.py <input.html> [output.md]
"""

import sys
import re
from collections import Counter
from bs4 import BeautifulSoup, NavigableString, Tag


# ─────────────────────────────────────────────
# COUCHE 1 : NETTOYAGE
# ─────────────────────────────────────────────

UI_TAGS = ['script', 'style', 'meta', 'link', 'noscript', 'iframe',
           'template', 'svg', 'header', 'footer', 'nav',
           # Balises Angular AI Studio portant uniquement des labels d'UI
           'ms-chunk-tab', 'ms-turn-chunk-header', 'ms-footer-info',
           'ms-thought-chunk-header', 'ms-turn-header']

UI_CLASS_PATTERNS = re.compile(
    r'tooltip|popover|modal|menu|nav|sidebar|toolbar|'
    r'notification|banner|cookie|overlay|badge|avatar|'
    r'copy-btn|action|button|share|like|rating',
    re.IGNORECASE
)


# Patterns de labels UI connus à supprimer du DOM
UI_TEXT_LABELS = re.compile(
    r'^(model|user|thoughts?|thinking\.?|réflexion(\s+durant\s+[\d,]+\s*s)?|'
    r'vous\s+avez\s+dit\s*:?|chatgpt\s+a\s+dit\s*:?|gemini\s+a\s+dit\s*:?|'
    r'claude\s+a\s+dit\s*:?|assistant\s*:?|expand\s+to\s+view.*|'
    r'chevron_right|[\d,]+\s*s)$',
    re.IGNORECASE
)

def strip_ui_noise(soup):
    """Supprime les éléments d'interface irrelevants."""
    for tag in soup(UI_TAGS):
        tag.decompose()

    for elem in list(soup.find_all(True)):
        if not hasattr(elem, 'attrs') or elem.attrs is None:
            continue
        classes = ' '.join(elem.get('class', []))
        if UI_CLASS_PATTERNS.search(classes):
            text = elem.get_text(strip=True)
            if len(text) < 40:
                elem.decompose()
                continue

        # Supprimer les nœuds dont le texte est uniquement un label UI
        text = elem.get_text(strip=True)
        if text and len(text) < 80 and UI_TEXT_LABELS.match(text):
            elem.decompose()


# ─────────────────────────────────────────────
# COUCHE 2 : DÉTECTION DES BLOCS RÉPÉTÉS
# ─────────────────────────────────────────────

def text_density(tag):
    """Nombre de mots dans un tag (indicateur de contenu)."""
    return len(tag.get_text(strip=True).split())


def has_role_signal(tag):
    """True si le tag ou ses descendants portent un signal de rôle."""
    attrs_text = ' '.join(
        str(v) for k, v in tag.attrs.items()
        if isinstance(v, (str, list))
    )
    combined = attrs_text + ' ' + tag.get_text()[:200]
    return bool(re.search(
        r'user|human|assistant|model|ai[-_]?message|turn|prompt|response|vous',
        combined, re.IGNORECASE
    ))


def depth_in_tree(tag):
    """Profondeur du tag dans l'arbre DOM."""
    return sum(1 for _ in tag.parents)


def detect_turn_blocks(soup):
    """
    Trouve les tours de parole en cherchant le parent
    qui contient LE PLUS de fils directs avec du contenu dense.
    Pénalise les parents trop superficiels (body, html, div#root)
    pour favoriser les conteneurs spécifiques de tours.
    """
    best_score = 0
    best_children = []

    # Profondeur maximale du DOM pour normaliser
    all_tags = soup.find_all(True)
    max_depth = max((depth_in_tree(t) for t in all_tags), default=1)

    for parent in all_tags:
        if not hasattr(parent, 'attrs') or parent.attrs is None:
            continue

        children = [c for c in parent.children if isinstance(c, Tag)]
        if len(children) < 2:
            continue

        dense_children = [c for c in children if text_density(c) > 10]
        n_dense = len(dense_children)
        if n_dense < 2:
            continue

        # Bonus de diversité des tags ou pénalité de contenu textuel (généralement les tours sont des div/section)
        # Si trop de paragraphes/p/h1/ul, c'est un bloc de texte, pas un conteneur de tours
        text_tags = sum(1 for c in dense_children if c.name in ['p', 'h1', 'h2', 'h3', 'h4', 'ul', 'ol', 'pre'])
        if text_tags > len(dense_children) * 0.4:
            continue  # Rejeter les conteneurs de paragraphes

        # Score basé sur la classe dominante
        classes_str = [' '.join(c.get('class', [])) for c in dense_children if c.get('class')]
        class_counts = {c: classes_str.count(c) for c in set(classes_str)}
        
        common_class_score = max(class_counts.values()) if class_counts else 1
        
        # Bonus rôle
        role_bonus = 2 if any(has_role_signal(c) for c in dense_children[:5]) else 1

        # Bonus profondeur : favoriser les nœuds à mi-arbre (ni trop haut, ni trop bas)
        depth = depth_in_tree(parent)
        depth_ratio = depth / max_depth  # 0 = racine, 1 = feuille
        # Pic à 0.3–0.6 de profondeur relative
        depth_bonus = 1 + 2 * max(0, 1 - abs(depth_ratio - 0.4) / 0.4)

        score = n_dense * common_class_score * role_bonus * depth_bonus

        if score > best_score:
            best_score = score
            best_children = dense_children

    if not best_children:
        return [t for t in all_tags if has_role_signal(t)]

    return best_children



# ─────────────────────────────────────────────
# COUCHE 3 : INFÉRENCE DES RÔLES PAR VOTE
# ─────────────────────────────────────────────

ROLE_SIGNALS = {
    'user':  re.compile(r'\buser\b|human|visitor|vous|question|prompt', re.IGNORECASE),
    'model': re.compile(r'\bassistant\b|\bmodel\b|\bai\b|bot|response|answer|reply|gemini|gpt|claude|mistral|llm', re.IGNORECASE),
}


def infer_role(tag, index, total):
    """
    Vote multi-signal pour déterminer le rôle d'un bloc.
    Retourne ('User' | 'Model', confiance 0-1).
    """
    votes = {'user': 0, 'model': 0}

    # Signal 1 : attributs data-* et class
    attrs_text = ' '.join(
        str(v) for v in tag.attrs.values() if isinstance(v, (str, list))
    )
    attrs_flat = attrs_text if isinstance(attrs_text, str) else ' '.join(attrs_text)

    for role, pattern in ROLE_SIGNALS.items():
        if pattern.search(attrs_flat):
            votes[role] += 3  # signal fort

    # Signal 2 : texte des enfants (labels, aria-label, titres courts)
    for child in tag.find_all(True, limit=10):
        child_text = child.get_text(strip=True)
        if 0 < len(child_text) < 30:  # courts = probablement labels
            for role, pattern in ROLE_SIGNALS.items():
                if pattern.search(child_text):
                    votes[role] += 2

    # Signal 3 : longueur du texte
    # Les réponses modèles sont généralement plus longues
    text_len = len(tag.get_text(strip=True))
    if text_len > 300:
        votes['model'] += 1
    elif text_len < 150:
        votes['user'] += 1

    # Signal 4 : position dans l'alternance (pairs = user, impairs = model)
    # Uniquement si aucun autre signal n'est dominant
    if votes['user'] == votes['model']:
        if index % 2 == 0:
            votes['user'] += 1
        else:
            votes['model'] += 1

    total_votes = votes['user'] + votes['model']
    if votes['user'] > votes['model']:
        return 'User', votes['user'] / total_votes
    else:
        return 'Model', votes['model'] / total_votes


# ─────────────────────────────────────────────
# COUCHE 4 : CONVERSION HTML → MARKDOWN
# ─────────────────────────────────────────────

def extract_code_blocks(tag):
    """Remplace les <pre> et div.mermaid par des placeholders avant la conversion."""
    code_map = {}
    
    # 1. Blocs de code standards (<pre>)
    for i, pre in enumerate(tag.find_all('pre')):
        lang = ''
        # Cherche le langage dans les classes ou l'en-tête
        for elem in pre.find_all(class_=True):
            for cls in elem.get('class', []):
                m = re.match(r'language-(\w+)', cls)
                if m:
                    lang = m.group(1)
                    break
        
        # Cas spécial Mermaid dans pre
        if 'mermaid' in ' '.join(pre.get('class', [])):
            lang = 'mermaid'
            
        code_text = pre.get_text('\n')
        placeholder = f'__CODE_{i}__'
        code_map[placeholder] = f'```{lang}\n{code_text.strip()}\n```'
        pre.replace_with(placeholder)

    # 2. Blocs Mermaid dans des divs (fréquent chez Grok/DeepSeek)
    for i, div in enumerate(tag.find_all('div', class_=re.compile(r'mermaid|code-block', re.I))):
        text = div.get_text().strip()
        if re.match(r'^(graph|flowchart|sequenceDiagram|classDiagram|stateDiagram|erDiagram|gantt|pie|gitGraph|journey|C4Context|mindmap|timeline)', text, re.I):
            placeholder = f'__MERM_{i}__'
            # Nettoyer d'éventuels prefix/suffix techniques
            clean_text = re.sub(r'^.*?({.*?}}%%|%%{.*?}}%%)', '', text, flags=re.S).strip()
            code_map[placeholder] = f'```mermaid\n{clean_text}\n```'
            div.replace_with(placeholder)

    return code_map


def tag_to_md(tag):
    """Convertit récursivement un tag BeautifulSoup en Markdown."""
    name = tag.name if tag.name else ''
    classes = tag.get('class', []) if tag.get('class') else []

    # Gestion spéciale KaTeX / MathJax (éviter les doublons MathML/HTML)
    if 'katex' in classes or name == 'math':
        ann = tag.find('annotation', encoding='application/x-tex')
        if ann:
            latex = ann.get_text().strip()
            # Vérifier si c'est un bloc ou inline (displayMode)
            is_block = 'katex-display' in classes or tag.find_parent(class_='katex-display') is not None
            if is_block:
                return f'\n\n$${latex}$$\n\n'
            return f'${latex}$'
        # Si on est dans un span katex mais sans annotation directe,
        # on continue mais on risque des doublons si on ne fait pas attention.
        # Souvent, l'annotation est plus bas. On laisse la récursion descendre
        # SAUF si on a déjà trouvé l'annotation.

    # Titres
    heading_map = {'h1': '# ', 'h2': '## ', 'h3': '### ',
                   'h4': '#### ', 'h5': '##### ', 'h6': '###### '}
    if name in heading_map:
        return f'\n{heading_map[name]}{tag.get_text(strip=True)}\n'

    # Gras / italique / code inline
    if name in ('strong', 'b'):
        return f'**{tag.get_text()}**'
    if name in ('em', 'i'):
        return f'*{tag.get_text()}*'
    if name == 'code' and tag.parent.name != 'pre':
        return f'`{tag.get_text()}`'

    # Liens
    if name == 'a':
        href = tag.get('href', '')
        text = tag.get_text(strip=True)
        return f'[{text}]({href})' if href else text

    # Listes
    if name == 'li':
        inner = node_to_md(tag)
        return f'\n- {inner.strip()}'
    if name in ('ul', 'ol'):
        return node_to_md(tag) + '\n'

    # Paragraphes et divs
    if name in ('p', 'div', 'section', 'article'):
        inner = node_to_md(tag)
        return f'\n{inner.strip()}\n'

    if name == 'br':
        return '\n'

    if name == 'hr':
        return '\n---\n'

    if name == 'blockquote':
        inner = node_to_md(tag)
        return '\n' + '\n'.join(f'> {l}' for l in inner.strip().split('\n')) + '\n'

    # Tables
    if name == 'table':
        return convert_table(tag)

    # Défaut : récursion
    return node_to_md(tag)


def node_to_md(tag):
    """Parcourt les enfants d'un nœud et les convertit."""
    parts = []
    for child in tag.children:
        if isinstance(child, NavigableString):
            parts.append(str(child))
        elif isinstance(child, Tag):
            parts.append(tag_to_md(child))
    return ''.join(parts)


def post_process_markdown(text):
    """Nettoyage final du Markdown produit."""
    # 1. Conversion des délimiteurs LaTeX alternatifs
    text = re.sub(r'\\\\\((.*?)\\\\\)', r'$\1$', text)
    text = re.sub(r'\\\[(.*?)\\\]', r'\n\n$$\1$$\n\n', text, flags=re.S)
    text = re.sub(r'\\\(', r'$', text)
    text = re.sub(r'\\\)', r'$', text)
    
    # 2. Détection heuristique de Mermaid non-fenced (pour les exports "bruts")
    # On cherche un mot clé précédé d'un saut de ligne ou début de texte.
    # On capture jusqu'à un bloc de séparation (double retour ou titre).
    mermaid_pattern = re.compile(
        r'(?:^|\n)((?:graph|flowchart|sequenceDiagram|classDiagram|stateDiagram|erDiagram|gantt|pie|gitGraph|journey|C4Context|mindmap|timeline)[\s\xa0].*?)(?=\n\n|\n#|$)',
        re.S | re.I
    )
    def wrap_m(match):
        content = match.group(1).strip()
        if '```' in content or len(content.splitlines()) < 2:
            return match.group(0)
        return f'\n\n```mermaid\n{content}\n```\n'
    
    text = mermaid_pattern.sub(wrap_m, text)

    # 3. Supprimer les lignes vides triples
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # 4. Supprimer les labels UI résiduels en début de ligne
    text = UI_LABELS.sub('', text)
    
    return text.strip()


def convert_table(table):
    """Convertit une table HTML en table Markdown."""
    rows = []
    # Ignorer les tables imbriquées dans des tours (souvent de l'UI)
    if len(table.find_all('table')) > 2:
        return ""
        
    for tr in table.find_all('tr'):
        cells = tr.find_all(['td', 'th'])
        if not cells: continue
        row = '| ' + ' | '.join(node_to_md(c).strip().replace('\n', ' ') for c in cells) + ' |'
        rows.append(row)
    
    if not rows:
        return ''
    
    # Trouver le nombre max de colonnes
    max_cols = max(len(r.split('|')) - 2 for r in rows) if rows else 0
    separator = '| ' + ' | '.join(['---'] * max_cols) + ' |'
    
    return '\n' + rows[0] + '\n' + separator + '\n' + '\n'.join(rows[1:]) + '\n'


# Labels UI à supprimer (insensible à la casse)
UI_LABELS = re.compile(
    r'^(vous avez dit\s*:?|chatgpt a dit\s*:?|gemini a dit\s*:?|claude a dit\s*:?|'
    r'assistant\s*:?|user\s*:?|human\s*:?|ai\s*:?|model\s*:?|'
    r'réflexion durant.*?secondes?\s*\.?|thinking\s*\.*)$',
    re.IGNORECASE | re.MULTILINE
)


def convert_to_markdown(tag):
    """Pipeline complet : extraction code → conversion → nettoyage."""
    import copy
    tag = copy.copy(tag)

    code_map = extract_code_blocks(tag)
    md = node_to_md(tag)

    # Réinjecter les blocs de code
    for placeholder, block in code_map.items():
        md = md.replace(placeholder, f'\n\n{block}\n\n')

    # Post-traitement (LaTeX, Mermaid, UI)
    md = post_process_markdown(md)

    return md


# ─────────────────────────────────────────────
# COUCHE 5 : VALIDATION
# ─────────────────────────────────────────────

MIN_WORDS = 3  # seuil pour rejeter les blocs quasi-vides

def is_valid_turn(text):
    return len(text.split()) >= MIN_WORDS


# ─────────────────────────────────────────────
# POINT D'ENTRÉE
# ─────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python clean.py <input.html> [output.md]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) >= 3 else \
        re.sub(r'\.(html?)(\.md)?$', '', input_file) + '.md'

    print(f"Lecture : {input_file}")
    # Lire tout le fichier d'un coup pour éviter les biais de parsing
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')

    strip_ui_noise(soup)

    blocks = detect_turn_blocks(soup)
    print(f"Blocs détectés : {len(blocks)}")

    turns = []
    for i, block in enumerate(blocks):
        role, confidence = infer_role(block, i, len(blocks))
        md = convert_to_markdown(block)
        if is_valid_turn(md):
            turns.append((role, confidence, md))

    print(f"Tours valides : {len(turns)}")

    with open(output_file, 'w', encoding='utf-8') as out:
        for role, conf, text in turns:
            conf_str = f'<!-- confiance rôle: {conf:.0%} -->' if conf < 0.7 else ''
            out.write(f'## {role}\n{conf_str}\n\n{text}\n\n---\n\n')

    print(f"Résultat : {output_file}")


if __name__ == '__main__':
    main()

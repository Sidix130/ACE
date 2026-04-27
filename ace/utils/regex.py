import re

# Labels UI à supprimer (insensible à la casse)
UI_LABELS_PATTERN = re.compile(
    r'^(vous avez dit\s*:?|chatgpt a dit\s*:?|gemini a dit\s*:?|claude a dit\s*:?|'
    r'assistant\s*:?|user\s*:?|human\s*:?|ai\s*:?|model\s*:?|'
    r'réflexion durant.*?secondes?\s*\.?|thinking\s*\.*)$',
    re.IGNORECASE | re.MULTILINE
)

# Pattern de détection Mermaid
MERMAID_KEYWORDS = [
    'graph', 'flowchart', 'sequenceDiagram', 'classDiagram', 
    'stateDiagram', 'erDiagram', 'gantt', 'pie', 'gitGraph', 
    'journey', 'C4Context', 'mindmap', 'timeline'
]

MERMAID_DETECTION_RE = re.compile(
    r'^\s*(?:}}%%|%%{.*?\}%%)?\s*(' + '|'.join(MERMAID_KEYWORDS) + r')\b',
    re.MULTILINE | re.IGNORECASE
)

# Delimiteurs LaTeX (KaTeX / MathJax)
LATEX_INLINE_RE = re.compile(r'\\\\\((.*?)\\\\\)|\\\((.*?)\\\)')
LATEX_BLOCK_RE = re.compile(r'\\\[(.*?)\\\]', re.DOTALL)

import re
text = "}}%%\ngraph TD\n%% === PENSEUR INTÉGRÉ ===\nsubgraph PENSEUR [\"🧠 Penseur Intégré\"]\nend\n\nNext section"

mermaid_pattern = re.compile(
    r'(?m)^((?:graph\s+(?:TD|LR|BT|RL)|flowchart|sequenceDiagram|classDiagram|stateDiagram|erDiagram|gantt|pie|gitGraph|journey|C4Context|mindmap|timeline).*?)(\n{2,}|(?=\n#)|$)',
    re.S
)

match = mermaid_pattern.search(text)
if match:
    print(f"Match found: {match.group(1)}")
else:
    print("No match found")

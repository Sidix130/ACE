import re
text = """}}%%
graph TD
%% === PENSEUR INTÉGRÉ ===
subgraph PENSEUR ["🧠 Penseur Intégré"]
end"""

mermaid_pattern = re.compile(
    r'(?m)^((?:graph\s+(?:TD|LR|BT|RL)|flowchart|sequenceDiagram|classDiagram|stateDiagram|erDiagram|gantt|pie|gitGraph|journey|C4Context|mindmap|timeline).*?)(\n{2,}|(?=\n#)|$)',
    re.S
)

def wrap_m(match):
    content = match.group(1).strip()
    return f'```mermaid\n{content}\n```\n'

new_text = mermaid_pattern.sub(wrap_m, text)
print(f"Match found: {bool(mermaid_pattern.search(text))}")
print("---")
print(new_text)

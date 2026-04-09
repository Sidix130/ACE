# [Atome 5] Pipeline & CLI

## 1. Objectif
Le "Chef d'Orchestre" qui lie tous les composants.

## 2. Template `ace/main.py`
```python
def process(input_html):
    soup = BeautifulSoup(input_html, 'html.parser')
    
    # 1. Sanctuarisation
    sanctuary = SanctuaryManager()
    sanctuary.extract(soup)
    
    # 2. Détection des tours
    detector = HeuristicDetector()
    blocks = detector.detect(soup)
    
    # 3. Traitement par tour
    for b in blocks:
        role = inferencer.infer(b)
        content = converter.convert(b)
        # Rentre dans la dataclass Session
        
    # 4. Restauration
    final_md = sanctuary.restore(full_markdown)
    return final_md
```

## 3. Livrables
- `ace/main.py`
- `ace/pipeline.py`

## 4. Test
`tests/test_atom_05.py` (E2E).

import json
try:
    import yaml
except ImportError:
    yaml = None

from datetime import datetime
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional

from ace.core.sanctuary import SanctuaryManager
from ace.engine.detector import TopologicalDetector
from ace.engine.heuristic import HeuristicDetector
from ace.engine.validator import ExtractionValidator
from ace.engine.inferencer import RoleInferrer
from ace.engine.converter import MarkdownDispatcher
from ace.models.chat import Role, Turn, ChatSession, MessagePart, ContentType, ExtractionOptions, ExtractionResult

def process_html(html_content: str, options: Optional[ExtractionOptions] = None) -> ExtractionResult:
    """Orchestre le pipeline complet d'extraction et de conversion."""
    if options is None:
        options = ExtractionOptions()
        
    if options.format == 'yaml' and yaml is None:
        raise ImportError("PyYAML est requis pour le format YAML. Installez-le avec 'pip install PyYAML'.")
        
    soup = BeautifulSoup(html_content, 'html.parser')
    debug_data: Dict[str, Any] = {}
    
    # 1. Sanctuaire (Extraction & Protection)
    sanctuary = SanctuaryManager()
    mapping = {}
    if not options.raw:
        mapping = sanctuary.extract(soup)
        if options.debug:
            # Sérialisation sécurisée du mapping pour le diagnostic
            debug_data['sanctuary_map'] = {
                k: v.to_dict() if hasattr(v, 'to_dict') else str(v) 
                for k, v in mapping.items()
            }
    
    # 2. Détermination de la stratégie de détection
    detector_topo = TopologicalDetector()
    detector_heur = HeuristicDetector()
    validator = ExtractionValidator()
    
    blocks = []
    winning_strategy = ""
    
    # Mode Forcé ou Hybride (Auto)
    if options.detector == 'topo':
        blocks = detector_topo.detect(soup)
        winning_strategy = "forced_topo"
    elif options.detector == 'heuristic':
        blocks = detector_heur.detect(soup)
        winning_strategy = "forced_heuristic"
    else:
        # V1.2.0 HYBRID ORCHESTRATION (AUTO)
        # 1. Passe Heuristique (très rapide, très précis)
        heur_blocks = detector_heur.detect(soup)
        if validator.is_valid(heur_blocks, soup):
            blocks = heur_blocks
            winning_strategy = "auto_heuristic"
        else:
            # 2. Passe Topologique (tolérant aux variations de flux, O(N))
            topo_blocks = detector_topo.detect(soup)
            if validator.is_valid(topo_blocks, soup):
                blocks = topo_blocks
                winning_strategy = "auto_topological"
    
    # 3. Fallback Lithos (Sécurité Absolue)
    if not blocks:
        body = soup.find('body')
        if body:
            blocks = [body]
            winning_strategy = "fallback_body"
            if not options.quiet:
                import sys
                print("⚠️  Avertissement : Les moteurs ont échoué ou ont été invalidés. Utilisation du fallback (corps entier).", file=sys.stderr)
    
    if options.debug:
        debug_data['detected_blocks_count'] = len(blocks)
        debug_data['winning_strategy'] = winning_strategy
    
    # 3. Traitement des tours
    inferrer = RoleInferrer()
    # Support de l'option no_table via le dispatcher
    dispatcher = MarkdownDispatcher(process_tables=not options.no_table)
    
    session = ChatSession()
    session.turns = []
    
    for i, block in enumerate(blocks):
        # Inférence du rôle
        role, confidence = inferrer.infer(block, context=session.turns)
        
        # Conversion Markdown (les UUID sont préservés)
        md_content = dispatcher.convert(block)
        
        # CRITIQUE LITHOS : Restauration des UUID pour chaque partie de message
        if not options.raw:
            restored_content = sanctuary.restore(md_content, mapping)
        else:
            restored_content = md_content
            
        # Création du tour (On pourrait segmenter ici à l'avenir)
        part = MessagePart(type=ContentType.TEXT, content=restored_content)
        turn = Turn(index=i, role=role, content=[part], confidence=confidence)
        session.turns.append(turn)
        
    # 4. Génération du résultat selon le format
    content = ""
    if options.format == 'json':
        data = {
            "session": {
                "id": session.id,
                "turns": [
                    {
                        "index": t.index,
                        "role": t.role.value,
                        "confidence": t.confidence,
                        "content": [{"type": p.type.value, "content": p.content} for p in t.content]
                    } for t in session.turns
                ]
            }
        }
        content = json.dumps(data, indent=2, ensure_ascii=False)
    elif options.format == 'yaml':
        data = {
            "session": {
                "id": session.id,
                "turns": [
                    {
                        "index": t.index,
                        "role": t.role.value,
                        "content": [{"type": p.type.value, "content": p.content} for p in t.content]
                    } for t in session.turns
                ]
            }
        }
        content = yaml.dump(data, allow_unicode=True, sort_keys=False)
    else:
        # Markdown par défaut
        full_md = ""
        if options.frontmatter:
            full_md += "---\n"
            full_md += f"title: {session.title or 'ACE Extraction'}\n"
            full_md += f"date: {datetime.now().isoformat()}\n"
            full_md += f"turns_count: {len(session.turns)}\n"
            full_md += "---\n\n"
            
        for turn in session.turns:
            role_label = "User" if turn.role == Role.USER else "MODEL"
            full_md += f"## {role_label}\n\n"
            for part in turn.content:
                full_md += part.content + "\n"
            full_md += "\n---\n\n"
            
        # Nettoyage final
        content = full_md.replace('\n\n\n', '\n\n')
    
    return ExtractionResult(content=content, format=options.format, session=session, debug_data=debug_data)

import sys
import argparse
import enum
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

from ace.main import process_html
from ace.models.chat import ExtractionOptions, ExtractionResult

class ExitCode(enum.IntEnum):
    SUCCESS = 0
    FILE_NOT_FOUND = 1
    PARSE_ERROR = 2
    NO_MESSAGES_DETECTED = 3
    CONVERSION_ERROR = 4
    INTERNAL_ERROR = 5
    USER_INTERRUPT = 130

def create_parser():
    parser = argparse.ArgumentParser(
        prog='ace',
        description='ACE - Adaptive Chat Extractor (agnostique et universel)',
        epilog='Utilisez --help-strategies pour plus de détails sur les algorithmes de détection.',
        add_help=False
    )
    
    # Groupes d'options
    io_group = parser.add_argument_group('Entrée/Sortie')
    io_group.add_argument('input', nargs='?', help='Fichier HTML ou - pour stdin')
    io_group.add_argument('output_arg', nargs='?', help='Fichier de sortie (défaut: INPUT.md ou stdout)')
    io_group.add_argument('-o', '--output', dest='output_opt', help='Spécifie explicitement le fichier de sortie')
    io_group.add_argument('-f', '--format', choices=['md', 'json', 'yaml'], help='Format de sortie')
    io_group.add_argument('-j', '--json', action='store_const', const='json', dest='format_opt', help='Sortie JSON')
    
    detect_group = parser.add_argument_group('Stratégies de détection')
    detect_group.add_argument('-t', '--topo', action='store_const', const='topo', dest='detector', default='topo')
    detect_group.add_argument('-H', '--heuristic', action='store_const', const='heuristic', dest='detector')
    detect_group.add_argument('-F', '--flux', action='store_const', const='flux', dest='detector')
    
    meta_group = parser.add_argument_group('Métadonnées et format')
    meta_group.add_argument('-m', '--frontmatter', action='store_true', help='Ajoute un en-tête YAML')
    
    debug_group = parser.add_argument_group('Diagnostic')
    debug_group.add_argument('-d', '--debug', action='store_true', help='Active le mode diagnostic')
    debug_group.add_argument('-q', '--quiet', action='store_true', help='Supprime les messages d\'information')
    
    expert_group = parser.add_argument_group('Options Expert')
    expert_group.add_argument('--raw', action='store_true', help='Désactive le Sanctuaire (protection des blocs complexes)')
    expert_group.add_argument('--no-table', action='store_true', help='Désactive le processeur de tableaux')
    
    # Aide classique
    parser.add_argument('-h', '--help', action='help', help='Affiche cette aide')
    parser.add_argument('--help-strategies', action='store_true', help='Affiche l\'aide sur les stratégies de détection')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.1.0')
    
    return parser

def print_strategies_help():
    print("""
Stratégies de détection disponibles :
  topo      (défaut) Analyse topologique agnostique, fonctionne sur tous les exports récents (ChatGPT, Claude, etc.).
  heuristic Détection basée sur des motifs courants (fallback pour les vieux exports ou structures simplistes).
  flux      Pour les conversations sans conteneur de messages explicite (ex: Grok avec <hr>).

Exemple d'utilisation :
  ace --topo chat.html -o output.md
  ace --flux simple_page.html --json
""")

def resolve_format(args):
    """Détermine le format de sortie avec priorité au flag explicite."""
    if args.format:
        return args.format
    if getattr(args, 'format_opt', None):
        return args.format_opt
        
    output_path = args.output_opt or args.output_arg
    if output_path and output_path != '-':
        ext = Path(output_path).suffix.lower()
        if ext == '.json':
            return 'json'
        elif ext in ['.yaml', '.yml']:
            return 'yaml'
        elif ext == '.md':
            return 'md'
    return 'md'

def resolve_output_path(args, format_final):
    """Détermine le chemin de sortie avec induction intelligente du nom."""
    if args.output_opt:
        return args.output_opt
    if args.output_arg:
        return args.output_arg
    if args.input == '-':
        return '-'
        
    # Induction automatique
    input_path = Path(args.input)
    suffix = f".{format_final}"
    if format_final == 'yaml':
        suffix = ".yaml"
    return str(input_path.with_suffix(suffix))

def generate_report(result: ExtractionResult, meta: dict, input_name: str) -> str:
    """Génère un rapport Markdown lisible pour le dossier de diagnostic."""
    report = f"# Rapport de Diagnostic ACE - {input_name}\n\n"
    report += f"- **Date** : {meta['date']}\n"
    report += f"- **Statut** : SUCCESS\n"
    report += f"- **Version** : {meta['version']}\n"
    report += f"- **Format** : {result.format}\n"
    report += f"- **Tours détectés** : {len(result.session.turns)}\n\n"
    
    report += "## Résumé des tours\n\n"
    for turn in result.session.turns:
        role = turn.role.value if hasattr(turn.role, 'value') else str(turn.role)
        content_preview = "N/A"
        if turn.content:
            content_preview = turn.content[0].content[:120].replace('\n', ' ') + "..."
            
        report += f"### Tour {turn.index} - {role} (Confiance: {turn.confidence:.2f})\n"
        report += f"> {content_preview}\n\n"
    
    return report

def main():
    try:
        parser = create_parser()
        args = parser.parse_args()
        
        if args.help_strategies:
            print_strategies_help()
            sys.exit(ExitCode.SUCCESS)
            
        if not args.input:
            parser.print_help()
            sys.exit(ExitCode.SUCCESS) # Or error? Success for help.
            
        # Résolution du format et de la sortie
        format_final = resolve_format(args)
        output_path_str = resolve_output_path(args, format_final)
        
        # Vérification de conflit format/extension
        if output_path_str != '-' and not args.quiet:
            ext = Path(output_path_str).suffix.lower()
            expected_ext = f".{format_final}"
            if format_final == 'yaml' and ext == '.yml':
                pass # Acceptable
            elif ext != expected_ext:
                print(f"⚠️  Avertissement : Le format demandé ({format_final}) diffère de l'extension de sortie ({ext}).", file=sys.stderr)

        # Gestion de l'entrée stdin
        if args.input == '-':
            html_content = sys.stdin.read()
            input_name = "stdin"
        else:
            input_path = Path(args.input)
            if not input_path.exists():
                print(f"Erreur : Le fichier {args.input} n'existe pas.", file=sys.stderr)
                sys.exit(ExitCode.FILE_NOT_FOUND)
            html_content = input_path.read_text(encoding="utf-8")
            input_name = input_path.name
            
        # Création des options
        options = ExtractionOptions(
            detector=args.detector,
            format=format_final,
            frontmatter=args.frontmatter,
            debug=args.debug,
            quiet=args.quiet,
            raw=args.raw,
            no_table=args.no_table
        )
        
        try:
            result = process_html(html_content, options)
            
            # Gestion du mode debug
            if options.debug:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                debug_dir = Path(f"debug/ace_debug_{Path(input_name).stem}_{timestamp}")
                debug_dir.mkdir(parents=True, exist_ok=True)
                
                meta = {
                    "version": "1.1.0",
                    "date": datetime.now().isoformat(),
                    "input": args.input,
                    "options": options.__dict__
                }
                (debug_dir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
                (debug_dir / "source.html").write_text(html_content, encoding="utf-8")
                
                for k, v in result.debug_data.items():
                    (debug_dir / f"{k}.json").write_text(json.dumps(v, indent=2), encoding="utf-8")
                
                # Génération du rapport lisible
                report_content = generate_report(result, meta, input_name)
                (debug_dir / "report.md").write_text(report_content, encoding="utf-8")
                    
                if not options.quiet:
                    print(f"Dossier de diagnostic créé : {debug_dir}", file=sys.stderr)

            # Sortie du résultat
            if output_path_str == '-':
                sys.stdout.write(result.content)
            else:
                Path(output_path_str).write_text(result.content, encoding="utf-8")
                if not options.quiet:
                    print(f"Conversion terminée ({format_final}) : {output_path_str}")
                    
            sys.exit(ExitCode.SUCCESS)
            
        except Exception as e:
            if options.debug:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                err_dir = Path(f"debug/ace_debug_ERROR_{Path(input_name).stem}_{timestamp}")
                err_dir.mkdir(parents=True, exist_ok=True)
                (err_dir / "error.log").write_text(str(e))
                import traceback
                (err_dir / "traceback.txt").write_text(traceback.format_exc())
                (err_dir / "source.html").write_text(html_content, encoding="utf-8")
                if not options.quiet:
                    print(f"Dossier de diagnostic d'erreur créé : {err_dir}", file=sys.stderr)
                    
            if not options.quiet:
                print(f"Erreur lors de la conversion : {e}", file=sys.stderr)
                if options.debug:
                    traceback.print_exc()
            sys.exit(ExitCode.CONVERSION_ERROR)

    except KeyboardInterrupt:
        print("\nInterruption détectée. Fermeture propre.", file=sys.stderr)
        sys.exit(ExitCode.USER_INTERRUPT)
    except Exception as e:
        print(f"Erreur système fatale : {e}", file=sys.stderr)
        sys.exit(ExitCode.INTERNAL_ERROR)

if __name__ == "__main__":
    main()

from bs4 import Tag, NavigableString
from ace.processors.tables import convert_table
import re

class MarkdownDispatcher:
    def __init__(self):
        self.handlers = {
            'p': self._handle_p,
            'h1': self._handle_header,
            'h2': self._handle_header,
            'h3': self._handle_header,
            'h4': self._handle_header,
            'h5': self._handle_header,
            'h6': self._handle_header,
            'ul': self._handle_list,
            'ol': self._handle_list,
            'li': self._handle_li,
            'br': self._handle_br,
            'hr': self._handle_hr,
            'table': self._handle_table,
            'strong': self._handle_inline,
            'b': self._handle_inline,
            'em': self._handle_inline,
            'i': self._handle_inline,
            'code': self._handle_code_inline,
        }

    def convert(self, tag: Tag) -> str:
        """Point d'entrée de la conversion récursive."""
        if isinstance(tag, NavigableString):
            return str(tag)
            
        # Règle Prioritaire : Si le tag a été remplacé par un UUID du Sanctuaire
        # BS4 renvoie le NavigableString de l'UUID. 
        # Si on est ici, c'est un Tag.
        
        # On vérifie si le tag contient uniquement un UUID (cas rare après replacement)
        text = tag.get_text(strip=True)
        if re.match(r'^__ACE_[A-Z]+_[a-f0-9]{8}__$', text):
            return text

        handler = self.handlers.get(tag.name, self._handle_generic)
        return handler(tag)

    def _handle_generic(self, tag: Tag) -> str:
        """Gère les tags inconnus en explorant récursivement leurs enfants."""
        content = ""
        for child in tag.children:
            if isinstance(child, NavigableString):
                content += str(child)
            else:
                content += self.convert(child)
        return content

    def _handle_p(self, tag: Tag) -> str:
        return f"\n{self._handle_generic(tag)}\n"

    def _handle_header(self, tag: Tag) -> str:
        level = int(tag.name[1])
        return f"\n{'#' * level} {self._handle_generic(tag)}\n"

    def _handle_list(self, tag: Tag) -> str:
        return f"\n{self._handle_generic(tag)}\n"

    def _handle_li(self, tag: Tag) -> str:
        prefix = "- "
        if tag.parent and tag.parent.name == 'ol':
            # Optionnel: gérer les index
            prefix = "1. "
        return f"{prefix}{self._handle_generic(tag)}\n"

    def _handle_br(self, tag: Tag) -> str:
        return "  \n"

    def _handle_hr(self, tag: Tag) -> str:
        return "\n---\n"

    def _handle_table(self, tag: Tag) -> str:
        return convert_table(tag)

    def _handle_inline(self, tag: Tag) -> str:
        sym = "**" if tag.name in ['strong', 'b'] else "*"
        return f"{sym}{self._handle_generic(tag)}{sym}"

    def _handle_code_inline(self, tag: Tag) -> str:
        # Ne pas doubler si c'est déjà un UUID injecté
        content = self._handle_generic(tag)
        if re.match(r'^__ACE_[A-Z]+_[a-f0-9]{8}__$', content):
            return content
        return f"`{content}`"

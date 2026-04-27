from bs4 import BeautifulSoup, Tag, NavigableString
import hashlib
import re
from typing import Dict, Any, List, Set
from ace.models.chat import ContentType
from ace.utils.regex import MERMAID_DETECTION_RE

class SanctuaryEntry:
    def __init__(self, raw_content: str, type: str, formatted_content: str = ""):
        self.raw_content = raw_content
        self.type = type
        self.formatted_content = formatted_content

    def to_dict(self) -> Dict[str, Any]:
        return {
            "raw_content": self.raw_content,
            "type": self.type,
            "formatted_content": self.formatted_content
        }

class SanctuaryManager:
    def __init__(self):
        self.mapping: Dict[str, SanctuaryEntry] = {}
        self.processed_ids: Set[int] = set()

    def _generate_uuid(self, content: str, prefix: str) -> str:
        h = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"__ACE_{prefix}_{h}__"

    def _mark_processed(self, tag: Tag):
        """Marque un tag et tous ses descendants comme traités."""
        self.processed_ids.add(id(tag))
        for descendant in tag.descendants:
            self.processed_ids.add(id(descendant))

    def extract(self, soup: BeautifulSoup) -> Dict[str, SanctuaryEntry]:
        """Extrait les blocs complexes et les remplace par des UUID."""
        self.processed_ids.clear()
        
        # 1. Extraction du CODE (pre)
        for pre in soup.find_all('pre'):
            if id(pre) in self.processed_ids: continue
            
            code_tag = pre.find('code')
            raw_content = code_tag.get_text() if code_tag else pre.get_text()
            uuid_key = self._generate_uuid(raw_content, "CODE")
            
            lang = ""
            if code_tag and code_tag.get('class'):
                for c in code_tag.get('class'):
                    if c.startswith('language-'):
                        lang = c.replace('language-', '')
                        break
            
            formatted = f"``` {lang}\n{raw_content}\n```"
            self.mapping[uuid_key] = SanctuaryEntry(raw_content, "code", formatted)
            
            self._mark_processed(pre)
            pre.clear()
            pre.append(NavigableString(uuid_key))

        # 2. Extraction MERMAID
        for tag in soup.find_all(['div', 'p']):
            if id(tag) in self.processed_ids: continue
            
            # Anti-Wrapper: Ne pas traiter les divs structurels comme du Mermaid
            if tag.name == 'div' and tag.find(['div', 'article', 'section', 'table']):
                continue
                
            text = tag.get_text()
            if MERMAID_DETECTION_RE.search(text):
                raw_mermaid = re.sub(r'^(?:}}%%|%%{.*?\}%%)', '', text).strip()
                uuid_key = self._generate_uuid(raw_mermaid, "MERM")
                formatted = f"```mermaid\n{raw_mermaid}\n```"
                self.mapping[uuid_key] = SanctuaryEntry(raw_mermaid, "mermaid", formatted)
                
                self._mark_processed(tag)
                tag.clear()
                tag.append(NavigableString(uuid_key))

        # 3. Extraction MATH (LaTeX/KaTeX)
        for annot in soup.find_all('annotation', encoding="application/x-tex"):
            if id(annot) in self.processed_ids: continue
            
            raw_math = annot.get_text().strip()
            uuid_key = self._generate_uuid(raw_math, "MATH")
            
            parent_math = annot.find_parent('math')
            is_block = (parent_math and parent_math.get('display') == 'block')
            
            formatted = f"$$\n{raw_math}\n$$" if is_block else f"${raw_math}$"
            self.mapping[uuid_key] = SanctuaryEntry(raw_math, "math", formatted)
            
            target = annot.find_parent(class_="katex") or parent_math or annot
            self._mark_processed(target)
            target.clear()
            target.append(NavigableString(uuid_key))

        return self.mapping

    def restore(self, text: str, mapping: Dict[str, SanctuaryEntry]) -> str:
        """Réinjecte les contenus protégés."""
        restored_text = text
        for uuid_key, entry in mapping.items():
            restored_text = restored_text.replace(uuid_key, entry.formatted_content)
        return restored_text

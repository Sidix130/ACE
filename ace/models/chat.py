from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

class Role(Enum):
    USER = "user"
    MODEL = "model"
    SYSTEM = "system"

class ContentType(Enum):
    TEXT = "text"
    CODE = "code"
    MATH_INLINE = "math_inline"
    MATH_BLOCK = "math_block"
    MERMAID = "mermaid"
    TABLE = "table"
    IMAGE = "image"

@dataclass
class MessagePart:
    type: ContentType
    content: str
    language: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Turn:
    index: int
    role: Role
    content: List[MessagePart]
    confidence: float
    timestamp: Optional[datetime] = None
    raw_html: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ChatSession:
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    source: Optional[str] = None
    title: Optional[str] = None
    created_at: Optional[datetime] = field(default_factory=datetime.now)
    turns: List[Turn] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExtractionOptions:
    detector: str = "topo"  # topo, heuristic, flux
    format: str = "md"      # md, json, yaml
    frontmatter: bool = False
    debug: bool = False
    quiet: bool = False
    raw: bool = False
    no_table: bool = False

@dataclass
class ExtractionResult:
    content: str
    format: str
    session: ChatSession
    debug_data: Dict[str, Any] = field(default_factory=dict)

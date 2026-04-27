from bs4 import Tag
from typing import List, Tuple, Optional, Any
from ace.models.chat import Role
import re

class RoleInferrer:
    def __init__(self):
        self.user_signals = ['user', 'human', 'you', 'vous']
        self.model_signals = ['assistant', 'model', 'chatgpt', 'deepseek', 'ai', 'thought', 'assistant-message']

    def infer(self, tag: Tag, context: List[Any] = []) -> Tuple[Role, float]:
        """
        Déduit le rôle d'un message.
        Retourne (Role, confidence).
        """
        user_score = 0.0
        model_score = 0.0
        
        # 1. Analyse des classes CSS
        classes = tag.get('class', [])
        if isinstance(classes, str): classes = [classes]
        class_str = " ".join(classes).lower()
        
        for sig in self.user_signals:
            if sig in class_str: user_score += 5.0
            
        for sig in self.model_signals:
            # 'thought' est un signal très fort pour MODEL
            if sig == 'thought' and sig in class_str: model_score += 8.0
            elif sig in class_str: model_score += 5.0
            
        # 2. Analyse du contenu (Signaux secondaires)
        # Présence de code ou LaTeX -> souvent MODEL
        if tag.find(['pre', 'code', 'annotation', 'math']):
            model_score += 2.0
            
        # 3. Arbitrage et Fallback par alternance
        if user_score > model_score:
            return Role.USER, 0.8
        elif model_score > user_score:
            return Role.MODEL, 0.8
        else:
            # Égalité ou absence de signal -> Alternance par rapport au contexte
            if context:
                last_role = context[-1].role
                if last_role == Role.USER:
                    return Role.MODEL, 0.5
                else:
                    return Role.USER, 0.5
            else:
                # Premier message du chat -> Souvent User
                return Role.USER, 0.4

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict
import os

try:
    from openai import OpenAI
except Exception:
    OpenAI = None  # type: ignore

@dataclass
class Subject:
    id: str
    name: str
    description: str = ""

@dataclass
class Option:
    text: str
    is_correct: bool = False

@dataclass
class Card:
    id: str
    subject_id: str
    type: str  # single | multi | text
    question: str
    expected_answer: str = ""
    options: List[Option] = field(default_factory=list)

class InMemoryRepo:
    def __init__(self) -> None:
        self.subjects: Dict[str, Subject] = {
            "bio": Subject(id="bio", name="Biologie"),
            "mathe": Subject(id="mathe", name="Mathematik"),
            "geschichte": Subject(id="geschichte", name="Geschichte"),
        }
        self.cards: Dict[str, Card] = {}
        # Demo cards
        self.add_card(Card(
            id="c1", subject_id="bio", type="single",
            question="Welches Tier ist ein Säugetier?",
            options=[Option("Krokodil"), Option("Delfin", True), Option("Adler")]
        ))
        self.add_card(Card(
            id="c2", subject_id="mathe", type="multi",
            question="Wähle alle Primzahlen:",
            options=[Option("2", True), Option("9"), Option("11", True), Option("15")]
        ))
        self.add_card(Card(
            id="c3", subject_id="bio", type="text",
            question="Definiere 'Photosynthese' in einem Satz.",
            expected_answer="Umwandlung von Lichtenergie in chemische Energie"
        ))

    def list_subjects(self, query: str = "") -> List[Subject]:
        items = list(self.subjects.values())
        if query:
            q = query.lower()
            items = [s for s in items if q in s.name.lower()]
        return sorted(items, key=lambda s: s.name.lower())

    def get_subject(self, sid: str) -> Optional[Subject]:
        return self.subjects.get(sid)

    def add_subject(self, name: str, description: str = "") -> Subject:
        sid = name.lower().replace(" ", "-")
        s = Subject(id=sid, name=name, description=description)
        self.subjects[sid] = s
        return s

    def add_card(self, card: Card) -> None:
        self.cards[card.id] = card

    def list_cards(self, subject_id: Optional[str] = None, qtype: Optional[str] = None, limit: int = 20) -> List[Card]:
        items = list(self.cards.values())
        if subject_id:
            items = [c for c in items if c.subject_id == subject_id]
        if qtype in {"single", "multi", "text"}:
            items = [c for c in items if c.type == qtype]
        return items[:limit]

class AIHelper:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o") -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model
        self.enabled = bool(self.api_key and OpenAI)
        self.client = OpenAI(api_key=self.api_key) if self.enabled else None

    def generate_distractors(self, question: str, correct: str, n: int = 3) -> List[str]:
        if not self.enabled:
            return ["Verwechslungsbegriff", "Oberbegriff", "Detailvariante"][:n]
        prompt = (
            f"Erzeuge {n} plausible kurze Falschantworten (JSON-Liste).\n"
            f"Frage: {question}\nKorrekte Antwort: {correct}"
        )
        try:
            resp = self.client.responses.create(model=self.model, input=prompt)
            import json
            return list(json.loads(resp.output_text))[:n]
        except Exception:
            return []

    def assess_free_text(self, question: str, expected: str, answer: str) -> dict:
        if not self.enabled:
            score = 1.0 if expected and expected.lower() in answer.lower() else 0.5 if answer else 0.0
            return {"score": score, "feedback": "Demo ohne KI", "missing_keywords": []}
        system = "JSON mit score(0..1), feedback, missing_keywords[]."
        user = f"Frage: {question}\nErwartet: {expected}\nAntwort: {answer}"
        try:
            resp = self.client.responses.create(model=self.model, instructions=system, input=user)
            import json
            return json.loads(resp.output_text)
        except Exception:
            return {"score": 0.0, "feedback": "Fehler bei KI", "missing_keywords": []}

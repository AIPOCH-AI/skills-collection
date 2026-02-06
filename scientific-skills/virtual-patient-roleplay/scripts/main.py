#!/usr/bin/env python3
"""
Virtual Patient Roleplay - Standardized Patient Simulator
Simulates patient interactions for medical education training.
"""

import json
import random
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class EmotionalState(Enum):
    CALM = "calm"
    ANXIOUS = "anxious"
    IRRITABLE = "irritable"
    DEPRESSED = "depressed"
    CONFUSED = "confused"


@dataclass
class PatientProfile:
    """Patient demographic and background information."""
    name: str
    age: int
    gender: str
    occupation: str
    medical_history: List[str] = field(default_factory=list)
    allergies: List[str] = field(default_factory=list)
    medications: List[str] = field(default_factory=list)


@dataclass
class ClinicalScenario:
    """Clinical case template."""
    chief_complaint: str
    history_of_present_illness: str
    associated_symptoms: List[str]
    key_findings: Dict[str, str]
    emotional_state: EmotionalState
    hidden_concerns: List[str]


class PatientSimulator:
    """Simulates standardized patient interactions."""
    
    SCENARIOS = {
        "chest_pain": {
            "chief_complaint": "Chest pain for 2 hours",
            "hpi": "Started while climbing stairs. Pressure-like, 8/10, radiates to left arm. Associated with shortness of breath and sweating.",
            "symptoms": ["dyspnea", "diaphoresis", "nausea"],
            "findings": {"vitals": "HR 110, BP 160/95", "ecg": "ST elevation in V1-V4"},
            "emotion": EmotionalState.ANXIOUS,
            "hidden": ["Family history of MI", "Smokes 1 pack/day", "Afraid of dying"]
        },
        "headache": {
            "chief_complaint": "Severe headache for 3 days",
            "hpi": "Worst headache of life. Sudden onset. Associated with photophobia and neck stiffness.",
            "symptoms": ["photophobia", "phonophobia", "neck_stiffness"],
            "findings": {"vitals": "BP 180/110", "neuro": "Positive Kernig sign"},
            "emotion": EmotionalState.IRRITABLE,
            "hidden": ["Had similar episode 6 months ago", "Takes ibuprofen daily"]
        },
        "abdominal_pain": {
            "chief_complaint": "Right lower quadrant pain",
            "hpi": "Started around belly button, moved to RLQ. Gradual worsening over 12 hours. Loss of appetite.",
            "symptoms": ["anorexia", "nausea", "low_grade_fever"],
            "findings": {"vitals": "T 37.8C, HR 95", "exam": "Tenderness at McBurney's point"},
            "emotion": EmotionalState.CALM,
            "hidden": ["Fear of surgery", "No health insurance"]
        }
    }
    
    def __init__(self, scenario: str = "chest_pain", difficulty: str = "intermediate"):
        self.scenario_type = scenario
        self.difficulty = difficulty
        self.scenario = self._load_scenario(scenario)
        self.conversation_history: List[Dict] = []
        self.asked_questions: set = set()
        self.revealed_info: set = set()
        
        # Generate patient profile
        self.patient = self._generate_patient_profile()
        
    def _load_scenario(self, scenario_type: str) -> Dict:
        """Load scenario template."""
        if scenario_type not in self.SCENARIOS:
            raise ValueError(f"Unknown scenario: {scenario_type}. Available: {list(self.SCENARIOS.keys())}")
        return self.SCENARIOS[scenario_type]
    
    def _generate_patient_profile(self) -> PatientProfile:
        """Generate random but consistent patient demographics."""
        first_names_m = ["James", "Robert", "John", "Michael", "David"]
        first_names_f = ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia"]
        
        gender = random.choice(["male", "female"])
        first_names = first_names_m if gender == "male" else first_names_f
        
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        age = random.randint(35, 75) if self.scenario_type == "chest_pain" else random.randint(18, 65)
        
        occupations = ["teacher", "retired", "office worker", "truck driver", "nurse"]
        
        return PatientProfile(
            name=name,
            age=age,
            gender=gender,
            occupation=random.choice(occupations),
            medical_history=["hypertension"] if random.random() > 0.5 else [],
            allergies=["penicillin"] if random.random() > 0.7 else [],
            medications=["lisinopril"] if random.random() > 0.5 else []
        )
    
    def ask(self, question: str) -> Dict:
        """
        Process student question and generate patient response.
        
        Args:
            question: Student's question text
            
        Returns:
            Response dictionary with patient answer and feedback
        """
        question_lower = question.lower()
        self.asked_questions.add(question_lower)
        
        # Determine response based on question type
        response = self._generate_response(question_lower)
        
        # Record in history
        exchange = {
            "question": question,
            "response": response["patient_response"],
            "revealed": list(self.revealed_info)
        }
        self.conversation_history.append(exchange)
        
        # Generate feedback
        feedback = self._generate_feedback()
        
        return {
            "patient_response": response["patient_response"],
            "emotional_state": self.scenario["emotion"].value,
            "physical_cues": response.get("physical_cues", ""),
            "hidden_information": self._get_unrevealed_info(),
            "conversation_history": self.conversation_history,
            "feedback": feedback
        }
    
    def _generate_response(self, question: str) -> Dict:
        """Generate contextual patient response."""
        responses = {
            "chest_pain": {
                "pain": ("It feels like an elephant is sitting on my chest. It's crushing and heavy.",
                        "Patient clutches chest while speaking"),
                "arm": ("Yes, it goes down my left arm. Feels numb and tingly.",
                       "Patient rubs left arm"),
                "family": ("My father died of a heart attack when he was 55.",
                          ""),
                "smoke": ("I smoke about a pack a day. I know I should quit...",
                         "Patient looks embarrassed"),
                "name": (f"I'm {self.patient.name}.",
                        ""),
                "default": ("I'm not sure I understand. Can you ask differently?",
                           "Patient looks confused")
            },
            "headache": {
                "head": ("It's the worst headache I've ever had. Like someone hit me with a hammer.",
                        "Patient holds head in hands, avoids light"),
                "light": ("Yes, the light hurts my eyes terribly.",
                         "Patient squints"),
                "neck": ("My neck is so stiff I can barely move it.",
                        "Patient demonstrates limited neck mobility"),
                "default": ("Could you repeat that? The pain makes it hard to concentrate.",
                           "Patient appears distracted")
            },
            "abdominal_pain": {
                "pain": ("It started near my belly button but now it's here on the right side.",
                        "Patient points to RLQ"),
                "eat": ("I haven't felt like eating anything since yesterday.",
                       ""),
                "fever": ("I think I might have a slight fever. I feel warm.",
                         "Patient touches forehead"),
                "surgery": ("I'm scared about needing surgery...",
                           "Patient voice trembles slightly"),
                "default": ("What do you mean?",
                           "Patient looks puzzled")
            }
        }
        
        scenario_responses = responses.get(self.scenario_type, responses["chest_pain"])
        
        # Match keywords
        for keyword, (answer, cue) in scenario_responses.items():
            if keyword != "default" and keyword in question:
                self.revealed_info.add(keyword)
                return {
                    "patient_response": answer,
                    "physical_cues": cue
                }
        
        # Default response
        return {
            "patient_response": scenario_responses.get("default", ("I'm not sure.", ""))[0],
            "physical_cues": scenario_responses.get("default", ("", ""))[1]
        }
    
    def _get_unrevealed_info(self) -> List[str]:
        """Return information not yet revealed to student."""
        hidden = set(self.scenario.get("hidden", []))
        return list(hidden - self.revealed_info)
    
    def _generate_feedback(self) -> Dict:
        """Generate educational feedback."""
        feedback = {
            "communication_tips": [],
            "missed_questions": [],
            "strengths": []
        }
        
        # Check for missed critical questions
        critical_questions = {
            "chest_pain": ["pain", "arm", "family"],
            "headache": ["head", "light", "neck"],
            "abdominal_pain": ["pain", "eat", "fever"]
        }
        
        scenario_critical = critical_questions.get(self.scenario_type, [])
        asked_keywords = set()
        for q in self.asked_questions:
            for keyword in scenario_critical:
                if keyword in q:
                    asked_keywords.add(keyword)
        
        missed = set(scenario_critical) - asked_keywords
        if missed:
            feedback["missed_questions"] = [f"Consider asking about: {m}" for m in missed]
        
        # Communication tips
        if len(self.conversation_history) > 5:
            feedback["communication_tips"].append("Good thoroughness in history taking.")
        else:
            feedback["communication_tips"].append("Consider asking more follow-up questions.")
        
        return feedback
    
    def get_case_summary(self) -> Dict:
        """Return complete case information for debriefing."""
        return {
            "patient_profile": {
                "name": self.patient.name,
                "age": self.patient.age,
                "gender": self.patient.gender,
                "occupation": self.patient.occupation
            },
            "chief_complaint": self.scenario["chief_complaint"],
            "history_of_present_illness": self.scenario["hpi"],
            "key_findings": self.scenario["findings"],
            "hidden_concerns": self.scenario.get("hidden", []),
            "questions_asked": len(self.asked_questions),
            "information_revealed": len(self.revealed_info),
            "conversation_transcript": self.conversation_history
        }


def main():
    """CLI interface for testing."""
    import sys
    
    scenario = sys.argv[1] if len(sys.argv) > 1 else "chest_pain"
    
    print(f"🩺 Virtual Patient Simulator - {scenario.upper()}\n")
    print("=" * 50)
    
    simulator = PatientSimulator(scenario=scenario)
    
    print(f"\nPatient: {simulator.patient.name}, {simulator.patient.age}y {simulator.patient.gender}")
    print(f"Occupation: {simulator.patient.occupation}")
    print("\nThe patient enters the room, holding their chest...")
    print("\nType your questions (or 'quit' to exit, 'summary' for debrief):\n")
    
    while True:
        try:
            question = input("> ").strip()
            
            if question.lower() == 'quit':
                break
            elif question.lower() == 'summary':
                summary = simulator.get_case_summary()
                print("\n" + "=" * 50)
                print("CASE DEBRIEF")
                print("=" * 50)
                print(json.dumps(summary, indent=2))
                continue
            
            if not question:
                continue
            
            result = simulator.ask(question)
            print(f"\n🧑 Patient: {result['patient_response']}")
            if result['physical_cues']:
                print(f"   [Physical: {result['physical_cues']}]")
            
            if result['feedback']['missed_questions']:
                print(f"\n💡 Tip: {result['feedback']['missed_questions'][0]}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    print("\nSession ended.")


if __name__ == "__main__":
    main()

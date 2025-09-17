from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from characters import ScenarioType, CharacterPersona

@dataclass
class Scenario:
    """Represents a social skills training scenario"""
    id: str
    name: str
    description: str
    scenario_type: ScenarioType
    characters: List[str]  # Character IDs
    objectives: List[str]
    context: str
    difficulty: str  # "beginner", "intermediate", "advanced"
    
    def get_character_ids(self) -> List[str]:
        """Get the character IDs for this scenario"""
        return self.characters

class ScenarioManager:
    """Manages all available scenarios"""
    
    def __init__(self):
        self.scenarios = self._initialize_scenarios()
    
    def _initialize_scenarios(self) -> Dict[str, Scenario]:
        """Initialize all pre-defined scenarios"""
        scenarios = {}
        
        # Workplace Scenarios
        scenarios["workplace_deadline"] = Scenario(
            id="workplace_deadline",
            name="Unrealistic Deadline",
            description="Your boss has given you an unrealistic deadline for a major project. Practice addressing this professionally while maintaining your boundaries.",
            scenario_type=ScenarioType.WORKPLACE,
            characters=["marcus", "sarah", "kai"],
            objectives=[
                "Address the unrealistic deadline professionally",
                "Propose alternative solutions",
                "Maintain professional boundaries",
                "Seek support from colleagues"
            ],
            context="""You're a software developer working on a critical project. Your boss Marcus has just informed you that the deadline has been moved up by 2 weeks, giving you only 1 week to complete what was originally planned as a 3-week project. 

Sarah, your supportive coworker, is also in the meeting and can provide backup. Coach Kai is available to guide you through the conversation.

The project involves:
- Building a new user authentication system
- Integrating with 3 external APIs
- Writing comprehensive tests
- Creating documentation

You know this timeline is unrealistic and could compromise code quality and team morale.""",
            difficulty="intermediate"
        )
        
        scenarios["workplace_feedback"] = Scenario(
            id="workplace_feedback",
            name="Giving Difficult Feedback",
            description="Practice giving constructive feedback to a team member whose performance has been declining.",
            scenario_type=ScenarioType.WORKPLACE,
            characters=["sarah", "kai"],
            objectives=[
                "Deliver feedback constructively",
                "Focus on specific behaviors",
                "Offer support and solutions",
                "Maintain professional relationship"
            ],
            context="""You're a team lead and need to have a difficult conversation with Sarah, a team member whose performance has been declining over the past month. 

Issues you've observed:
- Missing deadlines on 3 consecutive projects
- Quality of work has decreased significantly
- Less engagement in team meetings
- Arriving late to work multiple times

You want to address these issues while being supportive and helping Sarah get back on track. Coach Kai is available to guide you through this conversation.""",
            difficulty="advanced"
        )
        
        # Dating Scenarios
        scenarios["first_date"] = Scenario(
            id="first_date",
            name="First Date Conversation",
            description="Practice navigating a first date conversation, showing interest while being authentic and handling awkward moments gracefully.",
            scenario_type=ScenarioType.DATING,
            characters=["alex", "jordan", "kai"],
            objectives=[
                "Show genuine interest in your date",
                "Handle awkward moments gracefully",
                "Be authentic and engaging",
                "Know when to end the date appropriately"
            ],
            context="""You're on a first date with Alex at a cozy coffee shop. You met through a mutual friend and have been texting for about a week. This is your first in-person meeting.

Alex seems interesting and attractive, but you're feeling a bit nervous. Your friend Jordan is available via text for advice, and Coach Kai can provide real-time guidance.

The date has been going well so far - you've been talking for about 30 minutes. Alex just asked about your career goals, and you want to respond in a way that's engaging but not overwhelming.""",
            difficulty="beginner"
        )
        
        scenarios["relationship_talk"] = Scenario(
            id="relationship_talk",
            name="Defining the Relationship",
            description="Practice having 'the talk' about where your relationship is heading and what you both want.",
            scenario_type=ScenarioType.DATING,
            characters=["alex", "jordan", "kai"],
            objectives=[
                "Express your feelings clearly",
                "Listen to your partner's perspective",
                "Navigate potential differences",
                "Make decisions about the relationship"
            ],
            context="""You've been dating Alex for about 3 months now. Things have been going well, but you're starting to feel like you need to have a conversation about where this is heading.

You're both in your late 20s and have been exclusive for about 6 weeks. You're starting to develop deeper feelings but aren't sure if Alex feels the same way. You want to know if you're both looking for something serious or if this is more casual.

Your friend Jordan is available for advice, and Coach Kai can help guide the conversation.""",
            difficulty="intermediate"
        )
        
        # Family Scenarios
        scenarios["family_boundaries"] = Scenario(
            id="family_boundaries",
            name="Setting Family Boundaries",
            description="Practice setting healthy boundaries with an overbearing parent while maintaining the relationship.",
            scenario_type=ScenarioType.FAMILY,
            characters=["patricia", "michael", "kai"],
            objectives=[
                "Set clear boundaries respectfully",
                "Maintain family relationships",
                "Handle guilt and manipulation",
                "Get support from other family members"
            ],
            context="""Your mother Patricia has been calling you multiple times a day, showing up unannounced at your apartment, and constantly asking about your personal life. You're 28 years old and need more independence.

Recent incidents:
- She called you 5 times yesterday asking about your dating life
- She showed up at your apartment last week without calling
- She's been pressuring you to move closer to home
- She questions all your life decisions

Your brother Michael is supportive of you setting boundaries and is available to help. Coach Kai can guide you through this difficult conversation.""",
            difficulty="intermediate"
        )
        
        scenarios["family_finances"] = Scenario(
            id="family_finances",
            name="Family Financial Boundaries",
            description="Practice saying no to family members who repeatedly ask for financial help.",
            scenario_type=ScenarioType.FAMILY,
            characters=["patricia", "michael", "kai"],
            objectives=[
                "Say no to financial requests firmly but kindly",
                "Set clear financial boundaries",
                "Avoid enabling unhealthy patterns",
                "Maintain family relationships"
            ],
            context="""Your mother Patricia has been asking you for money regularly over the past year. You've helped her out several times, but it's becoming a pattern and affecting your own financial goals.

Recent requests:
- $500 for "emergency" car repairs (3rd time this year)
- $200 for groceries (she has a job and should be able to afford this)
- $1000 for a vacation she can't afford
- $300 for "unexpected bills"

You're trying to save for a house and your own future, but you feel guilty saying no. Your brother Michael has also been asked for money and is supportive of setting boundaries. Coach Kai can help you navigate this conversation.""",
            difficulty="advanced"
        )
        
        return scenarios
    
    def get_scenario(self, scenario_id: str) -> Optional[Scenario]:
        """Get a scenario by ID"""
        return self.scenarios.get(scenario_id)
    
    def get_scenarios_by_type(self, scenario_type: ScenarioType) -> List[Scenario]:
        """Get all scenarios of a specific type"""
        return [scenario for scenario in self.scenarios.values() 
                if scenario.scenario_type == scenario_type]
    
    def get_scenarios_by_difficulty(self, difficulty: str) -> List[Scenario]:
        """Get all scenarios of a specific difficulty level"""
        return [scenario for scenario in self.scenarios.values() 
                if scenario.difficulty == difficulty]
    
    def list_all_scenarios(self) -> List[Scenario]:
        """Get all available scenarios"""
        return list(self.scenarios.values())
    
    def get_scenario_summary(self, scenario_id: str) -> Optional[str]:
        """Get a brief summary of a scenario"""
        scenario = self.get_scenario(scenario_id)
        if not scenario:
            return None
        
        return f"""**{scenario.name}** ({scenario.difficulty.title()})
*{scenario.description}*

**Objectives:**
{chr(10).join(f"• {obj}" for obj in scenario.objectives)}

**Characters:** {', '.join(scenario.characters)}"""

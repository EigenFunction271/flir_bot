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
        
        # NEW UNCOMFORTABLE SCENARIOS
        
        scenarios["workplace_harassment"] = Scenario(
            id="workplace_harassment",
            name="Reporting Workplace Harassment",
            description="Practice reporting inappropriate behavior from a senior colleague while protecting your career.",
            scenario_type=ScenarioType.WORKPLACE,
            characters=["david", "sarah", "kai"],
            objectives=[
                "Document inappropriate behavior professionally",
                "Navigate power dynamics carefully",
                "Protect your career while standing up for yourself",
                "Seek support from trusted colleagues"
            ],
            context="""You're a junior employee and David, a senior executive, has been making increasingly inappropriate comments and advances toward you. This has been going on for 3 months and is escalating.

Recent incidents:
- He commented on your appearance in front of other colleagues
- He's been "accidentally" touching your arm during meetings
- He asked you to stay late for "one-on-one mentoring" that felt inappropriate
- He made a sexual joke about you in a group setting
- He's been texting you personal messages outside work hours

You're worried about retaliation if you report him, but you can't continue like this. Sarah, a trusted colleague, has noticed the behavior and is supportive. Coach Kai can help you navigate this extremely difficult situation.""",
            difficulty="advanced"
        )
        
        scenarios["workplace_sabotage"] = Scenario(
            id="workplace_sabotage",
            name="Confronting Workplace Sabotage",
            description="Practice confronting a colleague who has been sabotaging your work and spreading rumors about you.",
            scenario_type=ScenarioType.WORKPLACE,
            characters=["emma", "james", "kai"],
            objectives=[
                "Confront sabotage behavior directly but professionally",
                "Protect your reputation and work",
                "Document evidence of wrongdoing",
                "Maintain professionalism despite personal attacks"
            ],
            context="""You've discovered that Emma, a colleague you thought was a friend, has been systematically sabotaging your work and spreading false rumors about you to management.

Evidence you've found:
- She deleted important files from your shared project folder
- She's been telling your boss that you're "difficult to work with"
- She took credit for your ideas in a recent presentation
- She's been spreading rumors that you're planning to quit
- She's been excluding you from important meetings and decisions

You're furious and hurt, but you need to handle this professionally. James, another colleague, has witnessed some of this behavior and can provide support. Coach Kai can help you navigate this betrayal and confrontation.""",
            difficulty="advanced"
        )
        
        scenarios["dating_ghosting"] = Scenario(
            id="dating_ghosting",
            name="Confronting a Ghost",
            description="Practice confronting someone who ghosted you after months of dating, then suddenly reappeared.",
            scenario_type=ScenarioType.DATING,
            characters=["alex", "jordan", "kai"],
            objectives=[
                "Express your hurt and disappointment clearly",
                "Set boundaries about communication",
                "Decide whether to give them another chance",
                "Protect your emotional well-being"
            ],
            context="""You were dating Alex for 4 months and things seemed to be going well. You were starting to develop real feelings. Then suddenly, 3 weeks ago, Alex completely stopped responding to your texts and calls. No explanation, no warning - just complete silence.

You were devastated and confused. You tried reaching out multiple times but got no response. You finally accepted that you'd been ghosted and were starting to move on.

Now, out of nowhere, Alex has texted you saying "Hey, I'm sorry I disappeared. Can we talk?" and wants to meet up to "explain everything."

You're angry, hurt, and confused. Part of you wants to hear the explanation, but part of you wants to tell Alex exactly how much this hurt you. Your friend Jordan is supportive but thinks you should be cautious. Coach Kai can help you navigate this emotional minefield.""",
            difficulty="advanced"
        )
        
        scenarios["dating_cheating"] = Scenario(
            id="dating_cheating",
            name="Discovering Infidelity",
            description="Practice confronting a partner you've discovered has been cheating on you.",
            scenario_type=ScenarioType.DATING,
            characters=["riley", "casey", "kai"],
            objectives=[
                "Confront the cheating behavior directly",
                "Express your hurt and betrayal",
                "Decide whether to end the relationship",
                "Protect your dignity and self-worth"
            ],
            context="""You've been in a relationship with Riley for 8 months. You thought things were going well, but you've just discovered that Riley has been cheating on you with someone else.

Evidence you found:
- Suspicious text messages on Riley's phone
- Riley has been lying about where they were going
- You found a receipt for a hotel room from last week
- A mutual friend accidentally mentioned seeing Riley with someone else
- Riley's behavior has been distant and secretive lately

You're devastated, angry, and feel completely betrayed. You need to confront Riley about this, but you're not sure how to handle the conversation. Your friend Casey is supportive and thinks you deserve better. Coach Kai can help you navigate this extremely painful situation.""",
            difficulty="advanced"
        )
        
        scenarios["family_addiction"] = Scenario(
            id="family_addiction",
            name="Confronting Family Addiction",
            description="Practice confronting a family member about their addiction while maintaining love and boundaries.",
            scenario_type=ScenarioType.FAMILY,
            characters=["michael", "patricia", "kai"],
            objectives=[
                "Express concern about addiction behavior",
                "Set boundaries to protect yourself",
                "Encourage seeking help without enabling",
                "Maintain love while being firm"
            ],
            context="""Your brother Michael has been struggling with alcohol addiction for the past year. It's gotten worse recently and is affecting the entire family.

Recent incidents:
- He showed up drunk to your birthday dinner and caused a scene
- He's been borrowing money from family members to buy alcohol
- He lost his job due to showing up drunk
- He's been lying about his drinking and getting defensive when confronted
- He's been isolating himself and avoiding family gatherings

Your mother Patricia is in denial and keeps making excuses for him. You love your brother but you can't continue to enable his behavior. You need to have a difficult conversation about his addiction and set boundaries. Coach Kai can help you navigate this emotionally charged situation.""",
            difficulty="advanced"
        )
        
        scenarios["family_coming_out"] = Scenario(
            id="family_coming_out",
            name="Coming Out to Unsupportive Family",
            description="Practice coming out to family members who you know will not be supportive or accepting.",
            scenario_type=ScenarioType.FAMILY,
            characters=["patricia", "michael", "kai"],
            objectives=[
                "Express your authentic self despite potential rejection",
                "Set boundaries about respect and acceptance",
                "Protect your mental health and well-being",
                "Maintain relationships with supportive family members"
            ],
            context="""You've known you're gay for years but have been hiding it from your family. You're tired of living a lie and want to be authentic, but you know your mother Patricia will not be supportive.

Your concerns:
- Patricia has made homophobic comments in the past
- She's very religious and believes being gay is a sin
- She's been pressuring you to date and get married
- You're worried she might cut you off financially or emotionally
- You're afraid of how this will affect family gatherings and relationships

Your brother Michael is more open-minded and you think he'll be supportive, but you're not sure. You're terrified of the potential rejection but you can't continue hiding who you are. Coach Kai can help you navigate this life-changing conversation.""",
            difficulty="advanced"
        )
        
        scenarios["workplace_discrimination"] = Scenario(
            id="workplace_discrimination",
            name="Facing Workplace Discrimination",
            description="Practice confronting discriminatory behavior from management while protecting your career.",
            scenario_type=ScenarioType.WORKPLACE,
            characters=["marcus", "sarah", "kai"],
            objectives=[
                "Address discriminatory behavior professionally",
                "Document incidents for potential legal action",
                "Protect your career while standing up for your rights",
                "Seek support from colleagues and HR"
            ],
            context="""You've been experiencing subtle but persistent discrimination at work from your boss Marcus. You're the only person of color on your team and you've noticed a pattern of unfair treatment.

Incidents you've experienced:
- Marcus consistently gives you more difficult projects than your white colleagues
- He's made comments about your "communication style" being "too direct"
- You've been passed over for promotions despite having better performance reviews
- He's questioned your qualifications in front of other team members
- He's made microaggressions about your cultural background

You're frustrated and hurt, but you're worried about retaliation if you speak up. Sarah, a colleague, has noticed the pattern and is supportive. Coach Kai can help you navigate this complex and emotionally charged situation.""",
            difficulty="advanced"
        )
        
        scenarios["dating_abuse"] = Scenario(
            id="dating_abuse",
            name="Leaving an Abusive Relationship",
            description="Practice ending an emotionally abusive relationship and setting boundaries for your safety.",
            scenario_type=ScenarioType.DATING,
            characters=["victor", "taylor", "kai"],
            objectives=[
                "Recognize and name abusive behavior",
                "Set firm boundaries for your safety",
                "End the relationship safely",
                "Protect your mental health and well-being"
            ],
            context="""You've been in a relationship with Victor for 6 months, and you've slowly realized that it's become emotionally abusive. Victor has been manipulating and gaslighting you, and you need to end it.

Abusive behaviors you've experienced:
- Victor constantly criticizes your appearance and choices
- He isolates you from friends and family
- He makes you feel guilty for spending time with others
- He threatens to hurt himself if you leave
- He monitors your phone and social media
- He makes you feel like you're always wrong and he's always right
- He twists your words and makes you doubt your own memory
- He plays the victim when you try to address his behavior

You're scared but you know you need to end this relationship. Your friend Taylor is supportive and has been encouraging you to leave. Coach Kai can help you navigate this dangerous and emotionally complex situation.""",
            difficulty="advanced"
        )
        
        scenarios["workplace_bullying"] = Scenario(
            id="workplace_bullying",
            name="Confronting Workplace Bullying",
            description="Practice standing up to a workplace bully who has been targeting you and making your life miserable.",
            scenario_type=ScenarioType.WORKPLACE,
            characters=["brandon", "sarah", "kai"],
            objectives=[
                "Stand up to bullying behavior professionally",
                "Document incidents for HR",
                "Protect your mental health and career",
                "Seek support from colleagues and management"
            ],
            context="""Brandon, a senior manager, has been bullying you for the past 4 months. He's been making your work life miserable and you're starting to dread coming to work.

Bullying behaviors you've experienced:
- Brandon publicly humiliates you in meetings
- He gives you impossible deadlines and then criticizes you for not meeting them
- He takes credit for your work and ideas
- He spreads rumors about your performance to other managers
- He excludes you from important meetings and decisions
- He makes inappropriate comments about your personal life
- He threatens your job security when you try to stand up for yourself

You're afraid of retaliation if you report him, but you can't continue like this. Sarah, a colleague, has witnessed some of this behavior and is supportive. Coach Kai can help you navigate this extremely difficult situation.""",
            difficulty="advanced"
        )
        
        scenarios["family_manipulation"] = Scenario(
            id="family_manipulation",
            name="Confronting Family Manipulation",
            description="Practice setting boundaries with a family member who uses guilt and manipulation to control you.",
            scenario_type=ScenarioType.FAMILY,
            characters=["linda", "michael", "kai"],
            objectives=[
                "Recognize manipulative behavior",
                "Set firm boundaries without guilt",
                "Protect your mental health",
                "Maintain relationships with other family members"
            ],
            context="""Your mother Linda has been manipulating and controlling you for years. She uses guilt trips, emotional blackmail, and passive-aggressive behavior to get what she wants.

Manipulative behaviors you've experienced:
- Linda guilt-trips you about not visiting enough
- She makes backhanded compliments about your life choices
- She threatens to cut you off financially if you don't do what she wants
- She plays the victim when you try to set boundaries
- She uses family gatherings to publicly shame you
- She manipulates other family members to pressure you
- She makes you feel responsible for her happiness

You're tired of being controlled and manipulated, but you feel guilty about setting boundaries. Your brother Michael is supportive and has experienced similar behavior. Coach Kai can help you navigate this emotionally complex situation.""",
            difficulty="advanced"
        )
        
        scenarios["dating_manipulation"] = Scenario(
            id="dating_manipulation",
            name="Escaping a Manipulative Partner",
            description="Practice ending a relationship with someone who uses manipulation and emotional abuse to control you.",
            scenario_type=ScenarioType.DATING,
            characters=["chloe", "casey", "kai"],
            objectives=[
                "Recognize manipulative and toxic behavior",
                "Set firm boundaries for your safety",
                "End the relationship safely",
                "Protect your mental health and self-worth"
            ],
            context="""You've been dating Chloe for 8 months, and you've slowly realized that she's been manipulating and emotionally abusing you. She's been controlling your life and making you doubt yourself.

Manipulative behaviors you've experienced:
- Chloe isolates you from friends and family
- She plays the victim when you try to address her behavior
- She spreads rumors about you to mutual friends
- She makes you feel guilty for having other relationships
- She uses your insecurities against you
- She threatens to harm herself if you leave
- She makes you feel like you're always wrong and she's always right

You're scared but you know you need to end this relationship. Your friend Casey is supportive and has been encouraging you to leave. Coach Kai can help you navigate this dangerous and emotionally complex situation.""",
            difficulty="advanced"
        )
        
        scenarios["family_addiction_denial"] = Scenario(
            id="family_addiction_denial",
            name="Confronting Addiction Denial",
            description="Practice confronting a family member who is in complete denial about their addiction and refuses to get help.",
            scenario_type=ScenarioType.FAMILY,
            characters=["robert", "linda", "kai"],
            objectives=[
                "Confront denial and enabling behavior",
                "Set boundaries to protect yourself",
                "Encourage seeking help without enabling",
                "Maintain love while being firm about consequences"
            ],
            context="""Your father Robert has been struggling with alcohol addiction for years, but he's in complete denial about it. He refuses to acknowledge the problem and gets defensive when anyone tries to help.

Denial behaviors you've experienced:
- Robert denies he has a drinking problem despite clear evidence
- He blames others for his problems and mistakes
- He makes excuses for his behavior and broken promises
- He gets angry and defensive when confronted
- He manipulates family members to enable his behavior
- He refuses to seek help or treatment
- He makes you feel guilty for trying to help

Your mother Linda is also in denial and enables his behavior. You love your father but you can't continue to enable his addiction. Coach Kai can help you navigate this emotionally charged situation.""",
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

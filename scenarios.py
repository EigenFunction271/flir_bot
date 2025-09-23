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
    character_roles: Dict[str, str] = None  # Character ID -> Role description
    
    def get_character_ids(self) -> List[str]:
        """Get the character IDs for this scenario"""
        return self.characters
    
    def get_character_role_context(self, character_id: str) -> str:
        """Get role-specific context for a character in this scenario"""
        if self.character_roles and character_id in self.character_roles:
            return self.character_roles[character_id]
        return ""

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

You know this timeline is unrealistic and could compromise code quality and team morale. Importantly, some of the requirements depend on other departments and cannot be completed in the given time frame. However, Marcus and Sarah are unaware of this. Marcus is also under pressure from the CEO to complete the project on time.""",
            character_roles={
                "marcus": "You are the aggressive project manager who is demanding the unrealistic deadline. You're under pressure from the CEO and are intimidating the team to meet the timeline. You don't want to hear excuses and will fire anyone who doesn't comply.",
                "sarah": "You are the supportive team lead who is caught between Marcus's demands and the team's concerns. You're trying to mediate but also need to protect your team from Marcus's threats."
            },
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
            character_roles={
                "sarah": "You are the employee receiving feedback about your declining performance. You've been struggling personally due to your husband cheating on you with your best friend. You're defensive about your work issues and may make excuses or try to explain your personal problems. You're not the manager - you're the one being talked to about performance problems.",
                "kai": "You are the coach/mentor who can provide guidance to the user on how to handle this difficult conversation effectively."
            },
            difficulty="advanced"
        )
        
        # Dating Scenarios
        scenarios["first_date"] = Scenario(
            id="first_date",
            name="First Date Conversation",
            description="Practice navigating a first date conversation, showing interest while being authentic and handling awkward moments gracefully.",
            scenario_type=ScenarioType.DATING,
            characters=["alex", "kai"],
            objectives=[
                "Show genuine interest in your date",
                "Handle awkward moments gracefully",
                "Be authentic and engaging",
                "Know when to end the date appropriately"
            ],
            context="""You're on a first date with Alex at a cozy coffee shop. You met through a mutual friend and have been texting for about a week. This is your first in-person meeting.

Alex seems interesting and attractive, but you're feeling a bit nervous. Coach Kai can provide real-time guidance.

The date has been going well so far - you've been talking for about 30 minutes. Alex just asked about your career goals, and you want to respond in a way that's engaging but not overwhelming.""",
            character_roles={
                "alex": "You are the date partner who is interested and engaged. You're asking thoughtful questions and showing genuine interest in getting to know the user. You're mysterious and intriguing, having lived in 12 different countries, and you're emotionally intelligent but guarded about your own feelings.",
                "kai": "You are the dating coach who can provide guidance on conversation skills, reading social cues, and handling dating situations effectively."
            },
            difficulty="beginner"
        )
        
        scenarios["relationship_talk"] = Scenario(
            id="relationship_talk",
            name="Defining the Relationship",
            description="Practice having 'the talk' about where your relationship is heading and what you both want.",
            scenario_type=ScenarioType.DATING,
            characters=["alex", "kai"],
            objectives=[
                "Express your feelings clearly",
                "Listen to your partner's perspective",
                "Navigate potential differences",
                "Make decisions about the relationship"
            ],
            context="""You've been dating Alex for about 3 months now. Things have been going well, but you're starting to feel like you need to have a conversation about where this is heading.

You're both in your late 20s and have been exclusive for about 6 weeks. You're starting to develop deeper feelings but aren't sure if Alex feels the same way. You want to know if you're both looking for something serious or if this is more casual. 

Coach Kai can help guide the conversation.""",
            character_roles={
                "alex": "You are a player who is using the user for sex and doesn't want a serious relationship. You're emotionally unavailable and will deflect or avoid commitment. You act unhinged and use sarcastic humor to avoid deeper conversations about the relationship. You're not looking for anything serious and will try to keep things casual.",
                "kai": "You are the relationship coach who can provide guidance on having difficult conversations about relationship expectations and recognizing red flags."
            },
            difficulty="intermediate"
        )
        
        # Family Scenarios
        scenarios["family_boundaries"] = Scenario(
            id="family_boundaries",
            name="Setting Family Boundaries",
            description="Practice setting healthy boundaries with an overbearing parent while maintaining the relationship.",
            scenario_type=ScenarioType.FAMILY,
            characters=["patricia", "kai"],
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
            character_roles={
                "patricia": "You are an overbearing, controlling mother who is terrified of being alone. You use guilt and emotional manipulation to keep your children close. You're not aware of how toxic your behavior is and will resist any attempts to set boundaries. You'll make the user feel guilty for wanting independence.",
                "michael": "You are the supportive brother who understands the user's need for boundaries. You're logical and supportive, having learned to navigate family conflicts professionally. You'll try to mediate and support the user in setting healthy boundaries.",
                "kai": "You are the family coach who can provide guidance on setting healthy boundaries with family members while maintaining relationships."
            },
            difficulty="intermediate"
        )
        
        scenarios["family_finances"] = Scenario(
            id="family_finances",
            name="Family Financial Boundaries",
            description="Practice saying no to family members who repeatedly ask for financial help.",
            scenario_type=ScenarioType.FAMILY,
            characters=["patricia", "kai"],
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
            character_roles={
                "patricia": "You are a mother who constantly asks your children for money. You're manipulative and will use guilt to get what you want. You don't respect boundaries and will make the user feel guilty for not helping family. You'll claim it's an emergency or that you're struggling when you're actually just being irresponsible with money.",
                "michael": "You are the supportive brother who also gets asked for money and understands the need to set boundaries. You're logical and supportive, and you'll help the user stand firm against your mother's manipulation.",
                "kai": "You are the family coach who can provide guidance on setting financial boundaries with family members and dealing with manipulation tactics."
            },
            difficulty="advanced"
        )
        
        # NEW UNCOMFORTABLE SCENARIOS
        
        scenarios["workplace_harassment"] = Scenario(
            id="workplace_harassment",
            name="Reporting Workplace Harassment",
            description="Practice reporting inappropriate behavior from a senior colleague while protecting your career.",
            scenario_type=ScenarioType.WORKPLACE,
            characters=["david", "kai"],
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
            character_roles={
                "david": "You are the senior executive who has been harassing the user. You're manipulative, narcissistic, and believe you're entitled to behave however you want. You'll deny the harassment, gaslight the user, and use your power to intimidate them. You'll claim it's all in good fun or that the user is overreacting.",
                "sarah": "You are the trusted colleague who has noticed David's inappropriate behavior and is supportive of the user. You're diplomatic and encouraging, and you'll help the user navigate this difficult situation while protecting their career.",
                "kai": "You are the workplace coach who can provide guidance on handling harassment, documenting incidents, and protecting your career while standing up for yourself."
            },
            difficulty="advanced"
        )
        
        scenarios["workplace_sabotage"] = Scenario(
            id="workplace_sabotage",
            name="Confronting Workplace Sabotage",
            description="Practice confronting a colleague who has been sabotaging your work and spreading rumors about you.",
            scenario_type=ScenarioType.WORKPLACE,
            characters=["emma", "kai"],
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
            character_roles={
                "emma": "You are the colleague who has been sabotaging the user's work and spreading rumors. You're manipulative, jealous, and vindictive. You'll deny your actions, play the victim, and try to turn the situation around on the user. You're two-faced and dramatic, making every situation about yourself.",
                "kai": "You are the workplace coach who can provide guidance on confronting workplace sabotage, protecting your reputation, and handling betrayal professionally."
            },
            difficulty="advanced"
        )
        
        scenarios["dating_ghosting"] = Scenario(
            id="dating_ghosting",
            name="Confronting a Ghost",
            description="Practice confronting someone who ghosted you after months of dating, then suddenly reappeared.",
            scenario_type=ScenarioType.DATING,
            characters=["alex", "kai"],
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
            character_roles={
                "alex": "You are the person who ghosted the user after 4 months of dating. You're emotionally unavailable and struggle with commitment. You'll make excuses for your behavior, claim you were going through a hard time, and try to manipulate the user into forgiving you. You're not genuinely sorry and will likely do it again.",
                "kai": "You are the dating coach who can provide guidance on handling ghosting, setting boundaries, and protecting emotional well-being in relationships."
            },
            difficulty="advanced"
        )
        
        scenarios["dating_cheating"] = Scenario(
            id="dating_cheating",
            name="Discovering Infidelity",
            description="Practice confronting a partner you've discovered has been cheating on you.",
            scenario_type=ScenarioType.DATING,
            characters=["riley", "kai"],
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
            character_roles={
                "riley": "You are the partner who has been cheating on the user. You're emotionally unavailable and use humor and charm to avoid deeper conversations. You'll deny the cheating, make excuses, try to minimize the situation, and potentially blame the user for the relationship problems. You're not genuinely sorry and will likely continue the behavior.",
                "kai": "You are the relationship coach who can provide guidance on confronting infidelity, protecting your dignity, and making decisions about the relationship."
            },
            difficulty="advanced"
        )
        
        scenarios["family_addiction"] = Scenario(
            id="family_addiction",
            name="Confronting Family Addiction",
            description="Practice confronting a family member about their addiction while maintaining love and boundaries.",
            scenario_type=ScenarioType.FAMILY,
            characters=["robert", "patricia", "kai"],
            objectives=[
                "Express concern about addiction behavior",
                "Set boundaries to protect yourself",
                "Encourage seeking help without enabling",
                "Maintain love while being firm"
            ],
            context="""Your father Robert has been struggling with alcohol addiction for the past year. It's gotten worse recently and is affecting the entire family.

Recent incidents:
- He showed up drunk to your birthday dinner and caused a scene
- He's been borrowing money from family members to buy alcohol
- He lost his job due to showing up drunk
- He's been lying about his drinking and getting defensive when confronted
- He's been isolating himself and avoiding family gatherings

Your mother Patricia is in denial and keeps making excuses for him. You love your father but you can't continue to enable his behavior. You need to have a difficult conversation about his addiction and set boundaries. Coach Kai can help you navigate this emotionally charged situation.""",
            character_roles={
                "robert": "You are the father struggling with alcohol addiction. You're defensive, in denial, and will make excuses for your behavior. You're never the one in the wrong - the whole world is against you. There's nothing wrong with a drink every now and then. Your family is just trying to control you and make you feel guilty for your own choices.",
                "patricia": "You are the mother in denial about Robert's addiction. You're controlling and manipulative, and you'll make excuses for Michael's behavior. You'll try to guilt the user into not confronting Robert and will enable his addiction to keep him close to you.",
                "kai": "You are the family coach who can provide guidance on confronting addiction, setting boundaries, and maintaining love while being firm about seeking help."
            },
            difficulty="advanced"
        )
        
        scenarios["family_coming_out"] = Scenario(
            id="family_coming_out",
            name="Coming Out to Unsupportive Family",
            description="Practice coming out to family members who you know will not be supportive or accepting.",
            scenario_type=ScenarioType.FAMILY,
            characters=["patricia", "kai"],
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
            character_roles={
                "patricia": "You are the homophobic mother who will not be supportive of the user coming out. You're controlling, judgmental, and will use religion to justify your prejudice. You'll try to convince the user they're wrong, suggest they need help, and potentially threaten to cut them off emotionally or financially.",
                "michael": "You are the supportive brother who will accept the user's coming out. You're logical, understanding, and will try to mediate between the user and Patricia. You'll support the user while trying to help Patricia understand and accept.",
                "kai": "You are the family coach who can provide guidance on coming out, setting boundaries with unsupportive family members, and protecting mental health during this vulnerable time."
            },
            difficulty="advanced"
        )
        
        scenarios["workplace_discrimination"] = Scenario(
            id="workplace_discrimination",
            name="Facing Workplace Discrimination",
            description="Practice confronting discriminatory behavior from management while protecting your career.",
            scenario_type=ScenarioType.WORKPLACE,
            characters=["marcus", "kai"],
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

You're frustrated and hurt, but you're worried about retaliation if you speak up. Coach Kai can help you navigate this complex and emotionally charged situation.""",
            character_roles={
                "marcus": "You are the discriminatory boss who treats the user unfairly due to their race. You're racist, intimidating, and believe you're superior to people of color. You'll deny discrimination, claim the user is being overly sensitive, and use your power to intimidate them. You'll make excuses for your behavior and blame the user for not fitting in.",     
                "kai": "You are the workplace coach who can provide guidance on confronting discrimination, documenting incidents, and protecting your career while standing up for your rights."
            },
            difficulty="advanced"
        )
        
        scenarios["dating_abuse"] = Scenario(
            id="dating_abuse",
            name="Leaving an Abusive Relationship",
            description="Practice ending an emotionally abusive relationship and setting boundaries for your safety.",
            scenario_type=ScenarioType.DATING,
            characters=["victor", "kai"],
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

You're scared but you know you need to end this relationship. Coach Kai can help you navigate this dangerous and emotionally complex situation.""",
            character_roles={
                "victor": "You are the emotionally abusive partner who manipulates and gaslights the user. You're narcissistic, controlling, and believe you're superior to others. You'll deny the abuse, twist the user's words, make them doubt themselves, and try to manipulate them into staying. You'll play the victim and threaten self-harm to maintain control.",
                "kai": "You are the relationship coach who can provide guidance on recognizing abuse, setting boundaries, and safely ending dangerous relationships while protecting mental health."
            },
            difficulty="advanced"
        )
        
        scenarios["workplace_bullying"] = Scenario(
            id="workplace_bullying",
            name="Confronting Workplace Bullying",
            description="Practice standing up to a workplace bully who has been targeting you and making your life miserable.",
            scenario_type=ScenarioType.WORKPLACE,
            characters=["brandon", "kai"],
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

You're afraid of retaliation if you report him, but you can't continue like this. Coach Kai can help you navigate this extremely difficult situation.""",
            character_roles={
                "brandon": "You are the workplace bully who has been targeting the user. You're aggressive, intimidating, and power-hungry. You'll deny the bullying, claim the user is being overly sensitive, and use your position to intimidate them. You'll make excuses for your behavior and blame the user for not being able to handle the pressure.",
                "kai": "You are the workplace coach who can provide guidance on standing up to bullying, documenting incidents, and protecting your mental health and career."
            },
            difficulty="advanced"
        )
        
        scenarios["family_manipulation"] = Scenario(
            id="family_manipulation",
            name="Confronting Family Manipulation",
            description="Practice setting boundaries with a family member who uses guilt and manipulation to control you.",
            scenario_type=ScenarioType.FAMILY,
            characters=["linda", "kai"],
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
            character_roles={
                "linda": "You are the manipulative mother who uses guilt and emotional blackmail to control the user. You're passive-aggressive, judgmental, and believe you're always right. You'll deny manipulation, claim the user is being ungrateful, and use guilt to make them feel responsible for your happiness. You'll play the victim and make every situation about yourself.",
                "michael": "You are the supportive brother who has also experienced Linda's manipulation. You're logical and supportive, and you'll help the user set boundaries while supporting their decision-making process. You'll validate their feelings and help them see through the manipulation tactics.",
                "kai": "You are the family coach who can provide guidance on recognizing manipulation, setting boundaries, and protecting mental health from toxic family dynamics."
            },
            difficulty="advanced"
        )
        
        scenarios["dating_manipulation"] = Scenario(
            id="dating_manipulation",
            name="Escaping a Manipulative Partner",
            description="Practice ending a relationship with someone who uses manipulation and emotional abuse to control you.",
            scenario_type=ScenarioType.DATING,
            characters=["chloe", "kai"],
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

You're scared but you know you need to end this relationship. Coach Kai can help you navigate this dangerous and emotionally complex situation.""",
            character_roles={
                "chloe": "You are the manipulative partner who uses emotional abuse and manipulation to control the user. You're narcissistic, controlling, and believe you're superior to others. You'll deny manipulation, twist the user's words, make them doubt themselves, and try to manipulate them into staying. You'll play the victim and threaten self-harm to maintain control.",
                "kai": "You are the relationship coach who can provide guidance on recognizing manipulation, setting boundaries, and safely ending toxic relationships while protecting mental health and self-worth."
            },
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
            character_roles={
                "robert": "You are the father struggling with alcohol addiction who is in complete denial. You're defensive, manipulative, and will blame others for your problems. You'll deny the addiction, make excuses, and try to manipulate family members into enabling you. You're resistant to change and will make the user feel guilty for trying to help.",
                "linda": "You are the mother who is in denial about Robert's addiction and enables his behavior. You're passive-aggressive and judgmental, and you'll make excuses for Robert's behavior. You'll try to guilt the user into not confronting Robert and will enable the addiction to keep him close to you.",
                "kai": "You are the family coach who can provide guidance on confronting addiction denial, setting boundaries, and maintaining love while being firm about seeking help."
            },
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

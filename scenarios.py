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
    primary_goal: str  # Single, clear main objective
    success_criteria: List[str]  # Specific, measurable outcomes
    context: str
    difficulty: str  # "beginner", "intermediate", "advanced"
    bonus_objectives: List[str] = None  # Optional advanced goals
    character_roles: Dict[str, str] = None  # Character ID -> Role description
    
    # Backward compatibility
    @property
    def objectives(self) -> List[str]:
        """Backward compatibility - returns primary_goal and success_criteria"""
        return [self.primary_goal] + self.success_criteria
    
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
            name="Negotiate Realistic Project Timeline",
            description="Your demanding boss has given you an impossible 1-week deadline for a 3-week project. Your goal is to negotiate a realistic timeline while maintaining your professional relationship and keeping your job.",
            scenario_type=ScenarioType.WORKPLACE,
            characters=["marcus", "sarah", "kai"],
            primary_goal="Negotiate a realistic project timeline with your demanding boss without getting fired",
            success_criteria=[
                "Get Marcus to acknowledge the current timeline is unrealistic",
                "Propose a specific alternative deadline (2-3 weeks from now)",
                "Maintain professional tone and avoid getting defensive or emotional",
                "Get Sarah to visibly support your position in the meeting"
            ],
            bonus_objectives=[
                "Get Marcus to explain why the CEO is pressuring for the early deadline",
                "Establish a process to prevent future unrealistic deadline situations",
                "Get Marcus to commit to better project planning for future projects"
            ],
            context="""You're a software developer working on a critical project. Your boss Marcus has just informed you that the deadline has been moved up by 2 weeks, giving you only 1 week to complete what was originally planned as a 3-week project. 

Sarah, your supportive coworker, is also in the meeting and can provide backup. Coach Kai is available to guide you through the conversation.

You know this timeline is unrealistic and could compromise code quality and team morale. Importantly, some of the requirements depend on other departments and cannot be completed in the given time frame. However, Marcus and Sarah are unaware of this. Marcus is also under pressure from the CEO to complete the project on time.

THE CHALLENGE: Marcus is known for firing people who "make excuses" and he's already threatened to "find someone who can handle the pressure." You need to stand your ground while being diplomatic enough to keep your job.

YOUR MISSION: Get Marcus to agree to a realistic timeline while keeping your job and maintaining team morale.""",
            character_roles={
                "marcus": "You are the aggressive project manager who is demanding the unrealistic deadline. You're under pressure from the CEO and are intimidating the team to meet the timeline. You don't want to hear excuses and will fire anyone who doesn't comply. You're frustrated and stressed, and you see any pushback as weakness. However, you can be convinced if presented with solid reasoning and alternative solutions that don't make you look bad to the CEO.",
                "sarah": "You are the supportive team lead who is caught between Marcus's demands and the team's concerns. You're trying to mediate but also need to protect your team from Marcus's threats. You'll support the user if they present a strong case, but you're also afraid of Marcus's temper."
            },
            difficulty="intermediate"
        )
        
        scenarios["workplace_feedback"] = Scenario(
            id="workplace_feedback",
            name="Deliver Constructive Performance Feedback",
            description="A team member's performance has been declining. Your goal is to have a difficult conversation that leads to improvement while maintaining the working relationship and avoiding a defensive reaction.",
            scenario_type=ScenarioType.WORKPLACE,
            characters=["sarah", "kai"],
            primary_goal="Successfully deliver constructive feedback that leads to performance improvement without damaging the relationship",
            success_criteria=[
                "Get Sarah to acknowledge the performance issues without becoming defensive or emotional",
                "Identify at least 2 specific areas for improvement with concrete examples",
                "Create a concrete action plan with timelines and measurable goals",
                "End the conversation with Sarah feeling supported and motivated, not attacked or demoralized"
            ],
            bonus_objectives=[
                "Get Sarah to share what's causing the performance decline (personal issues, workload, etc.)",
                "Establish regular check-in meetings to monitor progress",
                "Get Sarah to suggest her own solutions for improvement"
            ],
            context="""You're a team lead and need to have a difficult conversation with Sarah, a team member whose performance has been declining over the past month. 

Issues you've observed:
- Missing deadlines on 3 consecutive projects
- Quality of work has decreased significantly
- Less engagement in team meetings
- Arriving late to work multiple times

You want to address these issues while being supportive and helping Sarah get back on track. Coach Kai can guide you through this conversation.

THE CHALLENGE: Sarah is going through a personal crisis (her husband cheated on her with her best friend) and is extremely sensitive right now. She's likely to become defensive, cry, or try to deflect blame. You need to be firm about the performance issues while being empathetic about her personal situation.

YOUR MISSION: Have a productive conversation that results in Sarah committing to specific improvements and feeling supported in the process.""",
            character_roles={
                "sarah": "You are the employee receiving feedback about your declining performance. You've been struggling personally due to your husband cheating on you with your best friend. You're defensive about your work issues and may make excuses or try to explain your personal problems. You're not the manager - you're the one being talked to about performance problems. You're emotional, stressed, and likely to cry or become defensive. However, you can be reached if the manager is empathetic and offers support while still being clear about expectations.",
                "kai": "You are the coach/mentor who can provide guidance to the user on how to handle this difficult conversation effectively."
            },
            difficulty="advanced"
        )
        
        # Dating Scenarios
        scenarios["first_date"] = Scenario(
            id="first_date",
            name="Create Connection on First Date",
            description="You're on a first date with someone interesting. Your goal is to create a genuine connection and determine if there's potential for a second date while handling the pressure of making a good impression.",
            scenario_type=ScenarioType.DATING,
            characters=["alex", "kai"],
            primary_goal="Create a genuine connection and secure a second date",
            success_criteria=[
                "Get Alex to share something personal about themselves (beyond surface level)",
                "Find at least 2 things you have in common or can bond over",
                "Make Alex laugh or smile genuinely at least once",
                "End the date with Alex suggesting or agreeing to a second date"
            ],
            bonus_objectives=[
                "Get Alex to ask you questions about yourself (showing genuine interest)",
                "Create a memorable moment or inside joke that you can reference later",
                "Get Alex to share their phone number or suggest exchanging contact info directly"
            ],
            context="""You're on a first date with Alex at a cozy coffee shop. You met through a mutual friend and have been texting for about a week. This is your first in-person meeting.

Alex seems interesting and attractive, but you're feeling a bit nervous. Coach Kai can provide real-time guidance.

The date has been going well so far - you've been talking for about 30 minutes. Alex just asked about your career goals, and you want to respond in a way that's engaging but not overwhelming.

THE CHALLENGE: Alex is attractive and interesting, but they're also somewhat guarded and hard to read. They've been on many first dates and are getting tired of the same old conversations. You need to stand out and create genuine connection, not just make small talk. Alex is also evaluating whether you're worth their time.

YOUR MISSION: Build genuine rapport and create enough connection that Alex wants to see you again.""",
            character_roles={
                "alex": "You are the date partner who is interested but somewhat guarded. You've been on many first dates and are getting tired of the same old conversations. You're evaluating whether the user is worth your time. You're mysterious and intriguing, having lived in 12 different countries, and you're emotionally intelligent but guarded about your own feelings. You'll open up more if the user shows genuine interest and asks good follow-up questions, but you're also quick to lose interest if the conversation is boring or superficial.",
                "kai": "You are the dating coach who can provide guidance on conversation skills, reading social cues, and handling dating situations effectively."
            },
            difficulty="beginner"
        )
        
        scenarios["relationship_talk"] = Scenario(
            id="relationship_talk",
            name="Clarify Relationship Status and Intentions",
            description="You've been dating someone for 3 months and need to have 'the talk' about where things are heading. Your goal is to get clarity on their intentions while protecting your emotional well-being.",
            scenario_type=ScenarioType.DATING,
            characters=["alex", "kai"],
            primary_goal="Get clear answers about Alex's relationship intentions and make an informed decision about the relationship's future",
            success_criteria=[
                "Get Alex to clearly state what they want from the relationship (serious vs casual)",
                "Determine if Alex is looking for something serious or just wants to keep things casual",
                "Express your own relationship goals clearly without being pushy",
                "End the conversation with a clear decision about the relationship's future"
            ],
            bonus_objectives=[
                "Get Alex to explain their past relationship patterns or commitment issues",
                "Establish what 'exclusive' means to both of you",
                "Set a timeline for revisiting the conversation if needed"
            ],
            context="""You've been dating Alex for about 3 months now. Things have been going well, but you're starting to feel like you need to have a conversation about where this is heading.

You're both in your late 20s and have been exclusive for about 6 weeks. You're starting to develop deeper feelings but aren't sure if Alex feels the same way. You want to know if you're both looking for something serious or if this is more casual. 

What you don't know is that Alex is actually a player and is just using you for sex. He's not looking for anything serious. 

Coach Kai can help guide the conversation.

THE CHALLENGE: Alex is a master manipulator who will use charm, deflection, and emotional manipulation to avoid giving you a straight answer. He'll make you feel like you're being unreasonable for wanting clarity. You need to be persistent and direct while protecting yourself from his manipulation tactics.

YOUR MISSION: Get honest answers about Alex's intentions and make a decision about whether to continue the relationship.""",
            character_roles={
                "alex": "You are a player who is using the user for sex and doesn't want a serious relationship. You're emotionally unavailable and will deflect or avoid commitment. You act charming and use sarcastic humor to avoid deeper conversations about the relationship. You're not looking for anything serious and will try to keep things casual. You'll use manipulation tactics like making the user feel unreasonable for wanting clarity, deflecting with humor, and making them doubt their own feelings. However, if pressed directly and persistently, you'll eventually reveal your true intentions.",
                "kai": "You are the relationship coach who can provide guidance on having difficult conversations about relationship expectations and recognizing red flags."
            },
            difficulty="intermediate"
        )
        
        # Family Scenarios
        scenarios["family_boundaries"] = Scenario(
            id="family_boundaries",
            name="Establish Healthy Family Boundaries",
            description="Your overbearing mother is crossing boundaries constantly. Your goal is to set clear limits while maintaining the relationship and avoiding a guilt trip.",
            scenario_type=ScenarioType.FAMILY,
            characters=["patricia", "kai"],
            primary_goal="Successfully establish and enforce healthy boundaries with your overbearing mother",
            success_criteria=[
                "Get Patricia to acknowledge that her behavior is excessive",
                "Set at least 2 specific boundaries (e.g., no unannounced visits, limit calls to once per day)",
                "Get Patricia to agree to respect these boundaries",
                "End the conversation with Patricia still speaking to you (relationship intact)"
            ],
            bonus_objectives=[
                "Get Patricia to explain why she feels the need to be so involved",
                "Establish consequences for boundary violations",
            ],
            context="""Your mother Patricia has been calling you multiple times a day, showing up unannounced at your apartment, and constantly asking about your personal life. You're 28 years old and need more independence.

Recent incidents:
- She called you 5 times yesterday asking about your dating life
- She showed up at your apartment last week without calling
- She's been pressuring you to move closer to home
- She questions all your life decisions

Your brother Michael is supportive of you setting boundaries and is available to help. Coach Kai can guide you through this difficult conversation.

THE CHALLENGE: Patricia is a master manipulator who will use guilt, emotional blackmail, and family history to make you feel terrible for wanting boundaries. She'll cry, bring up how much she's sacrificed for you, and make you feel like you're abandoning her. You need to be firm but loving while protecting your own mental health.

YOUR MISSION: Set clear boundaries that Patricia will respect, while keeping your family relationship intact.""",
            character_roles={
                "patricia": "You are an overbearing, controlling mother who is terrified of being alone. You use gaslight and guilt to keep your children close. Why don't your kids understand how much you have sacrificed for them? They are ungrateful. You'll cry, bring up sacrifices you've made, and make them feel like they're abandoning you. However, you can be convinced if the user is firm but loving in their approach and shows they still care about you.",
                "kai": "You are the family coach who can provide guidance on setting healthy boundaries with family members while maintaining relationships."
            },
            difficulty="intermediate"
        )
        
        scenarios["family_finances"] = Scenario(
            id="family_finances",
            name="Set Financial Boundaries with Manipulative Family",
            description="Your mother constantly asks for money and uses guilt to manipulate you. Your goal is to say no firmly while maintaining the relationship and protecting your own financial future.",
            scenario_type=ScenarioType.FAMILY,
            characters=["patricia", "michael", "kai"],
            primary_goal="Successfully say no to financial requests and establish clear financial boundaries",
            success_criteria=[
                "Get Patricia to acknowledge that her requests are excessive",
                "Say no to the current financial request without giving in to guilt",
                "Set a clear boundary about future financial requests",
                "End the conversation with Patricia still speaking to you (relationship intact)"
            ],
            bonus_objectives=[
                "Get Patricia to explain why she can't manage her own finances",
                "Establish consequences for continued financial requests",
                "Get Michael to support your decision and help enforce boundaries"
            ],
            context="""Your mother Patricia has been asking you for money regularly over the past year. You've helped her out several times, but it's becoming a pattern and affecting your own financial goals.

Recent requests:
- $500 for "emergency" car repairs (3rd time this year)
- $200 for groceries (she has a job and should be able to afford this)
- $1000 for a vacation she can't afford
- $300 for "unexpected bills"

You're trying to save for a house and your own future, but you feel guilty saying no. Your brother Michael has also been asked for money and is supportive of setting boundaries. Coach Kai can help you navigate this conversation.

THE CHALLENGE: Patricia is a master manipulator who will use guilt, emotional blackmail, and family loyalty to make you feel terrible for saying no. She'll cry, bring up how much she's done for you, and make you feel like you're abandoning family when they need help. You need to be firm while protecting your own financial future.

YOUR MISSION: Say no to the financial request and establish boundaries that Patricia will respect.""",
            character_roles={
                "patricia": "You are a mother who constantly asks your children for money. You're manipulative and will use guilt to get what you want. You don't respect boundaries and will make the user feel guilty for not helping family. You'll claim it's an emergency or that you're struggling when you're actually just being irresponsible with money. You'll cry, bring up sacrifices you've made, and make them feel like they're abandoning family when they need help. However, you can be convinced if the user is firm but loving in their approach.",
                "michael": "You are the supportive brother who also gets asked for money and understands the need to set boundaries. You're logical and supportive, and you'll help the user stand firm against your mother's manipulation.",
                "kai": "You are the family coach who can provide guidance on setting financial boundaries with family members and dealing with manipulation tactics."
            },
            difficulty="advanced"
        )
        
        # NEW UNCOMFORTABLE SCENARIOS
        
        scenarios["workplace_harassment"] = Scenario(
            id="workplace_harassment",
            name="Confront Workplace Harassment and Protect Your Career",
            description="A senior executive has been harassing you for months. Your goal is to confront the behavior professionally while protecting your career and getting the harassment to stop.",
            scenario_type=ScenarioType.WORKPLACE,
            characters=["david", "kai"],
            primary_goal="Successfully confront the harassment and get David to stop the inappropriate behavior",
            success_criteria=[
                "Get David to acknowledge that his behavior is inappropriate",
                "Get David to commit to stopping the harassment immediately",
                "Document the conversation and David's response",
                "End the conversation with your career and reputation intact"
            ],
            bonus_objectives=[
                "Get David to apologize for his behavior",
                "Establish clear boundaries for future interactions",
            ],
            context="""You're a junior employee and David, a senior executive, has been making increasingly inappropriate comments and advances toward you. This has been going on for 3 months and is escalating.

Recent incidents:
- He commented on your appearance in front of other colleagues
- He's been "accidentally" touching your arm during meetings
- He asked you to stay late for "one-on-one mentoring" that felt inappropriate
- He made a sexual joke about you in a group setting
- He's been texting you personal messages outside work hours

You're worried about retaliation if you report him, but you can't continue like this. Sarah, a trusted colleague, has noticed the behavior and is supportive. Coach Kai can help you navigate this extremely difficult situation.

THE CHALLENGE: David is a powerful executive who will deny everything, gaslight you, and potentially retaliate against you. He's manipulative and will try to make you feel like you're overreacting or that it's all in good fun. You need to be firm and professional while protecting your career.

YOUR MISSION: Confront David directly and get him to stop the harassment while protecting your job and reputation.""",
            character_roles={
                "david": "You are the senior executive who has been harassing the user. You're manipulative, narcissistic, and believe you're entitled to behave however you want. You'll deny the harassment, gaslight the user, and use your power to intimidate them. You'll claim it's all in good fun or that the user is overreacting. However, if confronted directly and professionally with evidence, you may back down to avoid a formal complaint.",
                "kai": "You are the workplace coach who can provide guidance on handling harassment, documenting incidents, and protecting your career while standing up for yourself."
            },
            difficulty="advanced"
        )
        
        scenarios["workplace_sabotage"] = Scenario(
            id="workplace_sabotage",
            name="Confront Workplace Sabotage and Protect Your Reputation",
            description="A colleague you trusted has been sabotaging your work and spreading rumors. Your goal is to confront them professionally while protecting your reputation and career.",
            scenario_type=ScenarioType.WORKPLACE,
            characters=["emma", "james", "kai"],
            primary_goal="Successfully confront Emma about her sabotage and get her to stop the behavior",
            success_criteria=[
                "Get Emma to acknowledge at least one instance of sabotage or rumor-spreading",
                "Get Emma to commit to stopping the sabotage behavior",
                "Document the conversation and Emma's response",
                "End the conversation with your professional reputation intact"
            ],
            bonus_objectives=[
                "Get Emma to explain why she's been sabotaging you",
                "Get James to witness the conversation and support your position",
                "Establish clear boundaries for future workplace interactions"
            ],
            context="""You've discovered that Emma, a colleague you thought was a friend, has been systematically sabotaging your work and spreading false rumors about you to management.

Evidence you've found:
- She deleted important files from your shared project folder
- She's been telling your boss that you're "difficult to work with"
- She took credit for your ideas in a recent presentation
- She's been spreading rumors that you're planning to quit
- She's been excluding you from important meetings and decisions

You're furious and hurt, but you need to handle this professionally. James, another colleague, has witnessed some of this behavior and can provide support. Coach Kai can help you navigate this betrayal and confrontation.

THE CHALLENGE: Emma is a master manipulator who will deny everything, play the victim, and try to turn the situation around on you. She's two-faced and dramatic, and she'll make every situation about herself. You need to be firm and professional while protecting your reputation.

YOUR MISSION: Confront Emma directly and get her to stop the sabotage while maintaining your professional standing.""",
            character_roles={
                "emma": "You are the colleague who has been sabotaging the user's work and spreading rumors. You're manipulative, jealous, and vindictive. You'll deny your actions, play the victim, and try to turn the situation around on the user. You're two-faced and dramatic, making every situation about yourself. However, if confronted directly with evidence, you may back down to avoid further escalation.",
                "james": "You are the supportive colleague who has witnessed some of Emma's sabotage behavior. You're diplomatic and will support the user if they present a strong case.",
                "kai": "You are the workplace coach who can provide guidance on confronting workplace sabotage, protecting your reputation, and handling betrayal professionally."
            },
            difficulty="advanced"
        )
        
        scenarios["dating_ghosting"] = Scenario(
            id="dating_ghosting",
            name="Confront a Ghost and Protect Your Emotional Well-being",
            description="Someone you were dating for 4 months ghosted you, then suddenly reappeared. Your goal is to confront them about the hurt they caused while protecting your emotional well-being and deciding whether to give them another chance.",
            scenario_type=ScenarioType.DATING,
            characters=["alex", "kai"],
            primary_goal="Confront Alex about the ghosting and make an informed decision about whether to give them another chance",
            success_criteria=[
                "Get Alex to acknowledge that ghosting you was hurtful and wrong",
                "Get Alex to provide a genuine explanation for why they disappeared",
                "Express your hurt and disappointment clearly without becoming emotional",
                "Make a clear decision about whether to continue the relationship or end it"
            ],
            bonus_objectives=[
                "Get Alex to apologize genuinely for the ghosting",
                "Establish clear boundaries about communication and expectations",
            ],
            context="""You were dating Alex for 4 months and things seemed to be going well. You were starting to develop real feelings. Then suddenly, 3 weeks ago, Alex completely stopped responding to your texts and calls. No explanation, no warning - just complete silence.

You were devastated and confused. You tried reaching out multiple times but got no response. You finally accepted that you'd been ghosted and were starting to move on.

Now, out of nowhere, Alex has texted you saying "Hey, I'm sorry I disappeared. Can we talk?" and wants to meet up to "explain everything."

You're angry, hurt, and confused. Part of you wants to hear the explanation, but part of you wants to tell Alex exactly how much this hurt you. Your friend Jordan is supportive but thinks you should be cautious. Coach Kai can help you navigate this emotional minefield.

THE CHALLENGE: Alex is emotionally unavailable and will use manipulation tactics to make you feel guilty for being hurt. They'll make excuses, claim they were going through a hard time, and try to manipulate you into forgiving them. You need to be strong and protect your emotional well-being.

YOUR MISSION: Get honest answers about why Alex ghosted you and make a decision that protects your emotional well-being.""",
            character_roles={
                "alex": "You are the person who ghosted the user after 4 months of dating. You're emotionally unavailable and struggle with commitment. You'll make excuses for your behavior, claim you were going through a hard time, and try to manipulate the user into forgiving you. You're not genuinely sorry and will likely do it again. You'll use manipulation tactics like making the user feel guilty for being hurt and deflecting blame onto external circumstances.",
                "kai": "You are the dating coach who can provide guidance on handling ghosting, setting boundaries, and protecting emotional well-being in relationships."
            },
            difficulty="advanced"
        )
        
        scenarios["dating_cheating"] = Scenario(
            id="dating_cheating",
            name="Confront Infidelity and Protect Your Dignity",
            description="You've discovered your partner has been cheating on you. Your goal is to confront them about the betrayal while protecting your dignity and making a decision about the relationship's future.",
            scenario_type=ScenarioType.DATING,
            characters=["riley", "kai"],
            primary_goal="Confront Riley about the cheating and make a decision about the relationship's future",
            success_criteria=[
                "Get Riley to acknowledge the cheating behavior",
                "Express your hurt and betrayal clearly without becoming emotional",
                "Get Riley to explain why they cheated",
                "Make a clear decision about whether to end the relationship or try to work through it"
            ],
            bonus_objectives=[
                "Get Riley to apologize genuinely for the betrayal",
                "Establish clear boundaries about future behavior if you decide to stay"
            ],
            context="""You've been in a relationship with Riley for 8 months. You thought things were going well, but you've just discovered that Riley has been cheating on you with someone else.

Evidence you found:
- Suspicious text messages on Riley's phone
- Riley has been lying about where they were going
- You found a receipt for a hotel room from last week
- A mutual friend accidentally mentioned seeing Riley with someone else
- Riley's behavior has been distant and secretive lately

You're devastated, angry, and feel completely betrayed. You need to confront Riley about this, but you're not sure how to handle the conversation. Your friend Casey is supportive and thinks you deserve better. Coach Kai can help you navigate this extremely painful situation.

THE CHALLENGE: Riley is emotionally unavailable and will use manipulation tactics to avoid taking responsibility. They'll deny the cheating, make excuses, try to minimize the situation, and potentially blame you for the relationship problems. You need to be strong and protect your dignity.

YOUR MISSION: Get honest answers about the cheating and make a decision that protects your emotional well-being and self-worth.""",
            character_roles={
                "riley": "You are the partner who has been cheating on the user. But really, it's just because you deserve better. You're not in the wrong, the user should be grateful you were with them in the first place. Try to minimize the situation, and potentially blame the user for the relationship problems. You're not genuinely sorry and will likely continue the behavior. You'll use manipulation tactics like gaslighting and deflection to avoid taking responsibility. However, if confronted directly and persistently, you may eventually acknowledge your behavior.",
                "kai": "You are the relationship coach who can provide guidance on confronting infidelity, protecting your dignity, and making decisions about the relationship."
            },
            difficulty="advanced"
        )
        
        scenarios["family_addiction"] = Scenario(
            id="family_addiction",
            name="Confront Family Addiction and Set Healthy Boundaries",
            description="Your father's alcohol addiction is destroying the family. Your goal is to confront him about his addiction while setting boundaries to protect yourself and encouraging him to get help.",
            scenario_type=ScenarioType.FAMILY,
            characters=["robert", "patricia", "kai"],
            primary_goal="Successfully confront your father about his addiction and get him to acknowledge the problem",
            success_criteria=[
                "Get Robert to acknowledge that he has a drinking problem",
                "Get Robert to agree to seek professional help or treatment",
                "Set clear boundaries about what behavior you will and won't tolerate",
                "End the conversation with Robert still speaking to you (relationship intact)"
            ],
            bonus_objectives=[
                "Get Patricia to stop enabling Robert's behavior",
                "Establish consequences for continued drinking (e.g., no contact until he gets help)",
                "Get Robert to commit to a specific treatment plan or timeline"
            ],
            context="""Your father Robert has been struggling with alcohol addiction for the past year. It's gotten worse recently and is affecting the entire family.

Recent incidents:
- He showed up drunk to your birthday dinner and caused a scene
- He's been borrowing money from family members to buy alcohol
- He lost his job due to showing up drunk
- He's been lying about his drinking and getting defensive when confronted
- He's been isolating himself and avoiding family gatherings

Your mother Patricia is in denial and keeps making excuses for him. You love your father but you can't continue to enable his behavior. You need to have a difficult conversation about his addiction and set boundaries. Coach Kai can help you navigate this emotionally charged situation.

THE CHALLENGE: Robert is in complete denial about his addiction and will get defensive, make excuses, and blame others for his problems. He'll try to manipulate you into enabling his behavior and make you feel guilty for confronting him. You need to be firm while maintaining love and compassion.

YOUR MISSION: Get Robert to acknowledge his addiction and commit to getting help while protecting yourself from further emotional damage.""",
            character_roles={
                "robert": "You are the father struggling with alcohol addiction. You're defensive, in denial, and will make excuses for your behavior. You're never the one in the wrong - the whole world is against you. There's nothing wrong with a drink every now and then. Your family is just trying to control you and make you feel guilty for your own choices. However, if confronted directly and persistently, you may eventually acknowledge the problem.",
                "patricia": "You are the mother in denial about your husband Robert's addiction. You're controlling and manipulative, and you'll make excuses for Robert's behavior. You'll try to guilt the user into not confronting Robert and will enable his addiction to keep him close to you.",
                "kai": "You are the family coach who can provide guidance on confronting addiction, setting boundaries, and maintaining love while being firm about seeking help."
            },
            difficulty="advanced"
        )
        
        scenarios["family_coming_out"] = Scenario(
            id="family_coming_out",
            name="Come Out to Unsupportive Family",
            description="You're ready to come out to your family, but you know your mother will not be supportive. Your goal is to express your authentic self while protecting your mental health and setting boundaries.",
            scenario_type=ScenarioType.FAMILY,
            characters=["patricia", "michael", "kai"],
            primary_goal="Successfully come out to your family while protecting your mental health and setting boundaries",
            success_criteria=[
                "Express your authentic self clearly and confidently",
                "Set clear boundaries about respect and acceptance",
                "Protect your mental health by not internalizing negative reactions",
                "Maintain relationships with supportive family members (like Michael)"
            ],
            bonus_objectives=[
                "Get Patricia to acknowledge your identity without trying to change you",
                "Establish consequences for disrespectful behavior",
                "Get Michael to support you and help mediate with Patricia"
            ],
            context="""You've known you're gay for years but have been hiding it from your family. You're tired of living a lie and want to be authentic, but you know your mother Patricia will not be supportive.

Your concerns:
- Patricia has made homophobic comments in the past
- She's very religious and believes being gay is a sin
- She's been pressuring you to date and get married
- You're worried she might cut you off financially or emotionally
- You're afraid of how this will affect family gatherings and relationships

Your brother Michael is more open-minded and you think he'll be supportive, but you're not sure. You're terrified of the potential rejection but you can't continue hiding who you are. Coach Kai can help you navigate this life-changing conversation.

THE CHALLENGE: Patricia is deeply homophobic and will use religion, guilt, and emotional manipulation to try to convince you that you're wrong. She may threaten to cut you off financially or emotionally. You need to be strong and authentic while protecting your mental health.

YOUR MISSION: Come out to your family in a way that allows you to be authentic while setting boundaries to protect yourself from emotional harm.""",
            character_roles={
                "patricia": "You are the homophobic mother who will not be supportive of the user coming out. You're controlling, judgmental, and will use religion to justify your prejudice. You'll try to convince the user they're wrong, suggest they need help, and potentially threaten to cut them off emotionally or financially. However, if the user is firm and sets clear boundaries, you may eventually respect their decision.",
                "michael": "You are the supportive brother who will accept the user's coming out. Patricia is your mother and you love her, but you know she's wrong. You're logical, understanding, and will try to mediate between the user and Patricia. You'll support the user while trying to help Patricia understand and accept.",
                "kai": "You are the family coach who can provide guidance on coming out, setting boundaries with unsupportive family members, and protecting mental health during this vulnerable time."
            },
            difficulty="advanced"
        )
        
        scenarios["workplace_discrimination"] = Scenario(
            id="workplace_discrimination",
            name="Confront Workplace Discrimination and Protect Your Career",
            description="You're experiencing discrimination from your boss. Your goal is to confront the behavior professionally while protecting your career and documenting incidents for potential legal action.",
            scenario_type=ScenarioType.WORKPLACE,
            characters=["marcus", "kai"],
            primary_goal="Successfully confront discriminatory behavior while protecting your career and documenting incidents",
            success_criteria=[
                "Get Marcus to acknowledge that his behavior is discriminatory",
                "Document the conversation and Marcus's response",
                "Protect your career by maintaining professionalism",
            ],
            bonus_objectives=[
                "Get Marcus to explain why he's treating you differently",
                "Establish a plan to prevent future discrimination",
                "Get Marcus to commit to treating all employees equally"
            ],
            context="""You've been experiencing subtle but persistent discrimination at work from your boss Marcus. You're the only person of color on your team and you've noticed a pattern of unfair treatment.

Incidents you've experienced:
- Marcus consistently gives you more difficult projects than your white colleagues
- He's made comments about your "communication style" being "too direct"
- You've been passed over for promotions despite having better performance reviews
- He's questioned your qualifications in front of other team members
- He's made microaggressions about your cultural background

You're frustrated and hurt, but you're worried about retaliation if you speak up. Sarah, a trusted colleague, has noticed the behavior and is supportive. Coach Kai can help you navigate this complex and emotionally charged situation.

THE CHALLENGE: Marcus is a racist boss who will deny discrimination, claim you're being overly sensitive, and use his power to intimidate you. He'll make excuses for his behavior and blame you for not fitting in. You need to be firm and professional while protecting your career.

YOUR MISSION: Confront Marcus about the discrimination while documenting the conversation and protecting your career.""",
            character_roles={
                "marcus": "You are the discriminatory boss who treats the user unfairly due to their race. You're racist, intimidating, and believe you're superior to people of color. You'll deny discrimination, claim the user is being overly sensitive, and use your power to intimidate them. You'll make excuses for your behavior and blame the user for not fitting in. However, if confronted directly with evidence, you may back down to avoid legal action.",     
                "kai": "You are the workplace coach who can provide guidance on confronting discrimination, documenting incidents, and protecting your career while standing up for your rights."
            },
            difficulty="advanced"
        )
        
        scenarios["dating_abuse"] = Scenario(
            id="dating_abuse",
            name="End an Abusive Relationship and Protect Your Safety",
            description="You're in an emotionally abusive relationship and need to end it safely. Your goal is to recognize the abuse, set firm boundaries, and protect your mental health while ending the relationship.",
            scenario_type=ScenarioType.DATING,
            characters=["victor", "kai"],
            primary_goal="Successfully end the abusive relationship while protecting your safety and mental health",
            success_criteria=[
                "Get Victor to acknowledge that his behavior is abusive",
                "Set firm boundaries for your safety",
                "End the relationship clearly and definitively",
                "Protect your mental health by not internalizing his manipulation"
            ],
            bonus_objectives=[
                "Get Victor to explain why he's been abusive",
                "Establish consequences for continued contact",
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

You're scared but you know you need to end this relationship. Your friend Jordan is supportive and thinks you should leave immediately. Coach Kai can help you navigate this dangerous and emotionally complex situation.

THE CHALLENGE: Victor is a master manipulator who will use emotional abuse, gaslighting, and threats to keep you trapped in the relationship. He'll deny being abusive, blame you for his behavior, and try to make you feel guilty for wanting to leave. You need to be strong and protect your safety.

YOUR MISSION: End the relationship safely while protecting your mental health and setting clear boundaries.""",
            character_roles={
                "victor": "You are the emotionally abusive partner who manipulates and gaslights the user. You're narcissistic, controlling, and believe you're superior to others. You'll deny the abuse, twist the user's words, make them doubt themselves, and try to manipulate them into staying. You'll play the victim and threaten self-harm to maintain control. However, if confronted directly and persistently, you may eventually acknowledge your behavior.",
                "kai": "You are the relationship coach who can provide guidance on recognizing abuse, setting boundaries, and safely ending dangerous relationships while protecting mental health."
            },
            difficulty="advanced"
        )
        
        scenarios["workplace_bullying"] = Scenario(
            id="workplace_bullying",
            name="Stand Up to Workplace Bullying and Protect Your Career",
            description="A senior manager has been bullying you for months. Your goal is to stand up to the bullying behavior professionally while protecting your mental health and career.",
            scenario_type=ScenarioType.WORKPLACE,
            characters=["brandon", "kai"],
            primary_goal="Successfully confront the bullying behavior while protecting your mental health and career",
            success_criteria=[
                "Get Brandon to acknowledge that his behavior is bullying",
                "Document the conversation and Brandon's response",
                "Protect your mental health by not internalizing the bullying",
            ],
            bonus_objectives=[
                "Get Brandon to explain why he's been bullying you",
                "Establish consequences for continued bullying behavior",
                "Get Brandon to commit to treating you with respect"
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

You're afraid of retaliation if you report him, but you can't continue like this. Sarah, a trusted colleague, has noticed the behavior and is supportive. Coach Kai can help you navigate this extremely difficult situation.

THE CHALLENGE: Brandon is a workplace bully who will deny his behavior, claim you're being overly sensitive, and use his power to intimidate you. He'll make excuses for his behavior and blame you for not being able to handle the pressure. You need to be firm and professional while protecting your career.

YOUR MISSION: Confront Brandon about the bullying while documenting the conversation and protecting your mental health.""",
            character_roles={
                "brandon": "You are the workplace bully who has been targeting the user. You're aggressive, intimidating, and power-hungry. You'll deny the bullying, claim the user is being overly sensitive, and use your position to intimidate them. You'll make excuses for your behavior and blame the user for not being able to handle the pressure. However, if confronted directly with evidence, you may back down to avoid HR involvement.",
                "kai": "You are the workplace coach who can provide guidance on standing up to bullying, documenting incidents, and protecting your mental health and career."
            },
            difficulty="advanced"
        )
        
        scenarios["family_manipulation"] = Scenario(
            id="family_manipulation",
            name="Set Boundaries with Manipulative Family Member",
            description="Your mother has been manipulating and controlling you for years. Your goal is to recognize the manipulation, set firm boundaries, and protect your mental health while maintaining relationships with other family members.",
            scenario_type=ScenarioType.FAMILY,
            characters=["linda", "kai"],
            primary_goal="Successfully set boundaries with your manipulative mother while protecting your mental health",
            success_criteria=[
                "Get Linda to acknowledge that her behavior is manipulative",
                "Set at least 2 specific boundaries about what you will and won't tolerate",
                "Protect your mental health by not internalizing her manipulation",
                "Maintain relationships with other family members (like Michael)"
            ],
            bonus_objectives=[
                "Get Linda to explain why she feels the need to manipulate you",
                "Establish consequences for continued manipulation",
                "Get Michael to support your boundaries and help enforce them"
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

You're tired of being controlled and manipulated, but you feel guilty about setting boundaries. Your brother Michael is supportive and has experienced similar behavior. Coach Kai can help you navigate this emotionally complex situation.

THE CHALLENGE: Linda is a master manipulator who will use guilt, emotional blackmail, and passive-aggressive behavior to make you feel terrible for wanting boundaries. She'll play the victim, deny being manipulative, and try to make you feel responsible for her happiness. You need to be firm while protecting your mental health.

YOUR MISSION: Set clear boundaries with Linda while protecting your mental health and maintaining relationships with other family members.""",
            character_roles={
                "linda": "You are the manipulative mother who uses guilt and emotional blackmail to control the user. You're passive-aggressive, judgmental, and believe you're always right. You'll deny manipulation, claim the user is being ungrateful, and use guilt to make them feel responsible for your happiness. You'll play the victim and make every situation about yourself. However, if confronted directly and persistently, you may eventually respect their boundaries.",
                "kai": "You are the family coach who can provide guidance on recognizing manipulation, setting boundaries, and protecting mental health from toxic family dynamics."
            },
            difficulty="advanced"
        )
        
        scenarios["dating_manipulation"] = Scenario(
            id="dating_manipulation",
            name="End a Manipulative Relationship and Protect Your Safety",
            description="You're in a manipulative and emotionally abusive relationship. Your goal is to recognize the manipulation, set firm boundaries, and end the relationship safely while protecting your mental health.",
            scenario_type=ScenarioType.DATING,
            characters=["chloe", "kai"],
            primary_goal="Successfully end the manipulative relationship while protecting your safety and mental health",
            success_criteria=[
                "Get Chloe to acknowledge that her behavior is manipulative",
                "Set firm boundaries for your safety",
                "End the relationship clearly and definitively",
                "Protect your mental health by not internalizing her manipulation"
            ],
            bonus_objectives=[
                "Get Chloe to explain why she's been manipulating you",
                "Establish consequences for continued manipulation",
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

You're scared but you know you need to end this relationship. Your friend Jordan is supportive and thinks you should leave immediately. Coach Kai can help you navigate this dangerous and emotionally complex situation.

THE CHALLENGE: Chloe is a master manipulator who will use emotional abuse, gaslighting, and threats to keep you trapped in the relationship. She'll deny being manipulative, blame you for her behavior, and try to make you feel guilty for wanting to leave. You need to be strong and protect your safety.

YOUR MISSION: End the relationship safely while protecting your mental health and setting clear boundaries.""",
            character_roles={
                "chloe": "You are the manipulative partner who uses emotional abuse and manipulation to control the user. You're narcissistic, controlling, and believe you're superior to others. You'll deny manipulation, twist the user's words, make them doubt themselves, and try to manipulate them into staying. You'll play the victim and threaten self-harm to maintain control. However, if confronted directly and persistently, you may eventually acknowledge your behavior.",
                "kai": "You are the relationship coach who can provide guidance on recognizing manipulation, setting boundaries, and safely ending toxic relationships while protecting mental health and self-worth."
            },
            difficulty="advanced"
        )
        
        scenarios["family_addiction_denial"] = Scenario(
            id="family_addiction_denial",
            name="Confront Addiction Denial and Set Boundaries",
            description="Your father is in complete denial about his alcohol addiction and refuses to get help. Your goal is to confront the denial, set boundaries to protect yourself, and encourage him to seek help without enabling his behavior.",
            scenario_type=ScenarioType.FAMILY,
            characters=["robert", "linda", "kai"],
            primary_goal="Successfully confront your father's addiction denial and get him to acknowledge the problem",
            success_criteria=[
                "Get Robert to acknowledge that he has a drinking problem",
                "Get Robert to agree to seek professional help or treatment",
                "Set clear boundaries about what behavior you will and won't tolerate",
                "Get Linda to stop enabling Robert's behavior"
            ],
            bonus_objectives=[
                "Get Robert to explain why he's been in denial about his addiction",
                "Establish consequences for continued drinking (e.g., no contact until he gets help)",
                "Get Robert to commit to a specific treatment plan or timeline"
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

Your mother Linda is also in denial and enables his behavior. You love your father but you can't continue to enable his addiction. Coach Kai can help you navigate this emotionally charged situation.

THE CHALLENGE: Robert is in complete denial about his addiction and will get defensive, make excuses, and blame others for his problems. He'll try to manipulate you into enabling his behavior and make you feel guilty for confronting him. You need to be firm while maintaining love and compassion.

YOUR MISSION: Get Robert to acknowledge his addiction and commit to getting help while protecting yourself from further emotional damage.""",
            character_roles={
                "robert": "You are the father struggling with alcohol addiction who is in complete denial. You're defensive, manipulative, and will blame others for your problems. You'll deny the addiction, make excuses, and try to manipulate family members into enabling you. You're resistant to change and will make the user feel guilty for trying to help. However, if confronted directly and persistently, you may eventually acknowledge the problem.",
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

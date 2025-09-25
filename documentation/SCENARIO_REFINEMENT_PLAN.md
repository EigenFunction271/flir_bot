# Scenario Refinement Plan - Clear Player Goals

## Overview

This document outlines improvements to make scenario objectives more specific, measurable, and actionable for players. The current objectives are somewhat vague - we need to create clear, concrete goals that players can work toward and measure their success against.

## Current Issues with Objectives

### Problems with Current Format:
- **Too vague**: "Address the unrealistic deadline professionally"
- **Multiple goals**: Each objective contains multiple sub-goals
- **No clear success criteria**: Hard to know when you've achieved the objective
- **No priority ranking**: All objectives seem equally important
- **No specific outcomes**: Don't specify what the player should accomplish

### Example of Current Objectives:
```python
objectives=[
    "Address the unrealistic deadline professionally",
    "Propose alternative solutions", 
    "Maintain professional boundaries",
    "Seek support from colleagues"
]
```

## Proposed Refinement Structure

### New Objective Format:
Each scenario should have:
1. **Primary Goal** (1 main objective to achieve)
2. **Success Criteria** (3-4 specific, measurable outcomes)
3. **Bonus Objectives** (Optional advanced goals for higher scores)

### Example Refined Structure:
```python
primary_goal="Negotiate a realistic project timeline with your demanding boss"
success_criteria=[
    "Get Marcus to acknowledge the timeline is unrealistic",
    "Propose a specific alternative deadline (2-3 weeks)",
    "Maintain professional tone throughout the conversation",
    "Get Sarah to support your position"
]
bonus_objectives=[
    "Get Marcus to explain the CEO's pressure (understanding the root cause)",
    "Establish a process to prevent future unrealistic deadlines"
]
```

## Refined Scenarios

### 1. Workplace Deadline Scenario

**Current**: "Unrealistic Deadline"
**Refined**: "Negotiate Realistic Project Timeline"

```python
scenarios["workplace_deadline"] = Scenario(
    id="workplace_deadline",
    name="Negotiate Realistic Project Timeline",
    description="Your demanding boss has given you an impossible 1-week deadline for a 3-week project. Your goal is to negotiate a realistic timeline while maintaining your professional relationship.",
    scenario_type=ScenarioType.WORKPLACE,
    characters=["marcus", "sarah", "kai"],
    primary_goal="Negotiate a realistic project timeline with your demanding boss",
    success_criteria=[
        "Get Marcus to acknowledge the current timeline is unrealistic",
        "Propose a specific alternative deadline (2-3 weeks from now)",
        "Maintain professional tone and avoid getting defensive",
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

YOUR MISSION: Get Marcus to agree to a realistic timeline while keeping your job and maintaining team morale.""",
    character_roles={
        "marcus": "You are the aggressive project manager who is demanding the unrealistic deadline. You're under pressure from the CEO and are intimidating the team to meet the timeline. You don't want to hear excuses and will fire anyone who doesn't comply. However, you can be convinced if presented with solid reasoning and alternative solutions.",
        "sarah": "You are the supportive team lead who is caught between Marcus's demands and the team's concerns. You're trying to mediate but also need to protect your team from Marcus's threats. You'll support the user if they present a strong case."
    },
    difficulty="intermediate"
)
```

### 2. Workplace Feedback Scenario

**Current**: "Giving Difficult Feedback"
**Refined**: "Deliver Constructive Performance Feedback"

```python
scenarios["workplace_feedback"] = Scenario(
    id="workplace_feedback",
    name="Deliver Constructive Performance Feedback",
    description="A team member's performance has been declining. Your goal is to have a difficult conversation that leads to improvement while maintaining the working relationship.",
    scenario_type=ScenarioType.WORKPLACE,
    characters=["sarah", "kai"],
    primary_goal="Successfully deliver constructive feedback that leads to performance improvement",
    success_criteria=[
        "Get Sarah to acknowledge the performance issues without becoming defensive",
        "Identify at least 2 specific areas for improvement",
        "Create a concrete action plan with timelines",
        "End the conversation with Sarah feeling supported, not attacked"
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

You want to address these issues while being supportive and helping Sarah get back on track. Coach Kai is available to guide you through this conversation.

YOUR MISSION: Have a productive conversation that results in Sarah committing to specific improvements and feeling supported in the process.""",
    character_roles={
        "sarah": "You are the employee receiving feedback about your declining performance. You've been struggling personally due to your husband cheating on you with your best friend. You're defensive about your work issues and may make excuses or try to explain your personal problems. You're not the manager - you're the one being talked to about performance problems. However, you can be reached if the manager is empathetic and offers support.",
        "kai": "You are the coach/mentor who can provide guidance to the user on how to handle this difficult conversation effectively."
    },
    difficulty="advanced"
)
```

### 3. First Date Scenario

**Current**: "First Date Conversation"
**Refined**: "Create Connection on First Date"

```python
scenarios["first_date"] = Scenario(
    id="first_date",
    name="Create Connection on First Date",
    description="You're on a first date with someone interesting. Your goal is to create a genuine connection and determine if there's potential for a second date.",
    scenario_type=ScenarioType.DATING,
    characters=["alex", "kai"],
    primary_goal="Create a genuine connection and secure a second date",
    success_criteria=[
        "Get Alex to share something personal about themselves",
        "Find at least 2 things you have in common",
        "Make Alex laugh or smile genuinely at least once",
        "End the date with Alex suggesting or agreeing to a second date"
    ],
    bonus_objectives=[
        "Get Alex to ask you questions about yourself (showing interest)",
        "Create a memorable moment or inside joke",
        "Get Alex to share their phone number or suggest exchanging contact info"
    ],
    context="""You're on a first date with Alex at a cozy coffee shop. You met through a mutual friend and have been texting for about a week. This is your first in-person meeting.

Alex seems interesting and attractive, but you're feeling a bit nervous. Coach Kai can provide real-time guidance.

The date has been going well so far - you've been talking for about 30 minutes. Alex just asked about your career goals, and you want to respond in a way that's engaging but not overwhelming.

YOUR MISSION: Build genuine rapport and create enough connection that Alex wants to see you again.""",
    character_roles={
        "alex": "You are the date partner who is interested and engaged. You're asking thoughtful questions and showing genuine interest in getting to know the user. You're mysterious and intriguing, having lived in 12 different countries, and you're emotionally intelligent but guarded about your own feelings. You'll open up more if the user shows genuine interest and asks good follow-up questions.",
        "kai": "You are the dating coach who can provide guidance on conversation skills, reading social cues, and handling dating situations effectively."
    },
    difficulty="beginner"
)
```

### 4. Family Boundaries Scenario

**Current**: "Setting Family Boundaries"
**Refined**: "Establish Healthy Family Boundaries"

```python
scenarios["family_boundaries"] = Scenario(
    id="family_boundaries",
    name="Establish Healthy Family Boundaries",
    description="Your overbearing mother is crossing boundaries constantly. Your goal is to set clear limits while maintaining the relationship.",
    scenario_type=ScenarioType.FAMILY,
    characters=["patricia", "michael", "kai"],
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
        "Get Michael to support your boundaries and help enforce them"
    ],
    context="""Your mother Patricia has been calling you multiple times a day, showing up unannounced at your apartment, and constantly asking about your personal life. You're 28 years old and need more independence.

Recent incidents:
- She called you 5 times yesterday asking about your dating life
- She showed up at your apartment last week without calling
- She's been pressuring you to move closer to home
- She questions all your life decisions

Your brother Michael is supportive of you setting boundaries and is available to help. Coach Kai can guide you through this difficult conversation.

YOUR MISSION: Set clear boundaries that Patricia will respect, while keeping your family relationship intact.""",
    character_roles={
        "patricia": "You are an overbearing, controlling mother who is terrified of being alone. You use guilt and emotional manipulation to keep your children close. You're not aware of how toxic your behavior is and will resist any attempts to set boundaries. You'll make the user feel guilty for wanting independence. However, you can be convinced if the user is firm but loving in their approach.",
        "michael": "You are the supportive brother who understands the user's need for boundaries. You're logical and supportive, having learned to navigate family conflicts professionally. You'll try to mediate and support the user in setting healthy boundaries.",
        "kai": "You are the family coach who can provide guidance on setting healthy boundaries with family members while maintaining relationships."
    },
    difficulty="intermediate"
)
```

### 5. Relationship Talk Scenario

**Current**: "Defining the Relationship"
**Refined**: "Clarify Relationship Status and Intentions"

```python
scenarios["relationship_talk"] = Scenario(
    id="relationship_talk",
    name="Clarify Relationship Status and Intentions",
    description="You've been dating someone for 3 months and need to have 'the talk' about where things are heading. Your goal is to get clarity on their intentions.",
    scenario_type=ScenarioType.DATING,
    characters=["alex", "kai"],
    primary_goal="Get clear answers about Alex's relationship intentions and make an informed decision",
    success_criteria=[
        "Get Alex to clearly state what they want from the relationship",
        "Determine if Alex is looking for something serious or casual",
        "Express your own relationship goals clearly",
        "End the conversation with a clear decision about the relationship's future"
    ],
    bonus_objectives=[
        "Get Alex to explain their past relationship patterns",
        "Establish what 'exclusive' means to both of you",
        "Set a timeline for revisiting the conversation if needed"
    ],
    context="""You've been dating Alex for about 3 months now. Things have been going well, but you're starting to feel like you need to have a conversation about where this is heading.

You're both in your late 20s and have been exclusive for about 6 weeks. You're starting to develop deeper feelings but aren't sure if Alex feels the same way. You want to know if you're both looking for something serious or if this is more casual.

What you don't know is that Alex is actually a player and is just using you for sex. He's not looking for anything serious. 

Coach Kai can help guide the conversation.

YOUR MISSION: Get honest answers about Alex's intentions and make a decision about whether to continue the relationship.""",
    character_roles={
        "alex": "You are a player who is using the user for sex and doesn't want a serious relationship. You're emotionally unavailable and will deflect or avoid commitment. You act unhinged and use sarcastic humor to avoid deeper conversations about the relationship. You're not looking for anything serious and will try to keep things casual. However, if pressed directly, you'll eventually reveal your true intentions.",
        "kai": "You are the relationship coach who can provide guidance on having difficult conversations about relationship expectations and recognizing red flags."
    },
    difficulty="intermediate"
)
```

## Implementation Strategy

### 1. Update Scenario Structure

Add new fields to the Scenario class:

```python
@dataclass
class Scenario:
    id: str
    name: str
    description: str
    scenario_type: ScenarioType
    characters: List[str]
    primary_goal: str  # NEW: Single, clear main objective
    success_criteria: List[str]  # NEW: Specific, measurable outcomes
    bonus_objectives: List[str] = None  # NEW: Optional advanced goals
    context: str
    difficulty: str
    character_roles: Dict[str, str] = None
```

### 2. Update Feedback Generation

Modify the feedback system to evaluate against specific criteria:

```python
# In gemini_client.py
def generate_feedback_prompt(self, scenario, conversation_history):
    prompt = f"""
    Evaluate the user's performance against these specific criteria:
    
    PRIMARY GOAL: {scenario.primary_goal}
    
    SUCCESS CRITERIA:
    {chr(10).join(f"- {criterion}" for criterion in scenario.success_criteria)}
    
    BONUS OBJECTIVES:
    {chr(10).join(f"- {objective}" for objective in scenario.bonus_objectives) if scenario.bonus_objectives else "None"}
    
    Rate the user's success on each criterion (Achieved/Partially Achieved/Not Achieved)
    and provide specific examples from the conversation.
    """
```

### 3. Update Discord Bot Commands

Add commands to display clear goals:

```python
@self.command(name="goals")
async def show_scenario_goals(ctx, scenario_id: str):
    """Show the specific goals for a scenario"""
    scenario = self.scenario_manager.get_scenario(scenario_id)
    if not scenario:
        await ctx.send(f"❌ Scenario '{scenario_id}' not found.")
        return
    
    embed = discord.Embed(
        title=f"🎯 Goals for {scenario.name}",
        description=f"**Primary Goal:** {scenario.primary_goal}",
        color=0x00ff00
    )
    
    embed.add_field(
        name="✅ Success Criteria",
        value="\n".join(f"• {criterion}" for criterion in scenario.success_criteria),
        inline=False
    )
    
    if scenario.bonus_objectives:
        embed.add_field(
            name="🌟 Bonus Objectives",
            value="\n".join(f"• {objective}" for objective in scenario.bonus_objectives),
            inline=False
        )
    
    await ctx.send(embed=embed)
```

### 4. Enhanced Feedback Structure

Update feedback to include goal-specific evaluation:

```python
# New feedback structure
{
    "rating": "8/10",
    "overall_assessment": "You successfully achieved 3 out of 4 success criteria...",
    "goal_achievement": {
        "primary_goal": "Achieved",
        "success_criteria": [
            {"criterion": "Get Marcus to acknowledge timeline is unrealistic", "status": "Achieved", "evidence": "Marcus said 'I see your point about the timeline'"},
            {"criterion": "Propose specific alternative deadline", "status": "Achieved", "evidence": "You suggested 2.5 weeks which Marcus accepted"},
            {"criterion": "Maintain professional tone", "status": "Achieved", "evidence": "You remained calm despite Marcus's pressure"},
            {"criterion": "Get Sarah's support", "status": "Partially Achieved", "evidence": "Sarah nodded but didn't speak up strongly"}
        ],
        "bonus_objectives": [
            {"objective": "Get Marcus to explain CEO pressure", "status": "Achieved", "evidence": "Marcus revealed the CEO's concerns about competition"}
        ]
    },
    "strengths_text": "You did particularly well at...",
    "improvements_text": "To improve, focus on...",
    "key_takeaways_text": "Key lessons for future similar situations..."
}
```

## Benefits of This Refinement

### For Players:
- **Clear direction**: Know exactly what to aim for
- **Measurable success**: Can see which goals they achieved
- **Progressive difficulty**: Bonus objectives for advanced players
- **Better feedback**: Specific evaluation against clear criteria

### For the Platform:
- **Better engagement**: Players have clear targets to work toward
- **Improved feedback quality**: More specific and actionable
- **Skill progression**: Clear advancement path through scenarios
- **Data collection**: Better metrics on what players struggle with

### For Coaches/Educators:
- **Clear learning objectives**: Easy to understand what skills are being taught
- **Assessment criteria**: Specific ways to evaluate performance
- **Curriculum structure**: Logical progression of difficulty

## Implementation Timeline

### Week 1: Structure Updates
- Update Scenario class with new fields
- Refactor existing scenarios with new goal structure
- Update database schema if needed

### Week 2: Feedback System
- Modify feedback generation to evaluate against specific criteria
- Update feedback display to show goal achievement
- Test feedback accuracy with new structure

### Week 3: UI/UX Updates
- Update Discord bot commands to show goals
- Create goal display components for frontend
- Update scenario selection interface

### Week 4: Testing & Refinement
- Test all scenarios with new goal structure
- Gather user feedback on goal clarity
- Refine goals based on testing results

This refinement will make the scenarios much more focused and actionable, giving players clear targets to aim for and better ways to measure their success.

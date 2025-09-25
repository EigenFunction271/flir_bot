# Scenario Refinements Summary

## Overview

Successfully updated all scenarios in `scenarios.py` to implement the new structure with clear, specific goals that put users in challenging situations to hone their conversational skills.

## Key Changes Made

### 1. Updated Scenario Class Structure
- **Added new fields**: `primary_goal`, `success_criteria`, `bonus_objectives`
- **Maintained backward compatibility**: Added `@property` for `objectives` field
- **Enhanced context**: Added "THE CHALLENGE" and "YOUR MISSION" sections

### 2. Refined All 6 Core Scenarios

#### **Workplace Scenarios**

**1. Negotiate Realistic Project Timeline** (workplace_deadline)
- **Primary Goal**: Negotiate a realistic project timeline with your demanding boss without getting fired
- **Success Criteria**: 
  - Get Marcus to acknowledge the current timeline is unrealistic
  - Propose a specific alternative deadline (2-3 weeks from now)
  - Maintain professional tone and avoid getting defensive or emotional
  - Get Sarah to visibly support your position in the meeting
- **Challenge**: Marcus is known for firing people who "make excuses" and has already threatened to "find someone who can handle the pressure"

**2. Deliver Constructive Performance Feedback** (workplace_feedback)
- **Primary Goal**: Successfully deliver constructive feedback that leads to performance improvement without damaging the relationship
- **Success Criteria**:
  - Get Sarah to acknowledge the performance issues without becoming defensive or emotional
  - Identify at least 2 specific areas for improvement with concrete examples
  - Create a concrete action plan with timelines and measurable goals
  - End the conversation with Sarah feeling supported and motivated, not attacked or demoralized
- **Challenge**: Sarah is going through a personal crisis and is extremely sensitive, likely to become defensive or cry

#### **Dating Scenarios**

**3. Create Connection on First Date** (first_date)
- **Primary Goal**: Create a genuine connection and secure a second date
- **Success Criteria**:
  - Get Alex to share something personal about themselves (beyond surface level)
  - Find at least 2 things you have in common or can bond over
  - Make Alex laugh or smile genuinely at least once
  - End the date with Alex suggesting or agreeing to a second date
- **Challenge**: Alex is guarded and has been on many first dates, getting tired of the same old conversations

**4. Clarify Relationship Status and Intentions** (relationship_talk)
- **Primary Goal**: Get clear answers about Alex's relationship intentions and make an informed decision about the relationship's future
- **Success Criteria**:
  - Get Alex to clearly state what they want from the relationship (serious vs casual)
  - Determine if Alex is looking for something serious or just wants to keep things casual
  - Express your own relationship goals clearly without being pushy
  - End the conversation with a clear decision about the relationship's future
- **Challenge**: Alex is a master manipulator who will use charm and deflection to avoid giving straight answers

#### **Family Scenarios**

**5. Establish Healthy Family Boundaries** (family_boundaries)
- **Primary Goal**: Successfully establish and enforce healthy boundaries with your overbearing mother
- **Success Criteria**:
  - Get Patricia to acknowledge that her behavior is excessive
  - Set at least 2 specific boundaries (e.g., no unannounced visits, limit calls to once per day)
  - Get Patricia to agree to respect these boundaries
  - End the conversation with Patricia still speaking to you (relationship intact)
- **Challenge**: Patricia is a master manipulator who will use guilt, emotional blackmail, and family history to make you feel terrible

**6. Set Financial Boundaries with Manipulative Family** (family_finances)
- **Primary Goal**: Successfully say no to financial requests and establish clear financial boundaries
- **Success Criteria**:
  - Get Patricia to acknowledge that her requests are excessive
  - Say no to the current financial request without giving in to guilt
  - Set a clear boundary about future financial requests
  - End the conversation with Patricia still speaking to you (relationship intact)
- **Challenge**: Patricia will use guilt, emotional blackmail, and family loyalty to make you feel terrible for saying no

### 3. Enhanced Advanced Scenarios

#### **Workplace Harassment** (workplace_harassment)
- **Primary Goal**: Successfully confront the harassment and get David to stop the inappropriate behavior
- **Challenge**: David is a powerful executive who will deny everything, gaslight you, and potentially retaliate

#### **Workplace Sabotage** (workplace_sabotage)
- **Primary Goal**: Successfully confront Emma about her sabotage and get her to stop the behavior
- **Challenge**: Emma is a master manipulator who will deny everything, play the victim, and try to turn the situation around

#### **Dating Ghosting** (dating_ghosting)
- **Primary Goal**: Confront Alex about the ghosting and make an informed decision about whether to give them another chance
- **Challenge**: Alex will use manipulation tactics to make you feel guilty for being hurt

#### **Dating Cheating** (dating_cheating)
- **Primary Goal**: Confront Riley about the cheating and make a decision about the relationship's future
- **Challenge**: Riley will use manipulation tactics to avoid taking responsibility

#### **Family Addiction** (family_addiction)
- **Primary Goal**: Successfully confront your father about his addiction and get him to acknowledge the problem
- **Challenge**: Robert is in complete denial and will get defensive, make excuses, and blame others

## Key Improvements

### **Clear, Measurable Goals**
- Each scenario now has one primary goal that's specific and actionable
- Success criteria are concrete and measurable
- Bonus objectives provide additional challenges for advanced users

### **Enhanced Difficulty and Challenge**
- Added "THE CHALLENGE" sections that explain the specific obstacles users will face
- Characters are more manipulative and will use advanced tactics to resist the user's goals
- Scenarios put users in genuinely difficult situations that require skill to navigate

### **Better Character Development**
- Characters now have more complex motivations and manipulation tactics
- They're designed to be challenging but not impossible to work with
- Each character has specific weaknesses that can be exploited with the right approach

### **Improved Context and Mission Clarity**
- Added "YOUR MISSION" sections that clearly state what the user needs to accomplish
- Context sections now include specific challenges and obstacles
- Users know exactly what they're trying to achieve and what they're up against

## Benefits for Users

1. **Clear Direction**: Users know exactly what they're trying to achieve
2. **Measurable Success**: Success criteria provide clear benchmarks for progress
3. **Realistic Challenges**: Scenarios mirror real-world difficult conversations
4. **Skill Development**: Each scenario targets specific conversational skills
5. **Progressive Difficulty**: Bonus objectives allow for advanced practice

## Technical Implementation

- **Backward Compatibility**: Existing code will continue to work with the `objectives` property
- **Enhanced Data Structure**: New fields provide richer scenario information
- **Improved Documentation**: Each scenario now has comprehensive context and challenge descriptions

The refined scenarios now provide users with clear, challenging goals that will help them develop real conversational skills for difficult situations they'll face in their personal and professional lives.

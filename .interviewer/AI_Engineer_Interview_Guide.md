# AI-Augmented Engineer Interview Guide

## Overview

This interview format is designed to assess candidates for a role on our AI-first development team. We need a senior engineer who excels at code review, debugging, and architectural thinking, we need to identify candidates who can:

- **Comprehend and critique** AI-generated code (not just write it)
- **Think architecturally** about scalability, integrations, and production concerns
- **Debug systematically** using logs and tooling
- **Collaborate effectively** with AI while maintaining healthy skepticism
- **Communicate clearly** across teams and clarify vague requirements
- **Stay focused** on core objectives without getting distracted by "side quests"

## Interview Format (60 minutes)

### Part 1: AI-Assisted Code Review (25 minutes)

**Setup:**
Provide the candidate with a ~150-line Python service that "works" and passes basic tests, but has production-ready issues:
- Scalability problem (e.g., loading all records into memory, no pagination)
- Integration anti-pattern (e.g., no retry logic or retry storms without backoff)
- Architecture smell (e.g., tight coupling, poor error handling, missing observability)

**Instructions to Candidate:**
> "This service was AI-generated and passes our basic test suite. Review it using Claude Code and identify any concerns you have. You have 15 minutes to review, then we'll discuss your findings for 10 minutes."

**Discussion Points (10 min):**
- What did you find and why does it matter?
- How did you use AI in your review process vs your own analysis?
- If this went to production tomorrow, what breaks first?
- What would you change and why?

**What We're Evaluating:**
- ✅ Can they read and comprehend code independently?
- ✅ Do they spot architectural and scalability issues?
- ✅ How do they balance AI assistance with personal code review?
- ✅ Do they think about production implications (monitoring, failure modes, costs)?
- ✅ Can they articulate WHY something is a problem, not just "AI said so"?

---

### Part 2: Architecture + Debug Scenario (25 minutes)

#### Architecture Discussion (12 minutes)

**Present this vague requirement:**
> "We need to pull data from TeamA's REST API (rate limited to 100 requests/minute) and push it to TeamB's system. We're expecting about 10,000 records per hour during peak times."

**Questions to Ask:**
1. "What's your first question before you start building this?"
2. "Sketch out a high-level approach - what components would you use, and what could go wrong?"
3. "How would this scale if we need to handle 50,000 records per hour next quarter?"

**What We're Evaluating:**
- ✅ Do they ask clarifying questions about failure modes, retry logic, idempotency, monitoring?
- ✅ Do they consider constraints on both systems (rate limits, data freshness, SLAs)?
- ✅ Can they design something that scales beyond the initial requirement?
- ✅ Do they think about observability and debugging when things go wrong?

#### Debug Scenario (13 minutes)

**Setup:**
Show production logs from a real past incident (sanitized) - examples:
- Lambda timeout errors
- Memory exhaustion
- API rate limit failures
- Unexpected error patterns

**Instructions to Candidate:**
> "This log snippet is from an incident last month that caused service degradation. Walk us through how you'd find the root cause. You can use Claude Code to help."

**What We're Evaluating:**
- ✅ Do they have a systematic debugging methodology or do they guess randomly?
- ✅ How do they use AI - as a log parser, hypothesis generator, or complete crutch?
- ✅ Can they distinguish correlation from causation in logs?
- ✅ Do they think about prevention and monitoring, not just immediate fixes?

---

### Part 3: Wrap-up Questions (10 minutes)

Ask these questions to understand their AI collaboration approach and experience:

**On AI Collaboration:**
1. "Do you review AI-generated code before using it? Walk me through your review process."
2. "Tell me about a time AI generated code that looked right but was actually wrong. How did you catch it?"
3. "How do you decide when to trust AI output vs dig deeper yourself?"
4. "If you don't understand code that AI wrote, what do you do?"

**On Experience:**
5. "Tell me about the most complex bug you've debugged. What was your process?"
6. "Describe a time you had to work with another team's API that wasn't well documented."

**What We're Evaluating:**
- ✅ Self-awareness about their AI collaboration style
- ✅ Ability to learn from past mistakes
- ✅ Communication skills and clarity of thought
- ✅ Real-world problem-solving experience

---

## Evaluation Criteria

### 🟢 Green Flags (What We're Looking For)

- **Validates AI suggestions**: "Claude suggested X, but I checked Y to confirm because..."
- **Thinks in systems**: Considers upstream/downstream impacts, failure modes, scaling
- **Asks great questions**: Clarifies requirements, challenges assumptions, identifies gaps
- **Can explain simply**: Breaks down complex technical problems for discussion
- **Pattern recognition**: "I've seen this type of issue before when..."
- **Balances speed with quality**: Uses AI to move fast but doesn't skip critical thinking
- **Production mindset**: Thinks about monitoring, logs, error handling, costs

### 🔴 Red Flags (Concerns)

- **Over-reliance on AI**: Can't articulate technical reasoning without "AI said..."
- **No debugging instinct**: Doesn't know how to systematically narrow down problems
- **Can't read code**: Needs AI to explain every file or function
- **No architectural intuition**: Doesn't think about scale, failure modes, or maintenance
- **Poor communication**: Can't explain technical tradeoffs clearly
- **Accepts AI output blindly**: Doesn't validate, question, or test suggestions
- **Gets lost in details**: Loses sight of core requirements and business value

---

## Sample Code Review Exercise

**Option 1: API Integration Service**
```python
# A service that fetches user data from external API and stores it
# Issues: No pagination, loads everything into memory, no retry logic,
# no rate limiting, poor error handling, missing logging
```

**Option 2: Data Processing Lambda**
```python
# A Lambda function that processes S3 files
# Issues: No streaming (loads entire file), no timeout handling,
# synchronous processing of large batches, no dead letter queue
```

**Option 3: Multi-Team Integration**
```python
# Service that calls TeamA API and forwards to TeamB
# Issues: No circuit breaker, retry storms, no idempotency,
# tight coupling, no observability
```

---

## Interview Team Roles

**Lead Interviewer**: Guides the candidate through each section, asks primary questions

**Technical Observer**: Takes notes on candidate responses, asks follow-up technical questions

**Team Member(s)**: Observe and ask questions about team collaboration and communication style

---

## Post-Interview Debrief Questions

After the candidate leaves, discuss:

1. **Code Review**: Did they demonstrate they can read and critique code independently?
2. **Architecture**: Did they think about scalability, failure modes, and integrations?
3. **Debugging**: Do they have a systematic approach or did they flail?
4. **AI Collaboration**: What's their balance between AI assistance and personal judgment?
5. **Communication**: Could they explain technical concepts clearly?
6. **Team Fit**: Would they work well in our loosely-defined, collaborative environment?
7. **Critical Concern**: Could they fill the gap left by our retiring senior engineer?

**Final Question**: On a scale of 1-5, how confident are we that this person can:
- Catch production issues before they ship? ___
- Debug complex problems in our codebase? ___
- Think architecturally about integrations and scale? ___
- Effectively balance AI assistance with critical thinking? ___
- Communicate clearly with other teams? ___

---

## Notes

- The candidate should have access to Claude Code during the interview
- Provide AWS documentation links if they need to look up specific services
- Watch HOW they collaborate with AI, not just the final answers
- Remember: We're not testing if they can code - we're testing if they can think, critique, and guide AI effectively


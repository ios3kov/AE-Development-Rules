# Product Discovery / Vision Template

Use this template for a new product, major feature, or material product-direction change.

Do not ask every question mechanically. Fill known context first, then ask only what can materially change scope, UX, constraints or success criteria.

## 1. Discovery status

- Product / feature:
- Discovery owner:
- Date:
- Existing product / greenfield:
- Existing Product Vision:
- Existing confirmed context already known:
- Remaining uncertainty:

## 2. Interview — first pass

Ask only the highest-value questions first.

### User

- Who is the primary user?
- What is their level of technical expertise?
- When / where do they use this product?

### Problem

- What are you trying to achieve?
- How do you do it today?
- What is painful, slow, risky or impossible in the current workflow?
- What matters most to improve?

### Desired outcome

- What would an ideal result look like?
- What absolutely must work?
- What would make the product feel unsuccessful even if it technically works?

### Core workflow

- What triggers the workflow?
- What are the main steps from start to useful result?
- Where should the product act automatically?
- Where must the user stay in control?

### Constraints

- Required After Effects versions:
- Required OS / architectures:
- Offline/network:
- Distribution:
- Security/privacy:
- Performance:
- Existing integrations/infrastructure:
- Forbidden technologies / constraints:

## 3. Follow-up questions

Only list questions that can materially change product decisions.

| Open question | Why it matters | Owner/source | Blocking? |
| --- | --- | --- | --- |
| <question> | <impact> | <who can answer> | yes/no |

## 4. Requirement ledger

| Requirement | Class | Source / rationale | Priority | Confirmed? |
| --- | --- | --- | --- | --- |
| <requirement> | Confirmed / Derived / Assumption / Idea / Non-goal | <source> | Core / Important / Later / Out | yes/no |

Rules:

- Assumption is not a Confirmed Requirement.
- Derived Requirement should point to the confirmed workflow/constraint it follows from.
- Idea does not enter scope automatically.

## 5. Product Vision

### What is it?

<one concise product description>

### For whom?

<primary user + context>

### Problem

<main problem being solved>

### Main user journey

<trigger → actions → useful result>

### Value proposition

<what becomes materially better>

### v1 / first production scope

<what the first complete version includes>

### Non-goals

<what it deliberately does not do>

### Key constraints

<technology / compatibility / performance / security / distribution>

## 6. Product Scope

### Core

- <must exist for product value>

### Important

- <high-value but not defining>

### Later

- <post-v1 possibility>

### Out of scope

- <explicitly excluded>

## 7. Core user flows

### Flow: <name>

- Trigger:
- Initial state:
- User actions:
- Product actions:
- Expected result:
- Empty/error/unavailable state:
- Recovery / cancel:
- Persistence/state:
- Dangerous/destructive boundary:

Repeat for each core flow.

## 8. Success Criteria

| Criterion | Observable measurement / evidence | Target |
| --- | --- | --- |
| <criterion> | <how it will be verified> | <threshold/outcome> |

Avoid vague criteria such as “easy”, “fast”, “professional” without a product-specific observable meaning.

## 9. Constraints

- After Effects:
- OS / architecture:
- Technology lifecycle:
- Performance:
- Security/privacy:
- Distribution:
- Licensing:
- Migration/backward compatibility:
- Other:

## 10. Assumptions and Open Questions

### Assumptions

- <assumption + what decision it affects>

### Open Questions

- <question + what it blocks>

## 11. Stage 0 exit check

- [ ] Primary user is clear
- [ ] Problem is clear
- [ ] Desired outcome is clear
- [ ] Main user flow is clear
- [ ] Core scope is clear
- [ ] Non-goals are explicit
- [ ] Material constraints are known
- [ ] Critical assumptions are confirmed or explicitly recorded
- [ ] Success Criteria are testable
- [ ] Remaining Open Questions do not block Product Spec / Technical Design / Production Plan

## 12. Handoff

Next outputs:

1. Product Spec
2. Technical Design
3. Production Plan / milestones

Do not begin detailed implementation planning while a blocking Stage 0 question remains unresolved.

# EvidenceBridge — Product & UI Design

**Design direction:** Clean, professional B2B procurement intelligence.

## 1. Design Principles

### Calm, not flashy
EvidenceBridge should look like a serious procurement tool rather than a generic AI chatbot.

### Evidence-first
Sources and supporting evidence should be visually close to the claim they support.

### Progressive disclosure
Show a concise summary first, then allow the user to inspect evidence details.

### Human decision
Avoid UI that implies the machine has made the payment decision for the user.

## 2. Visual Language

Suggested direction:
- Neutral light background
- White/near-white cards
- Dark typography
- One restrained accent color
- Thin borders
- Small, consistent shadows
- Rounded corners, but not excessive
- Clear icons used sparingly

Avoid:
- Purple/blue AI gradients everywhere
- Animated robot imagery
- Excessive glass effects
- Large glowing buttons
- Dense dashboard clutter

## 3. Primary Screens

### Screen 1 — Home / Verify Supplier

Purpose: start a verification.

Layout:

```text
-------------------------------------------------
EvidenceBridge                         New check
-------------------------------------------------

Verify a supplier before you pay.

Enter supplier details or upload a quotation.

Supplier name      [____________________]
Website            [____________________]
Location           [____________________]
Purchase amount    [ ₹ ________________ ]
Product / service  [____________________]

Quotation / Invoice
[ Drag & drop PDF here ]

                    [ Start Verification ]
-------------------------------------------------
```

### Screen 2 — Verification Progress

Purpose: make the agent process understandable.

```text
Verification in progress

✓ Reading quotation
✓ Extracting supplier claims
✓ Preparing research
● Checking public sources
○ Comparing evidence
○ Preparing report
```

The UI should show meaningful steps, not fake animation.

### Screen 3 — Findings

Purpose: explain the evidence.

Header:

```text
ABC Industrial Solutions
₹1,80,000 purchase
```

Summary cards:

```text
Claims checked    8
Consistent        5
Need verification 2
Mismatch          1
```

Finding card:

```text
ADDRESS

Submitted
Bengaluru, Karnataka

Public source
Hyderabad, Telangana

MISMATCH

The address in the quotation differs from the
address found on the referenced public source.

Source: example.com/company
[View Source]
```

### Screen 4 — Evidence Detail

Purpose: let a judge inspect why the finding exists.

Show:
- claim
- evidence
- source title
- source URL
- excerpt/snippet
- retrieval time

### Screen 5 — Verification Actions

Purpose: convert findings into action.

```text
What should you verify next?

☐ GST certificate
☐ Registered business address
☐ Customer references
☐ Warranty details
☐ Final delivery terms

[ Generate Verification Request ]
```

### Screen 6 — Generated Message

A clean copyable message with:
- recipient/supplier name
- requested documents
- clear reason
- professional closing

## 4. Status System

### CONSISTENT
Meaning: submitted information is consistent with the evidence found.

### MISMATCH
Meaning: a conflict was found between submitted information and evidence.

### NEEDS_VERIFICATION
Meaning: there is some evidence, but not enough to confidently reconcile the field.

### NOT_FOUND
Meaning: useful public evidence was not found.

Do not use `red = fraud`.

## 5. Report Hierarchy

1. Supplier identity
2. Purchase context
3. Verification summary
4. Findings
5. Evidence details
6. Verification gaps
7. Recommended next actions

## 6. Responsive Behavior

Desktop is the primary hackathon target.

Tablet/mobile should remain usable:
- stack cards vertically
- keep action buttons accessible
- preserve evidence readability

## 7. UX Copy Principles

Prefer:
- `Mismatch detected`
- `Evidence not found`
- `Needs verification`
- `Source unavailable`
- `Request additional documents`

Avoid:
- `Fraud detected`
- `Scam supplier`
- `100% safe`
- `Guaranteed legitimate`
- `AI says yes`

## 8. Demo UX

The judge should understand the product in under 30 seconds.

The key visual story is:

```text
SUPPLIER CLAIM
      ↓
PUBLIC EVIDENCE
      ↓
COMPARISON
      ↓
FINDING
      ↓
ACTION
```

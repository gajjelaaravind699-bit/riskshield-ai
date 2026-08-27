# RiskShield AI — Abuse-Ring Sentinel

## Problem
Detect coordinated payment abuse where multiple accounts or transactions
share suspicious signals and appear to be part of the same abuse/fraud ring.

## Goal
Identify suspicious transaction clusters, explain why they are suspicious,
and recommend one of:
- ALLOW
- REVIEW
- BLOCK

## Core Signals
- Account/customer relationship
- Device relationship
- IP relationship
- Payment-instrument relationship
- Transaction frequency
- Amount patterns
- Time-based patterns
- Repeated failures/successes

## Important Constraint
This is a decision-support system.
The AI must not make unrestricted financial actions.

## Required Output
For every flagged transaction or cluster:
1. Risk score
2. Decision: ALLOW / REVIEW / BLOCK
3. Explanation
4. Evidence/signals
5. Audit record
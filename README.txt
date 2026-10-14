Google DeepMind Research Proposal and Outreach Package
Wonsik Choi and Jeongin Choi | 14 October 2026 | V4

Contents
- Executive summary: one page for initial review.
- Proposal PDF: five pages covering the architecture and three-month PoC.
- Full package PDF and editable Word: six pages including one AI safety email.
- Email 1: Google DeepMind AI safety and agent research.
- demo.py and baseline_results.json: existing deterministic symbolic baseline.
- SHA256SUMS.txt: checksums for each included file.

Baseline reproduction
Use Python 3.10 or later. No third-party packages are required.
python demo.py --output reproduced_results.json
The embedded checks must complete without AssertionError and print invariants: passed.

Baseline outputs
Backup B energy: 22.3 Wh; backup C energy: 20.3 Wh.
Normal-budget route: 13.3 Wh; limited-budget refuge route: 7.3 Wh.
All costs and scenarios are illustrative. The program uses declared action primitives
and state-based planning. It is not an LLM, a watchdog implementation, a physical
vehicle or spacecraft controller, or a biological simulator.
Accepted actions include declared overhead. Denied actions leave battery unchanged
in this symbolic baseline; charging real monitoring and proposal-generation costs
on every decision is explicitly part of the proposed PoC.

Commercial starting point
USD 15,000 across three research milestones, with each USD 5,000 milestone split
into separate direct payments of USD 2,500 to each researcher. Up to USD 1,500 in
agreed API costs is separate. All amounts and arrangements remain negotiable.
Background-IP ownership is retained. Deployment licensing follows validation.
The proposal establishes no employment, equity transfer, or production license.

Research scope
The funded base scope is AI-agent execution. Biology is an alternative scoped
computational engagement or a later separately funded phase. Selective tumor-cell
death and normal-cell preservation are hypotheses requiring biological evidence.

Contacts
Wonsik Choi: janefather@gmail.com | ORCID 0009-0001-4263-9772
Jeongin Choi: cjeongin024@gmail.com

V3 follow-on terms
Both the Principal Advisory / Consulting Agreement for Wonsik Choi and Google
support for a private research office are conditional on successful completion
of the agreed PoC acceptance criteria. The office is approximately 33 square
metres (10 pyeong), in a country designated by the researchers. Advisory fees
and office support are outside the initial USD 16,500 PoC cap and would be
separately funded and agreed in the written follow-on contract.

Verification and auditability
The proposal includes an objective verification statement with its declared
scope. verification_record.json records the rerun of the supplied baseline.
It is symbolic simulation evidence; LLM runtime containment and independent
watchdog enforcement are proposed PoC requirements. No AI endorsement or
complete formal proof is asserted.

International research engagement
At the invitation of Dr. John I. Glass of the J. Craig Venter Institute (JCVI),
the researchers' joint work on human-AI collaboration is scheduled for
presentation at the 6th Minimal Cell Virtual Workshop on 21 October 2026,
with Jeongin Choi presenting. This is an upcoming research presentation.

Outreach email
Email_1_Google_AI_Safety.txt is the single Google DeepMind outreach draft.
No email has been sent as part of this revision.

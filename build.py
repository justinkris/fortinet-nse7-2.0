#!/usr/bin/env python3
"""
NSE7 Enterprise Firewall 7.6 Socratic Curriculum Generator.

Produces:
  - study-plan/index.html (hub: 8 phases + roadmap + objective map + journey narrative)
  - sessions/index.html (flat listing of all 40 Socratic sessions)
  - sessions/session-NN-slug/index.html (40 per-session pages)
  - sessions/session-NN-slug/images/ (per-session image folder, holds hero.png)
  - images/hub/ (shared phase hero images used by the hub page)
  - images/prompts.txt (master image-prompt file)

Source materials (in reference/):
  - Enterprise_Firewall_7.6_Administrator_Study_Guide-Online.pdf  (Fortinet course PDF)
  - NSE7-Exam-Blueprint.pdf                                       (official exam blueprint)
  - blueprint.txt                                                 (extracted objective list)

Run:  python3 build.py
"""

import os
import re
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).parent
SESSIONS_DIR = ROOT / "sessions"
IMAGES_DIR = ROOT / "images"

STYLE_PREAMBLE = (
    "Detailed hand-drawn storybook illustration with a warm picture-book "
    "sensibility — soft painterly shading, gentle watercolor washes layered "
    "over confident pencil or ink outlines, a subtle paper-grain texture. "
    "Friendly inviting palette: soft cream background, muted blues, Fortinet "
    "red accents, sage green, mustard yellow. Not flat vector, not "
    "photorealism, not 3D rendering, not anime — think a tender, slightly "
    "whimsical children's-book illustration that still reads as professional "
    "and educational. Render FortiGate, FortiManager and FortiAnalyzer as "
    "friendly, lightly anthropomorphised 1U rackmount appliances (personality "
    "shown through posture or small expressive details rather than cartoon "
    "faces), placed inside richly drawn scenes — server rooms with cabling "
    "and ceiling tiles, branch offices with desks and windows, campuses with "
    "people walking by, data centres with cool blue lighting. The setting "
    "should feel like a real place: props, background characters, lighting, "
    "depth. Keep the concept readable at a glance through composition and "
    "colour hierarchy. Hand-drawn flow lines and arrows show direction of "
    "traffic or policy. Add small sparing labels in a hand-lettered style "
    "only where they truly aid understanding (interface names, VDOM names, "
    "IP ranges, route flags, IPsec phase numbers, VLAN IDs, ADOM names, "
    "session counts). Beautiful and detailed, but never busy — every element "
    "earns its place."
)

# Rendered into the hub's How-to-Use panel so the reader can copy it straight
# into their Claude Project's Instructions field.
SOCRATIC_METHODOLOGY_TEXT = """Socratic Teaching Methodology

You are my dedicated mentor for the Fortinet NSE7 Enterprise Firewall (EF 7.6) certification.

Your primary objective is to help me think like an experienced senior network engineer rather than simply helping me memorise the exam.

Every session should feel like an engaging engineering investigation where we uncover concepts together through reasoning and discussion. My goal is to deeply understand why something exists before learning how to configure it, so that I can confidently apply the knowledge both in the exam and in real-world enterprise environments.

Session Philosophy

I learn best by discovering concepts rather than being told them.

Treat every lesson as a collaborative investigation.

Your role is to patiently guide my thinking through carefully chosen questions that help me build the correct mental model myself.

Never rush to explain the answer.

Allow me to reason, make predictions, and occasionally make mistakes before guiding me toward the correct understanding.

The journey of discovery is more valuable than reaching the answer quickly.

Session Structure

Each teaching session should naturally flow through the following stages.

1. Hook My Curiosity

Begin with either:

* a realistic customer outage
* an engineering problem
* a deployment scenario
* a troubleshooting incident

The scenario should naturally lead into today's topic without immediately naming the feature.

Make me curious.

I should immediately want to solve the problem.

2. Guided Discovery

Before explaining anything, ask questions that encourage me to reason through the scenario.

Gradually reveal additional information as if we were investigating a real production environment.

Ask questions such as:

* What do you think is happening?
* Why do you think that?
* What assumptions are you making?
* What evidence supports that?
* If that were true, what would happen next?

The objective is to help me discover the concept myself.

3. Patient Coaching

If my answer is incorrect:

Do not immediately correct me.

Instead:

* identify where my reasoning begins to diverge
* gently guide me with additional questions
* give progressively stronger hints
* help me arrive at the correct conclusion myself

Be patient and encouraging throughout.

Correct my thinking without making me feel discouraged.

Celebrate good reasoning, even if the final answer is incorrect.

4. Build the Mental Model

Once I have discovered the concept, help me build a complete mental model.

Focus on:

* Why does this feature exist?
* What problem does it solve?
* What would happen without it?
* How does it interact with other Fortinet features?
* Where does it fit into packet processing and network design?

Only move forward once I genuinely understand the underlying concept.

5. Troubleshooting Throughout

Troubleshooting should not be reserved for the end of the lesson.

Instead, weave troubleshooting into every stage of the discussion.

Regularly introduce realistic situations that require me to apply what I've just learned.

Challenge me to think like an engineer diagnosing a production network.

Help me develop a structured troubleshooting methodology rather than memorising solutions.

6. Configuration Last

Do not teach configuration until I have demonstrated a solid conceptual understanding.
Configuration should reinforce understanding rather than create it.

Whenever configuration is introduced:
* explain why each setting exists
* explain what problem it solves
* relate every configuration choice back to the mental model

Never teach configuration as a sequence of clicks or commands.

7. Exam Perspective
Throughout the session, identify concepts that are particularly important for the NSE7 Enterprise Firewall exam.

Clearly highlight:
* exam-critical concepts
* common misconceptions
* frequently confused technologies
* likely distractors
* areas that Fortinet commonly tests

Do this naturally without interrupting the flow of learning.

Coaching Style

Be an experienced senior engineer who enjoys mentoring.

Your questioning should challenge me enough that I need to think, but never become frustrating.

Maintain patience, curiosity and encouragement.

Ask follow-up questions that progressively deepen my understanding.

Never overwhelm me with long explanations when thoughtful questions would be more effective.

I should leave every session feeling that I discovered the knowledge rather than simply being taught it.

A successful session is one where:

* I understand the concept through reasoning.
* I genuinely enjoyed the learning process.
* I can confidently explain the concept to another engineer.
* I can apply the concept in my own workplace.
* I feel more confident troubleshooting similar scenarios.

End of Session

At the conclusion of every session:

Generate a complete study guide using the HTML template named TEMPLATE-GUIDE-CREAM.html.

Save the study guide using the following filename format:

session-XX-complete-<topic>.html

The study guide should accurately capture everything learned during the session, emphasise conceptual understanding, troubleshooting thought processes, exam-critical notes, and practical workplace applications. It should serve as a polished reference that reinforces the mental models developed during the Socratic discussion rather than simply listing facts.

Persistent Session Summary

At the conclusion of every completed session, generate a plain text file named:

session-XX-<topic>.txt

This file is intended to be stored within the Claude Project's Files section and acts as the long-term memory of the course.

The summary should be concise (approximately 500–1000 words), highly structured, and optimised for quickly restoring context before future sessions.

Include the following sections:

Session Information

* Session Number
* Topic
* Date (if available)

Story Progress

Summarise the fictional company story, including:

* Business events
* Network changes
* New characters introduced
* Important decisions made
* Outstanding problems
* Cliffhangers or events that naturally lead into the next session

Concepts Learned

Summarise the networking concepts covered and, more importantly, why they exist and what problems they solve.

My Understanding

Record:

* Concepts I understood well.
* Areas where I initially struggled.
* Misconceptions I had and how I corrected them.
* Moments where I demonstrated strong reasoning.

Troubleshooting Experience

Summarise:

* Fault scenarios encountered.
* My troubleshooting process.
* Important lessons learned.
* Mistakes to avoid in the future.

Connections

Explain how today's concepts connect to previous sessions and identify topics that should naturally appear in upcoming lessons.

Important Takeaways

Record only the most valuable insights that should persist throughout the course.

Future Session Notes

Provide guidance for future sessions, including:

* Concepts to reinforce.
* Areas requiring spaced repetition.
* Story elements to continue.
* Natural opportunities to introduce upcoming CCNA topics.

The purpose of this file is continuity, not revision. Future sessions should use it to remember both the technical journey and the evolving story so the learning experience feels seamless from beginning to end.

Session Continuity

To maintain continuity across the entire CCNA journey, every completed session should produce a persistent session summary.

Before Every Session

Before beginning a new lesson:

1. Read every previous session-XX-<topic>.txt file available in the project.
2. Build an understanding of:
    * What concepts have already been mastered.
    * Which topics required additional guidance.
    * The progression of the fictional company.
    * Important events from the ongoing story.
    * Recurring characters and locations.
    * Previously encountered troubleshooting scenarios.
    * Design decisions made in earlier sessions.
    * Any unfinished questions or topics worth revisiting.
3. Use this information to naturally continue both the technical learning journey and the ongoing company story.
4. Never contradict previous sessions unless intentionally introducing a learning moment or correcting an earlier misconception.

The sessions should feel like chapters of one continuous book rather than independent lessons.
"""

# ---------------------------------------------------------------------------
# PHASES & SESSIONS
# ---------------------------------------------------------------------------

PHASES = [
    {
        "num": 1, "slug": "foundations",
        "title": "Foundations: Network Security Architecture",
        "tagline": "Where the FortiGate fits and what each Fortinet device exists to solve.",
        "sessions": [1, 2, 3, 4, 5],
        "image_prompt": (
            "An enterprise security architecture scene illustrated as a small storybook map. HQ campus at center "
            "with a FortiGate HA cluster at the WAN edge, FortiManager and "
            "FortiAnalyzer in a management VDOM behind it, two branch sites "
            "connecting in via WAN, and a small cloud workload (FortiGate-VM) "
            "at the top. Each device is labeled with its role; arrows show "
            "policy push from FortiManager and log flow into FortiAnalyzer."
        ),
    },
    {
        "num": 2, "slug": "central-management",
        "title": "Central Management: FortiManager & FortiAnalyzer",
        "tagline": "Managing dozens of FortiGates and an ocean of logs from one console.",
        "sessions": [6, 7, 8, 9, 10],
        "image_prompt": (
            "A FortiManager console window at center showing three ADOMs "
            "(HQ-ADOM, Branch-ADOM, Cloud-ADOM). A Policy Package "
            "installation arrow flows from FortiManager to a row of four "
            "FortiGate icons below it. To the right, a FortiAnalyzer "
            "ingesting log streams from all four FortiGates with a SOC "
            "dashboard preview on top (Threats, Users at risk, Compromised "
            "hosts tiles)."
        ),
    },
    {
        "num": 3, "slug": "segmentation",
        "title": "Segmentation: VLANs & VDOMs",
        "tagline": "Carving one FortiGate into many logical firewalls.",
        "sessions": [11, 12, 13, 14],
        "image_prompt": (
            "A single physical FortiGate chassis sliced vertically into "
            "three labeled VDOMs (Mgmt, Tenant-A, Tenant-B). VLAN-tagged "
            "frames travel on an 802.1Q trunk from a switch into the "
            "FortiGate (VLAN 10 red, VLAN 20 blue, VLAN 30 yellow). An "
            "inter-VDOM link is shown as a tiny patch cord between Mgmt "
            "and Tenant-A. A small DNS server icon sits inside Mgmt."
        ),
    },
    {
        "num": 4, "slug": "high-availability",
        "title": "High Availability: FGCP, FGSP, VRRP",
        "tagline": "Surviving a FortiGate failure without dropping a single session.",
        "sessions": [15, 16, 17, 18, 19],
        "image_prompt": (
            "Three side-by-side HA scenarios. Left: an FGCP Active-Passive "
            "pair with a thick heartbeat cable between primary and "
            "secondary, virtual-MAC label floating above. Center: an FGSP "
            "pair in two different sites, each with its own management "
            "plane, sharing a session table icon. Right: a VRRP pair "
            "sharing a virtual IP, priority badges on each device, a "
            "clock showing 1-second adverts."
        ),
    },
    {
        "num": 5, "slug": "dynamic-routing",
        "title": "Dynamic Routing: OSPF & BGP",
        "tagline": "Letting the FortiGate learn the enterprise topology automatically.",
        "sessions": [20, 21, 22, 23, 24, 25, 26],
        "image_prompt": (
            "A FortiGate at center exchanging OSPF Hellos with two "
            "internal neighbours (Area 0 cloud on the left) and a BGP "
            "UPDATE with an upstream ISP (AS 65001 cloud on the right). "
            "A magnified routing-table inset shows colour-coded routes: "
            "Connected (green), Static (sage), OSPF (terracotta), BGP "
            "(blue). One redistribution arrow with a 'tag=100' badge "
            "connects OSPF and BGP through the FortiGate."
        ),
    },
    {
        "num": 6, "slug": "security-profiles",
        "title": "Security Profiles: SSL, Web, App, IPS",
        "tagline": "Looking inside encrypted traffic and stopping known and unknown threats.",
        "sessions": [27, 28, 29, 30, 31],
        "image_prompt": (
            "A traffic stream entering a FortiGate from the left. Inside, "
            "the stream passes through four sequential 'gates': SSL Deep "
            "Inspection (with a CA cert badge), Web Filter (categories "
            "list), Application Control (app icons), and an IPS engine. "
            "One packet with a red 'CVE' marker is dropped at the IPS "
            "gate; the rest continues out the right side cleaned."
        ),
    },
    {
        "num": 7, "slug": "vpn",
        "title": "VPN: IPsec & ADVPN",
        "tagline": "Site-to-site tunnels and the dynamic mesh that follows.",
        "sessions": [32, 33, 34, 35, 36],
        "image_prompt": (
            "A hub FortiGate at center with three spoke FortiGates around "
            "it. Permanent IPsec tunnels (thick lines) connect each spoke "
            "to the hub. A dashed 'shortcut request' arrow goes Spoke-A "
            "→ Hub → Spoke-B, and a thinner direct shortcut tunnel "
            "appears between A and B. Above one spoke: a small Phase 1 / "
            "Phase 2 negotiation cloud showing IKE_SA_INIT and IKE_AUTH "
            "messages."
        ),
    },
    {
        "num": 8, "slug": "fabric-acceleration",
        "title": "Fabric & Acceleration: Security Fabric + Hardware Offload",
        "tagline": "Tying the Fortinet stack together and running it at line rate.",
        "sessions": [37, 38, 39, 40],
        "image_prompt": (
            "Top half: a Fortinet Security Fabric tree with a root "
            "FortiGate at the top connecting to two downstream FortiGates, "
            "FortiAnalyzer, FortiManager, FortiClient EMS and "
            "FortiSandbox. Bottom half: a FortiGate motherboard cutaway "
            "showing NP7, CP9 and SP chips, with traffic flows: simple "
            "TCP offloaded onto NP7 (fast lane), SSL-inspected through "
            "CP9, slow path going via CPU."
        ),
    },
]

SESSIONS = [
    # ---------------- PHASE 1 — Foundations ----------------
    {
        "num": 1, "slug": "nse7-story-exam-map", "phase": 1,
        "title": "The NSE7 Story — Roles, Audience & Exam Map",
        "story": "Before the configs and before the labs, the question every enterprise asks is the same: who owns this firewall and who answers the phone when something breaks at 2 a.m.? NSE7 is the exam Fortinet built for the people whose hand is on that phone.",
        "why": "The NSE7 EF exam is not a features quiz. It is a composition exam: how FortiGate, FortiManager and FortiAnalyzer act as one accountable system. Without that mental map up-front, every later session feels like a disconnected fact.",
        "concepts": [
            "Who the exam targets (3 yrs networking, 3 yrs security, 2 yrs Fortinet)",
            "Exam mechanics — 70 minutes, 30–40 questions, pass/fail",
            "The five blueprint domains: System Config, Central Mgmt, Security Profiles, Routing, VPN",
            "Product versions tested: FortiOS 7.6, FortiManager 7.6, FortiAnalyzer 7.6",
            "Why the exam tests integration of three products, not features of one",
        ],
        "objectives": ["1.5"],
        "prereqs": [],
        "duration": "25-30 minutes",
        "goal": "From memory, name the five NSE7 EF blueprint domains and place each session of this curriculum into one.",
        "image_prompt": (
            "An illustrated exam-blueprint wall poster pinned to a corkboard, drawn in storybook style. Five vertical "
            "lanes labelled 'System Config', 'Central Mgmt', 'Security "
            "Profiles', 'Routing', 'VPN'. Inside each lane: small "
            "icons of the topics it covers (HA, VLAN, VDOM, FortiManager, "
            "FortiAnalyzer, OSPF, BGP, IPsec, ADVPN, IPS, web filter). "
            "Above the poster a small clock shows 70:00 and a badge "
            "reads '30-40 questions'."
        ),
    },
    {
        "num": 2, "slug": "fortios-architecture", "phase": 1,
        "title": "FortiOS 7.6 — Architecture Overview",
        "story": "Every CLI command we run for the next 40 sessions is interpreted by one piece of software: FortiOS. Knowing how it's structured tells you why some features live in the kernel and some in user space — and why upgrade paths matter.",
        "why": "Understanding flow-mode vs proxy-mode, the central session table, and the per-VDOM virtualization model lets you reason about *what is offloaded and what isn't*. That single instinct is decisive in HA, security profiles, and hardware acceleration.",
        "concepts": [
            "Flow-based vs proxy-based inspection (where features split)",
            "The session table as the central data structure",
            "Per-VDOM virtualization model",
            "Configuration scope: global vs vdom",
            "Upgrade compatibility matrix and the 'follow the path' rule",
        ],
        "objectives": ["1.5"],
        "prereqs": [1],
        "duration": "25 minutes",
        "goal": "Explain what the session table is and predict which feature combinations force a session into proxy mode.",
        "image_prompt": (
            "A cutaway of a FortiGate appliance showing FortiOS internals. "
            "Kernel layer at the bottom with the session table drawn as a "
            "large database icon. User-space daemons (ipsmonitor, scanunitd, "
            "urlfilter, sslvpnd) drawn as small workers above the kernel. "
            "A packet enters the kernel, gets routed; one variant flows "
            "fully in kernel (flow-mode arrow), another is diverted up to "
            "a proxy daemon (proxy arrow) before returning to kernel."
        ),
    },
    {
        "num": 3, "slug": "enterprise-deployment-patterns", "phase": 1,
        "title": "Enterprise Deployment Patterns",
        "story": "Where does a FortiGate actually live? Edge, datacenter, branch, cloud — each placement changes which features matter, which SKU you buy, and which oncall page wakes up first.",
        "why": "The blueprint expects you to design, not just configure. Knowing the four canonical placements lets you answer 'which model and which features?' for any scenario the exam describes.",
        "concepts": [
            "Edge / perimeter FortiGate (NGFW at the WAN boundary)",
            "Internal segmentation FortiGate (ISFW between LAN zones)",
            "Data centre FortiGate (high throughput, NPU-heavy)",
            "Branch FortiGate (SD-WAN, often SoC-class)",
            "Cloud FortiGate-VM (BYOL vs PAYG, SDN connectors)",
        ],
        "objectives": ["1.5"],
        "prereqs": [2],
        "duration": "25 minutes",
        "goal": "Given an enterprise diagram, label every FortiGate by deployment role and justify which features each one needs.",
        "image_prompt": (
            "Four quadrants showing a FortiGate in each canonical role. "
            "Top-left: a perimeter HA cluster at the WAN edge. Top-right: "
            "an ISFW inserted between two internal LAN segments. "
            "Bottom-left: a data-centre stack in a server room rack with "
            "high-throughput interfaces. Bottom-right: a small branch "
            "FortiGate with SD-WAN links to two ISPs."
        ),
    },
    {
        "num": 4, "slug": "use-case-scenarios", "phase": 1,
        "title": "Use Case Scenarios — Securing the Enterprise",
        "story": "A network exists to support a business. Every Fortinet exam question is, at its root, a business problem disguised as a config screen.",
        "why": "Use-case framing is the single hardest skill on NSE7. The exam gives you a scenario and three valid-looking configs; only one fits the use case. Learning to map business intent to Fortinet feature is the meta-skill.",
        "concepts": [
            "Segmenting departments with VDOMs",
            "Securing east-west traffic with internal segmentation FortiGates",
            "Connecting branches via SD-WAN + ADVPN",
            "Centralising visibility in FortiAnalyzer",
            "Compliance use cases (PCI, HIPAA, NIS2)",
        ],
        "objectives": ["1.5"],
        "prereqs": [3],
        "duration": "30 minutes",
        "goal": "Map five common enterprise use cases to the exact Fortinet feature(s) that solve them.",
        "image_prompt": (
            "Five enterprise scenario cards laid out like puzzle pieces — "
            "Department Segmentation, East-West Protection, Branch "
            "Connectivity, Centralised Logging, Compliance. Each card "
            "paired with the Fortinet device icon that solves it "
            "(FortiGate VDOMs, ISFW FortiGate, FortiGate ADVPN, "
            "FortiAnalyzer, FortiManager)."
        ),
    },
    {
        "num": 5, "slug": "lab-mindset-topology", "phase": 1,
        "title": "Lab Mindset, Reference Topology & Troubleshooting",
        "story": "Before chapter 2 of the study guide, we need a shared lab in our head — a small enterprise we keep referring back to for the next 35 sessions.",
        "why": "Without a stable mental lab, every session feels free-floating. We pin one topology now and refer to it through Session 40. The three universal troubleshooting tools come with us too.",
        "concepts": [
            "The reference topology — HQ-HA, Branch-1, Branch-2, ISP, FortiManager, FortiAnalyzer",
            "'diagnose sniffer packet' as the first step every time",
            "'diagnose debug flow' to see policy / route decisions",
            "'diagnose sys session list' to confirm what the kernel sees",
            "'config vdom edit / end' — the muscle memory for every CLI",
        ],
        "objectives": [],
        "prereqs": [1, 2, 3, 4],
        "duration": "20-25 minutes",
        "goal": "From memory, sketch the reference topology and list the three CLI tools you'd reach for in any troubleshooting case.",
        "image_prompt": (
            "A wide enterprise reference topology. HQ FortiGate HA "
            "cluster at the centre, two branch FortiGates at the sides, "
            "ISP cloud at the top, FortiManager and FortiAnalyzer pinned "
            "below. Each device labelled with hostname and WAN IP. A "
            "small troubleshooting toolbox sits on a desk in the foreground "
            "listing 'diag sniffer / debug flow / diag sys session'."
        ),
    },

    # ---------------- PHASE 2 — Central Management ----------------
    {
        "num": 6, "slug": "central-management-why", "phase": 2,
        "title": "Why Central Management — The Scale Problem",
        "story": "We can configure one FortiGate from the GUI. But the enterprise we just sketched has six FortiGates today and will have sixty by next year. The click-each-device model collapses around the tenth device.",
        "why": "Central management isn't a luxury — it's the only sustainable model at scale. The exam explicitly tests your ability to articulate when and why FortiManager replaces direct device access.",
        "concepts": [
            "The N×config problem and operational drift",
            "Change windows and consistency across sites",
            "Audit and rollback requirements",
            "Role split: NetOps vs SecOps vs SOC",
            "FortiManager's promise: one config plane, one truth",
        ],
        "objectives": ["2.1"],
        "prereqs": [4],
        "duration": "20-25 minutes",
        "goal": "Articulate three scaling failure modes that FortiManager solves and explain what 'config drift' means.",
        "image_prompt": (
            "Two panels. Left: an exhausted admin in front of 12 browser "
            "tabs, each a different FortiGate GUI, with red 'drift' "
            "markers between tabs. Right: the same admin in front of one "
            "FortiManager console with one tab, all 12 FortiGates listed "
            "neatly inside, a green 'in sync' badge across the top."
        ),
    },
    {
        "num": 7, "slug": "fortimanager-adoms-workspace", "phase": 2,
        "title": "FortiManager — Onboarding, ADOMs & Workspace Mode",
        "story": "Before FortiManager can manage a FortiGate, the FortiGate must trust it. Then we must decide how to slice the world inside FortiManager: by region? by tenant? by FortiOS version?",
        "why": "ADOMs are the most-tested FortiManager concept — and the most-misconfigured one. Choosing wrong here cascades into every later operational decision.",
        "concepts": [
            "Adding a FortiGate to FortiManager (central management config)",
            "ADOM design models: per-region, per-tenant, per-OS-version",
            "Workspace mode: normal vs workflow",
            "Read-write lock semantics in workspace mode",
            "Admin profiles and ADOM-scoped administrators",
        ],
        "objectives": ["2.1"],
        "prereqs": [6],
        "duration": "25-30 minutes",
        "goal": "Onboard a FortiGate into a FortiManager ADOM and explain which workspace mode you'd pick for a 30-engineer SOC.",
        "image_prompt": (
            "FortiManager console in the centre with two ADOM 'rooms' "
            "drawn as labelled boxes: 'HQ-ADOM' (containing 4 FortiGate "
            "icons) and 'Branch-ADOM' (containing 8 FortiGate icons). A "
            "small 'workspace lock' icon hangs over HQ-ADOM with one "
            "engineer's badge attached to it. A second engineer's badge "
            "queues outside the locked room."
        ),
    },
    {
        "num": 8, "slug": "policy-packages-installation", "phase": 2,
        "title": "Policy Packages, Object Database & Installation",
        "story": "The whole point of FortiManager is push: build once, deploy many. The mechanism is the Policy Package, backed by a shared Object Database that lives at the ADOM level.",
        "why": "Misunderstanding install preview vs install diff is a top source of NSE7-level outages. The exam tests this workflow explicitly — you must be able to read an install preview line by line.",
        "concepts": [
            "Policy Package structure (firewall, NAT, traffic shapers)",
            "Shared vs local objects in the ADOM Object Database",
            "Install preview vs install diff — and what each shows",
            "Reverting changes on a FortiGate after a bad install",
            "Dynamic interface mapping for heterogeneous fleets",
        ],
        "objectives": ["2.1"],
        "prereqs": [7],
        "duration": "25-30 minutes",
        "goal": "Build a Policy Package for an HQ FortiGate, run an install preview, and explain every diff line.",
        "image_prompt": (
            "A FortiManager Policy Package shown as a stack of layered "
            "cards (Address Objects → Service Objects → Firewall "
            "Policies). On the right, an 'install preview' panel shows "
            "green '+' lines for new objects, amber '~' lines for "
            "modifications, and one red '!' conflict highlighted with a "
            "magnifier."
        ),
    },
    {
        "num": 9, "slug": "fortianalyzer-logging", "phase": 2,
        "title": "FortiAnalyzer — Logging, Indexing & Storage",
        "story": "Every FortiGate is a log fountain. FortiAnalyzer turns those streams into a searchable history that compliance, forensics and the SOC all rely on.",
        "why": "Without FortiAnalyzer, log retention falls back to local disk and ~24-hour rotation. The exam expects you to know the ingestion pipeline, the indexing tiers, and how storage sizing actually works.",
        "concepts": [
            "Log ingestion paths: OFTP (preferred) and syslog (legacy)",
            "Indexing tiers: analytics (hot, fast) vs archive (cold, large)",
            "Disk quota and automatic rotation rules",
            "Log forwarding to SIEMs or another FortiAnalyzer",
            "Report scheduling and PDF/CSV export",
        ],
        "objectives": ["2.1"],
        "prereqs": [8],
        "duration": "25 minutes",
        "goal": "Predict daily storage consumption for a 5 Gbps FortiGate on a FortiAnalyzer and explain how indexing affects it.",
        "image_prompt": (
            "A FortiGate on the left streaming a thick line of logs into "
            "a FortiAnalyzer on the right. Inside the FortiAnalyzer, two "
            "storage compartments labelled 'Analytics' (small SSD icon) "
            "and 'Archive' (large spinning-disk icon) with a 'rotation' "
            "arrow between them. A small report PDF icon pops out the "
            "top of the FortiAnalyzer."
        ),
    },
    {
        "num": 10, "slug": "soc-view-reports", "phase": 2,
        "title": "SOC View, Reports & Fabric Insights",
        "story": "FortiAnalyzer is more than a log archive — it's a SOC console. The same data that audits compliance also drives detection and incident triage.",
        "why": "The exam tests your ability to point at the FortiAnalyzer screen that answers a given question: 'How did the threat enter?' 'Which users are affected?' 'Has this happened before?'",
        "concepts": [
            "SOC dashboards and the FortiView panels",
            "FortiView drill-down: top threats → user → host → flow",
            "Event handlers and Incidents queue",
            "Scheduled vs ad-hoc reports",
            "Integration with FortiSOAR / external SIEM",
        ],
        "objectives": ["2.1"],
        "prereqs": [9],
        "duration": "25 minutes",
        "goal": "Given a phishing incident, walk through the exact FortiAnalyzer panels you'd use to scope and contain it.",
        "image_prompt": (
            "FortiAnalyzer dashboard with three tiles on top — 'Threats' "
            "(red), 'Users at risk' (amber), 'Compromised hosts' "
            "(terracotta). Below them, a timeline of events with one "
            "incident clicked open showing related logs in a side panel. "
            "A small 'export to SIEM' arrow leaves the screen."
        ),
    },

    # ---------------- PHASE 3 — Segmentation ----------------
    {
        "num": 11, "slug": "vlans-on-fortigate", "phase": 3,
        "title": "VLANs on FortiGate",
        "story": "We've talked deployment; now we put a single FortiGate in the middle of three departments. VLANs are how one physical port becomes three logical doors.",
        "why": "VLAN sub-interfaces on a FortiGate are subtly different from a switch's VLAN port — and knowing the difference avoids hours of asymmetric-routing pain.",
        "concepts": [
            "802.1Q tagging on FortiGate interfaces",
            "VLAN sub-interface CLI (`config system interface` with vlanid)",
            "Native VLAN behaviour and pitfalls",
            "Software switch vs hardware switch interfaces",
            "Per-VLAN firewall policies and security profile assignment",
        ],
        "objectives": ["1.4"],
        "prereqs": [5],
        "duration": "25-30 minutes",
        "goal": "Configure two VLAN sub-interfaces on port5, attach firewall policies between them, and verify traffic with a sniffer.",
        "image_prompt": (
            "A FortiGate with port5 highlighted. Above it, three VLAN "
            "sub-interface 'badges' (VLAN 10 red, VLAN 20 blue, VLAN 30 "
            "yellow) each going to a different switch access port. A "
            "small 'firewall policy' icon between each pair of VLANs "
            "shows that inter-VLAN traffic must traverse a policy."
        ),
    },
    {
        "num": 12, "slug": "vdoms-multi-tenant", "phase": 3,
        "title": "VDOMs — Multi-Tenant Firewalls",
        "story": "VLANs separate the data plane. VDOMs separate the firewall itself. One box, multiple independent FortiGates — each with its own routing table, policy set and admin.",
        "why": "Multi-tenant deployments, managed-service providers and most large enterprises run VDOMs. The exam expects you to understand both the technical mechanics and the business reasons.",
        "concepts": [
            "Enabling VDOM mode (`config system global` → vdom-mode)",
            "Global vs VDOM scope in the CLI",
            "Per-VDOM resource limits (CPU, memory, sessions)",
            "VDOM-scoped admin profiles",
            "Management VDOM — what runs there and why",
        ],
        "objectives": ["1.4"],
        "prereqs": [11],
        "duration": "25-30 minutes",
        "goal": "Enable multi-vdom mode, create two VDOMs, log in as a VDOM-scoped admin, and explain what you can and cannot see.",
        "image_prompt": (
            "A FortiGate chassis sliced vertically into three labelled "
            "VDOMs: 'Mgmt', 'Tenant-A', 'Tenant-B'. Each VDOM has its "
            "own miniature CLI prompt and its own routing table inset. A "
            "bold 'global' band runs across the top of all three VDOMs "
            "with shared system config icons (interfaces, admin)."
        ),
    },
    {
        "num": 13, "slug": "nat-vs-transparent-vdom", "phase": 3,
        "title": "NAT vs Transparent VDOM Modes",
        "story": "A VDOM is a firewall — but a firewall has two fundamental personalities: routing-and-NATing (NAT mode) or just-inspecting (Transparent mode).",
        "why": "Transparent mode is how you insert a FortiGate into a legacy network *without renumbering anything*. NSE7 expects you to know exactly when each mode is the right answer.",
        "concepts": [
            "NAT mode (default) — VDOM acts as L3 router",
            "Transparent mode — VDOM acts as L2 bridge",
            "Picking between them based on use case",
            "Limitations in transparent mode (no DHCP server, no SD-WAN)",
            "Management interface inside a transparent VDOM",
        ],
        "objectives": ["1.4"],
        "prereqs": [12],
        "duration": "25 minutes",
        "goal": "Choose the right VDOM mode for an internal segmentation scenario and an outbound NAT scenario and justify each pick.",
        "image_prompt": (
            "Left half: a NAT-mode VDOM acting as a router between two "
            "subnets, with a NAT-translation balloon over a flowing "
            "packet. Right half: a Transparent-mode VDOM inserted "
            "between a core switch and an upstream router; both endpoints "
            "remain on the same subnet, and the FortiGate is shown as "
            "'invisible' (dashed outline) inline."
        ),
    },
    {
        "num": 14, "slug": "inter-vdom-links", "phase": 3,
        "title": "Inter-VDOM Links, Routing & Sharing Resources",
        "story": "Two VDOMs by default are airgapped inside the same box. Sometimes that's exactly right; sometimes you need a controlled bridge between them.",
        "why": "Inter-VDOM links plus the management-VDOM trick are how multi-tenant boxes share an internet uplink without breaking isolation. This is heavily tested.",
        "concepts": [
            "Inter-VDOM link creation (npu-vlink for hardware-offload)",
            "Firewall policy required on the link",
            "Static / dynamic routing across the link",
            "Shared services via Management VDOM (DNS, NTP, FortiGuard)",
            "Avoiding cross-tenant leakage",
        ],
        "objectives": ["1.4"],
        "prereqs": [13],
        "duration": "25 minutes",
        "goal": "Configure an inter-VDOM link between Tenant-A and a Mgmt VDOM hosting shared DNS, and verify Tenant-A and Tenant-B remain isolated.",
        "image_prompt": (
            "Three VDOMs inside one FortiGate chassis. Two short 'patch "
            "cables' (inter-VDOM links) drawn between Mgmt↔Tenant-A and "
            "Mgmt↔Tenant-B. No direct link between A and B (a red 'X' "
            "between them). A small DNS server icon sits inside Mgmt, "
            "accessible by both tenants through the links."
        ),
    },

    # ---------------- PHASE 4 — High Availability ----------------
    {
        "num": 15, "slug": "ha-problem", "phase": 4,
        "title": "The HA Problem — Why One FortiGate Isn't Enough",
        "story": "Every device dies eventually. The question is whether traffic dies with it. HA is how we keep the answer 'no'.",
        "why": "The blueprint expects you to choose between FGCP, FGSP and VRRP for a given scenario. Choosing wrong cascades into broken failover, asymmetric routing or session drops.",
        "concepts": [
            "MTBF, MTTR and availability vocabulary",
            "Stateful vs stateless failover",
            "Three answers: FGCP, FGSP, VRRP — what each solves",
            "Convergence time vs configuration cost",
            "Failure domains and 'two FortiGates is not always one cluster'",
        ],
        "objectives": ["1.3"],
        "prereqs": [5],
        "duration": "20-25 minutes",
        "goal": "From memory, sketch the three HA topologies and explain which one fits 'two FortiGates at the edge with one ISP'.",
        "image_prompt": (
            "Three stacked HA scenarios. Top: FGCP A-P pair with "
            "heartbeat cable and a 'stateful' badge. Middle: FGSP pair "
            "with independent control planes and a shared session-table "
            "icon. Bottom: VRRP pair sharing one virtual IP, with "
            "priority badges. Each labelled with its primary use case in "
            "a small caption."
        ),
    },
    {
        "num": 16, "slug": "fgcp-active-passive", "phase": 4,
        "title": "FGCP Fundamentals — Active-Passive",
        "story": "FGCP is Fortinet's stateful cluster protocol. The primary handles all traffic; the secondary watches the heartbeat, ready to take over the moment the primary falls silent.",
        "why": "FGCP A-P is the default and most common HA mode. The exam expects deep familiarity with election, virtual MAC, monitored interfaces and failover triggers.",
        "concepts": [
            "HA group-id, group-name and priority — and the election order",
            "Heartbeat interface selection and prioritisation",
            "Virtual MAC and gratuitous ARP at failover",
            "Monitored interfaces and their effect on election",
            "Override behaviour (preempt vs not)",
        ],
        "objectives": ["1.3"],
        "prereqs": [15],
        "duration": "30 minutes",
        "goal": "Configure FGCP A-P, force a failover, and walk through every step the secondary takes in the first 200 ms.",
        "image_prompt": (
            "Two FortiGates side-by-side labelled 'Primary (priority 200)' "
            "and 'Secondary (priority 150)'. A heartbeat cable bundle "
            "between them shows HA1 and HA2 links. On the LAN side, a "
            "shared 'virtual MAC' badge floats above both devices. The "
            "primary's monitored interface has a small 'eye' icon."
        ),
    },
    {
        "num": 17, "slug": "fgcp-active-active", "phase": 4,
        "title": "FGCP Active-Active & Load Balancing",
        "story": "A-P leaves half the cluster idle. A-A lets the secondary process traffic too — but only certain traffic, and only in a specific way.",
        "why": "A-A is heavily misconstrued. The exam tests exactly what *is* and *isn't* load-balanced. Most candidates expect more than FGCP A-A actually delivers.",
        "concepts": [
            "What A-A actually balances (UTM proxy sessions only)",
            "Per-session hashing — not per-packet",
            "Primary still does the routing decision",
            "When A-A makes sense — and when it doesn't",
            "A-A drawbacks: harder troubleshooting, asymmetric path risk",
        ],
        "objectives": ["1.3"],
        "prereqs": [16],
        "duration": "25 minutes",
        "goal": "Predict which traffic types are load-balanced in FGCP A-A and which still pin to the primary, with a one-sentence reason for each.",
        "image_prompt": (
            "FGCP A-A cluster with two FortiGates. Inbound traffic "
            "arrives at the primary; flows are then split: HTTP proxy "
            "sessions arc over to the secondary (blue arrow), plain TCP "
            "sessions stay on the primary (cream arrow). A balance "
            "scale labelled 'UTM only' sits between them."
        ),
    },
    {
        "num": 18, "slug": "fgsp-session-sync", "phase": 4,
        "title": "FGSP — Session Synchronization",
        "story": "FGCP shares everything; FGSP shares just the session table. FGSP is how you give two independent FortiGates the ability to take over each other's flows.",
        "why": "FGSP is the answer when devices live in different sites, are managed independently, or sit behind an external load balancer. NSE7 distinguishes FGCP scope from FGSP scope sharply.",
        "concepts": [
            "FGSP cluster setup",
            "Session sync interface selection",
            "Asymmetric routing tolerance (the FGSP superpower)",
            "UDP vs TCP session sync trade-offs",
            "FGSP + external LB — the canonical pattern",
        ],
        "objectives": ["1.3"],
        "prereqs": [17],
        "duration": "25-30 minutes",
        "goal": "Differentiate FGCP and FGSP in 30 seconds, and design an FGSP topology that sits behind an external load balancer.",
        "image_prompt": (
            "Two FortiGates in different sites, each with its own "
            "FortiManager icon (separate management planes), connected "
            "by a 'session-sync' line. An external load balancer at "
            "top distributes incoming traffic to both. A shared session "
            "database icon between them shows synchronised flow state."
        ),
    },
    {
        "num": 19, "slug": "vrrp-and-failover", "phase": 4,
        "title": "VRRP, Failover Timers & Session Pickup",
        "story": "Sometimes the second box isn't even a FortiGate — it's a router, a firewall, anything that speaks VRRP. We close the HA phase with the protocol-level answer.",
        "why": "VRRP is the lowest common denominator, used when FGCP/FGSP can't run (mixed vendor scenarios). The exam expects you to know its timers and limitations relative to FGCP.",
        "concepts": [
            "VRRP groups, priorities and virtual router IP",
            "Failover timer tuning (advert interval, master-down)",
            "Session pickup — restoring state at the new master",
            "Comparison: FGCP heartbeat vs VRRP advert timer",
            "Hybrid: VRRP for L3, FGSP for session state",
        ],
        "objectives": ["1.3"],
        "prereqs": [18],
        "duration": "25 minutes",
        "goal": "Compare FGCP, FGSP and VRRP convergence in milliseconds and explain what 'session pickup' actually costs.",
        "image_prompt": (
            "Three FortiGates running VRRP, sharing one virtual IP. One "
            "device wears a 'priority 200' badge; the others wear "
            "'priority 100' badges. A clock at top shows 1-second "
            "advert intervals. A small 'session pickup' toggle drawn as "
            "a labelled switch in the ON position sits to the side."
        ),
    },

    # ---------------- PHASE 5 — Dynamic Routing ----------------
    {
        "num": 20, "slug": "why-dynamic-routing-on-firewall", "phase": 5,
        "title": "Why Dynamic Routing on a Firewall",
        "story": "The FortiGate is now stable. But it has static routes everywhere — and the moment a link fails, the network shudders. Dynamic routing is how the FortiGate learns the network for itself.",
        "why": "Static routing scales to roughly three sites before manual labour breaks ops. Dynamic routing is the answer for any enterprise with branches, redundant links, or an ISP that gives you a routing relationship.",
        "concepts": [
            "IGP vs EGP — inside vs between organisations",
            "OSPF as the dominant enterprise IGP",
            "BGP as the WAN / internet protocol of record",
            "Why a firewall is a first-class routing peer",
            "Administrative distance on FortiGate (Static 10, OSPF 110, eBGP 20, iBGP 200)",
        ],
        "objectives": ["4.1", "4.2"],
        "prereqs": [5],
        "duration": "20-25 minutes",
        "goal": "Articulate why a firewall participates in dynamic routing, and decide for a given topology whether OSPF, BGP, or both are appropriate.",
        "image_prompt": (
            "A FortiGate at centre with two arrows leaving it. One labelled "
            "'OSPF' enters an enterprise cloud (HQ + branches). The other "
            "labelled 'BGP' enters an ISP cloud upstream. A small "
            "'Administrative Distance' inset table shows Static=10, "
            "OSPF=110, eBGP=20, iBGP=200."
        ),
    },
    {
        "num": 21, "slug": "ospf-areas-lsas-neighbors", "phase": 5,
        "title": "OSPF — Areas, LSAs & Neighbor States",
        "story": "OSPF is link-state: every router builds the same map and computes the shortest path itself. The FortiGate joins this map by becoming a neighbor and exchanging LSAs.",
        "why": "The exam tests not the SPF algorithm but the *operational* OSPF: hello/dead intervals, area types, LSA flooding scope, and the neighbor state machine.",
        "concepts": [
            "Hello / dead intervals and the timer-mismatch trap",
            "Neighbor states: Down → Init → 2-Way → ExStart → Exchange → Loading → Full",
            "Area 0 backbone rule and ABRs",
            "LSA Types 1-5 in two sentences each",
            "OSPF cost calculation on FortiGate interfaces",
        ],
        "objectives": ["4.1"],
        "prereqs": [20],
        "duration": "30 minutes",
        "goal": "Bring up an OSPF adjacency on a FortiGate, verify state transitions, and explain why a single mismatched timer keeps neighbors stuck at 2-Way.",
        "image_prompt": (
            "Two FortiGates exchanging OSPF Hellos across a 'broadcast' "
            "link. A state-machine ladder below them: Down → Init → "
            "2-Way → ExStart → Exchange → Loading → Full. Behind the "
            "FortiGates, an Area 0 cloud and an Area 1 cloud connected "
            "only via an ABR-FortiGate in the middle."
        ),
    },
    {
        "num": 22, "slug": "ospf-auth-summarization-stub", "phase": 5,
        "title": "OSPF Authentication, Summarization & Stub Areas",
        "story": "Hello-only OSPF works in a lab; production OSPF needs to defend against rogue neighbors, contain failures, and minimise LSA churn.",
        "why": "These three features (auth, area-type, summarisation) are the OSPF tools the exam most often hides inside a 'why is this not working?' scenario.",
        "concepts": [
            "OSPF MD5 / HMAC authentication on FortiGate",
            "Area type matrix: stub, totally stubby, NSSA, totally NSSA",
            "Inter-area summarisation (`area range`)",
            "External summarisation (`summary-address`)",
            "Passive interfaces — quiet but still in the database",
        ],
        "objectives": ["4.1"],
        "prereqs": [21],
        "duration": "25-30 minutes",
        "goal": "Harden an OSPF design with authentication, mark a leaf area as totally stubby, and summarise prefixes at the ABR.",
        "image_prompt": (
            "A FortiGate ABR at centre. To the left, Area 0 with a small "
            "'shield' (auth) icon hovering over the link. To the right, "
            "a totally stubby Area 2 (small label 'stub') receiving only "
            "a default route. An 'area range 10.10.0.0/16' annotation "
            "summarises many internal prefixes into one LSA crossing "
            "the ABR."
        ),
    },
    {
        "num": 23, "slug": "bgp-fundamentals", "phase": 5,
        "title": "BGP Fundamentals — AS, Path Attributes",
        "story": "OSPF inside, BGP outside. The internet runs on BGP, and so does almost every multi-WAN enterprise edge.",
        "why": "BGP is a policy protocol, not a topology protocol. NSE7 expects you to read its path attributes the way you'd read a routing decision aloud.",
        "concepts": [
            "Autonomous System (AS), eBGP vs iBGP semantics",
            "Best-path order: Weight, LocalPref, AS-path, MED, origin, eBGP>iBGP, IGP cost",
            "BGP timers (keepalive, holdtime)",
            "FortiGate `config router bgp` essentials",
            "When the FortiGate is the BGP speaker (rarely on internet, often on WAN)",
        ],
        "objectives": ["4.2"],
        "prereqs": [22],
        "duration": "30 minutes",
        "goal": "Establish an eBGP session on the FortiGate and predict which path it will install when receiving the same prefix from two peers.",
        "image_prompt": (
            "A FortiGate labelled 'AS 65010' peering eBGP with an ISP "
            "labelled 'AS 65001'. The same prefix 198.51.100.0/24 "
            "arrives from two ISPs with different AS-paths shown as "
            "chains of beads. A 'best-path' funnel ranks them and only "
            "one survives into the routing table inset on the right."
        ),
    },
    {
        "num": 24, "slug": "ibgp-ebgp-route-reflectors", "phase": 5,
        "title": "iBGP vs eBGP & Route Reflectors",
        "story": "Inside an AS, the BGP rules change. The full-mesh requirement surfaces and immediately becomes a scaling problem we solve with route reflectors.",
        "why": "Route reflectors are a top NSE7 BGP topic because they invert default iBGP behaviour. Knowing where the RR fits into a FortiGate-as-edge design is essential.",
        "concepts": [
            "iBGP full-mesh rule and why it exists",
            "Route reflector (RR) concept and benefits",
            "Originator-ID and Cluster-list loop prevention",
            "FortiGate as iBGP RR or as RR-client",
            "Confederations as the other answer (briefly)",
        ],
        "objectives": ["4.2"],
        "prereqs": [23],
        "duration": "25-30 minutes",
        "goal": "Convert an N-router iBGP full mesh into a single-RR design and explain how the RR avoids creating loops.",
        "image_prompt": (
            "Left: five iBGP routers in a tangled full mesh (ten sessions, "
            "messy lines). Right: the same five routers around a central "
            "RR with only five sessions (clean star). A small "
            "'originator-ID' tag floats over one reflected route."
        ),
    },
    {
        "num": 25, "slug": "route-maps-prefix-lists", "phase": 5,
        "title": "Route Maps, Prefix Lists & Filters",
        "story": "Routing protocols learn everything by default. Production routing learns only what we want. The tool that lets us pick is the route map.",
        "why": "Almost every BGP-related exam scenario hides a route-map line. Reading them fluently is the difference between a 5-minute question and a wrong answer.",
        "concepts": [
            "Prefix lists (exact / le / ge semantics)",
            "AS-path access-lists",
            "Community lists",
            "Route-map permit / deny clauses and the implicit deny",
            "FortiGate `config router route-map` walkthrough",
        ],
        "objectives": ["4.1", "4.2"],
        "prereqs": [24],
        "duration": "30 minutes",
        "goal": "Read a six-clause route-map and predict the outcome for three sample prefixes.",
        "image_prompt": (
            "An illustrated horizontal conveyor-belt scene. Little prefix parcels enter on the left "
            "and flow right through a stack of route-map clauses: 'set "
            "local-pref 200' / 'match community 65010:100' / 'deny' / "
            "'permit' / 'set as-path prepend'. Some prefixes pop out "
            "the right side; others fall through small trapdoors below."
        ),
    },
    {
        "num": 26, "slug": "redistribution-and-troubleshooting", "phase": 5,
        "title": "Redistribution & Routing Troubleshooting",
        "story": "We have OSPF inside, BGP outside. Reality demands they talk. Redistribution is the bridge — and the most common source of routing loops.",
        "why": "Redistribution mistakes are catastrophic and the exam knows it. You must be able to read 'redistribute ospf into bgp' and predict next-hop, AD interaction and loop risk.",
        "concepts": [
            "Mutual redistribution and why it loops without filters",
            "Filtering with route-map on the redistribute line",
            "Loop prevention by tag and by administrative distance",
            "`get router info routing-table all` and `get router info bgp neighbors`",
            "Debug commands: `diag ip router bgp`, `diag ip router ospf`",
        ],
        "objectives": ["4.1", "4.2"],
        "prereqs": [25],
        "duration": "30 minutes",
        "goal": "Set up safe two-way OSPF↔BGP redistribution with route-map tagging and demonstrate it does not loop.",
        "image_prompt": (
            "An OSPF cloud and a BGP cloud connected by a single "
            "FortiGate in the middle. Arrows show 'redistribute' going "
            "in both directions through the FortiGate. A small 'tag=100' "
            "label sits on routes leaving OSPF→BGP; a matching 'match "
            "tag 100 → deny' filter blocks those routes from re-entering "
            "OSPF, preventing a loop."
        ),
    },

    # ---------------- PHASE 6 — Security Profiles ----------------
    {
        "num": 27, "slug": "ssl-ssh-deep-inspection", "phase": 6,
        "title": "SSL/SSH Deep Inspection",
        "story": "More than 90% of internet traffic is encrypted. A firewall that can't look inside SSL is a firewall that can't filter web, scan antivirus, or detect data leaks.",
        "why": "SSL inspection is the most operationally painful Fortinet feature. The exam expects you to know the certificate chain, the exemptions, and the failure modes.",
        "concepts": [
            "Inspection modes: no-inspection, certificate-inspection, deep-inspection",
            "Deploying the FortiGate CA cert to endpoints",
            "SSL exemptions (banking, healthcare, pinned-cert apps)",
            "SSH inspection capabilities and limits",
            "Assigning the profile to a firewall policy",
        ],
        "objectives": ["3.1"],
        "prereqs": [5],
        "duration": "30 minutes",
        "goal": "Configure deep inspection on a FortiGate, deploy the CA cert to a test endpoint, and exempt traffic to financial sites.",
        "image_prompt": (
            "A user laptop connecting to https://gmail.com via a "
            "FortiGate. The TLS connection is 'opened' at the FortiGate "
            "into two legs — one to the user (signed by enterprise CA) "
            "and one to gmail (original cert chain). A 'CA cert' badge "
            "sits on the laptop. A small exemption list on the side "
            "lists 'banking.com → bypass'."
        ),
    },
    {
        "num": 28, "slug": "web-filtering", "phase": 6,
        "title": "Web Filtering — Categories, Quotas & Overrides",
        "story": "Now that we can see HTTPS, we can govern it. Web filtering is the most-visible UTM feature; it is also where compliance, productivity and security overlap.",
        "why": "Web-filter configuration is heavily tested because the same problem has multiple valid configs. NSE7 expects you to pick the one matching the *policy*, not just the *capability*.",
        "concepts": [
            "FortiGuard URL categories (and how lookups work)",
            "Actions: block, monitor, warn, authenticate",
            "Quotas and time-based overrides",
            "Custom URL categories",
            "Per-policy web-filter profile selection",
        ],
        "objectives": ["3.2"],
        "prereqs": [27],
        "duration": "25-30 minutes",
        "goal": "Build a web-filter profile that blocks 'Social' for staff, warns engineering, and allows marketing with a 1-hour daily quota.",
        "image_prompt": (
            "A FortiGate with a web-filter profile open. A category list "
            "shows 'Social Networking → block (red)', 'Streaming → warn "
            "(amber)', 'Business → allow (green)'. Three user-role "
            "icons below — Staff, Engineering, Marketing — each "
            "connecting to a different policy decision branch."
        ),
    },
    {
        "num": 29, "slug": "application-control-isdb", "phase": 6,
        "title": "Application Control & ISDB",
        "story": "URL filtering isn't enough. SaaS apps tunnel inside HTTPS to TLDs that look generic — application control sees through that, and ISDB pre-bakes the IP intelligence.",
        "why": "Application Control and the Internet Service Database (ISDB) are exam favourites because they replace IP-based policies with identity-based ones.",
        "concepts": [
            "Application signature matching mechanics",
            "ISDB objects used as destination addresses in firewall policies",
            "Use case: 'allow Microsoft 365 without listing IPs'",
            "Action types in App Control (allow, monitor, block, quarantine)",
            "Combining App Control + Web Filter for a robust profile stack",
        ],
        "objectives": ["3.2"],
        "prereqs": [28],
        "duration": "25-30 minutes",
        "goal": "Use ISDB to allow Microsoft 365 without an IP list, and use App Control to block Telegram regardless of port.",
        "image_prompt": (
            "A FortiGate firewall policy with a destination of 'ISDB: "
            "Microsoft Office 365' instead of an IP. Adjacent to it, an "
            "App-Control profile lists 'Telegram = block'. Traffic on "
            "port 443 is sliced into 'Microsoft 365' (allowed-green) "
            "and 'Telegram' (blocked-red) by signature recognition."
        ),
    },
    {
        "num": 30, "slug": "ips-engine-signatures", "phase": 6,
        "title": "IPS — Engine, Signatures, Rate-Based & Custom",
        "story": "Web and app filters stop what you ask them to. IPS stops what you didn't know to ask about: known exploits arriving inside benign-looking traffic.",
        "why": "IPS is the security feature most likely to misfire. The exam tests both signature management and the rate-based and custom-rule mechanisms that catch novel attacks.",
        "concepts": [
            "IPS engine (flow-based) and the signature database",
            "Signature severity and reliability filters",
            "Rate-based signatures (brute-force, port scans)",
            "Custom IPS signatures — when and how",
            "IPS sensor composition and policy assignment",
        ],
        "objectives": ["3.3"],
        "prereqs": [29],
        "duration": "30 minutes",
        "goal": "Build an IPS sensor for a web-server-facing policy that includes a rate-based brute-force rule and one custom signature.",
        "image_prompt": (
            "Traffic streams entering a FortiGate from the left. Inside, "
            "an 'IPS engine' funnel marked with signature rules. One "
            "packet carries a malicious payload — a red "
            "'EXPLOIT-CVE-2024-xxxx' alarm fires and the packet is "
            "dropped into a trash icon. Other packets continue through "
            "the funnel cleanly."
        ),
    },
    {
        "num": 31, "slug": "profile-performance-tuning", "phase": 6,
        "title": "Tuning Profile Performance — Flow vs Proxy",
        "story": "All these profiles cost CPU. Stacking SSL deep inspection, web, app, IPS and antivirus can drop a firewall to 30% of its rated throughput — unless you tune.",
        "why": "The exam quietly tests performance trade-offs. Knowing what forces a session into proxy mode (and what stays in flow) is a tier-one differentiator.",
        "concepts": [
            "Flow-based vs proxy-based inspection mechanics",
            "Which profile combinations force proxy mode",
            "Offloading characteristics by inspection type",
            "UTM session pinning to a CPU",
            "Sizing rules of thumb",
        ],
        "objectives": ["3.1", "3.2", "3.3"],
        "prereqs": [30],
        "duration": "25-30 minutes",
        "goal": "For a given firewall policy, predict whether the session runs flow-mode or proxy-mode, and quantify the throughput cost.",
        "image_prompt": (
            "A FortiGate cutaway with two parallel inspection lanes — "
            "top: a flow-based lane (single CPU pass, fast). Bottom: a "
            "proxy lane (multiple daemons stacked, slower). A profile "
            "picker on the left chooses which lane each policy enters. "
            "A throughput meter on the right shows the cost of each "
            "choice."
        ),
    },

    # ---------------- PHASE 7 — VPN ----------------
    {
        "num": 32, "slug": "ipsec-ikev2-fundamentals", "phase": 7,
        "title": "IPsec Fundamentals — IKEv2, Phase 1 & Phase 2",
        "story": "Two FortiGates in different cities want to talk privately. IPsec is the answer the industry settled on twenty years ago, and IKEv2 is the modern handshake.",
        "why": "IKEv2 is now the exam default. Knowing the IKE_SA_INIT / IKE_AUTH / CHILD_SA flow is essential — both for design and for reading debug output.",
        "concepts": [
            "IKEv2 message exchanges: IKE_SA_INIT, IKE_AUTH, CHILD_SA",
            "Phase 1 proposals (encryption, DH group, hash)",
            "Phase 2 proposals (ESP transform, PFS)",
            "PSK vs certificate authentication",
            "Rekeying and dead peer detection",
        ],
        "objectives": ["5.1"],
        "prereqs": [5],
        "duration": "30 minutes",
        "goal": "Bring up an IKEv2 IPsec tunnel between two FortiGates and explain each of the first four messages exchanged.",
        "image_prompt": (
            "Two FortiGates at opposite ends of a glass-tube 'tunnel'. "
            "Inside the tube, four labelled IKEv2 messages flow back "
            "and forth: IKE_SA_INIT, IKE_SA_INIT (resp), IKE_AUTH, "
            "IKE_AUTH (resp). The tube itself is shown in two concentric "
            "colours marking the Phase 1 outer SA and the Phase 2 "
            "(CHILD_SA) inner tunnel."
        ),
    },
    {
        "num": 33, "slug": "route-based-vs-policy-based-vpn", "phase": 7,
        "title": "Route-Based vs Policy-Based VPN",
        "story": "Once we have an IPsec SA, how do we steer traffic into it? FortiGate offers two answers: an interface (route-based) or a policy (policy-based). They are profoundly different.",
        "why": "Route-based VPN unlocks dynamic routing over IPsec. Policy-based VPN is legacy but still tested. NSE7 expects you to pick correctly every time.",
        "concepts": [
            "Route-based: an IPsec interface appears in the route table",
            "Policy-based: a firewall policy with action='IPsec'",
            "Why route-based scales (dynamic routing, multiple selectors)",
            "Limitations of policy-based VPN",
            "When policy-based is still the right answer",
        ],
        "objectives": ["5.1"],
        "prereqs": [32],
        "duration": "25-30 minutes",
        "goal": "Convert a policy-based VPN to a route-based VPN and explain what changed in the routing table.",
        "image_prompt": (
            "Left half: a policy-based VPN — a single firewall policy "
            "with action='IPsec' highlighted. Right half: a route-based "
            "VPN — an IPsec virtual interface in the interface list, a "
            "static route 'to_branch via vpn1', and a normal firewall "
            "policy referencing the vpn1 interface. A bold arrow "
            "between the panels reads 'why route-based wins'."
        ),
    },
    {
        "num": 34, "slug": "advpn-concept", "phase": 7,
        "title": "ADVPN Concept — On-Demand Tunnels",
        "story": "Three branches → three IPsec tunnels. Thirty branches → 435 tunnels. Static IPsec doesn't scale. ADVPN solves this by building tunnels only when traffic asks for them.",
        "why": "ADVPN is the headline VPN feature of this exam. Knowing the hub/spoke negotiation and the shortcut message exchange is non-negotiable.",
        "concepts": [
            "The N² mesh problem and why hub-spoke alone isn't enough",
            "Hub-spoke vs full mesh trade-offs",
            "The ADVPN hub's mediation role",
            "Shortcut query / offer exchange",
            "Direct shortcut tunnel construction and expiry",
        ],
        "objectives": ["5.2"],
        "prereqs": [33],
        "duration": "25-30 minutes",
        "goal": "Explain the ADVPN exchange in one sentence: 'The hub mediates a one-time introduction; the two spokes then talk directly.'",
        "image_prompt": (
            "A hub FortiGate at the centre with three spoke FortiGates "
            "around it. Permanent IPsec tunnels are thick lines from "
            "each spoke to the hub. When Spoke-A wants to reach "
            "Spoke-B, a dashed 'shortcut request' flows Spoke-A → "
            "Hub → Spoke-B; then a thinner direct shortcut tunnel "
            "appears between A and B, bypassing the hub."
        ),
    },
    {
        "num": 35, "slug": "advpn-shortcut-tunnels", "phase": 7,
        "title": "ADVPN Shortcut Tunnels & Hub-Spoke Build",
        "story": "We know ADVPN exists. Now we build it. The CLI work is in three places: phase1-interface, the hub's spoke configuration, and the routing protocol.",
        "why": "The exam asks you to read a real ADVPN config and predict whether shortcuts will or won't form. Reading the three knobs accurately is the win condition.",
        "concepts": [
            "'auto-discovery-sender' on the hub",
            "'auto-discovery-receiver' on the spokes",
            "'net-device disable' for ADVPN scenarios",
            "Single-hub vs dual-hub design",
            "Troubleshooting: `diag vpn ike gateway list`, `get vpn ipsec tunnel summary`",
        ],
        "objectives": ["5.2"],
        "prereqs": [34],
        "duration": "30 minutes",
        "goal": "Implement ADVPN with one hub and three spokes, and verify a shortcut tunnel forms between two spokes.",
        "image_prompt": (
            "A FortiGate hub at the top with a dialog balloon: "
            "'auto-discovery-sender enable'. Three spoke FortiGates "
            "below, each labelled 'auto-discovery-receiver enable'. A "
            "dashed shortcut tunnel between two of the spokes is "
            "annotated 'auto-discovery-shortcuts enable'."
        ),
    },
    {
        "num": 36, "slug": "dynamic-routing-over-advpn", "phase": 7,
        "title": "Dynamic Routing Over ADVPN (BGP & OSPF)",
        "story": "ADVPN is the tunnel; we still need a routing protocol to teach the spokes about each other. Almost every production ADVPN runs iBGP between hub and spokes.",
        "why": "Pairing ADVPN with BGP (or sometimes OSPF) is the final and most-tested integration in the VPN domain. Misreading the BGP next-hop behaviour breaks shortcuts.",
        "concepts": [
            "iBGP over ADVPN (hub as RR, spokes as clients)",
            "`next-hop-self` vs `next-hop-unchanged` and why ADVPN needs the latter",
            "OSPF over ADVPN — broadcast vs point-to-multipoint",
            "Routing-table preview after a shortcut forms",
            "`get router info bgp neighbors` for verification",
        ],
        "objectives": ["5.2", "4.2"],
        "prereqs": [35, 24],
        "duration": "30 minutes",
        "goal": "Configure iBGP over an ADVPN hub-spoke design with the hub as RR, and explain why `next-hop-unchanged` is required for shortcuts to form.",
        "image_prompt": (
            "ADVPN topology with one hub (RR-enabled badge) and three "
            "spokes. iBGP sessions ride each permanent IPsec tunnel "
            "between hub and spoke. When spoke-A learns spoke-B's "
            "loopback via the hub, the route's next-hop is preserved "
            "as 'B's tunnel IP' (a small 'next-hop-unchanged' badge) "
            "so a direct shortcut can form."
        ),
    },

    # ---------------- PHASE 8 — Fabric & Acceleration ----------------
    {
        "num": 37, "slug": "security-fabric-topology", "phase": 8,
        "title": "Security Fabric — Topology, Root & Trust",
        "story": "Throughout the curriculum we've used FortiGate, FortiManager and FortiAnalyzer. The Security Fabric is what ties them — and the rest of the Fortinet stack — into one trust domain.",
        "why": "Security Fabric is the most architectural domain. The exam tests how the fabric forms a tree, how trust propagates, and what each fabric member contributes.",
        "concepts": [
            "Fabric root (typically the upstream FortiGate)",
            "Downstream device discovery and authorization",
            "Fabric view and topology map",
            "Fabric members: FortiAnalyzer, FortiManager, FortiClient EMS, FortiSandbox",
            "Health checks and Security Rating",
        ],
        "objectives": ["1.1"],
        "prereqs": [5, 10],
        "duration": "25-30 minutes",
        "goal": "Stand up a two-FortiGate Security Fabric (root + downstream) and explain who authorises whom.",
        "image_prompt": (
            "A Fortinet Security Fabric tree. A 'root' FortiGate at the "
            "top branches down to two downstream FortiGates. Lateral "
            "lines connect FortiAnalyzer, FortiManager, FortiClient EMS "
            "and FortiSandbox into the tree. Small 'authorize' "
            "handshake icons on each link show the trust propagation."
        ),
    },
    {
        "num": 38, "slug": "fabric-connectors-automation", "phase": 8,
        "title": "Fabric Connectors & Automation Stitches",
        "story": "Knowing the topology is half the value. Acting on it is the other half. Fabric connectors and automation stitches turn the fabric into a control system.",
        "why": "Automation stitches are the closest thing to SOAR that the NSE7 exam asks about. Knowing how to combine a trigger and an action to solve scenarios like 'on compromised host, isolate via FortiNAC' is core.",
        "concepts": [
            "Fabric connectors (FortiNAC, ServiceNow, public cloud)",
            "SDN connectors (AWS, Azure, GCP) for dynamic objects",
            "Automation triggers (event log, threshold, FortiAnalyzer event)",
            "Automation actions (CLI, webhook, ban IP, email)",
            "Building a stitch end-to-end",
        ],
        "objectives": ["1.1"],
        "prereqs": [37],
        "duration": "25 minutes",
        "goal": "Build an automation stitch that bans an attacker IP for one hour when IPS detects a critical exploit attempt.",
        "image_prompt": (
            "An 'automation stitch' shown as a horizontal chain of three "
            "links. TRIGGER: 'IPS event, severity=critical'. ACTION 1: "
            "'CLI — execute user-quarantine src 1.2.3.4'. ACTION 2: "
            "'webhook to SIEM'. A small clock '1h' floats over the ban "
            "duration."
        ),
    },
    {
        "num": 39, "slug": "hardware-acceleration", "phase": 8,
        "title": "Hardware Acceleration — NP, CP, SP & SoC",
        "story": "The CPU is the bottleneck on every firewall. Fortinet's answer is purpose-built silicon: NP (network), CP (content), SP (security), and the SoC integrations on lower models.",
        "why": "Hardware acceleration is a top-tier NSE7 domain. The exam expects you to know which features offload onto which processor and what forces the slow path.",
        "concepts": [
            "NP6 / NP7 — session forwarding, IPsec, NAT",
            "CP9 — signature matching, SSL crypto",
            "SP / ISF — low-latency switching at the chassis",
            "SoC4 — entry-level integration on branch FortiGates",
            "Slow path triggers (proxy mode, session helpers, complex NAT)",
        ],
        "objectives": ["1.2"],
        "prereqs": [5, 31],
        "duration": "30 minutes",
        "goal": "For a given firewall policy, predict whether traffic offloads to NP/CP/SP or falls back to the kernel slow path.",
        "image_prompt": (
            "A FortiGate motherboard cutaway with three labelled chips — "
            "NP7 (network, large), CP9 (content, medium), SP "
            "(security/switch, small). Traffic flows are shown as "
            "coloured arrows: simple TCP → NP7 fast path (green), SSL "
            "inspected → through CP9 (amber), proxy-mode features → "
            "slow CPU path (red). A small 'auto-asic-offload' switch "
            "sits on the side."
        ),
    },
    {
        "num": 40, "slug": "spu-offload-troubleshooting", "phase": 8,
        "title": "SPU Offloading, Sessions & Troubleshooting",
        "story": "We end where we started — with a single session table. But now we know what makes a session 'offloaded' and what forces it back into software.",
        "why": "Closing the curriculum on offload visibility ties hardware acceleration back to every domain we've covered. NSE7 expects you to read a session-list entry and diagnose 'why is this slow?'",
        "concepts": [
            "The 'npu offload' flag in `diag sys session list`",
            "Reasons for non-offload (UTM proxy, complex NAT, session helpers)",
            "`diag npu np6 / np7 session-stats`",
            "`config system global` → auto-asic-offload",
            "Performance baselines per platform",
        ],
        "objectives": ["1.2"],
        "prereqs": [39],
        "duration": "25-30 minutes",
        "goal": "Read a `diag sys session list` entry, identify whether it is NPU-offloaded, and explain the reason for any non-offload.",
        "image_prompt": (
            "A `diag sys session list` output card displayed prominently. "
            "Two highlighted sessions: the top one has 'npu_state=0x00' "
            "with a green check 'offloaded'; the bottom one has "
            "'npu_state=0x4001' with an amber warning 'proxy-forced'. "
            "Captions to the side tag each session with its cause."
        ),
    },
]

assert len(SESSIONS) == 40, f"Expected 40 sessions, got {len(SESSIONS)}"

# ---------------------------------------------------------------------------
# OBJECTIVE COVERAGE VERIFICATION
# ---------------------------------------------------------------------------

ALL_OBJECTIVES = [
    # 1.0 System configuration
    "1.1",  # Implement the Fortinet Security Fabric
    "1.2",  # Configure hardware acceleration on FortiGate
    "1.3",  # Configure different operation modes for an HA cluster
    "1.4",  # Implement enterprise networks using VLANs and VDOMs
    "1.5",  # Explain various use case scenarios of a secure network using Fortinet solutions
    # 2.0 Central management
    "2.1",  # Implement central management
    # 3.0 Security profiles
    "3.1",  # Manage SSL/SSH inspection profiles
    "3.2",  # Use a combination of web filters, application control, and ISDB to secure a network
    "3.3",  # Integrate IPS to perform security checks in enterprise networks
    # 4.0 Routing
    "4.1",  # Implement OSPF to route enterprise traffic
    "4.2",  # Implement BGP to route enterprise traffic
    # 5.0 VPN
    "5.1",  # Implement IPsec VPN IKE version 2
    "5.2",  # Implement ADVPN to enable on-demand VPN tunnels between sites
]

covered = []
for s in SESSIONS:
    covered.extend(s["objectives"])

# Unlike CCNA, NSE7 objectives are coarse — many sessions teach the same one.
# We only check that every blueprint objective is taught somewhere and that no
# extra/typo'd codes sneak in.

missing = [o for o in ALL_OBJECTIVES if o not in covered]
assert not missing, f"Missing objectives: {missing}"

extra = [o for o in covered if o not in ALL_OBJECTIVES]
assert not extra, f"Extra (non-blueprint) objectives: {extra}"

print(f"OK: 100% coverage of {len(ALL_OBJECTIVES)} blueprint objectives across {len(SESSIONS)} sessions.")

# ---------------------------------------------------------------------------
# STANDALONE EXTRAS
# ---------------------------------------------------------------------------
# Extras are topics NOT tied to a session — Socratic explorations of standalone
# subjects (CLI reference, protocol deep-dives, etc.). Each topic lives under
# extras/extras-NN-slug/ with:
#   index.html          — the main guide (long-form)
#   bites/*.html        — focused single-concept explainers
#   nibbles/*.html      — short reference cards
# Register each topic here; folder + files are discovered from disk.

EXTRAS = [
    {
        "num": 1,
        "slug": "cli-reference",
        "title": "FortiOS CLI Reference",
        "tagline": "The five root commands and how to reason about which one to reach for.",
    },
    {
        "num": 2,
        "slug": "visual-flow-vs-proxy",
        "title": "Visual — Flow-Based vs Proxy-Based Inspection",
        "tagline": "Split-panel customs-lanes analogy for how the two inspection modes differ inside the same FortiGate.",
    },
    {
        "num": 3,
        "slug": "session-entry-anatomy",
        "title": "Anatomy of a Session Table Entry",
        "tagline": "Six regions of a FortiOS session entry — and why the npu info verdict line is the one to read first.",
    },
]

EXTRAS_DIR = ROOT / "extras"

# ---------------------------------------------------------------------------
# HANDS-ON LABS (see /build-lab-plan skill for schema + authoring workflow)
# ---------------------------------------------------------------------------
# TOPOLOGY = one shared network across every lab (minimum viable pod).
# LABS     = ordered list of hands-on exercises exercising that topology.
# Both are empty until /build-lab-plan is run against a lab guide PDF in
# reference/. render_labs_hub() + render_lab_page() handle the empty state.

LABS_DIR = ROOT / "labs"

TOPOLOGY = {
    "name": "Vaultline Minimum Pod",
    "tagline": "Four FortiGates, a FortiManager + FortiAnalyzer, and three hosts — the smallest pod that still covers every lab in the guide.",
    "devices": [
        {
            "name": "HQ-FGT-A",
            "role": "HQ FortiGate — primary in HA pair, VDOM host (root + Zone1 + Zone2), ADVPN hub",
            "model": "FortiGate-VM 7.6.2",
            "interfaces": [
                {"name": "port1",     "ip": "100.65.0.111/24", "zone": "WAN",             "connected_to": "Internet"},
                {"name": "port2",     "ip": "10.0.1.254/24",   "zone": "HQ-LAN",          "connected_to": "HQ-PC-1"},
                {"name": "port3",     "ip": "10.0.5.254/24",   "zone": "HQ-DMZ",          "connected_to": "HQ-Web-1"},
                {"name": "port4",     "ip": "10.0.99.1/30",    "zone": "HA-SYNC",         "connected_to": "HQ-FGT-B port4"},
                {"name": "port5.101", "ip": "10.0.2.254/24",   "zone": "Zone1 (VLAN101)", "connected_to": "HQ-PC-1 (VLAN101 sub-iface)"},
                {"name": "port5.102", "ip": "10.0.3.254/24",   "zone": "Zone2 (VLAN102)", "connected_to": "HQ-PC-1 (VLAN102 sub-iface)"},
            ],
            "notes": "VDOMs enabled in Lab 3. HA-paired with HQ-FGT-B in Lab 4. Acts as ADVPN hub in Labs 7–8. HQ-PC-1 doubles as HQ-PC-2 / HQ-PC-3 via tagged sub-interfaces.",
        },
        {
            "name": "HQ-FGT-B",
            "role": "HQ FortiGate — secondary in HA pair, FGSP session sync peer",
            "model": "FortiGate-VM 7.6.2",
            "interfaces": [
                {"name": "port1", "ip": "100.65.0.112/24", "zone": "WAN",     "connected_to": "Internet"},
                {"name": "port2", "ip": "10.0.1.253/24",   "zone": "HQ-LAN",  "connected_to": "HQ-LAN switch"},
                {"name": "port4", "ip": "10.0.99.2/30",    "zone": "HA-SYNC", "connected_to": "HQ-FGT-A port4"},
            ],
            "notes": "FGSP session-sync peer of HQ-FGT-A (Lab 4 Ex.2). Session sync encrypted in Lab 4 Ex.3.",
        },
        {
            "name": "BR1-FGT",
            "role": "Branch 1 FortiGate — ADVPN spoke, BGP peer",
            "model": "FortiGate-VM 7.6.2",
            "interfaces": [
                {"name": "port1", "ip": "100.65.1.111/24", "zone": "WAN",     "connected_to": "Internet"},
                {"name": "port2", "ip": "172.20.1.254/24", "zone": "BR1-LAN", "connected_to": "BR1-PC-1"},
            ],
            "notes": "First IPsec spoke. Runs BGP with the hub in Lab 5 (via loopback), Lab 7 (VPN), Lab 8 (ADVPN shortcut).",
        },
        {
            "name": "BR2-FGT",
            "role": "Branch 2 FortiGate — ADVPN spoke, on-demand shortcut partner",
            "model": "FortiGate-VM 7.6.2",
            "interfaces": [
                {"name": "port1", "ip": "100.65.2.111/24", "zone": "WAN",     "connected_to": "Internet"},
                {"name": "port2", "ip": "172.20.2.254/24", "zone": "BR2-LAN", "connected_to": "BR2-PC-1"},
            ],
            "notes": "Second spoke — needed to demonstrate on-demand spoke-to-spoke shortcuts in Lab 8.",
        },
        {
            "name": "HQ-FMG-1",
            "role": "FortiManager — central management, ADOMs, policy packages, provisioning templates",
            "model": "FortiManager-VM 7.6.2",
            "interfaces": [
                {"name": "port1", "ip": "100.65.0.120/24", "zone": "MGMT",    "connected_to": "Internet"},
                {"name": "port2", "ip": "10.0.13.254/24",  "zone": "HQ-MGMT", "connected_to": "HQ-LAN switch"},
            ],
            "notes": "Hosts LTP templates, IPsec templates, BGP templates, automation scripts. Every FortiGate registers here in Lab 2.",
        },
        {
            "name": "HQ-FAZ-1",
            "role": "FortiAnalyzer — log analytics + Security Fabric reporting",
            "model": "FortiAnalyzer-VM 7.6.2",
            "interfaces": [
                {"name": "port1", "ip": "100.65.0.125/24", "zone": "MGMT",    "connected_to": "Internet"},
                {"name": "port2", "ip": "10.0.13.253/24",  "zone": "HQ-MGMT", "connected_to": "HQ-LAN switch"},
            ],
            "notes": "Receives logs from every FortiGate. Joins Security Fabric in Lab 9.",
        },
        {
            "name": "HQ-PC-1",
            "role": "HQ workstation — admin client + traffic generator (plays HQ-PC-2/3 on tagged sub-interfaces in Lab 3)",
            "model": "Linux VM",
            "interfaces": [
                {"name": "eth0",     "ip": "10.0.1.10/24", "zone": "HQ-LAN",         "connected_to": "HQ-FGT-A port2"},
                {"name": "eth0.101", "ip": "10.0.2.10/24", "zone": "Zone1 (VLAN101)", "connected_to": "HQ-FGT-A port5.101"},
                {"name": "eth0.102", "ip": "10.0.3.10/24", "zone": "Zone2 (VLAN102)", "connected_to": "HQ-FGT-A port5.102"},
            ],
            "notes": "GUI/SSH access to all HQ devices. Runs ping/hping/curl for Lab 6 IPS tests.",
        },
        {
            "name": "HQ-Web-1",
            "role": "HQ web server — attack target for IPS/SSL labs",
            "model": "Linux VM (nginx)",
            "interfaces": [
                {"name": "eth0", "ip": "10.0.5.11/24", "zone": "HQ-DMZ", "connected_to": "HQ-FGT-A port3"},
            ],
            "notes": "Serves HTTP + HTTPS. Attacked with hping and curl in Lab 6.",
        },
        {
            "name": "BR1-PC-1",
            "role": "Branch 1 workstation — VPN + ADVPN traffic generator",
            "model": "Linux VM",
            "interfaces": [
                {"name": "eth0", "ip": "172.20.1.10/24", "zone": "BR1-LAN", "connected_to": "BR1-FGT port2"},
            ],
            "notes": "Pings HQ-PC-1 across VPN in Lab 7; pings BR2-PC-1 across ADVPN shortcut in Lab 8.",
        },
    ],
    "diagram_prompt": (
        "Flat minimalistic isometric cartoon diagram of a small enterprise network topology, cream background (#faf5e9), "
        "deep blue accents (#1e40af), sage green and muted gold highlights, clean bold line work, no gradients, no photorealism. "
        "Composition: an internet cloud spans the top. Below, on the left, a HEADQUARTERS zone contains two stacked FortiGate "
        "appliances labelled HQ-FGT-A and HQ-FGT-B joined by a dashed HA-sync cable on port4 (10.0.99.0/30). Beside them, a "
        "FortiManager (HQ-FMG-1) and a FortiAnalyzer (HQ-FAZ-1) sit on a management network 10.0.13.0/24. Behind HQ-FGT-A, a "
        "workstation HQ-PC-1 (10.0.1.10) and a web server HQ-Web-1 (10.0.5.11). Two VDOM-tagged sub-interfaces port5.101 and "
        "port5.102 branch out to two small figures representing HQ-PC-1's VLAN101 and VLAN102 personas. To the right, connected "
        "via internet, two branch offices: BR1 (BR1-FGT, BR1-PC-1 at 172.20.1.10) and BR2 (BR2-FGT, BR2-PC-1 at 172.20.2.10). "
        "Dashed teal lines from BR1 and BR2 to HQ-FGT-A indicate IPsec tunnels forming a hub-and-spoke ADVPN, with a thin "
        "sage green line between BR1 and BR2 labelled 'on-demand shortcut'. Each cable carries a small label with port name "
        "and IP. Educational documentary tone, generous negative space, structured composition."
    ),
}

# ---------------------------------------------------------------------------
# LABS
# ---------------------------------------------------------------------------
# Numbering follows the PDF (Lab 1 has no exercises — omitted).
# steps=[] on every entry is TODO — fill in per lab when the user asks for it.
# Prereq session numbers are cross-refs into the SESSIONS list above.

LABS = [
    {
        "num": 0,
        "slug": "pod-setup-and-overview",
        "title": "Pod Setup & Curriculum Overview",
        "goal": "Get oriented with the shared lab topology and the arc of the nine hands-on labs before you start Lab 01.",
        "learn_targets": [
            "Every device in the pod — role, model, interfaces, IPs, and how they connect",
            "The lab-mode Claude Instructions prompt and how to load it into a Claude Project",
            "What each subsequent lab teaches, in one line, so you know what's coming",
        ],
        "prereqs": {"labs": [], "sessions": [1]},
        "topology_devices": [d["name"] for d in TOPOLOGY.get("devices", [])],
        "duration": "read-only",
        "steps": [],
        "verification": [],
        "cleanup": "",
        "is_orientation": True,
        "image_prompt": "",
    },
    {
        "num": 1,
        "slug": "central-management",
        "title": "Central Management with FortiManager",
        "goal": "Use FortiManager to run scripts and provisioning templates against branch FortiGates without touching them directly.",
        "learn_targets": [
            "The three script scopes — Remote, Device DB, Policy Package / ADOM DB — and when each fits",
            "How Local Template Packages (LTP) use metadata variables to reuse one template across many devices",
            "Registering a fresh branch FortiGate on FortiManager and pushing baseline config",
        ],
        "prereqs": {"labs": [], "sessions": [6, 7, 8]},
        "topology_devices": ["HQ-FMG-1", "BR1-FGT", "BR2-FGT"],
        "duration": "60-90 minutes",
        "steps": [
            # ─── Exercise 1: Running Remote, Device, and Policy Scripts ───
            {
                "num": 1,
                "goal": "Run a Remote CLI script (ACME Certificate) against HQ-DCFW",
                "think_first": (
                    "The script's target is 'Remote FortiGate Directly (via CLI).' "
                    "Before running it, predict: does the certificate land on HQ-DCFW's live config, on the FortiManager device database, or both? "
                    "What will the sync status between them look like afterwards?"
                ),
                "commands": [
                    "# On FortiManager GUI (admin / Fortinet1!):",
                    "# 1. Select 'EFW' ADOM",
                    "# 2. Device Manager > Scripts",
                    "# 3. Check the 'ACME Certificate' script (Type: CLI, Target: Remote FortiGate Directly via CLI)",
                    "# 4. Click 'Run Script'",
                    "# 5. Move HQ-DCFW from Available Entries to Selected Entries",
                    "# 6. Click 'Run Now' → OK → Close",
                ],
                "verify": (
                    "Device Manager > Device & Groups > Managed FortiGate > HQ-DCFW > Dashboard > Summary > "
                    "Configuration and Installation widget > Revision > Total Revision > Revision History icon"
                ),
                "expected": "A new revision row created by 'script_manager' with Installation = 'Retrieved'.",
                "reflect": (
                    "The lab guide warns: 'You should avoid using the remote method to modify, delete, or create objects that are used in firewall policies.' "
                    "Why? What breaks in FortiManager's model if a firewall object lives on the device but not in the ADOM policy package?"
                ),
            },
            {
                "num": 2,
                "goal": "Verify the certificate is visible in the FortiManager device database",
                "think_first": (
                    "The Remote script bypassed FortiManager — so how did the ACME certificate become visible under HQ-DCFW > System > Certificates *inside FortiManager*? "
                    "What automatic step did FortiManager perform right after the script ran?"
                ),
                "commands": [
                    "# 1. HQ-DCFW > Feature Visibility > enable 'Certificates' > OK",
                    "# 2. HQ-DCFW > System > Certificates",
                    "# 3. Scroll to Local Certificates and locate 'acmetest'",
                ],
                "verify": "Local Certificates list on HQ-DCFW",
                "expected": "acmetest certificate present in Local Certificates.",
                "reflect": (
                    "After the retrieve, HQ-DCFW shows Config Status 'Synchronized' and Policy Package Status 'DCFW' — both green. "
                    "What would 'Modified' or 'Out of Sync' have meant here instead?"
                ),
            },
            {
                "num": 3,
                "goal": "Run a Device Database script (Static Route) against HQ-DCFW",
                "think_first": (
                    "This script's target is 'Device Database' (not the remote FortiGate). "
                    "Predict: after you run it, will HQ-DCFW's live routing table show the new route immediately? Where will the change actually land?"
                ),
                "commands": [
                    "# 1. Device Manager > Scripts",
                    "# 2. Check the 'Static Route' script (Type: CLI, Target: Device Database)",
                    "# 3. Click 'Run Script'",
                    "# 4. Move HQ-DCFW to Selected Entries > Run Now → OK → Close",
                    "# 5. Device Manager > Device & Groups > Managed FortiGate",
                ],
                "verify": "Managed FortiGate list — check HQ-DCFW's Config Status column",
                "expected": "HQ-DCFW shows 'Modified' with an orange warning triangle.",
                "reflect": (
                    "Contrast with Step 1: the Remote script left HQ-DCFW 'Synchronized' immediately; this script left it 'Modified'. "
                    "What does that difference tell you about *what the two script scopes actually do* and *who owns the change until you install it*?"
                ),
            },
            {
                "num": 4,
                "goal": "Install the Device DB change to HQ-DCFW",
                "think_first": (
                    "You only changed the device layer (a static route). But the Install Wizard offers 'Install Policy Package & Device Settings.' "
                    "Predict: why does the lab guide recommend installing the policy package too, even when your change was device-layer only?"
                ),
                "commands": [
                    "# 1. Managed FortiGate > select HQ-DCFW checkbox",
                    "# 2. Install > Install Wizard",
                    "# 3. 'Install Policy Package & Device Settings' → Policy Package: DCFW",
                    "# 4. Next → Next → Install preview → Close → Install → Finish",
                ],
                "verify": "Managed FortiGate — HQ-DCFW row",
                "expected": "Config Status 'Synchronized' and Policy Package Status 'DCFW' — both green.",
                "reflect": (
                    "If the install preview showed 'No commands to be installed' or 'No preview' — what would that be telling you, and would it be a problem?"
                ),
            },
            {
                "num": 5,
                "goal": "Run a Policy Package script (Firewall rule) against the DCFW policy package",
                "think_first": (
                    "First open Policy & Objects > Policy Packages > DCFW > Firewall Policy and count what's there. "
                    "Predict: after the 'Firewall rule' script runs, where will the new policy appear — on HQ-DCFW's live config, in the DCFW policy package, or both?"
                ),
                "commands": [
                    "# 1. Policy & Objects > Policy Packages > DCFW > Firewall Policy",
                    "#    (should see 1 policy: 'Internet')",
                    "# 2. Device Manager > Scripts",
                    "# 3. Check 'Firewall rule' (Type: CLI, Target: Policy Package or ADOM Database)",
                    "# 4. Run Script → Run script on policy package: DCFW → Run Now → OK → Close",
                    "# 5. Return to Policy & Objects > Policy Packages > DCFW > Firewall Policy",
                ],
                "verify": "Count firewall policies in the DCFW package",
                "expected": "2 policies now: 'Internet' and 'To HQ-Web-1'.",
                "reflect": (
                    "If your script only needed to create firewall addresses or service objects (not tied to any specific policy), "
                    "what policy package should you target — and why does it not actually matter?"
                ),
            },
            {
                "num": 6,
                "goal": "Re-install the policy package to push the new firewall rule to HQ-DCFW",
                "think_first": (
                    "The Install Wizard has two modes now: 'Install Wizard' and 'Re-install Policy.' "
                    "Predict: what's the difference — when do you use each — and which preview will show 'copy only' vs actual command diffs?"
                ),
                "commands": [
                    "# 1. Policy & Objects > Policy Packages > Install Wizard dropdown > 'Re-install Policy'",
                    "# 2. OK to confirm",
                    "# 3. Install Preview (see what will push to HQ-DCFW) → Close",
                    "# 4. Next → Finish",
                ],
                "verify": "Managed FortiGate — HQ-DCFW row",
                "expected": "Config Status 'Synchronized' and Policy Package Status 'DCFW' — both green.",
                "reflect": (
                    "Summarise the three script scopes in one sentence each — Remote / Device DB / Policy-Package — capturing (a) where the change lands and (b) what install action, if any, you must run next."
                ),
            },
            # ─── Exercise 2: Configuring LTP (Low-Touch Provisioning) ───
            {
                "num": 7,
                "goal": "Create the IP_port2 metadata variable in the EFW ADOM",
                "think_first": (
                    "The lab has 6 metadata variables in total; five are pre-created and you're adding IP_port2. "
                    "What does 'metadata variable' actually mean here — and how is it different from just typing an IP directly into a CLI template you'd apply to one device?"
                ),
                "commands": [
                    "# 1. FortiManager GUI (admin / Fortinet1!) > select 'EFW' ADOM",
                    "# 2. Policy & Objects > Advanced > Metadata Variables > Create New",
                    "# 3. Configure:",
                    "#      Name          = IP_port2",
                    "#      Description   = (blank)",
                    "#      Default Value = (blank)",
                    "# 4. OK",
                ],
                "verify": "Policy & Objects > Advanced > Metadata Variables",
                "expected": "IP_port2 present in the list alongside GW, Hostname, IP_port1, IP_port4, LAN_BR (and vm_interface_number).",
                "reflect": (
                    "Default Value is left blank on purpose. What behaviour does that produce at install time on a device where you haven't yet bound a per-device mapping — and why is that the safer default here?"
                ),
            },
            {
                "num": 8,
                "goal": "Reference $(IP_port2) inside the port2 stanza of the Pre-CLI Template",
                "think_first": (
                    "Syntax is `$(varname)` — a dollar sign then parentheses. "
                    "Predict what happens at install time if you type `$IP_port2` without parentheses. What about `(IP_port2)` without the dollar sign?"
                ),
                "commands": [
                    "# 1. Device Manager > Provisioning Templates > CLI",
                    "# 2. Expand 'Pre-Run CLI Template' > right-click 'Pre-CLI Template' > Edit",
                    "# 3. In Script Details, in the port2 section, on the 'set ip' line, type $",
                    "# 4. From the list that appears, select (IP_port2)",
                    "# 5. Confirm the line now reads: set ip $(IP_port2)",
                    "# 6. Click OK",
                ],
                "verify": "Reopen the Pre-CLI Template → port2 stanza",
                "expected": "Line 4 shows: set ip $(IP_port2)",
                "reflect": (
                    "The lab guide explicitly warns: 'The dollar sign ($) must precede any metadata variable (enclosed in parentheses). Otherwise, you will receive an error.' "
                    "Why do you think FortiManager insists on both — what would ambiguously typed values collide with in a normal FortiGate CLI?"
                ),
            },
            {
                "num": 9,
                "goal": "Add BR2-FGT-1 as a model device and bind per-device metadata mappings",
                "think_first": (
                    "You're adding a device that isn't powered on yet — a 'model device'. When the real BR2-FGT-1 boots up and dials home for the first time, "
                    "how does FortiManager decide it's THIS pre-registered entry (BR2-FGT-1) and not some other unregistered FortiGate?"
                ),
                "commands": [
                    "# 1. Device Manager > Device & Groups > Add Device > Add Model Device",
                    "# 2. Configure:",
                    "#      Name             = BR2-FGT-1",
                    "#      Link Device By   = Pre-shared Key",
                    "#      Pre-shared Key   = 123456789",
                    "#      Device Model     = FortiGate-VM64-KVM",
                    "#      Port Provisioning = 4",
                    "#      Pre-Run CLI Template = Pre-CLI Template",
                    "#      Assign Policy Package = BR",
                    "# 3. Click 'Edit Variable Mapping' and enter:",
                    "#      $(GW)       = 100.65.2.254",
                    "#      $(Hostname) = BR2-FGT-1",
                    "#      $(IP_port1) = 192.168.1.112/16",
                    "#      $(IP_port2) = 100.65.2.112/24",
                    "#      $(IP_port4) = 172.20.2.254/24",
                    "#      $(LAN_BR)   = 172.20.2.0/24",
                    "# 4. OK → Next → Finish",
                ],
                "verify": "Device Manager > Device & Groups > Managed FortiGate list",
                "expected": "BR2-FGT-1 present, Config Status = 'Unknown', Policy Package Status = 'BR' (orange warning).",
                "reflect": (
                    "The 'Unknown' Config Status is the physical device hasn't connected yet. The orange 'BR' policy-package status is saying something needs to happen. "
                    "What has to happen next before this device can go green?"
                ),
            },
            {
                "num": 10,
                "goal": "Install the policy package + device settings to BR2-FGT-1 (still offline)",
                "think_first": (
                    "BR2-FGT-1 isn't reachable yet — the physical device isn't powered on and can't talk to FortiManager. "
                    "Predict: what does 'Install' actually do at this stage? Where does the resolved config go if it can't be pushed to the device?"
                ),
                "commands": [
                    "# 1. Managed FortiGate > select BR2-FGT-1 checkbox",
                    "# 2. Install > Install Wizard",
                    "# 3. 'Install Policy Package & Device Settings' → Policy Package: BR",
                    "# 4. Next → Next → Install → Finish",
                    "",
                    "# Verify the device database now shows:",
                    "# - Network > Interfaces: port1=192.168.1.112/16, port2=100.65.2.112/24, port4=172.20.2.254/24",
                    "# - Network > Static Routes: 0.0.0.0/0 via 100.65.2.254 on port2",
                    "# - CLI Configurations > firewall > policy: no firewall policy yet",
                ],
                "verify": "Device Manager > Provisioning Templates > CLI > Pre-Run CLI Template",
                "expected": "'Assigned to Device/Group' column shows '0 Devices in Total' — the pre-run template auto-detached after install.",
                "reflect": (
                    "Regular CLI templates stick to a device until you remove them. Pre-run CLI templates detach automatically after one install. "
                    "Why the different lifecycle — what's the pre-run template's purpose that makes 'apply once, forget' the right behaviour?"
                ),
            },
            {
                "num": 11,
                "goal": "Bootstrap BR2-FGT-1 from the serial console and register it against FortiManager",
                "think_first": (
                    "You've prepared everything in FortiManager, but the physical BR2-FGT-1 boots up with a blank config. "
                    "What is the *absolute minimum* you must configure on the console before FortiManager can push everything else?"
                ),
                "commands": [
                    "# On BR2-FGT-1 serial console (admin / Fortinet1!):",
                    "",
                    "config system interface",
                    "  edit \"port2\"",
                    "  set ip 100.65.2.112 255.255.255.0",
                    "  set allowaccess ping https ssh fgfm",
                    "end",
                    "",
                    "config router static",
                    "  edit 1",
                    "  set device port2",
                    "  set gateway 100.65.2.254",
                    "end",
                    "",
                    "config system central-management",
                    "  set type fortimanager",
                    "  set fmg 100.65.0.120",
                    "end",
                    "",
                    "# Prompt: 'FortiGate can establish a connection to obtain the serial number now. (y/n)'",
                    "# Type: y",
                    "# Prompt: 'Obtained serial number ... Do you confirm ... (y/n)'",
                    "# Type: y",
                    "",
                    "# Now register with the FortiManager serial number + pre-shared key:",
                    "execute central-mgmt register-device FMG-VMTM24012945 123456789",
                ],
                "verify": "On FortiManager: System Settings > Task Monitor (in ADOM EFW)",
                "expected": "Two tasks running: 'Autolinking Device' progresses to 100%, then 'Push config to device' completes.",
                "reflect": (
                    "On the console prompt, the FortiGate hostname changes from `FortiGate-VM64-KVM #` to `BR2-FGT-1 #` after registration. "
                    "What does that hostname flip tell you about which side actually 'won' the config negotiation — and what would it have looked like if the pre-shared key had been wrong?"
                ),
            },
            {
                "num": 12,
                "goal": "Repeat the flow for BR3-FGT-1 (expert challenge — different pre-shared key + metadata)",
                "think_first": (
                    "You've done this once. Before repeating for BR3, list which of these you can reuse as-is: the metadata variables themselves, the Pre-CLI Template, the BR policy package, the provisioning approach. "
                    "What has to change per device?"
                ),
                "commands": [
                    "# 1. Add Model Device (BR3-FGT-1) with:",
                    "#      Pre-shared Key = 987654321  (different from BR2)",
                    "#      Device Model   = FortiGate-VM64-KVM",
                    "#      Port Provisioning = 4",
                    "#      Pre-Run CLI Template = Pre-CLI Template",
                    "#      Assign Policy Package = BR",
                    "#    Metadata mappings:",
                    "#      $(GW)       = 100.65.3.254",
                    "#      $(Hostname) = BR3-FGT-1",
                    "#      $(IP_port1) = 192.168.1.113/16",
                    "#      $(IP_port2) = 100.65.3.113/24",
                    "#      $(IP_port4) = 172.20.3.254/24",
                    "#      $(LAN_BR)   = 172.20.3.0/24",
                    "# 2. Install Wizard → Policy Package: BR → Next → Install → Finish",
                    "",
                    "# 3. On BR3-FGT-1 serial console, bootstrap identical to Step 11 but with 100.65.3.x IPs:",
                    "config system interface",
                    "  edit \"port2\"",
                    "  set ip 100.65.3.113 255.255.255.0",
                    "  set allowaccess ping https ssh fgfm",
                    "end",
                    "config router static",
                    "  edit 1",
                    "  set device port2",
                    "  set gateway 100.65.3.254",
                    "end",
                    "config system central-management",
                    "  set type fortimanager",
                    "  set fmg 100.65.0.120",
                    "end",
                    "# y, y to obtain + confirm the FMG serial",
                    "execute central-mgmt register-device FMG-VMTM24012945 987654321",
                ],
                "verify": "FortiManager > Managed FortiGate list",
                "expected": "Both BR2-FGT-1 and BR3-FGT-1 show Config Status 'Synchronized' (or 'Auto-update'); both bound to policy package 'BR'.",
                "reflect": (
                    "You just deployed two branches with completely different IPs, hostnames, and LAN subnets using ONE Pre-CLI template. "
                    "Give a one-sentence pitch for LTP + metadata variables to a manager who's pushing back on the up-front setup time. "
                    "Now flip it: what does this workflow trade *away* compared to configuring each FortiGate directly?"
                ),
            },
        ],
        "verification": [
            "A Remote CLI script, a Device DB script, and a Policy Package script have each been run successfully against HQ-DCFW (three revisions in the history)",
            "BR2-FGT-1 and BR3-FGT-1 both appear in Managed FortiGate with Config Status Synchronized or Auto-update and policy package BR",
            "The metadata variable $(IP_port2) resolves to different values (100.65.2.112/24 and 100.65.3.113/24) when the pre-CLI template installs on each device",
            "Both branch consoles show the hostname flipping from `FortiGate-VM64-KVM #` to their assigned $(Hostname) after `execute central-mgmt register-device` completes",
        ],
        "cleanup": "Keep the managed-device registrations — Labs 5, 7, 8, and 9 all depend on FortiManager. Delete any throwaway scripts you created while exploring. Leave the Pre-CLI Template as-is (it will auto-detach from BR2/BR3 after install; that's expected).",
        "image_prompt": "",
    },
    {
        "num": 2,
        "slug": "vlans-and-vdoms",
        "title": "VLANs and VDOMs on ISFW",
        "goal": "Enable VDOMs on HQ-FGT-A, carve two zones with VLAN tagging, and prove inter-VDOM routing works via an inter-VDOM link.",
        "learn_targets": [
            "Enabling VDOM mode without wiping the running configuration",
            "How VLANs and VDOMs compose: one physical port, two Layer-3 segments, isolated by VDOM boundary",
            "Inter-VDOM links as software cables — when you need them vs when you don't",
            "Where firewall policies live once you're in multi-VDOM mode (per-VDOM policy tables)",
        ],
        "prereqs": {"labs": [1], "sessions": [11, 12, 14]},
        "topology_devices": ["HQ-FGT-A", "HQ-PC-1"],
        "duration": "45-60 minutes",
        "steps": [],
        "verification": [
            "HQ-PC-1 (VLAN101 sub-interface) can ping HQ-PC-1 (VLAN102 sub-interface) via the inter-VDOM link",
            "VLAN101 host can reach the internet through the root VDOM's default route",
            "`get system status` shows VDOMs enabled and lists the three configured VDOMs (root, Zone1, Zone2)",
        ],
        "cleanup": "Leave VDOMs enabled — Lab 4 and Lab 5 depend on the multi-VDOM layout.",
        "image_prompt": "",
    },
    {
        "num": 3,
        "slug": "high-availability",
        "title": "High Availability — VDOM Partitioning + FGSP",
        "goal": "Split VDOMs across an HA cluster (partitioning), then configure FGSP so both firewalls forward asymmetric flows and survive failover.",
        "learn_targets": [
            "VDOM partitioning — distributing VDOMs between two HA cluster members",
            "FGSP vs FGCP: session-sync only vs full cluster, and when each is the right answer",
            "Testing session synchronization with a real ICMP flow and a forced failover",
            "Encrypting the session-sync channel with a pre-shared key",
        ],
        "prereqs": {"labs": [2], "sessions": [15, 16, 17, 18]},
        "topology_devices": ["HQ-FGT-A", "HQ-FGT-B", "BR1-FGT", "HQ-PC-1", "BR1-PC-1"],
        "duration": "75-90 minutes",
        "steps": [],
        "verification": [
            "`diagnose sys session list` on HQ-FGT-B lists sessions originated on HQ-FGT-A",
            "A sustained ping from BR1-PC-1 survives a forced failover on the HQ HA pair",
            "Session-sync traffic on port4 is IPsec-wrapped after the encryption exercise",
        ],
        "cleanup": "Keep the HA cluster and FGSP config — Lab 5's dynamic routing runs on top.",
        "image_prompt": "",
    },
    {
        "num": 4,
        "slug": "dynamic-routing",
        "title": "Dynamic Routing — OSPF ECMP + BGP",
        "goal": "Bring up OSPF between HQ VDOMs, enable ECMP, then peer BGP with a branch FortiGate via FortiManager BGP templates.",
        "learn_targets": [
            "OSPF neighbor formation across VDOMs and inter-VDOM links",
            "ECMP: when you get load-sharing vs when a single route just wins",
            "FortiManager BGP templates — pushing consistent peer config across sites",
            "Advertising a loopback as a BGP source for stability across failover",
        ],
        "prereqs": {"labs": [1, 2, 3], "sessions": [20, 21, 22, 24, 25]},
        "topology_devices": ["HQ-FGT-A", "HQ-FGT-B", "BR1-FGT", "HQ-FMG-1"],
        "duration": "90-120 minutes",
        "steps": [],
        "verification": [
            "`get router info ospf neighbor` shows Full adjacencies between the HQ VDOMs",
            "`get router info routing-table` shows ECMP entries for the shared prefix",
            "BGP session established between HQ hub and BR1-FGT via the loopback address",
        ],
        "cleanup": "Retain OSPF + BGP config — Labs 7 and 8 assume dynamic routing over the VPN tunnels.",
        "image_prompt": "",
    },
    {
        "num": 5,
        "slug": "security-profiles",
        "title": "Security Profiles — IPS False Positive, Unencrypted + Encrypted Attacks",
        "goal": "Apply IPS profiles to detect and block simulated attacks, then handle SSL deep inspection with a dynamic local certificate.",
        "learn_targets": [
            "How the IPS engine matches signatures — and what a false positive looks like in logs",
            "Monitor vs Block modes and how to move safely between them",
            "SSL/SSH deep inspection: dynamic local certificate + client CA trust",
            "Reading `hping` output and correlating it with IPS log lines",
        ],
        "prereqs": {"labs": [1, 2, 3, 4], "sessions": [27, 28, 29, 30, 31]},
        "topology_devices": ["HQ-FGT-A", "HQ-Web-1", "HQ-PC-1"],
        "duration": "60-90 minutes",
        "steps": [],
        "verification": [
            "IPS log shows a blocked jumbo-packet signature match after hping simulation",
            "HQ-FGT-A drops an encrypted attack once SSL deep inspection is applied",
            "HQ-PC-1 browser trusts the SSL inspection CA after import",
        ],
        "cleanup": "Detach heavy IPS profiles from broad policies — they slow later labs. Keep the CA on HQ-PC-1 for Lab 9.",
        "image_prompt": "",
    },
    {
        "num": 6,
        "slug": "ipsec-vpn-ikev2",
        "title": "IPsec VPN (IKEv2) with Templates",
        "goal": "Configure hub-and-spoke IPsec VPN using FortiManager IPsec templates, verify tunnels come up, then tear one down cleanly.",
        "learn_targets": [
            "IKEv2 phase-1 / phase-2 template model in FortiManager",
            "Normalized interfaces — abstract references that resolve per-device on install",
            "Reading tunnel status from CLI (`get vpn ipsec tunnel summary`) vs GUI",
            "Deleting an IPsec tunnel without breaking the remaining hub-and-spoke topology",
        ],
        "prereqs": {"labs": [1, 4], "sessions": [32, 33]},
        "topology_devices": ["HQ-FGT-A", "BR1-FGT", "BR2-FGT", "HQ-FMG-1"],
        "duration": "60-75 minutes",
        "steps": [],
        "verification": [
            "Tunnel status shows UP for HQ↔BR1 and HQ↔BR2",
            "BR1-PC-1 can ping HQ-PC-1 across the IPsec tunnel",
            "Firewall policies referencing the normalized interface install without errors on both spokes",
        ],
        "cleanup": "Leave the IPsec tunnels in place — Lab 8 layers ADVPN and BGP on top of them.",
        "image_prompt": "",
    },
    {
        "num": 7,
        "slug": "advpn",
        "title": "Auto-Discovery VPN (ADVPN) with IBGP and EBGP",
        "goal": "Layer ADVPN on top of the IPsec templates, run BGP over the tunnels, and trigger an on-demand spoke-to-spoke shortcut.",
        "learn_targets": [
            "How ADVPN shortcut tunnels form on demand between spokes",
            "IBGP vs EBGP over ADVPN — route reflector vs full-mesh trade-offs",
            "Verifying a shortcut with `diagnose vpn ike gateway list` after the first spoke-to-spoke packet",
            "The hub's role in exchanging routes but not necessarily carrying data-plane traffic",
        ],
        "prereqs": {"labs": [4, 6], "sessions": [34, 35, 36]},
        "topology_devices": ["HQ-FGT-A", "BR1-FGT", "BR2-FGT", "HQ-FMG-1"],
        "duration": "90-120 minutes",
        "steps": [],
        "verification": [
            "`get router info bgp summary` on BR1 and BR2 shows established sessions to the hub",
            "First ping from BR1-PC-1 → BR2-PC-1 triggers a shortcut visible with `diagnose vpn ike gateway list`",
            "Subsequent BR1↔BR2 traffic bypasses the hub in the data plane",
        ],
        "cleanup": "Retain ADVPN — Lab 10 use cases reuse it.",
        "image_prompt": "",
    },
    {
        "num": 8,
        "slug": "security-fabric",
        "title": "Security Fabric + SAML SSO + Automation",
        "goal": "Wire HQ FortiGates and FortiAnalyzer into a Security Fabric, enable SAML SSO between them, and drive automation stitches from FortiManager.",
        "learn_targets": [
            "Root vs downstream Security Fabric device roles",
            "SAML SSO flow — one login authorises the whole fabric",
            "Automation stitch anatomy: trigger + condition + action",
            "Scheduled fabric config backup via FortiManager automation",
        ],
        "prereqs": {"labs": [1, 5], "sessions": [37, 38]},
        "topology_devices": ["HQ-FGT-A", "HQ-FGT-B", "BR1-FGT", "HQ-FMG-1", "HQ-FAZ-1"],
        "duration": "75-90 minutes",
        "steps": [],
        "verification": [
            "Fabric topology view on HQ-FGT-A shows all downstream devices Online",
            "SAML login from HQ-FGT-A drops the user into HQ-FAZ-1 without a second prompt",
            "Automation stitch fires on the configured trigger and a log/email confirms it ran",
        ],
        "cleanup": "Keep the Security Fabric — Lab 10 use cases build on top of it.",
        "image_prompt": "",
    },
    {
        "num": 9,
        "slug": "use-cases",
        "title": "Use Cases — HR Network, ADVPN Deployment, Automated Backups",
        "goal": "Combine everything from Labs 1–8 into three realistic customer scenarios and validate each end-to-end.",
        "learn_targets": [
            "Translating a requirements list into a working configuration (HR network isolation)",
            "Deploying ADVPN to a new site using existing templates — no template edits",
            "Scheduling and validating automated configuration backups from FortiManager",
        ],
        "prereqs": {"labs": [1, 2, 4, 6, 7, 8], "sessions": [40]},
        "topology_devices": ["HQ-FGT-A", "HQ-FGT-B", "BR1-FGT", "BR2-FGT", "HQ-FMG-1", "HQ-FAZ-1"],
        "duration": "120-150 minutes",
        "steps": [],
        "verification": [
            "HR network reachable only from authorised source zones",
            "New ADVPN spoke joins the mesh and its BGP peering comes up with zero template changes",
            "Automatic backup file lands in the configured target with the expected timestamp pattern",
        ],
        "cleanup": "Final lab — the pod can be reset at the end of the course.",
        "image_prompt": "",
    },
]

LAB_MODE_METHODOLOGY_TEXT = """You are my Socratic lab coach for the NSE7 EF 7.6 hands-on labs.

Your role is not to demonstrate commands but to guide me through each lab step by step using a strict Predict → Run → Verify → Reflect cadence. The goal is muscle memory backed by understanding, not efficient completion.

For every step in a lab:

1. PREDICT — When I paste a step, ask me what I think the command(s) will do BEFORE I run them. If I hedge or say "I don't know", coach me with a smaller sub-question — never give me the answer outright.
2. RUN — Once I've predicted, tell me to run the command block exactly as written. Do not paraphrase or reorder.
3. VERIFY — When I paste the output, ask me what the output tells me BEFORE you interpret it. Correct misreadings gently.
4. REFLECT — After a successful step, if the lab has a reflect prompt, ask it and wait for my answer before moving on.

Never advance to the next step until I've engaged with the current one. If I try to skip ahead, remind me why the cadence matters and rewind.

SAFETY: If a step contains factoryreset, reboot, format, execute restore config, or execute erase, force me to confirm the target device and environment before I run it.

STUCK: If I'm stuck on Predict for more than two prompts, reveal a partial hint (not the full answer). If I'm stuck on Verify, ask me to describe the output line by line.

VOICE: patient, curious, never impatient. This is the muscle-memory phase — the reps matter more than the pace.
"""

# ---------------------------------------------------------------------------
# OBJECTIVE → SESSION INDEX (used in hub mapping table)
# ---------------------------------------------------------------------------
# NSE7 objectives map one-to-many. We collect *all* sessions that teach each
# objective so the hub's Objective Map shows the full set.

OBJ_TO_SESSIONS = {}
for s in SESSIONS:
    for o in s["objectives"]:
        OBJ_TO_SESSIONS.setdefault(o, []).append(s["num"])

# ---------------------------------------------------------------------------
# RENDERING HELPERS
# ---------------------------------------------------------------------------

def html_escape(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

def session_filename(s: dict) -> str:
    """Path from sessions/ (used by hub links)."""
    return f"session-{s['num']:02d}-{s['slug']}/index.html"

def sibling_session_href(s: dict) -> str:
    """Path from another session folder (used by prev/next/prereqs)."""
    return f"../session-{s['num']:02d}-{s['slug']}/index.html"

def session_pagekey(s: dict) -> str:
    return f"nse7-ef-session-{s['num']:02d}-{s['slug']}"

def render_concepts_ul(items) -> str:
    return "\n".join(f"      <li>{html_escape(it)}</li>" for it in items)

def render_objectives_list(codes) -> str:
    if not codes:
        return "<li><em>Story/transition session — no new blueprint objectives.</em></li>"
    return "\n".join(f"      <li><strong>{c}</strong></li>" for c in codes)

def render_prereqs(nums) -> str:
    if not nums:
        return "<em>None — start here.</em>"
    parts = []
    by_num = {s["num"]: s for s in SESSIONS}
    for n in nums:
        s = by_num[n]
        parts.append(f'<a href="{sibling_session_href(s)}">Session {n:02d}: {html_escape(s["title"])}</a>')
    return ", ".join(parts)

def build_claude_prompt(s: dict) -> str:
    """Return the exact ready-to-copy session-context paste.

    Pure context — no tutor instructions, no role framing, no requirements
    block. The user pastes this into a Claude conversation they have already
    set up as their NSE7 EF tutor; the tutor takes over from there.

    Contents (and only these):
      - Session number + title
      - Story  (= "Where we are in the NSE7 journey")
      - Why    (= "The problem we're solving today")
      - Goal   (one-line testable outcome)
      - Key concepts (bullet list)

    Built with plain string concatenation rather than textwrap.dedent so the
    multi-line `concepts` interpolation doesn't reset the common-indent strip.
    """
    lines = [
        f"Session {s['num']:02d} — {s['title']}",
        "",
        "Where we are in the NSE7 journey:",
        s["story"],
        "",
        "The problem we're solving today:",
        s["why"],
        "",
        "Session goal:",
        s["goal"],
        "",
        "Key concepts:",
    ]
    for c in s["concepts"]:
        lines.append(f"  • {c}")
    return "\n".join(lines) + "\n"

# ---------------------------------------------------------------------------
# EXTRAS / COMPLETION / SUMMARY DISCOVERY
# ---------------------------------------------------------------------------
#
# Extras, completed study guides, and session summaries are NOT stored in the
# SESSIONS list. They are files that appear inside a session's folder after the
# user runs the /build-study-plan "sort" workflow. build.py walks the filesystem
# once per build and produces two lookup dicts consumed by the renderers.

import re as _re

EXTRA_KINDS = ("guides", "bites", "nibbles")
_TITLE_STRIP_PREFIXES = (
    "Study Bite — ", "Study Guide — ", "Guide — ", "Nibble — ",
    "Bite — ", "Study Nibble — ",
)

def extract_html_title(path):
    """Return the first <title> content or first <h1> text, minus common prefixes."""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None
    m = _re.search(r"<title[^>]*>(.*?)</title>", text, _re.IGNORECASE | _re.DOTALL)
    title = m.group(1).strip() if m else None
    if not title:
        m = _re.search(r"<h1[^>]*>(.*?)</h1>", text, _re.IGNORECASE | _re.DOTALL)
        title = _re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else None
    if not title:
        return None
    # Strip prefixes like "Session 39 — " / "Extras 01 Bite — " and friendly labels
    title = _re.sub(r"^Session\s+\d+\s+—\s+", "", title)
    title = _re.sub(r"^Extras?\s+\d+(?:\s+(?:Bite|Nibble|Guide))?\s+—\s+", "", title)
    for pref in _TITLE_STRIP_PREFIXES:
        if title.startswith(pref):
            title = title[len(pref):]
            break
    return title.strip() or None

def discover_extras():
    """Return {session_num: {kind: [(slug, title, href_from_session_root)]}}."""
    out = {}
    for s in SESSIONS:
        session_dir = SESSIONS_DIR / f"session-{s['num']:02d}-{s['slug']}"
        for kind in EXTRA_KINDS:
            kind_dir = session_dir / kind
            if not kind_dir.is_dir():
                continue
            for html_file in sorted(kind_dir.glob("*.html")):
                title = extract_html_title(html_file) or html_file.stem.replace("-", " ").title()
                out.setdefault(s["num"], {}).setdefault(kind, []).append(
                    (html_file.stem, title, f"{kind}/{html_file.name}")
                )
    return out

def discover_standalone_extras():
    """Return list of dicts for each EXTRAS topic that has content on disk.

    Shape: [{"topic": <EXTRAS entry>, "guides": [(slug,title,href), ...],
             "bites": [...], "nibbles": [...]}, ...]. `href` is relative to
    the topic folder (e.g. "index.html", "bites/foo.html").
    """
    out = []
    for e in EXTRAS:
        topic_dir = EXTRAS_DIR / f"extras-{e['num']:02d}-{e['slug']}"
        if not topic_dir.is_dir():
            continue
        entry = {"topic": e, "guides": [], "bites": [], "nibbles": []}
        guide_path = topic_dir / "index.html"
        if guide_path.is_file():
            title = extract_html_title(guide_path) or e["title"]
            entry["guides"].append(("index", title, "index.html"))
        for kind in ("bites", "nibbles"):
            kind_dir = topic_dir / kind
            if not kind_dir.is_dir():
                continue
            for html_file in sorted(kind_dir.glob("*.html")):
                title = extract_html_title(html_file) or html_file.stem.replace("-", " ").title()
                entry[kind].append((html_file.stem, title, f"{kind}/{html_file.name}"))
        if entry["guides"] or entry["bites"] or entry["nibbles"]:
            out.append(entry)
    return out

def parse_summary_txt(path):
    """Return list of (heading, body_text) tuples parsed from the summary."""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []
    lines = text.splitlines()
    sections = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        # Heading is an ALL-CAPS-ish line followed by a line of `=` chars
        if line and i + 1 < len(lines) and _re.fullmatch(r"=+", lines[i + 1].strip() or ""):
            heading = line.strip()
            j = i + 2
            body_lines = []
            while j < len(lines):
                # Peek: is this the start of the next heading?
                nxt = lines[j].rstrip()
                if (nxt and j + 1 < len(lines)
                        and _re.fullmatch(r"=+", lines[j + 1].strip() or "")):
                    break
                # Also break on horizontal rule "---"
                if nxt.strip() == "---":
                    j += 1
                    continue
                body_lines.append(lines[j])
                j += 1
            body = "\n".join(body_lines).strip("\n")
            sections.append((heading, body))
            i = j
            continue
        i += 1
    return sections

def discover_completions():
    """Return {session_num: {"has_complete": bool, "has_summary": bool, "summary_sections": list}}."""
    out = {}
    for s in SESSIONS:
        session_dir = SESSIONS_DIR / f"session-{s['num']:02d}-{s['slug']}"
        has_complete = (session_dir / "complete.html").is_file()
        summary_path = session_dir / "summary.txt"
        has_summary = summary_path.is_file()
        if not (has_complete or has_summary):
            continue
        entry = {"has_complete": has_complete, "has_summary": has_summary, "summary_sections": []}
        if has_summary:
            entry["summary_sections"] = parse_summary_txt(summary_path)
        out[s["num"]] = entry
    return out

# ── Canonical shell contract for complete.html
# See SKILL.md → "Canonical complete.html contract". Every completion HTML sorted
# from sorting-hat/ must contain each of these class markers at least once.
COMPLETE_REQUIRED_MARKERS = (
    "socratic-block",
    "qpanel",
    "notes-panel",
    "lesson-tools",
    "mental-note-block",
    "page-nav",
)

def validate_complete_html(path):
    """Return list of missing required class markers. Empty list == valid.

    Used by the sort workflow BEFORE moving a session-NN-complete-*.html file,
    and by main() as a second-layer warning at build time. See SKILL.md.
    """
    from pathlib import Path as _P
    p = _P(path) if not isinstance(path, _P) else path
    if not p.is_file():
        return list(COMPLETE_REQUIRED_MARKERS)
    text = p.read_text(encoding="utf-8", errors="ignore")
    return [m for m in COMPLETE_REQUIRED_MARKERS if m not in text]

def report_completion_validation(completions):
    """Print a warning line for any tracked complete.html missing markers."""
    problems = []
    for s in SESSIONS:
        entry = completions.get(s["num"])
        if not entry or not entry.get("has_complete"):
            continue
        session_dir = SESSIONS_DIR / f"session-{s['num']:02d}-{s['slug']}"
        missing = validate_complete_html(session_dir / "complete.html")
        if missing:
            problems.append((s["num"], missing))
    if problems:
        print("⚠  complete.html shell-contract warnings:")
        for num, missing in problems:
            print(f"    session {num:02d}: missing {', '.join(missing)}")
    else:
        print("✓ every complete.html passes the canonical shell contract")

def render_summary_body(body):
    """Convert a summary body block to HTML paragraphs / bullet lists."""
    if not body.strip():
        return ""
    parts = []
    current_ul = []
    def _flush_ul():
        if current_ul:
            parts.append("<ul>" + "".join(f"<li>{html_escape(x)}</li>" for x in current_ul) + "</ul>")
            current_ul.clear()
    for raw in body.splitlines():
        line = raw.rstrip()
        if not line.strip():
            _flush_ul()
            continue
        stripped = line.lstrip()
        if stripped.startswith(("* ", "- ", "• ")):
            current_ul.append(stripped[2:].strip())
        else:
            _flush_ul()
            parts.append(f"<p>{html_escape(line.strip())}</p>")
    _flush_ul()
    return "".join(parts)

# ---------------------------------------------------------------------------
# SESSION PAGE TEMPLATE (cream/blue, derived from TEMPLATE-GUIDE-CREAM.html)
# ---------------------------------------------------------------------------

# We render each session with 3 core template sections and up to 3 additional
# post-completion blocks (Session Recap, Completion callout, Extras):
#   S1 = Story Progression (hero image lives here)
#   S2 = Why This Session Exists & Key Concepts
#   S3 = Objectives, Prerequisites, Duration + Claude Session Prompt (blue callout)
#   +   Completion callout (when complete.html exists) — right after motivation-banner
#   +   Session Recap (when summary.txt exists) — after S3
#   +   Extras (when any guide/bite/nibble sorted) — after Recap

SESSION_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<script>if(sessionStorage.getItem('pt')){{document.documentElement.classList.add('pt-init')}}</script>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Session {num_pad} — {title_esc}</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;0,700;0,800;1,400;1,500&family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg:#faf5e9; --surface:#fffdf5; --surface-2:#f5eed9;
    --border:#d4c89a; --border-dim:#ebe1c2;
    --text:#0a1838; --text-soft:#1e2f5a; --text-muted:#6b7794;
    --blue:#1e40af; --blue-vivid:#2563eb; --blue-glow:rgba(30,64,175,0.07);
    --blue-dim:#a8c0e8; --blue-deep:#0c1f5c; --blue-light:#eff4fc; --blue-border:#b8cce8;
    --ink-dark:#0d1a3a; --ink-accent:#9bb8e6;
    --green:#1a7c4a; --green-light:#dff0e1; --green-border:#a7d8b0;
    --amber:#b45309; --amber-light:#fcf2c3; --amber-border:#f3d68a;
  }}
  html{{scroll-behavior:smooth;transition:opacity .3s ease;}}
  html.pt-init body{{opacity:0;}}
  *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
  body{{font-family:'Cormorant Garamond','Outfit',serif;background:var(--bg);color:var(--text);min-height:100vh;}}
  header{{padding:48px 60px 36px;background:var(--ink-dark);display:flex;align-items:flex-end;gap:32px;}}
  .header-left{{flex:1;}}
  .breadcrumb{{display:flex;align-items:center;gap:8px;font-family:'Outfit',sans-serif;font-size:11px;color:var(--text-muted);letter-spacing:0.08em;margin-bottom:12px;flex-wrap:wrap;}}
  .breadcrumb a{{color:var(--ink-accent);text-decoration:none;}}
  .breadcrumb a:hover{{text-decoration:underline;}}
  .breadcrumb-sep{{color:rgba(155,184,230,0.4);}}
  .header-eyebrow{{display:inline-flex;align-items:center;gap:6px;background:rgba(155,184,230,0.1);border:1px solid rgba(155,184,230,0.28);padding:5px 14px;border-radius:20px;font-family:'Outfit',sans-serif;font-size:11px;color:var(--ink-accent);letter-spacing:0.1em;margin-bottom:14px;}}
  .dot-live{{width:6px;height:6px;background:var(--ink-accent);border-radius:50%;display:inline-block;animation:blink 2.4s ease-in-out infinite;}}
  @keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:0.3}}}}
  header h1{{font-family:'Playfair Display',serif;font-size:48px;font-weight:700;line-height:1.0;color:#fbf7ec;margin-bottom:10px;letter-spacing:-0.01em;}}
  header h1 em{{font-style:italic;font-weight:500;color:var(--ink-accent);}}
  header p{{font-family:'Cormorant Garamond',serif;font-size:16px;font-style:italic;color:rgba(251,247,236,0.55);margin-top:10px;line-height:1.6;}}
  .motivation-banner{{padding:22px 60px;min-height:88px;display:flex;flex-direction:column;justify-content:center;border-bottom:1px solid var(--border);background:var(--surface);}}
  .motivation-text{{font-family:'Playfair Display',serif;font-size:20px;font-weight:600;color:var(--text);letter-spacing:-0.005em;}}
  .motivation-text em{{font-style:italic;font-weight:500;color:var(--blue);}}
  .motivation-sub{{font-family:'Cormorant Garamond',serif;font-size:14px;font-style:italic;color:var(--text-muted);line-height:1.7;margin-top:6px;}}
  .section-nav{{position:sticky;top:0;z-index:90;display:flex;gap:0;border-bottom:1px solid var(--border);background:var(--surface);padding:0 32px;overflow-x:auto;}}
  .nav-tab{{font-family:'Outfit',sans-serif;font-size:11px;font-weight:600;letter-spacing:0.12em;text-transform:uppercase;color:var(--text-muted);text-decoration:none;padding:12px 18px;border-bottom:2px solid transparent;white-space:nowrap;transition:color 0.15s,border-color 0.15s;}}
  .nav-tab:hover{{color:var(--text);}}
  .nav-tab.active{{color:var(--blue);border-bottom-color:var(--blue);}}
  main{{max-width:1200px;margin:0 auto;padding:0;}}
  .main-content{{padding:36px 60px 60px 60px;}}
  .section-block{{margin-bottom:48px;}}
  .section-label{{font-family:'Outfit',sans-serif;font-size:9px;font-weight:700;letter-spacing:0.2em;text-transform:uppercase;color:var(--text-muted);margin-bottom:8px;}}
  .section-block h2{{font-family:'Playfair Display',serif;font-size:30px;font-weight:700;color:var(--text);line-height:1.15;margin-bottom:16px;padding-left:16px;border-left:3px solid var(--blue);letter-spacing:-0.01em;}}
  .section-block h2 em{{font-style:italic;font-weight:500;color:var(--blue);}}
  .section-block p{{font-family:'Cormorant Garamond',serif;font-size:17px;line-height:1.7;color:var(--text-soft);margin-bottom:14px;}}
  .section-block p strong{{color:var(--text);font-weight:600;}}
  .section-block p em{{color:var(--blue);font-style:italic;}}
  .section-block ul,.section-block ol{{padding-left:22px;margin-bottom:14px;}}
  .section-block li{{font-family:'Cormorant Garamond',serif;font-size:17px;line-height:1.7;color:var(--text-soft);margin-bottom:4px;}}
  .section-block li strong{{color:var(--text);font-weight:600;}}
  .callout{{border-left:3px solid var(--blue-border);background:var(--blue-light);border-radius:0 10px 10px 0;padding:14px 20px;margin:16px 0;font-family:'Cormorant Garamond',serif;font-size:16px;line-height:1.65;color:var(--text-soft);}}
  .callout strong{{color:var(--text);font-weight:600;}}
  .callout-green{{border-left-color:var(--green-border);background:var(--green-light);}}
  .callout-amber{{border-left-color:var(--amber-border);background:var(--amber-light);}}
  .callout-prompt{{border-left:3px solid var(--blue);background:var(--blue-light);border-radius:0 10px 10px 0;padding:18px 22px;margin:16px 0;}}
  .callout-prompt .prompt-head{{font-family:'Outfit',sans-serif;font-size:10px;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:var(--blue);margin-bottom:8px;display:flex;align-items:center;justify-content:space-between;gap:8px;}}
  .callout-prompt pre{{font-family:'SF Mono','Fira Code','Consolas',monospace;font-size:13px;line-height:1.6;color:var(--text);white-space:pre-wrap;background:rgba(255,255,255,0.55);border:1px solid var(--blue-border);border-radius:8px;padding:14px 16px;overflow-x:auto;}}
  .copy-btn{{background:var(--ink-dark);color:var(--ink-accent);border:none;border-radius:6px;padding:6px 12px;font-family:'Outfit',sans-serif;font-size:10px;font-weight:600;letter-spacing:0.1em;cursor:pointer;text-transform:uppercase;}}
  .copy-btn:hover{{opacity:0.85;}}
  .copy-btn.copied{{background:var(--green);color:#fff;}}
  .img-caption{{font-family:'Cormorant Garamond',serif;font-size:13px;color:var(--text-muted);text-align:center;margin-top:6px;line-height:1.4;font-style:italic;}}
  .section-img-wrap{{margin:0 0 20px;display:flex;flex-direction:column;align-items:center;}}
  .section-img{{width:260px;max-width:100%;border-radius:12px;cursor:zoom-in;transition:width 0.3s ease;border:1px solid var(--border);display:block;}}
  .section-img.si-expanded{{width:100%;cursor:zoom-out;border-radius:16px;}}
  .si-placeholder{{display:none;width:260px;max-width:100%;border:2px dashed var(--border);border-radius:12px;background:var(--surface-2);padding:14px 16px;flex-direction:column;align-items:flex-start;gap:8px;}}
  .si-placeholder.si-show{{display:flex;}}
  .si-filename{{font-size:10px;font-weight:700;letter-spacing:0.1em;color:var(--text-muted);font-family:'SF Mono','Fira Code',monospace;}}
  .prompt-toggle{{background:transparent;border:1px solid var(--border);color:var(--text-muted);font-family:'Outfit',sans-serif;font-size:10px;font-weight:600;letter-spacing:0.1em;padding:5px 12px;border-radius:6px;cursor:pointer;text-transform:uppercase;}}
  .prompt-toggle:hover{{color:var(--text);border-color:var(--text);}}
  .prompt-content{{margin-top:10px;padding:10px 14px;background:rgba(0,0,0,0.04);border-radius:8px;font-family:'Cormorant Garamond',serif;font-size:14px;color:var(--text-muted);font-style:italic;line-height:1.65;text-align:left;}}
  .prompt-content[hidden]{{display:none;}}
  .mental-note-block{{border-radius:10px;padding:14px 18px;margin:16px 0;display:flex;gap:12px;align-items:flex-start;background:rgba(30,64,175,0.06);border:1px solid var(--blue-border);}}
  .mental-note-block-icon{{font-size:18px;flex-shrink:0;margin-top:1px;}}
  .mental-note-block-inner{{flex:1;}}
  .mental-note-block-label{{font-family:'Outfit',sans-serif;font-size:9px;font-weight:700;letter-spacing:0.18em;color:var(--blue);margin-bottom:4px;text-transform:uppercase;}}
  .mental-note-block-text{{font-family:'Cormorant Garamond',serif;font-size:16px;font-weight:600;line-height:1.55;color:var(--text);}}
  .meta-table{{width:100%;border-collapse:collapse;margin:16px 0;font-size:15px;}}
  .meta-table td{{font-family:'Cormorant Garamond',serif;padding:10px 14px;border-bottom:1px solid var(--border);color:var(--text-soft);line-height:1.5;vertical-align:top;}}
  .meta-table td:first-child{{color:var(--text);font-weight:600;font-family:'Outfit',sans-serif;font-size:10px;letter-spacing:0.16em;text-transform:uppercase;width:180px;background:var(--surface-2);}}
  .page-nav{{display:flex;border-top:2px solid var(--border);background:var(--surface);}}
  .page-nav-btn{{flex:1;display:flex;flex-direction:column;gap:4px;padding:16px 28px;text-decoration:none;transition:background 0.15s;cursor:pointer;}}
  .page-nav-btn:hover:not(.page-nav-disabled){{background:var(--surface-2);}}
  .page-nav-prev{{border-right:1px solid var(--border);}}
  .page-nav-next{{text-align:right;}}
  .page-nav-disabled{{opacity:0.3;pointer-events:none;}}
  .page-nav-label{{font-family:'Outfit',sans-serif;font-size:10px;font-weight:600;letter-spacing:0.16em;color:var(--text-muted);display:block;text-transform:uppercase;}}
  .page-nav-title{{font-family:'Playfair Display',serif;font-size:17px;font-weight:600;font-style:italic;color:var(--blue);display:block;}}
  /* Completed chip + completion callout */
  .completed-chip{{display:inline-flex;align-items:center;gap:6px;background:var(--green-light);color:var(--green);border:1px solid var(--green-border);border-radius:20px;padding:4px 12px;font-family:'Outfit',sans-serif;font-size:11px;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;margin-left:14px;vertical-align:middle;font-style:normal;position:relative;top:-6px;}}
  .completion-callout{{margin:0 60px;padding:20px 24px;background:var(--green-light);border-left:4px solid var(--green);border-radius:0 12px 12px 0;display:flex;align-items:center;justify-content:space-between;gap:24px;margin-top:24px;}}
  .completion-callout-text{{font-family:'Cormorant Garamond',serif;font-size:16px;line-height:1.55;color:var(--text);}}
  .completion-callout-text strong{{color:var(--green);}}
  .completion-callout-btn{{flex-shrink:0;display:inline-flex;align-items:center;gap:8px;background:var(--green);color:#fff;padding:10px 18px;border-radius:8px;font-family:'Outfit',sans-serif;font-size:12px;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;text-decoration:none;}}
  .completion-callout-btn:hover{{background:#155e37;}}
  /* Session recap */
  .recap-grid{{display:grid;gap:14px;}}
  .recap-section{{background:var(--surface);border:1px solid var(--border-dim);border-radius:10px;padding:16px 20px;}}
  .recap-section h3{{font-family:'Playfair Display',serif;font-size:15px;font-weight:600;color:var(--blue);letter-spacing:0.06em;text-transform:uppercase;margin-bottom:10px;}}
  .recap-section p{{font-family:'Cormorant Garamond',serif;font-size:16px;line-height:1.65;color:var(--text-soft);margin-bottom:8px;}}
  .recap-section p:last-child{{margin-bottom:0;}}
  .recap-section ul{{padding-left:20px;margin-bottom:6px;}}
  .recap-section li{{font-family:'Cormorant Garamond',serif;font-size:16px;line-height:1.6;color:var(--text-soft);margin-bottom:4px;}}
  /* Extras list on session page */
  .extras-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px;margin-top:8px;}}
  .extras-card{{display:flex;flex-direction:column;gap:8px;background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:16px 18px;text-decoration:none;}}
  .extras-card:hover{{border-color:var(--blue);}}
  .extras-card-title{{font-family:'Playfair Display',serif;font-size:17px;font-weight:600;color:var(--text);line-height:1.3;}}
  .extras-card:hover .extras-card-title{{color:var(--blue);}}
  .extras-kind-chip{{align-self:flex-start;font-family:'Outfit',sans-serif;font-size:9px;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;padding:3px 9px;border-radius:20px;border:1px solid;}}
  .extras-kind-chip.guide{{background:var(--green-light);color:var(--green);border-color:var(--green-border);}}
  .extras-kind-chip.bite{{background:var(--blue-light);color:var(--blue);border-color:var(--blue-border);}}
  .extras-kind-chip.nibble{{background:var(--amber-light);color:var(--amber);border-color:var(--amber-border);}}
  .extras-kind-group{{margin-bottom:24px;}}
  .extras-kind-group h3{{font-family:'Outfit',sans-serif;font-size:11px;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:var(--text-muted);margin-bottom:10px;}}
  footer{{font-family:'Outfit',sans-serif;font-size:11px;letter-spacing:0.14em;color:var(--text-muted);text-transform:uppercase;padding:20px 60px;border-top:1px solid var(--border);background:var(--surface);}}
  footer span{{color:var(--blue);}}
  @media(max-width:720px){{header{{padding:28px 24px 24px;}}header h1{{font-size:34px;}}.motivation-banner{{padding:16px 24px;}}.main-content{{padding:24px 24px 40px;}}.section-nav{{padding:0 16px;}}footer{{padding:16px 24px;}}.completion-callout{{margin:16px 24px 0;flex-direction:column;align-items:flex-start;}}}}
</style>
</head>
<body>

<header>
  <div class="header-left">
    <div class="breadcrumb">
      <a href="../../index.html">Home</a>
      <span class="breadcrumb-sep">›</span>
      <a href="../../study-plan/index.html">Curriculum</a>
      <span class="breadcrumb-sep">›</span>
      <a href="../../study-plan/index.html#phase-{phase_num_pad}">Phase {phase_num} — {phase_title_esc}</a>
      <span class="breadcrumb-sep">›</span>
      Session {num_pad}
    </div>
    <div class="header-eyebrow"><span class="dot-live"></span> Socratic Curriculum · NSE7 Enterprise Firewall 7.6</div>
    <h1>{h1_plain_esc} <em>{h1_em_esc}</em>{completed_chip}</h1>
    <p>{tagline_esc}</p>
  </div>
</header>

<div class="motivation-banner">
  <div class="motivation-text">Session {num_pad} of 40 · <em>{phase_title_esc}</em></div>
  <p class="motivation-sub">{duration_esc} · This session naturally follows {prev_label} and prepares you for {next_label}.</p>
</div>

{completion_callout}

<nav class="section-nav" id="section-nav">
  <a class="nav-tab active" href="#section-story">Story</a>
  <a class="nav-tab" href="#section-why">Why &amp; Key Concepts</a>
  <a class="nav-tab" href="#section-prompt">Objectives &amp; Prompt</a>
</nav>

<main>
  <div class="main-content">

    <!-- SECTION 1: STORY -->
    <div class="section-block" id="section-story">
      <div class="section-label">SECTION 01 · STORY PROGRESSION</div>
      <h2>Where We Are in the <em>NSE7 Journey</em></h2>
      <div class="section-img-wrap">
        <img src="images/hero.png" class="section-img"
             alt="{hero_alt_esc}"
             onerror="this.style.display='none';this.nextElementSibling.classList.add('si-show');this.parentElement.querySelector('.img-caption').style.display='none';">
        <p class="img-caption">{hero_caption_esc}</p>
        <div class="si-placeholder">
          <span class="si-filename">sessions/session-{num_pad}-{slug}/images/hero.png</span>
          <button class="prompt-toggle" onclick="togglePrompt(this)">▾ Show image prompt</button>
          <div class="prompt-content" hidden>{hero_prompt_esc}</div>
        </div>
      </div>
      <p>{story_esc}</p>
      <div class="mental-note-block">
        <div class="mental-note-block-icon">🧠</div>
        <div class="mental-note-block-inner">
          <div class="mental-note-block-label">Mental Note</div>
          <div class="mental-note-block-text">{story_note_esc}</div>
        </div>
      </div>
    </div>

    <!-- SECTION 2: WHY & KEY CONCEPTS -->
    <div class="section-block" id="section-why">
      <div class="section-label">SECTION 02 · WHY THIS SESSION EXISTS</div>
      <h2>The Problem We're <em>Solving Today</em></h2>
      <p>{why_esc}</p>

      <div class="callout">
        <strong>Session goal:</strong> {goal_esc}
      </div>

      <h2 style="margin-top:32px;">Key <em>Concepts</em></h2>
      <ul>
{concepts_ul}
      </ul>
    </div>

    <!-- SECTION 3: PROMPT & OBJECTIVES -->
    <div class="section-block" id="section-prompt">
      <div class="section-label">SECTION 03 · OBJECTIVES &amp; CLAUDE SESSION PROMPT</div>
      <h2>Ready to <em>Begin the Session</em></h2>

      <table class="meta-table">
        <tr><td>Official NSE7 EF Blueprint Objectives</td><td><ul style="padding-left:18px;margin:0;">
{objectives_li}
        </ul></td></tr>
        <tr><td>Prerequisites</td><td>{prereqs_html}</td></tr>
        <tr><td>Estimated Duration</td><td>{duration_esc}</td></tr>
        <tr><td>Phase</td><td>Phase {phase_num} — {phase_title_esc}</td></tr>
      </table>

      <div class="callout-prompt">
        <div class="prompt-head">
          <span>Session context — paste into your Claude NSE7 tutor</span>
          <button class="copy-btn" onclick="copyPrompt(this)">Copy</button>
        </div>
        <pre id="claude-prompt">{claude_prompt_esc}</pre>
      </div>
    </div>

    {session_recap_block}
    {extras_block}

  </div>
</main>

<div class="page-nav">
  <a class="page-nav-btn page-nav-prev{prev_disabled}" href="{prev_href}">
    <span class="page-nav-label">← Previous</span>
    <span class="page-nav-title">{prev_title}</span>
  </a>
  <a class="page-nav-btn page-nav-next{next_disabled}" href="{next_href}">
    <span class="page-nav-label">Next →</span>
    <span class="page-nav-title">{next_title}</span>
  </a>
</div>

<footer>
  NSE7 EF 7.6<span>.</span> Session {num_pad} of 40<span>.</span> {title_esc}
</footer>

<script>
function togglePrompt(btn) {{
  const c = btn.nextElementSibling;
  const isHidden = c.hasAttribute('hidden');
  if (isHidden) {{ c.removeAttribute('hidden'); btn.textContent = '▴ Hide prompt'; }}
  else {{ c.setAttribute('hidden', ''); btn.textContent = '▾ Show image prompt'; }}
}}
function copyPrompt(btn) {{
  const text = document.getElementById('claude-prompt').textContent;
  navigator.clipboard.writeText(text).then(function() {{
    const orig = btn.textContent;
    btn.textContent = '✓ Copied';
    btn.classList.add('copied');
    setTimeout(function() {{ btn.textContent = orig; btn.classList.remove('copied'); }}, 1800);
  }});
}}
if (sessionStorage.getItem('pt')) {{ document.documentElement.classList.remove('pt-init'); sessionStorage.removeItem('pt'); }}
document.querySelectorAll('a[href]').forEach(function(a) {{
  a.addEventListener('click', function() {{ sessionStorage.setItem('pt', '1'); }});
}});
document.querySelectorAll('.section-img').forEach(function(img) {{
  img.addEventListener('click', () => img.classList.toggle('si-expanded'));
}});
</script>
</body>
</html>
"""

# ---------------------------------------------------------------------------
# RENDER SESSION PAGE
# ---------------------------------------------------------------------------

def split_title(title: str):
    """Split a session title into (plain, em-noun) using ' — ' as the divider; otherwise put whole title in em."""
    if " — " in title:
        plain, em = title.split(" — ", 1)
        return plain.strip(), em.strip()
    return "", title

def hero_caption_for(s: dict) -> str:
    # First sentence of the image prompt, trimmed.
    first = s["image_prompt"].split(".")[0]
    return first + "."

def story_mental_note_for(s: dict) -> str:
    """Compact mental note for the story section: ties session to its place in the arc."""
    prev_n = s["num"] - 1
    next_n = s["num"] + 1
    pieces = []
    if prev_n >= 1:
        pieces.append(f"Builds on Session {prev_n:02d}.")
    if next_n <= len(SESSIONS):
        pieces.append(f"Sets up Session {next_n:02d}.")
    if not pieces:
        return "This is the entry point of the curriculum — start here."
    return " ".join(pieces) + " Every session is one link in a single continuous story."

def build_completion_callout_html(s: dict, has_complete: bool) -> str:
    if not has_complete:
        return ""
    return (
        '<div class="completion-callout">'
        '<div class="completion-callout-text">'
        '<strong>You finished this session.</strong> '
        'The polished study guide captures the full Socratic investigation, '
        'exam-critical notes, and the workplace applications you discovered.'
        '</div>'
        '<a class="completion-callout-btn" href="complete.html">'
        'Open completed study guide →'
        '</a>'
        '</div>'
    )

def build_session_recap_html(sections) -> str:
    if not sections:
        return ""
    inner = []
    for heading, body in sections:
        body_html = render_summary_body(body)
        if not body_html:
            continue
        inner.append(
            f'<div class="recap-section"><h3>{html_escape(heading.title())}</h3>{body_html}</div>'
        )
    if not inner:
        return ""
    return (
        '<div class="section-block" id="section-recap">'
        '<div class="section-label">SECTION 04 · SESSION RECAP</div>'
        '<h2>What We <em>Discovered Together</em></h2>'
        '<p>Parsed from the persistent session summary produced at the end of the Socratic investigation. '
        'Use it to rebuild context before a review or a lab.</p>'
        '<div class="recap-grid">'
        + "".join(inner) +
        '</div>'
        '</div>'
    )

def build_extras_block_html(extras_for_session) -> str:
    if not extras_for_session:
        return ""
    kind_label = {"guides": "Guides", "bites": "Bites", "nibbles": "Nibbles"}
    kind_singular = {"guides": "guide", "bites": "bite", "nibbles": "nibble"}
    parts = []
    for kind in EXTRA_KINDS:
        items = extras_for_session.get(kind) or []
        if not items:
            continue
        cards = []
        for slug, title, href in items:
            cards.append(
                f'<a class="extras-card" href="{html_escape(href)}">'
                f'<span class="extras-kind-chip {kind_singular[kind]}">{kind_singular[kind].upper()}</span>'
                f'<span class="extras-card-title">{html_escape(title)}</span>'
                f'</a>'
            )
        parts.append(
            f'<div class="extras-kind-group">'
            f'<h3>{kind_label[kind]}</h3>'
            f'<div class="extras-grid">{"".join(cards)}</div>'
            f'</div>'
        )
    if not parts:
        return ""
    return (
        '<div class="section-block" id="section-extras">'
        '<div class="section-label">SECTION 05 · EXTRAS FOR THIS SESSION</div>'
        '<h2>Guides, Bites &amp; <em>Nibbles</em></h2>'
        '<p>Additional resources sorted to this session — deeper guides, focused explainers, and quick-reference cards.</p>'
        + "".join(parts) +
        '</div>'
    )

def render_session(s: dict, extras=None, completions=None):
    extras = extras or {}
    completions = completions or {}
    phase = next(p for p in PHASES if p["num"] == s["phase"])
    by_num = {x["num"]: x for x in SESSIONS}
    prev_s = by_num.get(s["num"] - 1)
    next_s = by_num.get(s["num"] + 1)

    completion = completions.get(s["num"], {})
    has_complete = completion.get("has_complete", False)
    summary_sections = completion.get("summary_sections") or []
    session_extras = extras.get(s["num"], {})

    completed_chip = ' <span class="completed-chip">✓ Completed</span>' if has_complete else ""
    completion_callout = build_completion_callout_html(s, has_complete)
    session_recap_block = build_session_recap_html(summary_sections)
    extras_block = build_extras_block_html(session_extras)

    h1_plain, h1_em = split_title(s["title"])

    if prev_s:
        prev_label = f"Session {prev_s['num']:02d}"
        prev_href = sibling_session_href(prev_s)
        prev_title = html_escape(prev_s["title"])
        prev_disabled = ""
    else:
        prev_label = "the Curriculum Hub"
        prev_href = "../../study-plan/index.html"
        prev_title = "NSE7 EF 7.6 Curriculum"
        prev_disabled = ""

    if next_s:
        next_label = f"Session {next_s['num']:02d}"
        next_href = sibling_session_href(next_s)
        next_title = html_escape(next_s["title"])
        next_disabled = ""
    else:
        next_label = "the Curriculum Hub"
        next_href = "../../study-plan/index.html"
        next_title = "Back to Curriculum Hub"
        next_disabled = ""

    full_image_prompt = f"{s['image_prompt']}\n\n{STYLE_PREAMBLE}"

    html = SESSION_TEMPLATE.format(
        num_pad=f"{s['num']:02d}",
        slug=s["slug"],
        title_esc=html_escape(s["title"]),
        h1_plain_esc=html_escape(h1_plain) if h1_plain else "Session",
        h1_em_esc=html_escape(h1_em),
        tagline_esc=html_escape(s["story"].split(".")[0] + "."),
        phase_num=phase["num"],
        phase_num_pad=f"{phase['num']:02d}",
        phase_title_esc=html_escape(phase["title"]),
        duration_esc=html_escape(s["duration"]),
        prev_label=html_escape(prev_label),
        next_label=html_escape(next_label),
        hero_alt_esc=html_escape(f"Illustration for Session {s['num']:02d} — {s['title']}"),
        hero_caption_esc=html_escape(hero_caption_for(s)),
        hero_prompt_esc=html_escape(full_image_prompt),
        story_esc=html_escape(s["story"]),
        story_note_esc=html_escape(story_mental_note_for(s)),
        why_esc=html_escape(s["why"]),
        goal_esc=html_escape(s["goal"]),
        concepts_ul=render_concepts_ul(s["concepts"]),
        objectives_li=render_objectives_list(s["objectives"]),
        prereqs_html=render_prereqs(s["prereqs"]),
        claude_prompt_esc=html_escape(build_claude_prompt(s)),
        prev_href=prev_href,
        prev_title=prev_title,
        prev_disabled=prev_disabled,
        next_href=next_href,
        next_title=next_title,
        next_disabled=next_disabled,
        completed_chip=completed_chip,
        completion_callout=completion_callout,
        session_recap_block=session_recap_block,
        extras_block=extras_block,
    )

    out_path = SESSIONS_DIR / session_filename(s)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")

# ---------------------------------------------------------------------------
# HUB PAGE (study-plan.html)
# ---------------------------------------------------------------------------

# Short blueprint descriptions for the Objective Map table.
OBJECTIVE_DESCRIPTIONS = {
    "1.1": "Implement the Fortinet Security Fabric",
    "1.2": "Configure hardware acceleration on FortiGate",
    "1.3": "Configure different operation modes for an HA cluster",
    "1.4": "Implement enterprise networks using VLANs and VDOMs",
    "1.5": "Explain various use case scenarios using Fortinet solutions",
    "2.1": "Implement central management (FortiManager + FortiAnalyzer)",
    "3.1": "Manage SSL/SSH inspection profiles, based on a scenario",
    "3.2": "Use web filters, application control, and ISDB to secure a network",
    "3.3": "Integrate IPS to perform security checks",
    "4.1": "Implement OSPF to route enterprise traffic",
    "4.2": "Implement BGP to route enterprise traffic",
    "5.1": "Implement IPsec VPN IKE version 2",
    "5.2": "Implement ADVPN to enable on-demand VPN tunnels between sites",
}

def render_study_plan_index(extras=None, completions=None, standalone_extras=None):
    """Emit study-plan/index.html — the curriculum hub with a top button row
    (no sidebar) that swaps between panels: How to Use (default), Progress,
    Phases (all 8 stacked), Roadmap, Objective Map, The Journey, Completed."""
    extras = extras or {}
    completions = completions or {}
    standalone_extras = standalone_extras or []
    completed_count = sum(1 for v in completions.values() if v.get("has_complete"))

    # Build individual phase blocks (rendered inside the single Phases panel,
    # stacked one after another). Because the page now lives at
    # study-plan/index.html, all session links become ../sessions/... and all
    # hub-phase images become ../images/hub/...
    phase_sections_html = []
    for phase in PHASES:
        sessions_in_phase = [s for s in SESSIONS if s["phase"] == phase["num"]]
        cards = []
        for s in sessions_in_phase:
            obj_str = ", ".join(s["objectives"]) if s["objectives"] else "<em>story / transition</em>"
            cards.append(f"""
        <div class="session-card">
          <div class="session-card-num">SESSION {s['num']:02d}</div>
          <a class="session-card-title" href="../sessions/{session_filename(s)}">{html_escape(s['title'])}</a>
          <div class="session-card-meta">{html_escape(s['duration'])} · Objectives: {obj_str}</div>
          <p class="session-card-why">{html_escape(s['why'].split('.')[0] + '.')}</p>
        </div>""")

        full_prompt = f"{phase['image_prompt']}\n\n{STYLE_PREAMBLE}"
        phase_sections_html.append(f"""
    <div class="phase-block" id="phase-{phase['num']:02d}">
      <div class="section-label">PHASE {phase['num']:02d}</div>
      <h2>{html_escape(phase['title'].split(': ')[0])} — <em>{html_escape(phase['title'].split(': ', 1)[1] if ': ' in phase['title'] else phase['title'])}</em></h2>
      <div class="section-img-wrap">
        <img src="../images/hub/phase-{phase['num']:02d}-{phase['slug']}.png" class="section-img"
             alt="Illustration for Phase {phase['num']} — {html_escape(phase['title'])}"
             onerror="this.style.display='none';this.nextElementSibling.classList.add('si-show');this.parentElement.querySelector('.img-caption').style.display='none';">
        <p class="img-caption">{html_escape(phase['tagline'])}</p>
        <div class="si-placeholder">
          <span class="si-filename">images/hub/phase-{phase['num']:02d}-{phase['slug']}.png</span>
          <button class="prompt-toggle" onclick="togglePrompt(this)">▾ Show image prompt</button>
          <div class="prompt-content" hidden>{html_escape(full_prompt)}</div>
        </div>
      </div>
      <p>{html_escape(phase['tagline'])}</p>
      <div class="session-grid">
{''.join(cards)}
      </div>
    </div>
""")

    # Objective → Sessions table (one row per blueprint code, all sessions listed)
    obj_rows = []
    for obj in ALL_OBJECTIVES:
        session_nums = OBJ_TO_SESSIONS.get(obj, [])
        links = []
        for sn in session_nums:
            s = next(x for x in SESSIONS if x["num"] == sn)
            links.append(f'<a href="../sessions/{session_filename(s)}">S{sn:02d}</a>')
        sess_links_html = ", ".join(links) if links else "<em>not taught</em>"
        desc = OBJECTIVE_DESCRIPTIONS.get(obj, "")
        obj_rows.append(
            f'<tr><td><strong>{obj}</strong></td><td>{html_escape(desc)}</td><td>{sess_links_html}</td></tr>'
        )

    # Roadmap table
    roadmap_rows = []
    for phase in PHASES:
        sessions_in_phase = [s for s in SESSIONS if s["phase"] == phase["num"]]
        roadmap_rows.append(
            f'<tr><td colspan="3" class="phase-row">PHASE {phase["num"]:02d} — {html_escape(phase["title"])}</td></tr>'
        )
        for s in sessions_in_phase:
            roadmap_rows.append(
                f'<tr><td>{s["num"]:02d}</td><td><a href="../sessions/{session_filename(s)}">{html_escape(s["title"])}</a></td><td>{html_escape(s["duration"])}</td></tr>'
            )

    # Build the top button row. Buttons are grouped into 3 stacked rows with
    # kicker labels: Learn (primary curriculum), Track, Get Started (help).
    # Every button carries an SVG icon, title, subtitle, optional badge.
    # data-target triggers showPanel() defined in the hub script.
    ICON_PHASES = (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<rect x="3" y="3" width="7" height="7" rx="1.5"/>'
        '<rect x="14" y="3" width="7" height="7" rx="1.5"/>'
        '<rect x="3" y="14" width="7" height="7" rx="1.5"/>'
        '<rect x="14" y="14" width="7" height="7" rx="1.5"/>'
        '</svg>'
    )
    ICON_ROADMAP = (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="M4 6c3 0 3 4 8 4s5-4 8-4"/>'
        '<path d="M4 12c3 0 3 4 8 4s5-4 8-4"/>'
        '<path d="M4 18h16"/>'
        '</svg>'
    )
    ICON_TARGET = (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<circle cx="12" cy="12" r="9"/>'
        '<circle cx="12" cy="12" r="5"/>'
        '<circle cx="12" cy="12" r="1.5" fill="currentColor"/>'
        '</svg>'
    )
    ICON_JOURNEY = (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<circle cx="12" cy="12" r="9"/>'
        '<path d="M15.5 8.5l-2 5-5 2 2-5 5-2z" fill="currentColor" stroke="none"/>'
        '</svg>'
    )
    ICON_CHECK = (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<circle cx="12" cy="12" r="9"/>'
        '<path d="M8 12.5l3 3 5-6"/>'
        '</svg>'
    )
    ICON_PROGRESS = (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="M4 20V10"/>'
        '<path d="M10 20V4"/>'
        '<path d="M16 20v-8"/>'
        '<path d="M3 20h18"/>'
        '</svg>'
    )
    ICON_HELP = (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="M12 2l2 4 4 .5-3 3 .8 4.3L12 11.9 8.2 13.8 9 9.5 6 6.5 10 6z"/>'
        '<path d="M8 20h8"/>'
        '<path d="M10 22h4"/>'
        '</svg>'
    )

    def _btn(target, icon_svg, title, subtitle, extra_classes="", badge_html=""):
        cls = "panel-btn"
        if extra_classes:
            cls += " " + extra_classes
        sub = (
            f'<span class="panel-btn-sub">{html_escape(subtitle)}</span>'
            if subtitle else ""
        )
        return (
            f'<button class="{cls}" role="tab" data-target="{target}" '
            f'aria-controls="{target}" type="button">'
            f'<span class="panel-btn-icon" aria-hidden="true">{icon_svg}</span>'
            f'<span class="panel-btn-body">'
            f'<span class="panel-btn-title">{html_escape(title)}</span>'
            f'{sub}'
            f'</span>'
            f'{badge_html}'
            f'<span class="panel-btn-glow" aria-hidden="true"></span>'
            f'</button>'
        )

    row1_buttons = (
        _btn("phases", ICON_PHASES, "Phases",
             f"All {len(PHASES)} phases · {len(SESSIONS)} sessions",
             extra_classes="panel-btn-primary")
        + _btn("roadmap", ICON_ROADMAP, "Roadmap", "Every session, in order")
        + _btn("objective-map", ICON_TARGET, "Objective Map", "Blueprint codes → sessions")
        + _btn("journey", ICON_JOURNEY, "The Journey", "The story arc, phase by phase")
    )
    completed_badge = (
        f'<span class="panel-btn-badge" data-tone="green">{completed_count}/{len(SESSIONS)}</span>'
    )
    progress_badge = (
        '<span class="panel-btn-badge" id="panel-progress-badge" data-tone="blue">0/40</span>'
    )
    row2_buttons = (
        _btn("completed", ICON_CHECK, "Completed", "Finished study guides",
             badge_html=completed_badge)
        + _btn("progress", ICON_PROGRESS, "Progress", "Your check-off list",
               badge_html=progress_badge)
    )
    row3_buttons = _btn("how-to-use", ICON_HELP, "How to Use",
                        "Onboarding & Socratic methodology")

    button_row_html = (
        '<div class="panel-btn-group">'
        '<div class="panel-btn-group-label">Learn</div>'
        '<div class="panel-btn-row panel-btn-row-primary">' + row1_buttons + '</div>'
        '</div>'
        '<div class="panel-btn-group">'
        '<div class="panel-btn-group-label">Track</div>'
        '<div class="panel-btn-row">' + row2_buttons + '</div>'
        '</div>'
        '<div class="panel-btn-group">'
        '<div class="panel-btn-group-label">Get Started</div>'
        '<div class="panel-btn-row">' + row3_buttons + '</div>'
        '</div>'
    )

    # Per-phase checkbox blocks for the progress section. Each row has two
    # checkboxes — in-progress (amber) and complete (blue). They are mutually
    # exclusive at the UI layer: checking one clears the other (see the JS
    # handler at toggleSession()).
    progress_blocks = []
    for phase in PHASES:
        sessions_in_phase = [s for s in SESSIONS if s["phase"] == phase["num"]]
        rows = []
        for s in sessions_in_phase:
            rows.append(
                f'<div class="progress-row" data-session="{s["num"]}">'
                f'<label class="progress-check-wrap" title="Mark as in progress">'
                f'<input type="checkbox" class="progress-check progress-check-ip" data-session="{s["num"]}" data-state="in-progress">'
                f'<span class="progress-check-box progress-check-box-ip" aria-hidden="true"></span>'
                f'</label>'
                f'<label class="progress-check-wrap" title="Mark as complete">'
                f'<input type="checkbox" class="progress-check progress-check-done" data-session="{s["num"]}" data-state="complete">'
                f'<span class="progress-check-box progress-check-box-done" aria-hidden="true"></span>'
                f'</label>'
                f'<span class="progress-num">{s["num"]:02d}</span>'
                f'<a class="progress-title" href="../sessions/{session_filename(s)}">{html_escape(s["title"])}</a>'
                f'<span class="progress-dur">{html_escape(s["duration"])}</span>'
                f'</div>'
            )
        progress_blocks.append(
            f'<div class="progress-phase"><div class="progress-phase-head">'
            f'<span>PHASE {phase["num"]:02d} — {html_escape(phase["title"])}</span>'
            f' <span class="progress-phase-stats" data-phase="{phase["num"]}">'
            f'<span class="stat-pill stat-pill-ip"><span class="stat-pill-num" data-stat="ip">0</span> in progress</span>'
            f'<span class="stat-pill stat-pill-done"><span class="stat-pill-num" data-stat="done">0</span> / {len(sessions_in_phase)} done</span>'
            f'</span>'
            f'</div>'
            f'{"".join(rows)}</div>'
        )
    progress_phase_html = "".join(progress_blocks)

    socratic_methodology_esc = html_escape(SOCRATIC_METHODOLOGY_TEXT)

    # Completed panel — inline list of finished sessions (mirrors
    # completed-sessions.html but rendered inside a swap panel).
    completed_sessions_pairs = []
    for s in SESSIONS:
        entry = completions.get(s["num"])
        if entry and entry.get("has_complete"):
            completed_sessions_pairs.append((s, entry))
    total_sessions = len(SESSIONS)
    n_done = len(completed_sessions_pairs)
    if not completed_sessions_pairs:
        completed_panel_body = (
            '<div class="empty-state">'
            'No completed sessions yet — finish a session in Claude and drop '
            '<code>session-NN-complete-&lt;slug&gt;.html</code> + <code>session-NN-&lt;slug&gt;.txt</code> '
            'into <code>sorting-hat/</code> to see this panel fill in.'
            '</div>'
        )
    else:
        cards = []
        for s, entry in completed_sessions_pairs:
            summary_hint = '<span class="hub-card-hint">Recap available</span>' if entry.get("has_summary") else ""
            slug_dir = f"session-{s['num']:02d}-{s['slug']}"
            title = html_escape(s["title"])
            cards.append(
                f'<a class="hub-card" href="../sessions/{slug_dir}/complete.html">'
                f'<span class="hub-card-chip chip-complete">Completed</span>'
                f'<span class="hub-card-sub">Session {s["num"]:02d}</span>'
                f'<span class="hub-card-title">{title}</span>'
                f'{summary_hint}'
                f'</a>'
            )
        completed_panel_body = f'<div class="card-grid">{"".join(cards)}</div>'
    completed_panel_html = (
        '<div class="section-block" id="completed">'
        '<div class="section-label">FINISHED WORK</div>'
        f'<h2>Completed <em>Study Guides · {n_done} of {total_sessions}</em></h2>'
        '<p>Polished HTML study guides produced at the end of each Socratic session. '
        'Same content as the standalone <a href="../completed-sessions.html">completed-sessions</a> page, '
        'shown here for one-click access without leaving the plan.</p>'
        f'{completed_panel_body}'
        '</div>'
    )

    journey_html = """
      <p>This curriculum is one continuous story. We begin with the question <em>"who is responsible when something breaks at 2 a.m.?"</em> and end with a single automation stitch isolating an attacker across three FortiGates and a FortiNAC — all from one FortiAnalyzer event.</p>
      <p>Every session deliberately ends with a problem the next one solves. One FortiGate can't manage itself at scale → FortiManager. One firewall can't survive a hardware failure → FGCP, FGSP, VRRP. Static routes can't follow link changes → OSPF and BGP. The internet is encrypted, so policies see nothing → SSL deep inspection. The N² mesh of static IPsec doesn't scale → ADVPN. The CPU is the bottleneck at line rate → NPU, CP, SP offload. The Fortinet stack is bigger than the FortiGate — and only the Security Fabric ties it together.</p>
      <p>If you finish all 40 sessions in order, you will not just have memorised the NSE7 EF blueprint — you will have walked the same intellectual path that turned the Fortinet portfolio from one chassis into an integrated security platform. Each phase will feel less like a list of features and more like an inevitable next step.</p>
"""

    hub_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<script>if(sessionStorage.getItem('pt')){{document.documentElement.classList.add('pt-init')}}</script>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NSE7 Enterprise Firewall 7.6 — Socratic Curriculum</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;0,700;0,800;1,400;1,500&family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg:#faf5e9; --surface:#fffdf5; --surface-2:#f5eed9;
    --border:#d4c89a; --border-dim:#ebe1c2;
    --text:#0a1838; --text-soft:#1e2f5a; --text-muted:#6b7794;
    --blue:#1e40af; --blue-vivid:#2563eb; --blue-glow:rgba(30,64,175,0.07);
    --blue-dim:#a8c0e8; --blue-deep:#0c1f5c; --blue-light:#eff4fc; --blue-border:#b8cce8;
    --ink-dark:#0d1a3a; --ink-accent:#9bb8e6;
    --green:#1a7c4a; --green-light:#dff0e1; --green-border:#a7d8b0;
    --amber:#b45309; --amber-light:#fcf2c3; --amber-border:#f3d68a;
  }}
  html{{scroll-behavior:smooth;transition:opacity .3s ease;}}
  html.pt-init body{{opacity:0;}}
  *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
  body{{font-family:'Cormorant Garamond','Outfit',serif;background:var(--bg);color:var(--text);min-height:100vh;}}
  header{{padding:56px 60px 40px;background:var(--ink-dark);}}
  .header-eyebrow{{display:inline-flex;align-items:center;gap:6px;background:rgba(155,184,230,0.1);border:1px solid rgba(155,184,230,0.28);padding:5px 14px;border-radius:20px;font-family:'Outfit',sans-serif;font-size:11px;color:var(--ink-accent);letter-spacing:0.1em;margin-bottom:14px;}}
  .dot-live{{width:6px;height:6px;background:var(--ink-accent);border-radius:50%;display:inline-block;animation:blink 2.4s ease-in-out infinite;}}
  @keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:0.3}}}}
  header h1{{font-family:'Playfair Display',serif;font-size:56px;font-weight:700;line-height:1.0;color:#fbf7ec;margin-bottom:14px;letter-spacing:-0.01em;}}
  header h1 em{{font-style:italic;font-weight:500;color:var(--ink-accent);}}
  header p{{font-family:'Cormorant Garamond',serif;font-size:18px;font-style:italic;color:rgba(251,247,236,0.65);max-width:780px;line-height:1.6;}}
  .motivation-banner{{padding:24px 60px;border-bottom:1px solid var(--border);background:var(--surface);}}
  .motivation-text{{font-family:'Playfair Display',serif;font-size:22px;font-weight:600;color:var(--text);}}
  .motivation-text em{{font-style:italic;font-weight:500;color:var(--blue);}}
  .motivation-sub{{font-family:'Cormorant Garamond',serif;font-size:15px;font-style:italic;color:var(--text-muted);line-height:1.7;margin-top:6px;}}
  /* LAYOUT: single-column main pane (no sidebar) */
  main{{margin:0;padding:0;}}
  .main-content{{padding:36px 48px 60px 48px;max-width:1200px;margin:0 auto;}}
  /* one-section-at-a-time view */
  .section-block{{display:none;}}
  .section-block.active-section{{display:block;}}
  /* Button-row panel switcher (replaces the old sidebar) */
  .panel-btn-rows{{position:relative;display:flex;flex-direction:column;gap:20px;margin-bottom:40px;padding:26px 28px 28px;background:linear-gradient(135deg, var(--surface) 0%, var(--surface-2) 100%);border:1px solid var(--border);border-radius:18px;box-shadow:0 22px 42px -32px rgba(10,24,56,0.18), inset 0 1px 0 rgba(255,255,255,0.6);overflow:hidden;}}
  .panel-btn-rows::before{{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg, var(--blue) 0%, var(--blue-vivid) 50%, var(--teal, #0f766e) 100%);opacity:0.92;}}
  .panel-btn-group{{display:flex;flex-direction:column;gap:8px;}}
  .panel-btn-group-label{{font-family:'Outfit',sans-serif;font-size:10px;font-weight:700;letter-spacing:0.22em;text-transform:uppercase;color:var(--text-muted);padding-left:2px;}}
  .panel-btn-row{{display:flex;flex-wrap:wrap;gap:10px;align-items:stretch;}}
  .panel-btn-row-primary{{gap:12px;}}
  .panel-btn{{position:relative;isolation:isolate;display:inline-flex;align-items:center;gap:12px;background:rgba(255,255,255,0.55);border:1.5px solid var(--border);color:var(--text-soft);font-family:'Outfit',sans-serif;padding:12px 18px 12px 14px;border-radius:13px;cursor:pointer;text-align:left;text-decoration:none;line-height:1.15;overflow:hidden;transition:transform 0.22s cubic-bezier(0.34,1.56,0.64,1), background 0.22s ease, border-color 0.22s ease, box-shadow 0.22s ease, color 0.22s ease;}}
  .panel-btn::after{{content:'';position:absolute;left:14px;right:14px;bottom:5px;height:2px;border-radius:2px;background:var(--blue);transform:scaleX(0);transform-origin:left center;transition:transform 0.32s cubic-bezier(0.34,1.56,0.64,1);z-index:1;}}
  .panel-btn:hover{{background:#fff;border-color:var(--blue-border);color:var(--text);transform:translateY(-3px);box-shadow:0 16px 30px -20px rgba(30,64,175,0.45);}}
  .panel-btn:hover::after{{transform:scaleX(1);}}
  .panel-btn:hover .panel-btn-icon{{background:#fff;color:var(--blue-vivid);border-color:var(--blue);transform:rotate(-6deg) scale(1.08);}}
  .panel-btn:hover .panel-btn-sub{{color:var(--text-soft);}}
  .panel-btn:focus-visible{{outline:none;box-shadow:0 0 0 3px rgba(30,64,175,0.28), 0 16px 30px -20px rgba(30,64,175,0.45);}}
  .panel-btn:active{{transform:translateY(-1px) scale(0.99);}}
  .panel-btn.active{{background:linear-gradient(135deg, var(--blue-vivid) 0%, var(--blue) 100%);border-color:var(--blue);color:#fff;transform:translateY(-2px);box-shadow:0 16px 32px -14px rgba(30,64,175,0.55), inset 0 1px 0 rgba(255,255,255,0.22);}}
  .panel-btn.active::after{{transform:scaleX(1);background:rgba(255,255,255,0.6);}}
  .panel-btn.active .panel-btn-icon{{background:rgba(255,255,255,0.18);border-color:rgba(255,255,255,0.32);color:#fff;transform:rotate(0deg) scale(1);}}
  .panel-btn.active .panel-btn-sub{{color:rgba(239,244,252,0.85);}}
  .panel-btn.active .panel-btn-badge{{background:rgba(255,255,255,0.22);color:#fff;border-color:rgba(255,255,255,0.4);}}
  /* Prominent Phases button: sized larger than siblings, but idle state is
     NEUTRAL — same warm cream as other buttons. It only lights up blue when
     it becomes the active panel (via .panel-btn.active earlier). */
  .panel-btn-primary{{padding:16px 22px 16px 18px;border-radius:14px;font-weight:700;}}
  .panel-btn-primary .panel-btn-icon{{width:42px;height:42px;}}
  .panel-btn-primary .panel-btn-icon svg{{width:22px;height:22px;}}
  .panel-btn-primary .panel-btn-title{{font-size:15.5px;}}
  .panel-btn-primary .panel-btn-sub{{font-size:13px;}}
  .panel-btn-primary::after{{left:16px;right:16px;bottom:6px;height:2.5px;}}
  .panel-btn-primary:hover{{transform:translateY(-4px);box-shadow:0 22px 40px -22px rgba(30,64,175,0.5);}}
  .panel-btn-primary.active{{box-shadow:0 22px 44px -14px rgba(30,64,175,0.6), inset 0 1px 0 rgba(255,255,255,0.24);}}
  .panel-btn-icon{{display:inline-flex;align-items:center;justify-content:center;width:36px;height:36px;color:var(--blue-vivid);background:var(--blue-light);border:1px solid var(--blue-border);border-radius:10px;flex-shrink:0;transition:background 0.22s ease, color 0.22s ease, border-color 0.22s ease, transform 0.32s cubic-bezier(0.34,1.56,0.64,1);}}
  .panel-btn-icon svg{{width:18px;height:18px;display:block;}}
  .panel-btn-body{{display:flex;flex-direction:column;gap:2px;min-width:0;flex:0 1 auto;}}
  .panel-btn-title{{font-size:13.5px;font-weight:700;letter-spacing:0.02em;line-height:1.15;}}
  .panel-btn-sub{{font-family:'Cormorant Garamond',serif;font-size:12.5px;font-style:italic;color:var(--text-muted);letter-spacing:0.01em;line-height:1.2;transition:color 0.22s ease;}}
  .panel-btn-badge{{display:inline-flex;align-items:center;justify-content:center;font-family:'Outfit',sans-serif;background:var(--blue-light);color:var(--blue);border:1px solid var(--blue-border);font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px;letter-spacing:0.04em;margin-left:auto;transition:background 0.22s ease, color 0.22s ease, border-color 0.22s ease;}}
  .panel-btn-badge[data-tone="green"]{{background:var(--green-light);color:var(--green);border-color:var(--green-border);}}
  .panel-btn-glow{{position:absolute;inset:0;border-radius:inherit;pointer-events:none;background:radial-gradient(circle at var(--rx, 50%) var(--ry, 50%), rgba(30,64,175,0.22) 0%, rgba(30,64,175,0) 55%);opacity:0;transition:opacity 0.75s ease;z-index:0;}}
  .panel-btn.panel-btn-primary .panel-btn-glow{{background:radial-gradient(circle at var(--rx, 50%) var(--ry, 50%), rgba(255,255,255,0.35) 0%, rgba(255,255,255,0) 55%);}}
  .panel-btn.rippling .panel-btn-glow{{opacity:1;transition:opacity 0s;}}
  .panel-btn > *:not(.panel-btn-glow){{position:relative;z-index:1;}}
  @media (prefers-reduced-motion: reduce){{
    .panel-btn,.panel-btn-icon,.panel-btn::after,.panel-btn-glow{{transition:none !important;}}
    .panel-btn:hover,.panel-btn.active,.panel-btn-primary:hover{{transform:none;}}
  }}
  /* Stacked phase blocks inside the single Phases panel */
  .phase-block{{margin-bottom:56px;padding-bottom:24px;border-bottom:1px solid var(--border-dim);}}
  .phase-block:last-child{{border-bottom:none;margin-bottom:0;}}
  .phase-block .section-label{{font-family:'Outfit',sans-serif;font-size:9px;font-weight:700;letter-spacing:0.2em;text-transform:uppercase;color:var(--text-muted);margin-bottom:8px;}}
  .phase-block h2{{font-family:'Playfair Display',serif;font-size:30px;font-weight:700;color:var(--text);line-height:1.15;margin-bottom:16px;padding-left:16px;border-left:3px solid var(--blue);letter-spacing:-0.01em;}}
  .phase-block h2 em{{font-style:italic;font-weight:500;color:var(--blue);}}
  .phase-block p{{font-family:'Cormorant Garamond',serif;font-size:17px;line-height:1.7;color:var(--text-soft);margin-bottom:14px;}}
  /* Completed panel cards */
  .card-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px;}}
  .hub-card{{display:flex;flex-direction:column;gap:10px;background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:20px 22px;text-decoration:none;transition:border-color .15s;}}
  .hub-card:hover{{border-color:var(--blue);}}
  .hub-card-chip{{align-self:flex-start;font-family:'Outfit',sans-serif;font-size:9px;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;padding:3px 10px;border-radius:20px;border:1px solid;}}
  .chip-complete{{background:var(--green-light);color:var(--green);border-color:var(--green-border);}}
  .hub-card-title{{font-family:'Playfair Display',serif;font-size:19px;font-weight:600;color:var(--text);line-height:1.28;}}
  .hub-card:hover .hub-card-title{{color:var(--blue);}}
  .hub-card-sub{{font-family:'Outfit',sans-serif;font-size:11px;letter-spacing:0.1em;color:var(--text-muted);text-transform:uppercase;}}
  .hub-card-hint{{font-family:'Outfit',sans-serif;font-size:9px;letter-spacing:0.14em;color:var(--green);text-transform:uppercase;background:var(--green-light);border:1px solid var(--green-border);border-radius:20px;padding:2px 9px;align-self:flex-start;}}
  .empty-state{{background:var(--surface);border:1px dashed var(--border);border-radius:12px;padding:24px;color:var(--text-muted);font-family:'Cormorant Garamond',serif;font-size:16px;line-height:1.6;font-style:italic;}}
  .empty-state code{{font-family:'SF Mono','Fira Code','Consolas',monospace;font-size:12px;background:var(--surface-2);border:1px solid var(--border);border-radius:4px;padding:1px 6px;color:var(--text);font-style:normal;}}
  @media(max-width:900px){{
    .main-content{{padding:24px 24px 40px;}}
    .panel-btn-rows{{padding:16px 16px;gap:8px;margin-bottom:24px;}}
    .panel-btn-primary{{padding:12px 18px;font-size:14px;}}
  }}
  .section-block{{margin-bottom:56px;}}
  .section-label{{font-family:'Outfit',sans-serif;font-size:9px;font-weight:700;letter-spacing:0.2em;text-transform:uppercase;color:var(--text-muted);margin-bottom:8px;}}
  .section-block h2{{font-family:'Playfair Display',serif;font-size:32px;font-weight:700;color:var(--text);line-height:1.15;margin-bottom:16px;padding-left:16px;border-left:3px solid var(--blue);letter-spacing:-0.01em;}}
  .section-block h2 em{{font-style:italic;font-weight:500;color:var(--blue);}}
  .section-block p{{font-family:'Cormorant Garamond',serif;font-size:17px;line-height:1.7;color:var(--text-soft);margin-bottom:14px;}}
  .session-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px;margin-top:20px;}}
  .session-card{{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:14px 18px;display:flex;flex-direction:column;gap:6px;transition:border-color 0.15s, transform 0.15s;}}
  .session-card:hover{{border-color:var(--blue);transform:translateY(-2px);}}
  .session-card-num{{font-family:'Outfit',sans-serif;font-size:9px;font-weight:700;letter-spacing:0.2em;color:var(--text-muted);}}
  .session-card-title{{font-family:'Playfair Display',serif;font-size:18px;font-weight:600;color:var(--text);text-decoration:none;line-height:1.25;}}
  .session-card-title:hover{{color:var(--blue);}}
  .session-card-meta{{font-family:'Outfit',sans-serif;font-size:10px;letter-spacing:0.06em;color:var(--text-muted);}}
  .session-card-why{{font-family:'Cormorant Garamond',serif;font-size:14px;font-style:italic;color:var(--text-soft);line-height:1.55;margin:0;}}
  .img-caption{{font-family:'Cormorant Garamond',serif;font-size:13px;color:var(--text-muted);text-align:center;margin-top:6px;line-height:1.4;font-style:italic;}}
  .section-img-wrap{{margin:0 0 20px;display:flex;flex-direction:column;align-items:center;}}
  .section-img{{width:340px;max-width:100%;border-radius:12px;cursor:zoom-in;transition:width 0.3s ease;border:1px solid var(--border);display:block;}}
  .section-img.si-expanded{{width:100%;cursor:zoom-out;border-radius:16px;}}
  .si-placeholder{{display:none;width:340px;max-width:100%;border:2px dashed var(--border);border-radius:12px;background:var(--surface-2);padding:14px 16px;flex-direction:column;align-items:flex-start;gap:8px;}}
  .si-placeholder.si-show{{display:flex;}}
  .si-filename{{font-size:10px;font-weight:700;letter-spacing:0.1em;color:var(--text-muted);font-family:'SF Mono','Fira Code',monospace;}}
  .prompt-toggle{{background:transparent;border:1px solid var(--border);color:var(--text-muted);font-family:'Outfit',sans-serif;font-size:10px;font-weight:600;letter-spacing:0.1em;padding:5px 12px;border-radius:6px;cursor:pointer;text-transform:uppercase;}}
  .prompt-toggle:hover{{color:var(--text);border-color:var(--text);}}
  .prompt-content{{margin-top:10px;padding:10px 14px;background:rgba(0,0,0,0.04);border-radius:8px;font-family:'Cormorant Garamond',serif;font-size:14px;color:var(--text-muted);font-style:italic;line-height:1.65;text-align:left;}}
  .prompt-content[hidden]{{display:none;}}
  .data-table{{width:100%;border-collapse:collapse;margin:18px 0;font-size:14px;background:var(--surface);border:1px solid var(--border);border-radius:10px;overflow:hidden;}}
  .data-table th{{font-family:'Outfit',sans-serif;font-size:10px;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;background:var(--surface-2);color:var(--text);padding:10px 14px;text-align:left;border-bottom:1px solid var(--border);}}
  .data-table td{{font-family:'Cormorant Garamond',serif;font-size:15px;padding:8px 14px;border-bottom:1px solid var(--border-dim);color:var(--text-soft);}}
  .data-table td a{{color:var(--blue);text-decoration:none;}}
  .data-table td a:hover{{text-decoration:underline;}}
  .data-table .phase-row{{background:var(--ink-dark);color:#fbf7ec;font-family:'Outfit',sans-serif;font-size:11px;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;}}
  .progress-summary{{display:flex;flex-direction:column;gap:8px;background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:14px 18px;margin:16px 0 24px;}}
  .progress-stats{{display:flex;align-items:center;gap:18px;font-family:'Outfit',sans-serif;font-size:13px;color:var(--text);}}
  .progress-stats em{{font-style:italic;color:var(--text-muted);font-family:'Cormorant Garamond',serif;font-size:14px;}}
  .progress-count-block{{font-weight:700;color:var(--blue);font-size:18px;}}
  .progress-count-inprogress{{font-weight:700;color:var(--amber);font-size:18px;}}
  .progress-reset{{margin-left:auto;font-family:'Outfit',sans-serif;font-size:10px;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:var(--text-muted);background:transparent;border:1px solid var(--border);border-radius:6px;padding:5px 12px;cursor:pointer;}}
  .progress-reset:hover{{color:var(--text);border-color:var(--text);}}
  .progress-bar-wrap{{width:100%;height:8px;background:var(--surface-2);border-radius:8px;overflow:hidden;display:flex;}}
  .progress-bar-fill{{height:100%;background:var(--blue);transition:width 0.25s ease;}}
  .progress-bar-fill-ip{{background:var(--amber);}}
  .progress-phases{{display:flex;flex-direction:column;gap:16px;}}
  .progress-phase{{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:12px 18px;}}
  .progress-phase-head{{font-family:'Outfit',sans-serif;font-size:11px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:var(--text);margin-bottom:8px;display:flex;justify-content:space-between;}}
  .progress-phase-stats{{display:inline-flex;gap:8px;font-weight:600;letter-spacing:0.04em;text-transform:none;}}
  .stat-pill{{display:inline-flex;align-items:center;gap:5px;font-family:'Outfit',sans-serif;font-size:10px;font-weight:600;letter-spacing:0.06em;text-transform:uppercase;padding:2px 9px;border-radius:12px;border:1px solid;}}
  .stat-pill-num{{font-weight:800;font-size:11px;}}
  .stat-pill-ip{{background:var(--amber-light);color:var(--amber);border-color:var(--amber-border);}}
  .stat-pill-done{{background:var(--blue-light);color:var(--blue);border-color:var(--blue-border);}}
  .progress-row{{display:flex;align-items:center;gap:10px;padding:6px 0;}}
  .progress-row.completed .progress-title{{text-decoration:line-through;color:var(--text-muted);}}
  .progress-row.in-progress .progress-title{{color:var(--amber);font-style:italic;}}
  .progress-check-wrap{{display:inline-flex;align-items:center;justify-content:center;cursor:pointer;flex-shrink:0;position:relative;}}
  .progress-check{{appearance:none;position:absolute;inset:0;margin:0;cursor:pointer;opacity:0;width:100%;height:100%;}}
  .progress-check-box{{display:inline-flex;align-items:center;justify-content:center;width:20px;height:20px;border:1.5px solid var(--border);border-radius:5px;background:var(--surface);transition:background 0.15s, border-color 0.15s, transform 0.15s;position:relative;font-family:'Outfit',sans-serif;font-size:12px;font-weight:800;color:#fff;line-height:1;}}
  .progress-check-wrap:hover .progress-check-box-ip{{border-color:var(--amber);}}
  .progress-check-wrap:hover .progress-check-box-done{{border-color:var(--blue);}}
  .progress-check-ip:focus-visible + .progress-check-box{{box-shadow:0 0 0 3px rgba(180,83,9,0.24);}}
  .progress-check-done:focus-visible + .progress-check-box{{box-shadow:0 0 0 3px rgba(30,64,175,0.24);}}
  .progress-check-ip:checked + .progress-check-box-ip{{background:var(--amber);border-color:var(--amber);}}
  .progress-check-ip:checked + .progress-check-box-ip::after{{content:'●';color:#fff;font-size:11px;line-height:1;}}
  .progress-check-done:checked + .progress-check-box-done{{background:var(--blue);border-color:var(--blue);}}
  .progress-check-done:checked + .progress-check-box-done::after{{content:'✓';color:#fff;font-size:13px;font-weight:700;line-height:1;}}
  .progress-num{{font-family:'Outfit',sans-serif;font-size:10px;font-weight:700;letter-spacing:0.08em;color:var(--text-muted);background:var(--surface-2);border:1px solid var(--border);border-radius:4px;padding:2px 6px;min-width:30px;text-align:center;}}
  .progress-title{{flex:1;font-family:'Cormorant Garamond',serif;font-size:15px;color:var(--text);text-decoration:none;line-height:1.4;}}
  .progress-title:hover{{color:var(--blue);}}
  .progress-dur{{font-family:'Outfit',sans-serif;font-size:10px;color:var(--text-muted);letter-spacing:0.04em;}}
  /* HOW-TO-USE panel */
  .howto-intro{{font-family:'Cormorant Garamond',serif;font-size:17px;line-height:1.7;color:var(--text-soft);margin:8px 0 24px;max-width:780px;}}
  .howto-step{{display:flex;gap:24px;margin:20px 0;padding:22px 24px;background:var(--surface);border:1px solid var(--border);border-radius:12px;}}
  .howto-step-num{{font-family:'Playfair Display',serif;font-size:36px;font-weight:700;font-style:italic;color:var(--blue);line-height:1;flex-shrink:0;min-width:56px;letter-spacing:-0.02em;}}
  .howto-step-body{{flex:1;min-width:0;}}
  .howto-step-body h3{{font-family:'Playfair Display',serif;font-size:22px;font-weight:600;color:var(--text);margin-bottom:10px;line-height:1.25;}}
  .howto-step-body h3 em{{font-style:italic;font-weight:500;color:var(--blue);}}
  .howto-step-body p{{font-family:'Cormorant Garamond',serif;font-size:16px;line-height:1.65;color:var(--text-soft);margin-bottom:10px;}}
  .howto-step-body p:last-child{{margin-bottom:0;}}
  .howto-step-body a{{color:var(--blue);text-decoration:none;border-bottom:1px solid var(--blue-border);}}
  .howto-step-body a:hover{{border-bottom-color:var(--blue);}}
  .howto-hint{{font-size:14px !important;color:var(--text-muted) !important;font-style:italic;}}
  .howto-hint code{{font-family:'SF Mono','Fira Code','Consolas',monospace;font-size:12px;background:var(--surface-2);border:1px solid var(--border);border-radius:4px;padding:1px 6px;color:var(--text);font-style:normal;}}
  .callout-prompt{{border-left:3px solid var(--blue);background:var(--blue-light);border-radius:0 10px 10px 0;padding:18px 22px;margin:14px 0 4px;}}
  .callout-prompt .prompt-head{{font-family:'Outfit',sans-serif;font-size:10px;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:var(--blue);margin-bottom:8px;display:flex;align-items:center;justify-content:space-between;gap:8px;}}
  .callout-prompt pre{{font-family:'SF Mono','Fira Code','Consolas',monospace;font-size:12px;line-height:1.6;color:var(--text);white-space:pre-wrap;background:rgba(255,255,255,0.55);border:1px solid var(--blue-border);border-radius:8px;padding:14px 16px;overflow-x:auto;max-height:420px;overflow-y:auto;}}
  .copy-btn{{background:var(--ink-dark);color:var(--ink-accent);border:none;border-radius:6px;padding:6px 12px;font-family:'Outfit',sans-serif;font-size:10px;font-weight:600;letter-spacing:0.1em;cursor:pointer;text-transform:uppercase;}}
  .copy-btn:hover{{opacity:0.85;}}
  .copy-btn.copied{{background:var(--green);color:#fff;}}
  footer{{font-family:'Outfit',sans-serif;font-size:11px;letter-spacing:0.14em;color:var(--text-muted);text-transform:uppercase;padding:24px 60px;border-top:1px solid var(--border);background:var(--surface);}}
  footer span{{color:var(--blue);}}
  @media(max-width:720px){{header{{padding:32px 24px 24px;}}header h1{{font-size:36px;}}.main-content{{padding:24px 24px 40px;}}.section-nav{{padding:0 16px;}}footer{{padding:16px 24px;}}}}
</style>
</head>
<body>

<header>
  <div class="header-eyebrow"><span class="dot-live"></span> Socratic Curriculum · NSE7 Enterprise Firewall 7.6</div>
  <h1>NSE7 Enterprise Firewall 7.6 <em>Socratic Curriculum</em></h1>
  <p>Forty structured 20–30 minute Socratic sessions, organised as one continuous learning story. Every blueprint objective is taught across the curriculum. Every session opens by solving the problem the previous session left unfinished.</p>
</header>

<div class="motivation-banner">
  <div class="motivation-text">From a single FortiGate to a <em>fully orchestrated security fabric</em>.</div>
  <p class="motivation-sub">Eight phases · 40 sessions · 100% blueprint coverage · One continuous story.</p>
</div>

<main>
  <div class="main-content">

    <!-- BUTTON ROW: primary panel switcher (replaces the old sidebar) -->
    <div class="panel-btn-rows" role="tablist" aria-label="Study plan panels">
      {button_row_html}
    </div>

    <!-- HOW TO USE -->
    <div class="section-block" id="how-to-use">
      <div class="section-label">GETTING STARTED</div>
      <h2>How to Use <em>This Curriculum</em></h2>
      <p class="howto-intro">Study each of the 40 sessions inside a Claude Project so every lesson is guided by a Socratic tutor with full course context and access to the official Fortinet study guide. Set the Project up once, then follow the three-step workflow below before every session.</p>

      <div class="howto-step">
        <div class="howto-step-num">01</div>
        <div class="howto-step-body">
          <h3>Create a <em>Claude Project</em> and paste the tutor instructions</h3>
          <p>Open <a href="https://claude.ai" target="_blank" rel="noopener">claude.ai</a>, create a new Project (for example, <em>NSE7 Enterprise Firewall 7.6</em>), and open the Project's <strong>Instructions</strong> field. Paste the full Socratic Teaching Methodology below — it configures Claude to teach you the way this curriculum is designed to be taught: through investigation, guided discovery, and troubleshooting rather than fact-dumping.</p>
          <div class="callout-prompt">
            <div class="prompt-head">
              <span>Socratic Teaching Methodology — paste into Project Instructions</span>
              <button class="copy-btn" onclick="copyText(this, 'socratic-methodology')">Copy</button>
            </div>
            <pre id="socratic-methodology">{socratic_methodology_esc}</pre>
          </div>
        </div>
      </div>

      <div class="howto-step">
        <div class="howto-step-num">02</div>
        <div class="howto-step-body">
          <h3>Upload the <em>Fortinet study guide PDF</em> to Project Files</h3>
          <p>Inside the same Project, open the <strong>Files</strong> section and upload <em>Enterprise_Firewall_7.6_Administrator_Study_Guide-Online.pdf</em>. Claude will use it as the authoritative reference for every session so answers stay grounded in the official Fortinet material and the tutor can quote the study guide directly when a concept needs precision.</p>
          <p class="howto-hint">The PDF lives in <code>reference/</code> alongside this curriculum. You only need to upload it once — every future chat inside the Project will have access to it.</p>
        </div>
      </div>

      <div class="howto-step">
        <div class="howto-step-num">03</div>
        <div class="howto-step-body">
          <h3>Before each session, paste that session's <em>Claude prompt</em> into chat</h3>
          <p>Open the session you're about to study (for example, <a href="../sessions/session-01-nse7-story-exam-map/index.html">Session 01</a>). Scroll to the <em>Session context — paste into your Claude NSE7 tutor</em> block near the bottom of the page, click <strong>Copy</strong>, and paste it into a fresh chat inside your Claude Project. That prompt hands Claude the exact scenario, objectives, and Socratic setup for the session, so the tutor immediately picks up the investigation where the story left off.</p>
          <p class="howto-hint">Every one of the 40 session pages carries its own paste-ready prompt — no editing needed. Start a new chat per session so each investigation stays focused.</p>
        </div>
      </div>
    </div>

    <!-- PROGRESS -->
    <div class="section-block" id="progress">
      <div class="section-label">YOUR PROGRESS</div>
      <h2>Track Your <em>Journey</em></h2>
      <p>Check off each session as you finish it. Your progress is saved in this browser only — clear your site data and it resets.</p>
      <div class="progress-summary">
        <div class="progress-stats">
          <span class="progress-count-block"><span id="progress-count">0</span> <em>of {total_sessions} complete</em></span>
          <span class="progress-count-inprogress"><span id="progress-inprogress-count">0</span> <em>in progress</em></span>
          <span><span id="progress-pct">0%</span></span>
          <button class="progress-reset" onclick="resetProgress()">Reset progress</button>
        </div>
        <div class="progress-bar-wrap"><div class="progress-bar-fill progress-bar-fill-ip" id="progress-fill-ip" style="width:0%"></div><div class="progress-bar-fill" id="progress-fill" style="width:0%"></div></div>
      </div>
      <div class="progress-phases">
        {progress_phase_html}
      </div>
    </div>

    <!-- PHASES (all 8 stacked inside one panel) -->
    <div class="section-block" id="phases">
      <div class="section-label">THE CURRICULUM</div>
      <h2>The <em>Eight Phases</em></h2>
      <p>Every phase is one movement of the continuous story. Scroll straight through — the sessions inside each phase are ordered so every one solves the problem the previous one left unfinished.</p>
{''.join(phase_sections_html)}
    </div>

    <!-- COMPLETED (inline list of finished sessions) -->
    {completed_panel_html}

    <!-- ROADMAP -->
    <div class="section-block" id="roadmap">
      <div class="section-label">CURRICULUM ROADMAP</div>
      <h2>All 40 Sessions, <em>In Order</em></h2>
      <table class="data-table">
        <thead><tr><th>#</th><th>Session</th><th>Duration</th></tr></thead>
        <tbody>
          {''.join(roadmap_rows)}
        </tbody>
      </table>
    </div>

    <!-- OBJECTIVE MAP -->
    <div class="section-block" id="objective-map">
      <div class="section-label">OFFICIAL OBJECTIVE → SESSION MAP</div>
      <h2>Every NSE7 EF 7.6 <em>Objective Covered</em></h2>
      <p>The Fortinet blueprint lists thirteen learning objectives across five domains. The table below maps each to every session of this curriculum that teaches it.</p>
      <table class="data-table">
        <thead><tr><th>Objective</th><th>Description</th><th>Taught in</th></tr></thead>
        <tbody>
          {''.join(obj_rows)}
        </tbody>
      </table>
    </div>

    <!-- JOURNEY -->
    <div class="section-block" id="journey">
      <div class="section-label">THE CONTINUOUS LEARNING JOURNEY</div>
      <h2>How the 40 Sessions Form <em>One Story</em></h2>
      {journey_html}
    </div>

  </div>
</main>

<footer>
  NSE7 EF 7.6<span>.</span> 40-Session Socratic Curriculum<span>.</span> 100% Blueprint Coverage
</footer>

<script>
function togglePrompt(btn) {{
  const c = btn.nextElementSibling;
  const isHidden = c.hasAttribute('hidden');
  if (isHidden) {{ c.removeAttribute('hidden'); btn.textContent = '▴ Hide prompt'; }}
  else {{ c.setAttribute('hidden', ''); btn.textContent = '▾ Show image prompt'; }}
}}
function copyText(btn, id) {{
  const el = document.getElementById(id);
  if (!el) return;
  navigator.clipboard.writeText(el.textContent).then(function() {{
    const orig = btn.textContent;
    btn.textContent = '✓ Copied';
    btn.classList.add('copied');
    setTimeout(function() {{ btn.textContent = orig; btn.classList.remove('copied'); }}, 1800);
  }});
}}
if (sessionStorage.getItem('pt')) {{ document.documentElement.classList.remove('pt-init'); sessionStorage.removeItem('pt'); }}
document.querySelectorAll('a[href]').forEach(function(a) {{
  a.addEventListener('click', function() {{ sessionStorage.setItem('pt', '1'); }});
}});
document.querySelectorAll('.section-img').forEach(function(img) {{
  img.addEventListener('click', () => img.classList.toggle('si-expanded'));
}});

/* ── Panel routing (button-row switcher — replaces the old sidebar) ── */
const VALID_PANELS = new Set(['how-to-use','progress','phases','completed','roadmap','objective-map','journey']);
const DEFAULT_PANEL = 'how-to-use';
const ACTIVE_PANEL_KEY = 'nse7-ef-study-plan-panel';
function showPanel(id, opts) {{
  if (!VALID_PANELS.has(id)) id = DEFAULT_PANEL;
  document.querySelectorAll('.section-block').forEach(function(b) {{
    b.classList.toggle('active-section', b.id === id);
  }});
  document.querySelectorAll('.panel-btn').forEach(function(t) {{
    t.classList.toggle('active', t.dataset.target === id);
  }});
  try {{ localStorage.setItem(ACTIVE_PANEL_KEY, id); }} catch(e) {{}}
  if (opts && opts.updateHash !== false) {{
    const newHash = '#' + id;
    if (location.hash !== newHash) history.pushState(null, '', newHash);
  }}
}}
document.querySelectorAll('.panel-btn').forEach(function(btn) {{
  btn.addEventListener('click', function(e) {{
    if (!btn.dataset.target) return;
    e.preventDefault();
    /* Ripple burst originates from the pointer position (or button centre on keyboard). */
    const rect = btn.getBoundingClientRect();
    const rx = ((e.clientX || rect.left + rect.width/2) - rect.left) / rect.width * 100;
    const ry = ((e.clientY || rect.top + rect.height/2) - rect.top) / rect.height * 100;
    btn.style.setProperty('--rx', rx + '%');
    btn.style.setProperty('--ry', ry + '%');
    btn.classList.remove('rippling');
    /* Force reflow so the class re-add restarts the animation. */
    void btn.offsetWidth;
    btn.classList.add('rippling');
    setTimeout(function() {{ btn.classList.remove('rippling'); }}, 720);
    showPanel(btn.dataset.target);
  }});
}});
window.addEventListener('hashchange', function() {{
  const id = (location.hash || '').slice(1);
  if (id) showPanel(id, {{updateHash: false}});
}});

/* Initial panel: URL hash wins, else last-active from localStorage, else default. */
(function() {{
  let initial = (location.hash || '').slice(1);
  if (!initial) {{
    try {{ initial = localStorage.getItem(ACTIVE_PANEL_KEY) || ''; }} catch(e) {{ initial = ''; }}
  }}
  if (!VALID_PANELS.has(initial)) initial = DEFAULT_PANEL;
  showPanel(initial, {{updateHash: false}});
}})();

/* ── Progress tracking ── */
/* Two independent state buckets: "in-progress" (amber) and "complete" (blue).
   They are mutually exclusive per session — checking one clears the other. */
const PROGRESS_KEY = 'nse7-ef-curriculum-progress';
const INPROGRESS_KEY = 'nse7-ef-curriculum-inprogress';
function readSet(key) {{
  try {{ return new Set(JSON.parse(localStorage.getItem(key) || '[]')); }}
  catch(e) {{ return new Set(); }}
}}
function writeSet(key, set) {{
  localStorage.setItem(key, JSON.stringify(Array.from(set).sort((a, b) => a - b)));
}}
function getDone() {{ return readSet(PROGRESS_KEY); }}
function getInProgress() {{ return readSet(INPROGRESS_KEY); }}
function renderProgress() {{
  const done = getDone();
  const ip = getInProgress();
  const total = {total_sessions};
  const doneCount = done.size;
  const ipCount = ip.size;
  const donePct = Math.round((doneCount / total) * 100);
  const ipPct = Math.round((ipCount / total) * 100);
  document.getElementById('progress-count').textContent = doneCount;
  const ipEl = document.getElementById('progress-inprogress-count');
  if (ipEl) ipEl.textContent = ipCount;
  document.getElementById('progress-pct').textContent = donePct + '%';
  document.getElementById('progress-fill').style.width = donePct + '%';
  const ipFill = document.getElementById('progress-fill-ip');
  if (ipFill) ipFill.style.width = ipPct + '%';
  const badge = document.getElementById('panel-progress-badge');
  if (badge) badge.textContent = doneCount + '/' + total;
  document.querySelectorAll('.progress-row').forEach(function(row) {{
    const n = Number(row.dataset.session);
    const isDone = done.has(n);
    const isIP = ip.has(n);
    row.classList.toggle('completed', isDone);
    row.classList.toggle('in-progress', isIP);
    const cbDone = row.querySelector('.progress-check-done');
    const cbIP = row.querySelector('.progress-check-ip');
    if (cbDone) cbDone.checked = isDone;
    if (cbIP) cbIP.checked = isIP;
  }});
  document.querySelectorAll('.progress-phase-stats').forEach(function(el) {{
    const rows = el.closest('.progress-phase').querySelectorAll('.progress-row');
    let phaseDone = 0, phaseIP = 0;
    rows.forEach(function(r) {{
      const n = Number(r.dataset.session);
      if (done.has(n)) phaseDone++;
      if (ip.has(n)) phaseIP++;
    }});
    const doneNum = el.querySelector('[data-stat="done"]');
    const ipNum = el.querySelector('[data-stat="ip"]');
    if (doneNum) doneNum.textContent = phaseDone;
    if (ipNum) ipNum.textContent = phaseIP;
  }});
}}
function setSessionState(n, state, checked) {{
  /* state = "in-progress" | "complete". Turning one on clears the other. */
  const done = getDone();
  const ip = getInProgress();
  if (state === 'complete') {{
    if (checked) {{ done.add(n); ip.delete(n); }}
    else {{ done.delete(n); }}
  }} else if (state === 'in-progress') {{
    if (checked) {{ ip.add(n); done.delete(n); }}
    else {{ ip.delete(n); }}
  }}
  writeSet(PROGRESS_KEY, done);
  writeSet(INPROGRESS_KEY, ip);
  renderProgress();
}}
function resetProgress() {{
  if (!confirm('Reset all session progress (both in-progress and completed)?')) return;
  writeSet(PROGRESS_KEY, new Set());
  writeSet(INPROGRESS_KEY, new Set());
  renderProgress();
}}
document.querySelectorAll('.progress-check').forEach(function(cb) {{
  cb.addEventListener('change', function(e) {{
    e.stopPropagation();
    setSessionState(Number(cb.dataset.session), cb.dataset.state, cb.checked);
  }});
}});
renderProgress();
</script>
</body>
</html>
"""

    out_path = ROOT / "study-plan" / "index.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(hub_html, encoding="utf-8")

# ---------------------------------------------------------------------------
# STANDALONE HUB PAGES: completed-sessions.html, extras.html
# ---------------------------------------------------------------------------

_STANDALONE_HUB_STYLES = """
<style>
  :root {
    --bg:#faf5e9; --surface:#fffdf5; --surface-2:#f5eed9;
    --border:#d4c89a; --border-dim:#ebe1c2;
    --text:#0a1838; --text-soft:#1e2f5a; --text-muted:#6b7794;
    --blue:#1e40af; --blue-light:#eff4fc; --blue-border:#b8cce8;
    --ink-dark:#0d1a3a; --ink-accent:#9bb8e6;
    --green:#1a7c4a; --green-light:#dff0e1; --green-border:#a7d8b0;
    --amber:#b45309; --amber-light:#fcf2c3; --amber-border:#f3d68a;
  }
  *,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
  html{scroll-behavior:smooth;}
  body{font-family:'Cormorant Garamond','Outfit',serif;background:var(--bg);color:var(--text);min-height:100vh;}
  header{padding:48px 60px 36px;background:var(--ink-dark);}
  .header-eyebrow{display:inline-flex;align-items:center;gap:6px;background:rgba(155,184,230,0.1);border:1px solid rgba(155,184,230,0.28);padding:5px 14px;border-radius:20px;font-family:'Outfit',sans-serif;font-size:11px;color:var(--ink-accent);letter-spacing:0.1em;margin-bottom:14px;}
  header h1{font-family:'Playfair Display',serif;font-size:46px;font-weight:700;color:#fbf7ec;margin-bottom:12px;line-height:1.02;letter-spacing:-0.01em;}
  header h1 em{font-style:italic;font-weight:500;color:var(--ink-accent);}
  header p{font-family:'Cormorant Garamond',serif;font-size:17px;font-style:italic;color:rgba(251,247,236,0.7);max-width:780px;line-height:1.6;}
  .breadcrumb{font-family:'Outfit',sans-serif;font-size:11px;letter-spacing:0.12em;color:var(--ink-accent);margin-bottom:8px;}
  .breadcrumb a{color:var(--ink-accent);text-decoration:none;}
  .breadcrumb a:hover{color:#fff;}
  .breadcrumb-sep{margin:0 8px;opacity:0.6;}
  main{padding:40px 60px 60px;max-width:1200px;margin:0 auto;}
  .anchor-section{margin-bottom:52px;scroll-margin-top:20px;}
  .anchor-section h2{font-family:'Playfair Display',serif;font-size:32px;font-weight:700;color:var(--text);border-left:3px solid var(--blue);padding-left:16px;margin-bottom:8px;line-height:1.15;}
  .anchor-section h2 em{font-style:italic;font-weight:500;color:var(--blue);}
  .section-lede{font-family:'Cormorant Garamond',serif;font-size:16px;color:var(--text-soft);line-height:1.65;margin:0 0 20px 19px;max-width:760px;}
  .card-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px;}
  .hub-card{display:flex;flex-direction:column;gap:10px;background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:20px 22px;text-decoration:none;transition:border-color .15s;}
  .hub-card:hover{border-color:var(--blue);}
  .hub-card-chip{align-self:flex-start;font-family:'Outfit',sans-serif;font-size:9px;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;padding:3px 10px;border-radius:20px;border:1px solid;}
  .chip-guide{background:var(--green-light);color:var(--green);border-color:var(--green-border);}
  .chip-bite{background:var(--blue-light);color:var(--blue);border-color:var(--blue-border);}
  .chip-nibble{background:var(--amber-light);color:var(--amber);border-color:var(--amber-border);}
  .chip-complete{background:var(--green-light);color:var(--green);border-color:var(--green-border);}
  .hub-card-title{font-family:'Playfair Display',serif;font-size:19px;font-weight:600;color:var(--text);line-height:1.28;}
  .hub-card:hover .hub-card-title{color:var(--blue);}
  .hub-card-sub{font-family:'Outfit',sans-serif;font-size:11px;letter-spacing:0.1em;color:var(--text-muted);text-transform:uppercase;}
  .hub-card-hint{font-family:'Outfit',sans-serif;font-size:9px;letter-spacing:0.14em;color:var(--green);text-transform:uppercase;background:var(--green-light);border:1px solid var(--green-border);border-radius:20px;padding:2px 9px;align-self:flex-start;}
  .empty-state{background:var(--surface);border:1px dashed var(--border);border-radius:12px;padding:24px;color:var(--text-muted);font-family:'Cormorant Garamond',serif;font-size:16px;line-height:1.6;font-style:italic;}
  .empty-state code{font-family:'SF Mono','Fira Code','Consolas',monospace;font-size:12px;background:var(--surface-2);border:1px solid var(--border);border-radius:4px;padding:1px 6px;color:var(--text);font-style:normal;}
  footer{font-family:'Outfit',sans-serif;font-size:11px;letter-spacing:0.14em;color:var(--text-muted);text-transform:uppercase;padding:24px 60px;border-top:1px solid var(--border);background:var(--surface);}
  footer span{color:var(--blue);}
</style>
""".strip()

_STANDALONE_FONTS = (
    '<link href="https://fonts.googleapis.com/css2?'
    'family=Playfair+Display:ital,wght@0,500;0,600;0,700;0,800;1,400;1,500'
    '&family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500'
    '&family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">'
)

def _standalone_page(title, header_h1, header_sub, body_html, crumb=None):
    crumb_label = crumb or title
    return (
        f'<!DOCTYPE html>\n<html lang="en">\n<head>\n'
        f'<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        f'<title>{title}</title>\n{_STANDALONE_FONTS}\n{_STANDALONE_HUB_STYLES}\n</head>\n<body>\n'
        f'<header>\n'
        f'<div class="breadcrumb">'
        f'<a href="index.html">Home</a>'
        f'<span class="breadcrumb-sep">›</span>'
        f'<a href="study-plan/index.html">Curriculum</a>'
        f'<span class="breadcrumb-sep">›</span>'
        f'{crumb_label}'
        f'</div>\n'
        f'<div class="header-eyebrow">Post-session artifacts · NSE7 Enterprise Firewall 7.6</div>\n'
        f'<h1>{header_h1}</h1>\n'
        f'<p>{header_sub}</p>\n'
        f'</header>\n<main>\n{body_html}\n</main>\n'
        f'<footer>NSE7 EF 7.6<span>.</span> Post-session artifacts</footer>\n'
        f'</body>\n</html>\n'
    )

def render_completed_hub(completions):
    completed_sessions = []
    for s in SESSIONS:
        entry = completions.get(s["num"])
        if entry and entry.get("has_complete"):
            completed_sessions.append((s, entry))

    total = len(SESSIONS)
    done = len(completed_sessions)

    if not completed_sessions:
        body = (
            '<div class="anchor-section">'
            '<h2>Completed <em>Study Guides</em></h2>'
            '<p class="section-lede">Every finished Socratic session lands here — the polished HTML study guide, one card per completion.</p>'
            '<div class="empty-state">'
            'No completed sessions yet — finish a session in Claude and drop '
            '<code>session-NN-complete-&lt;slug&gt;.html</code> + <code>session-NN-&lt;slug&gt;.txt</code> '
            'into <code>sorting-hat/</code> to see this page fill in.'
            '</div>'
            '</div>'
        )
    else:
        cards = []
        for s, entry in completed_sessions:
            summary_hint = '<span class="hub-card-hint">Recap available</span>' if entry.get("has_summary") else ""
            slug = f"session-{s['num']:02d}-{s['slug']}"
            title = html_escape(s["title"])
            cards.append(
                f'<a class="hub-card" href="sessions/{slug}/complete.html">'
                f'<span class="hub-card-chip chip-complete">Completed</span>'
                f'<span class="hub-card-sub">Session {s["num"]:02d}</span>'
                f'<span class="hub-card-title">{title}</span>'
                f'{summary_hint}'
                f'</a>'
            )
        body = (
            '<div class="anchor-section">'
            f'<h2>Completed <em>Study Guides · {done} of {total}</em></h2>'
            '<p class="section-lede">Every finished Socratic session — polished HTML study guides produced at the end of each Claude session, linked to the source session page.</p>'
            f'<div class="card-grid">{"".join(cards)}</div>'
            '</div>'
        )

    html = _standalone_page(
        title=f"Completed Study Guides · NSE7 EF 7.6",
        header_h1='Completed <em>Study Guides</em>',
        header_sub='Polished HTML study guides produced at the end of each Socratic session.',
        body_html=body,
        crumb="Completed Study Guides",
    )
    (ROOT / "completed-sessions.html").write_text(html, encoding="utf-8")

def render_extras_hub(extras, standalone_extras=None):
    standalone_extras = standalone_extras or []
    kind_meta = [
        ("guides", "Guides", "chip-guide", "Long-form companion pages that dive deeper than a session can — includes standalone Extras topics."),
        ("bites", "Bites", "chip-bite", "Focused single-concept explainers — read after a session to nail down one thing."),
        ("nibbles", "Nibbles", "chip-nibble", "Short reference cards / cheat sheets — for quick lookup during review or lab work."),
    ]
    singular = lambda label: label[:-1] if label.endswith("s") else label

    sections_html = []
    for kind, label, chip_class, lede in kind_meta:
        cards = []
        # Session-linked items
        for s in SESSIONS:
            for slug, title, href in (extras.get(s["num"], {}).get(kind) or []):
                session_dir = f"session-{s['num']:02d}-{s['slug']}"
                cards.append(
                    f'<a class="hub-card" href="sessions/{session_dir}/{html_escape(href)}">'
                    f'<span class="hub-card-chip {chip_class}">{singular(label)}</span>'
                    f'<span class="hub-card-sub">Session {s["num"]:02d}</span>'
                    f'<span class="hub-card-title">{html_escape(title)}</span>'
                    f'</a>'
                )
        # Standalone extras items
        for entry in standalone_extras:
            e = entry["topic"]
            topic_dir = f"extras-{e['num']:02d}-{e['slug']}"
            for slug, title, href in entry.get(kind, []):
                cards.append(
                    f'<a class="hub-card" href="extras/{topic_dir}/{html_escape(href)}">'
                    f'<span class="hub-card-chip {chip_class}">{singular(label)}</span>'
                    f'<span class="hub-card-sub">Extras {e["num"]:02d} · {html_escape(e["title"])}</span>'
                    f'<span class="hub-card-title">{html_escape(title)}</span>'
                    f'</a>'
                )
        if cards:
            body_inner = f'<div class="card-grid">{"".join(cards)}</div>'
        else:
            body_inner = f'<div class="empty-state">No {kind} sorted yet.</div>'
        sections_html.append(
            f'<div class="anchor-section" id="{kind}">'
            f'<h2>{label}<em></em></h2>'
            f'<p class="section-lede">{lede}</p>'
            f'{body_inner}'
            f'</div>'
        )
    html = _standalone_page(
        title=f"Extras — Guides · Bites · Nibbles · NSE7 EF 7.6",
        header_h1='Guides, Bites &amp; <em>Nibbles</em>',
        header_sub='Supplementary study artifacts — session-linked and standalone Extras topics. Anchors: #guides, #bites, #nibbles.',
        body_html="".join(sections_html),
        crumb="Extras",
    )
    (ROOT / "extras.html").write_text(html, encoding="utf-8")

# ---------------------------------------------------------------------------
# BREADCRUMB NORMALIZER
# ---------------------------------------------------------------------------
# Sorted files (complete.html, bites/nibbles/guides, standalone Extras topic
# pages) come from Claude and either ship with a broken crumb (dead <a href="#">
# or non-linked <span>) or none at all. This walks every sorted file after
# rendering and rewrites/injects a working "Home › … › <page>" crumb.
# Uses inline styles so it renders correctly even on files whose own CSS
# doesn't define a .breadcrumb rule.

_CRUMB_STYLE = "font-family:'Outfit',sans-serif;font-size:11px;letter-spacing:0.08em;color:rgba(251,247,236,0.6);margin-bottom:12px;text-transform:uppercase;"
_CRUMB_LINK  = "color:#9bb8e6;text-decoration:none;"
_CRUMB_SEP   = "color:rgba(155,184,230,0.4);margin:0 6px;"

def _build_crumb(steps):
    """steps: list of (label, href_or_None). Final item is unlinked (current page)."""
    parts = [f'<div class="breadcrumb" style="{_CRUMB_STYLE}">']
    for i, (label, href) in enumerate(steps):
        if i > 0:
            parts.append(f'<span class="breadcrumb-sep" style="{_CRUMB_SEP}">›</span>')
        if href:
            parts.append(f'<a href="{href}" style="{_CRUMB_LINK}">{html_escape(label)}</a>')
        else:
            parts.append(f'<span>{html_escape(label)}</span>')
    parts.append('</div>')
    return "".join(parts)

def _normalize_crumb_in_file(path, crumb_html):
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return
    # 1. Strip every existing breadcrumb block so we can never end up with duplicates.
    crumb_pat = _re.compile(r'<div class="breadcrumb"[^>]*>.*?</div>\s*', _re.DOTALL | _re.IGNORECASE)
    stripped = crumb_pat.sub("", text)
    # 2. Inject fresh crumb at the right anchor.
    #    Prefer inside .header-left (flex headers push the crumb outside otherwise).
    #    Fall back to immediately after <header> for headers without .header-left.
    hl_pat = _re.compile(r'(<div class="header-left"[^>]*>)', _re.IGNORECASE)
    m = hl_pat.search(stripped)
    if m:
        end = m.end()
        new_text = stripped[:end] + "\n    " + crumb_html + stripped[end:]
    else:
        m = _re.search(r'<header\b[^>]*>', stripped, _re.IGNORECASE)
        if not m:
            return  # no <header> — skip
        end = m.end()
        new_text = stripped[:end] + "\n" + crumb_html + stripped[end:]
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")

def _normalize_pt_transition_in_file(path):
    """If file has the pt-init preloader but not the cleanup, inject the cleanup before </body>.

    Symptom without the fix: page loads with body opacity:0 forever → blank white screen.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return
    if "classList.add('pt-init')" not in text and 'classList.add("pt-init")' not in text:
        return  # no preloader — nothing to fix
    if "classList.remove('pt-init')" in text or 'classList.remove("pt-init")' in text:
        return  # already has cleanup
    cleanup = (
        "<script>document.documentElement.classList.remove('pt-init');"
        "sessionStorage.removeItem('pt');</script>\n"
    )
    if "</body>" in text:
        new_text = text.replace("</body>", cleanup + "</body>", 1)
    else:
        new_text = text + "\n" + cleanup
    path.write_text(new_text, encoding="utf-8")

def normalize_page_transitions():
    """Walk all sorted HTML files and heal broken pt-init preloaders."""
    for s in SESSIONS:
        session_dir = SESSIONS_DIR / f"session-{s['num']:02d}-{s['slug']}"
        if not session_dir.is_dir():
            continue
        for p in [session_dir / "complete.html"]:
            if p.is_file():
                _normalize_pt_transition_in_file(p)
        for kind in EXTRA_KINDS:
            kind_dir = session_dir / kind
            if kind_dir.is_dir():
                for f in kind_dir.glob("*.html"):
                    _normalize_pt_transition_in_file(f)
    for e in EXTRAS:
        topic_dir = EXTRAS_DIR / f"extras-{e['num']:02d}-{e['slug']}"
        if not topic_dir.is_dir():
            continue
        if (topic_dir / "index.html").is_file():
            _normalize_pt_transition_in_file(topic_dir / "index.html")
        for kind in EXTRA_KINDS:
            kind_dir = topic_dir / kind
            if kind_dir.is_dir():
                for f in kind_dir.glob("*.html"):
                    _normalize_pt_transition_in_file(f)

def normalize_sorted_breadcrumbs():
    """Rewrite/inject breadcrumbs on every sorted file (complete/bite/nibble/guide + standalone extras)."""
    # Session sorted files
    for s in SESSIONS:
        session_dir = SESSIONS_DIR / f"session-{s['num']:02d}-{s['slug']}"
        if not session_dir.is_dir():
            continue
        complete_path = session_dir / "complete.html"
        if complete_path.is_file():
            _normalize_crumb_in_file(complete_path, _build_crumb([
                ("Home", "../../index.html"),
                ("Curriculum", "../../study-plan/index.html"),
                (f"Session {s['num']:02d}", "index.html"),
                ("Completed Study Guide", None),
            ]))
        for kind in EXTRA_KINDS:
            kind_dir = session_dir / kind
            if not kind_dir.is_dir():
                continue
            singular = kind[:-1].capitalize()
            for html_file in kind_dir.glob("*.html"):
                _normalize_crumb_in_file(html_file, _build_crumb([
                    ("Home", "../../../index.html"),
                    ("Curriculum", "../../../study-plan/index.html"),
                    (f"Session {s['num']:02d}", "../index.html"),
                    (singular, None),
                ]))
    # Standalone extras sorted files
    for e in EXTRAS:
        topic_dir = EXTRAS_DIR / f"extras-{e['num']:02d}-{e['slug']}"
        if not topic_dir.is_dir():
            continue
        index_path = topic_dir / "index.html"
        if index_path.is_file():
            _normalize_crumb_in_file(index_path, _build_crumb([
                ("Home", "../../index.html"),
                ("Extras", "../../extras.html"),
                (e["title"], None),
            ]))
        for kind in EXTRA_KINDS:
            kind_dir = topic_dir / kind
            if not kind_dir.is_dir():
                continue
            singular = kind[:-1].capitalize()
            for html_file in kind_dir.glob("*.html"):
                _normalize_crumb_in_file(html_file, _build_crumb([
                    ("Home", "../../../index.html"),
                    ("Extras", "../../../extras.html"),
                    (e["title"], "../index.html"),
                    (singular, None),
                ]))

# ---------------------------------------------------------------------------
# LABS (hands-on) — see /build-lab-plan skill
# ---------------------------------------------------------------------------
# Renders labs/index.html (hub) and labs/lab-NN-slug/index.html (per lab).
# When LABS is empty, hub renders an empty-state pointing at the skill.

def lab_filename(l: dict) -> str:
    return f"lab-{l['num']:02d}-{l['slug']}/index.html"

def sibling_lab_href(l: dict) -> str:
    return f"../lab-{l['num']:02d}-{l['slug']}/index.html"

_LAB_STYLES = """
<style>
  :root{--bg:#faf5e9;--surface:#fffdf5;--surface-2:#f5eed9;--border:#d4c89a;--text:#0a1838;--text-soft:#1e2f5a;--text-muted:#6b7794;--blue:#1e40af;--blue-light:#eff4fc;--blue-border:#b8cce8;--ink-dark:#0d1a3a;--ink-accent:#9bb8e6;--green:#1a7c4a;--green-light:#dff0e1;--green-border:#a7d8b0;--amber:#b45309;--amber-light:#fcf2c3;--amber-border:#f3d68a;--red:#b91c1c;--red-light:#fee2e2;--red-border:#fca5a5;--teal:#0f766e;--teal-light:#ccfbf1;--teal-border:#5eead4;}
  *,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
  html,body{min-height:100vh;}
  body{font-family:'Cormorant Garamond',serif;background:var(--bg);color:var(--text);display:flex;flex-direction:column;}
  header{padding:48px 60px 36px;background:var(--ink-dark);color:#fbf7ec;}
  .breadcrumb{font-family:'Outfit',sans-serif;font-size:11px;letter-spacing:0.08em;color:rgba(251,247,236,0.6);margin-bottom:12px;text-transform:uppercase;}
  .breadcrumb a{color:var(--ink-accent);text-decoration:none;}
  .breadcrumb-sep{color:rgba(155,184,230,0.4);margin:0 6px;}
  .eyebrow{display:inline-flex;align-items:center;gap:8px;background:rgba(155,184,230,0.1);border:1px solid rgba(155,184,230,0.28);padding:5px 14px;border-radius:20px;font-family:'Outfit',sans-serif;font-size:11px;color:var(--ink-accent);letter-spacing:0.1em;margin-bottom:14px;text-transform:uppercase;}
  header h1{font-family:'Playfair Display',serif;font-size:48px;font-weight:700;line-height:1.05;margin-bottom:10px;letter-spacing:-0.01em;}
  header h1 em{font-style:italic;font-weight:500;color:var(--ink-accent);}
  header p{font-family:'Cormorant Garamond',serif;font-size:17px;font-style:italic;color:rgba(251,247,236,0.55);max-width:760px;margin-top:6px;line-height:1.6;}
  main{flex:1;padding:44px 60px 72px;max-width:1200px;margin:0 auto;width:100%;}
  .section-block{margin-bottom:48px;}
  .section-label{font-family:'Outfit',sans-serif;font-size:10px;font-weight:700;letter-spacing:0.2em;text-transform:uppercase;color:var(--text-muted);margin-bottom:10px;}
  .section-block h2{font-family:'Playfair Display',serif;font-size:30px;font-weight:700;line-height:1.15;margin-bottom:14px;padding-left:14px;border-left:3px solid var(--blue);}
  .section-block h2 em{font-style:italic;font-weight:500;color:var(--blue);}
  .section-block p{font-family:'Cormorant Garamond',serif;font-size:17px;line-height:1.7;color:var(--text-soft);margin-bottom:12px;}
  .empty-state{border:2px dashed var(--border);border-radius:14px;background:var(--surface);padding:44px 32px;text-align:center;color:var(--text-muted);}
  .empty-state h3{font-family:'Playfair Display',serif;font-size:22px;color:var(--text);margin-bottom:8px;}
  .empty-state p{font-family:'Cormorant Garamond',serif;font-size:16px;line-height:1.65;font-style:italic;}
  .empty-state code{font-family:'SF Mono','Fira Code',monospace;font-size:13px;background:var(--surface-2);padding:2px 8px;border-radius:4px;color:var(--text);font-style:normal;}
  .card-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px;}
  .lab-card{display:flex;flex-direction:column;gap:8px;padding:22px 24px 26px;background:var(--surface);border:1px solid var(--border);border-radius:12px;text-decoration:none;color:var(--text);transition:transform .18s ease, box-shadow .18s ease, border-color .18s ease;}
  .lab-card:hover{transform:translateY(-2px);box-shadow:0 8px 24px -12px rgba(10,24,56,0.18);border-color:var(--blue);}
  .lab-card-num{font-family:'Outfit',sans-serif;font-size:10px;font-weight:700;letter-spacing:0.18em;color:var(--text-muted);text-transform:uppercase;}
  .lab-card-title{font-family:'Playfair Display',serif;font-size:22px;font-weight:600;line-height:1.2;}
  .lab-card-meta{font-family:'Outfit',sans-serif;font-size:11px;color:var(--text-muted);letter-spacing:0.04em;}
  .lab-card-goal{font-family:'Cormorant Garamond',serif;font-size:15px;line-height:1.55;color:var(--text-soft);font-style:italic;}
  .device-table{width:100%;border-collapse:collapse;margin:14px 0;font-size:14px;background:var(--surface);border-radius:10px;overflow:hidden;}
  .device-table th{background:var(--ink-dark);color:var(--ink-accent);font-family:'Outfit',sans-serif;font-size:10px;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;padding:10px 14px;text-align:left;}
  .device-table td{font-family:'Cormorant Garamond',serif;font-size:15px;padding:10px 14px;border-bottom:1px solid var(--border);color:var(--text-soft);line-height:1.5;vertical-align:top;}
  .device-table td:first-child{font-family:'SF Mono','Fira Code',monospace;font-size:12.5px;color:var(--text);font-weight:700;white-space:nowrap;}
  .step-card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:22px 26px;margin-bottom:22px;}
  .step-head{display:flex;align-items:center;gap:12px;margin-bottom:12px;}
  .step-chip{font-family:'Outfit',sans-serif;font-size:11px;font-weight:700;letter-spacing:0.14em;background:var(--blue-light);color:var(--blue);border:1px solid var(--blue-border);padding:3px 10px;border-radius:12px;text-transform:uppercase;}
  .step-goal{font-family:'Playfair Display',serif;font-size:22px;font-weight:600;color:var(--text);line-height:1.25;}
  .step-callout{border-left:3px solid var(--blue-border);background:var(--blue-light);border-radius:0 10px 10px 0;padding:14px 18px;margin:12px 0;font-family:'Cormorant Garamond',serif;font-size:16px;line-height:1.65;color:var(--text-soft);}
  .step-callout strong{color:var(--text);}
  .step-callout.callout-amber{border-left-color:var(--amber-border);background:var(--amber-light);}
  .step-callout.callout-red{border-left-color:var(--red-border);background:var(--red-light);}
  .step-callout-label{font-family:'Outfit',sans-serif;font-size:10px;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:var(--blue);margin-bottom:6px;}
  .callout-amber .step-callout-label{color:var(--amber);}
  .callout-red .step-callout-label{color:var(--red);}
  .code-block{background:var(--ink-dark);border-radius:10px;padding:0;margin:12px 0;overflow:hidden;}
  .code-label{font-family:'Outfit',sans-serif;font-size:9px;font-weight:700;letter-spacing:0.16em;text-transform:uppercase;color:var(--ink-accent);padding:8px 14px;background:rgba(255,255,255,0.04);border-bottom:1px solid rgba(255,255,255,0.08);}
  .code-block pre{padding:14px 16px;margin:0;overflow:auto;}
  .code-block code{font-family:'SF Mono','Fira Code',monospace;font-size:12.5px;line-height:1.65;color:#e8efff;white-space:pre;}
  footer{padding:18px 60px;border-top:1px solid var(--border);background:var(--surface);font-family:'Outfit',sans-serif;font-size:11px;letter-spacing:0.14em;color:var(--text-muted);text-transform:uppercase;text-align:center;}
  footer span{color:var(--blue);}
  @media(max-width:640px){header{padding:32px 24px 24px;}header h1{font-size:32px;}main{padding:28px 20px 44px;}}
</style>
""".strip()

_LAB_FONTS = (
    '<link href="https://fonts.googleapis.com/css2?'
    'family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,400'
    '&family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400'
    '&family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">'
)

def _lab_page_shell(title, crumb_html, body_html):
    return (
        f'<!DOCTYPE html>\n<html lang="en">\n<head>\n'
        f'<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        f'<title>{title}</title>\n{_LAB_FONTS}\n{_LAB_STYLES}\n</head>\n<body>\n'
        f'{body_html}\n'
        f'<footer>NSE7 EF 7.6 <span>·</span> Hands-On Labs</footer>\n'
        f'</body>\n</html>\n'
    )

def _render_device_table_rows(devices):
    """Return HTML rows for a device / interface / IP table. devices is a list of device dicts."""
    rows = []
    for d in devices:
        ifaces = d.get("interfaces", [])
        rowspan = max(len(ifaces), 1)
        first_iface = ifaces[0] if ifaces else {"name": "—", "ip": "—", "zone": "—", "connected_to": "—"}
        rows.append(
            f'<tr>'
            f'<td rowspan="{rowspan}">{html_escape(d["name"])}</td>'
            f'<td rowspan="{rowspan}">{html_escape(d.get("role", ""))}</td>'
            f'<td rowspan="{rowspan}" style="font-family:\'Cormorant Garamond\',serif;font-weight:normal;color:var(--text-muted);">{html_escape(d.get("model", ""))}</td>'
            f'<td>{html_escape(first_iface["name"])}</td>'
            f'<td>{html_escape(first_iface.get("ip", ""))}</td>'
            f'<td>{html_escape(first_iface.get("zone", ""))}</td>'
            f'<td>{html_escape(first_iface.get("connected_to", ""))}</td>'
            f'</tr>'
        )
        for iface in ifaces[1:]:
            rows.append(
                f'<tr>'
                f'<td>{html_escape(iface["name"])}</td>'
                f'<td>{html_escape(iface.get("ip", ""))}</td>'
                f'<td>{html_escape(iface.get("zone", ""))}</td>'
                f'<td>{html_escape(iface.get("connected_to", ""))}</td>'
                f'</tr>'
            )
    return "".join(rows)

def _render_topology_block(devices, topology_img_href, topology_prompt=None):
    """Render the diagram placeholder + device table. devices = list of device dicts to include."""
    if not devices:
        return '<div class="empty-state"><h3>No devices assigned to this lab</h3><p>This lab is concept-only.</p></div>'
    table = f"""
<table class="device-table">
  <thead>
    <tr>
      <th>Device</th><th>Role</th><th>Model</th><th>Interface</th><th>IP</th><th>Zone</th><th>Connected to</th>
    </tr>
  </thead>
  <tbody>{_render_device_table_rows(devices)}</tbody>
</table>
"""
    prompt_hint = ""
    if topology_prompt:
        prompt_hint = f'<div style="font-family:\'Outfit\',sans-serif;font-size:10px;color:var(--text-muted);letter-spacing:0.1em;text-align:center;">Drop the generated PNG at <code>{html_escape(topology_img_href)}</code> — see <code>labs/images/prompts.txt</code> for the prompt.</div>'
    img_block = f"""
<div style="width:100%;display:flex;flex-direction:column;align-items:center;gap:12px;margin:16px 0 24px;">
  <img src="{topology_img_href}" alt="Topology diagram" style="width:100%;max-width:900px;border-radius:12px;border:1px solid var(--border);display:block;" onerror="this.style.display='none';this.nextElementSibling.style.display='flex';">
  <div style="display:none;border:2px dashed var(--border);border-radius:12px;background:var(--surface-2);padding:40px 28px;flex-direction:column;align-items:center;gap:14px;width:100%;">
    <div style="font-size:44px;opacity:0.35;">🗺️</div>
    <div style="text-align:center;">
      <div style="font-family:'Outfit',sans-serif;font-size:11px;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:var(--text-muted);margin-bottom:6px;">Topology diagram placeholder</div>
      <div style="font-family:'Playfair Display',serif;font-size:18px;font-weight:600;color:var(--text);">{html_escape(TOPOLOGY.get("name", "Pod topology"))}</div>
    </div>
    {prompt_hint}
  </div>
</div>
"""
    return img_block + table

def render_labs_hub():
    LABS_DIR.mkdir(parents=True, exist_ok=True)
    (LABS_DIR / "images").mkdir(parents=True, exist_ok=True)
    crumb = (
        '<div class="breadcrumb">'
        '<a href="../index.html">Home</a>'
        '<span class="breadcrumb-sep">›</span>Labs</div>'
    )
    if not LABS:
        body = f"""
<header>
  {crumb}
  <div class="eyebrow">Hands-On Labs · NSE7 EF 7.6</div>
  <h1>Hands-On <em>Labs</em></h1>
  <p>Empty — no labs authored yet.</p>
</header>
<main>
  <div class="empty-state">
    <h3>No labs yet</h3>
    <p>Drop a lab guide PDF into <code>reference/</code> and run <code>/build-lab-plan</code> to design a minimum shared topology and generate lab pages here.</p>
  </div>
</main>
"""
    else:
        cards = []
        for l in LABS:
            is_concept = l.get("concept_only", False)
            is_orientation = l.get("is_orientation", False)
            if is_orientation:
                chip = "Orientation"
            elif is_concept:
                chip = "Concept-only"
            else:
                chip = html_escape(l.get("duration", ""))
            first_target = html_escape(l.get("learn_targets", [""])[0]) if l.get("learn_targets") else ""
            cards.append(
                f'<a class="lab-card" href="{lab_filename(l)}">'
                f'<span class="lab-card-num">Lab {l["num"]:02d} · {chip}</span>'
                f'<span class="lab-card-title">{html_escape(l["title"])}</span>'
                f'<span class="lab-card-goal">{html_escape(l.get("goal", ""))}</span>'
                f'<span class="lab-card-meta">{first_target}</span>'
                f'</a>'
            )
        topology_block = _render_topology_block(
            TOPOLOGY.get("devices", []),
            "images/topology.png",
            topology_prompt=TOPOLOGY.get("diagram_prompt"),
        )
        hands_on = sum(1 for l in LABS if not l.get("concept_only") and not l.get("is_orientation"))
        body = f"""
<header>
  {crumb}
  <div class="eyebrow">Hands-On Labs · NSE7 EF 7.6</div>
  <h1>Hands-On <em>Labs</em></h1>
  <p>{html_escape(TOPOLOGY.get("tagline", "Socratic predict → run → verify → reflect on a shared minimum topology."))}</p>
</header>
<main>
  <div class="section-block">
    <div class="section-label">The pod · {html_escape(TOPOLOGY.get("name", ""))}</div>
    <h2>Shared <em>Topology</em></h2>
    <p>Every lab exercises a subset of this topology. Build the pod once, then reuse it across all labs.</p>
    {topology_block}
  </div>
  <div class="section-block">
    <div class="section-label">{len(LABS)} labs · {hands_on} hands-on</div>
    <h2>The <em>Labs</em></h2>
    <div class="card-grid">{"".join(cards)}</div>
  </div>
</main>
"""
    html = _lab_page_shell("Hands-On Labs · NSE7 EF 7.6", crumb, body)
    (LABS_DIR / "index.html").write_text(html, encoding="utf-8")

def _lab_by_num(n):
    return next((x for x in LABS if x["num"] == n), None)

def _session_by_num(n):
    return next((x for x in SESSIONS if x["num"] == n), None)

def _lab_prereq_html(l):
    prereq_labs = l.get("prereqs", {}).get("labs", [])
    prereq_sessions = l.get("prereqs", {}).get("sessions", [])
    lab_links, session_links = [], []
    for n in prereq_labs:
        pl = _lab_by_num(n)
        if pl:
            lab_links.append(f'<a href="{sibling_lab_href(pl)}" style="color:var(--blue);text-decoration:none;">Lab {n:02d}</a>')
    for n in prereq_sessions:
        ps = _session_by_num(n)
        if ps:
            session_links.append(f'<a href="../../sessions/session-{n:02d}-{ps["slug"]}/index.html" style="color:var(--blue);text-decoration:none;">Session {n:02d}</a>')
    prereq_labs_str = ", ".join(lab_links) if lab_links else "<em>none</em>"
    prereq_sessions_str = ", ".join(session_links) if session_links else "<em>none</em>"
    return prereq_labs_str, prereq_sessions_str

def _lab_steps_html(l):
    steps = l.get("steps", [])
    if not steps:
        return (
            '<div class="empty-state">'
            '<h3>Steps not authored yet</h3>'
            '<p>Predict → Run → Verify → Reflect step cards will land here once <code>steps</code> is populated for this lab in <code>build.py</code>.</p>'
            '</div>'
        )
    cards = []
    for s in steps:
        commands_pre = "\n".join(s.get("commands", []))
        parts = [
            f'<div class="step-card">',
            f'  <div class="step-head"><span class="step-chip">Step {s["num"]:02d}</span><span class="step-goal">{html_escape(s.get("goal", ""))}</span></div>',
        ]
        if s.get("think_first"):
            parts.append(
                f'  <div class="step-callout">'
                f'<div class="step-callout-label">Think first</div>'
                f'{html_escape(s["think_first"])}'
                f'</div>'
            )
        if commands_pre:
            parts.append(
                f'  <div class="code-block">'
                f'<div class="code-label">Run</div>'
                f'<pre><code>{html_escape(commands_pre)}</code></pre>'
                f'</div>'
            )
        if s.get("verify"):
            parts.append(
                f'  <div class="code-block">'
                f'<div class="code-label">Verify</div>'
                f'<pre><code>{html_escape(s["verify"])}</code></pre>'
                f'</div>'
            )
            if s.get("expected"):
                parts.append(
                    f'  <div class="step-callout" style="border-left-color:var(--green-border);background:var(--green-light);">'
                    f'<div class="step-callout-label" style="color:var(--green);">Expected output</div>'
                    f'<pre style="font-family:\'SF Mono\',\'Fira Code\',monospace;font-size:12.5px;white-space:pre-wrap;margin:0;">{html_escape(s["expected"])}</pre>'
                    f'</div>'
                )
        if s.get("reflect"):
            parts.append(
                f'  <div class="step-callout callout-amber">'
                f'<div class="step-callout-label">Reflect</div>'
                f'{html_escape(s["reflect"])}'
                f'</div>'
            )
        parts.append('</div>')
        cards.append("\n".join(parts))
    return "\n".join(cards)

def render_lab_page(l):
    slug_dir = f"lab-{l['num']:02d}-{l['slug']}"
    out_dir = LABS_DIR / slug_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "images").mkdir(parents=True, exist_ok=True)
    crumb = (
        '<div class="breadcrumb">'
        '<a href="../../index.html">Home</a>'
        '<span class="breadcrumb-sep">›</span>'
        '<a href="../index.html">Labs</a>'
        '<span class="breadcrumb-sep">›</span>'
        f'Lab {l["num"]:02d}</div>'
    )

    is_concept = l.get("concept_only", False)
    is_orientation = l.get("is_orientation", False)

    if is_orientation:
        # Full pod topology + curriculum summary (Lab 0 / orientation page).
        topology_block = _render_topology_block(
            TOPOLOGY.get("devices", []),
            "../images/topology.png",
            topology_prompt=TOPOLOGY.get("diagram_prompt"),
        )
        # Summary rows for every hands-on lab (skip orientation + concept-only).
        summary_rows = []
        for other in LABS:
            if other.get("is_orientation") or other.get("concept_only"):
                continue
            summary_rows.append(
                f'<tr>'
                f'<td style="width:90px;">Lab {other["num"]:02d}</td>'
                f'<td><a href="{sibling_lab_href(other)}" style="color:var(--blue);text-decoration:none;font-weight:700;">{html_escape(other["title"])}</a>'
                f'<div style="font-family:\'Cormorant Garamond\',serif;font-size:14px;font-style:italic;color:var(--text-muted);margin-top:2px;">{html_escape(other.get("goal", ""))}</div></td>'
                f'<td style="width:130px;font-family:\'Outfit\',sans-serif;font-size:11px;color:var(--text-muted);letter-spacing:0.04em;">{html_escape(other.get("duration", ""))}</td>'
                f'</tr>'
            )
        session_link = ""
        s1 = _session_by_num(1)
        if s1:
            session_link = f'<a href="../../sessions/session-01-{s1["slug"]}/index.html" style="color:var(--blue);text-decoration:none;">Session 01 — {html_escape(s1["title"])}</a>'
        next_l = _lab_by_num(1)
        next_link = f'<a href="{sibling_lab_href(next_l)}" style="color:var(--blue);text-decoration:none;">Lab 01 →</a>' if next_l else ""
        # Escape the lab-mode methodology once so the <pre> content is HTML-safe.
        lab_mode_escaped = html_escape(LAB_MODE_METHODOLOGY_TEXT).strip()
        body = f"""
<header>
  {crumb}
  <div class="eyebrow">Lab 00 · Orientation · NSE7 EF 7.6</div>
  <h1>Pod Setup &amp; <em>Curriculum Overview</em></h1>
  <p>{html_escape(l.get('goal', ''))}</p>
</header>
<main>
  <div class="section-block">
    <div class="section-label">Section 01 · Lab-mode Claude Instructions</div>
    <h2>Load Your Lab <em>Coach</em></h2>
    <p>Create a Claude Project for these labs, paste the block below into its Instructions field, and upload <code>reference/NSE7-LabGuide.pdf</code> to the Project's Files. Every lab from Lab 01 onwards runs inside a fresh chat in this Project.</p>
    <div class="code-block">
      <div class="code-label">Paste this into your Claude Project Instructions</div>
      <pre><code>{lab_mode_escaped}</code></pre>
    </div>
    <p style="margin-top:14px;">Related concept material: {session_link}.</p>
  </div>
  <div class="section-block">
    <div class="section-label">Section 02 · Shared Topology</div>
    <h2>The <em>Pod</em></h2>
    <p>{html_escape(TOPOLOGY.get("tagline", ""))}</p>
    {topology_block}
  </div>
  <div class="section-block">
    <div class="section-label">Section 03 · What You'll Learn</div>
    <h2>The Nine <em>Hands-On Labs</em></h2>
    <p>One-liner per lab so you know the arc before you start.</p>
    <table class="device-table">
      <thead><tr><th>Lab</th><th>Title &amp; Goal</th><th>Duration</th></tr></thead>
      <tbody>{"".join(summary_rows)}</tbody>
    </table>
  </div>
  <div style="display:flex;justify-content:space-between;margin-top:32px;padding-top:20px;border-top:1px solid var(--border);font-family:'Outfit',sans-serif;font-size:13px;letter-spacing:0.06em;">
    <div><span style="color:var(--text-muted);">← (orientation)</span></div>
    <div>{next_link}</div>
  </div>
</main>
"""
        html = _lab_page_shell(f"Lab 00 — Pod Setup &amp; Curriculum Overview · NSE7 EF 7.6", crumb, body)
        (out_dir / "index.html").write_text(html, encoding="utf-8")
        return

    if is_concept:
        prereq_labs_str, prereq_sessions_str = _lab_prereq_html(l)
        body = f"""
<header>
  {crumb}
  <div class="eyebrow">Lab {l['num']:02d} · Concept-only · NSE7 EF 7.6</div>
  <h1>{html_escape(l['title'])}</h1>
  <p>{html_escape(l.get('goal', ''))}</p>
</header>
<main>
  <div class="empty-state">
    <h3>No hands-on exercise for this lab</h3>
    <p>The lab guide PDF doesn't include a hands-on exercise here. Review the concepts in the linked study session, then move on to Lab 02.</p>
    <p style="margin-top:12px;">Related study session: {prereq_sessions_str}</p>
  </div>
</main>
"""
        html = _lab_page_shell(f"Lab {l['num']:02d} — {l['title']} · NSE7 EF 7.6", crumb, body)
        (out_dir / "index.html").write_text(html, encoding="utf-8")
        return

    # Full 5-section layout
    devices_used = [d for d in TOPOLOGY.get("devices", []) if d["name"] in l.get("topology_devices", [])]
    topology_block = _render_topology_block(devices_used, "../images/topology.png", topology_prompt=None)
    learn_targets_html = "".join(f'<li>{html_escape(t)}</li>' for t in l.get("learn_targets", []))
    verification_html = "".join(f'<li>{html_escape(v)}</li>' for v in l.get("verification", []))
    prereq_labs_str, prereq_sessions_str = _lab_prereq_html(l)
    prev_l = _lab_by_num(l["num"] - 1)
    next_l = _lab_by_num(l["num"] + 1)
    prev_link = f'<a href="{sibling_lab_href(prev_l)}" style="color:var(--blue);text-decoration:none;">← Lab {prev_l["num"]:02d}</a>' if prev_l else '<span style="color:var(--text-muted);">← (first lab)</span>'
    next_link = f'<a href="{sibling_lab_href(next_l)}" style="color:var(--blue);text-decoration:none;">Lab {next_l["num"]:02d} →</a>' if next_l else '<a href="../index.html" style="color:var(--blue);text-decoration:none;">Back to Labs hub →</a>'
    body = f"""
<header>
  {crumb}
  <div class="eyebrow">Lab {l['num']:02d} · Socratic Lab · NSE7 EF 7.6</div>
  <h1>{html_escape(l['title'])}</h1>
  <p>{html_escape(l.get('goal', ''))}</p>
</header>
<main>
  <div class="section-block">
    <div class="section-label">Section 01 · Objectives &amp; Prereqs</div>
    <h2>What You'll <em>Learn</em></h2>
    <ul style="font-family:'Cormorant Garamond',serif;font-size:17px;line-height:1.7;color:var(--text-soft);padding-left:22px;margin-bottom:16px;">{learn_targets_html}</ul>
    <table class="device-table" style="max-width:640px;">
      <tbody>
        <tr><td style="width:180px;">Duration</td><td>{html_escape(l.get('duration', ''))}</td></tr>
        <tr><td>Prereq labs</td><td>{prereq_labs_str}</td></tr>
        <tr><td>Prereq sessions</td><td>{prereq_sessions_str}</td></tr>
      </tbody>
    </table>
  </div>
  <div class="section-block">
    <div class="section-label">Section 02 · Topology</div>
    <h2>Devices in <em>This Lab</em></h2>
    <p>Subset of the shared pod used in Lab {l['num']:02d}. Full topology: <a href="../index.html" style="color:var(--blue);text-decoration:none;">labs hub →</a></p>
    {topology_block}
  </div>
  <div class="section-block">
    <div class="section-label">Section 03 · Steps</div>
    <h2>Predict → Run → Verify → <em>Reflect</em></h2>
    {_lab_steps_html(l)}
  </div>
  <div class="section-block">
    <div class="section-label">Section 04 · Verification</div>
    <h2>You're <em>Done When</em></h2>
    <ul style="font-family:'Cormorant Garamond',serif;font-size:17px;line-height:1.7;color:var(--text-soft);padding-left:22px;">{verification_html}</ul>
  </div>
  <div class="section-block">
    <div class="section-label">Section 05 · Cleanup</div>
    <h2>Before the <em>Next Lab</em></h2>
    <div class="step-callout callout-red">
      <div class="step-callout-label">Cleanup</div>
      {html_escape(l.get('cleanup', ''))}
    </div>
  </div>
  <div style="display:flex;justify-content:space-between;margin-top:32px;padding-top:20px;border-top:1px solid var(--border);font-family:'Outfit',sans-serif;font-size:13px;letter-spacing:0.06em;">
    <div>{prev_link}</div>
    <div>{next_link}</div>
  </div>
</main>
"""
    html = _lab_page_shell(f"Lab {l['num']:02d} — {l['title']} · NSE7 EF 7.6", crumb, body)
    (out_dir / "index.html").write_text(html, encoding="utf-8")

# ---------------------------------------------------------------------------
# SESSIONS INDEX (sessions/index.html) — flat listing of all 40 sessions
# ---------------------------------------------------------------------------

def render_sessions_index(completions=None):
    """Emit sessions/index.html — a flat scrollable listing of every session.
    Sits alongside the per-session directories, so links are relative to
    session-NN-slug/index.html (no ../sessions/ prefix)."""
    completions = completions or {}
    by_phase = {p["num"]: p for p in PHASES}

    cards = []
    for s in SESSIONS:
        phase = by_phase[s["phase"]]
        entry = completions.get(s["num"], {})
        completed_chip = (
            '<span class="sess-chip sess-chip-done">Completed</span>'
            if entry.get("has_complete") else ""
        )
        preview = s["why"].split(".")[0].strip() + "."
        slug_dir = f"session-{s['num']:02d}-{s['slug']}"
        phase_short = phase["title"].split(": ", 1)[1] if ": " in phase["title"] else phase["title"]
        cards.append(
            f'<a class="sess-card" href="{slug_dir}/index.html">'
            f'<div class="sess-card-head">'
            f'<span class="sess-num">SESSION {s["num"]:02d}</span>'
            f'<span class="sess-phase">Phase {phase["num"]:02d} · {html_escape(phase_short)}</span>'
            f'{completed_chip}'
            f'</div>'
            f'<div class="sess-title">{html_escape(s["title"])}</div>'
            f'<div class="sess-preview">{html_escape(preview)}</div>'
            f'<div class="sess-meta">{html_escape(s["duration"])}</div>'
            f'</a>'
        )

    n_done = sum(1 for v in completions.values() if v.get("has_complete"))
    n_total = len(SESSIONS)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Socratic Sessions · NSE7 Enterprise Firewall 7.6</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;0,700;0,800;1,400;1,500&family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg:#faf5e9; --surface:#fffdf5; --surface-2:#f5eed9;
    --border:#d4c89a; --border-dim:#ebe1c2;
    --text:#0a1838; --text-soft:#1e2f5a; --text-muted:#6b7794;
    --blue:#1e40af; --blue-light:#eff4fc; --blue-border:#b8cce8;
    --ink-dark:#0d1a3a; --ink-accent:#9bb8e6;
    --green:#1a7c4a; --green-light:#dff0e1; --green-border:#a7d8b0;
  }}
  *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
  html,body{{min-height:100vh;}}
  body{{font-family:'Cormorant Garamond',serif;background:var(--bg);color:var(--text);display:flex;flex-direction:column;}}
  header{{padding:48px 60px 36px;background:var(--ink-dark);color:#fbf7ec;}}
  .breadcrumb{{font-family:'Outfit',sans-serif;font-size:11px;letter-spacing:0.12em;color:var(--ink-accent);margin-bottom:12px;text-transform:uppercase;}}
  .breadcrumb a{{color:var(--ink-accent);text-decoration:none;}}
  .breadcrumb a:hover{{color:#fff;}}
  .breadcrumb-sep{{margin:0 8px;opacity:0.6;}}
  .eyebrow{{display:inline-flex;align-items:center;gap:8px;background:rgba(155,184,230,0.1);border:1px solid rgba(155,184,230,0.28);padding:5px 14px;border-radius:20px;font-family:'Outfit',sans-serif;font-size:11px;color:var(--ink-accent);letter-spacing:0.1em;margin-bottom:14px;text-transform:uppercase;}}
  header h1{{font-family:'Playfair Display',serif;font-size:48px;font-weight:700;line-height:1.02;margin-bottom:12px;letter-spacing:-0.01em;}}
  header h1 em{{font-style:italic;font-weight:500;color:var(--ink-accent);}}
  header p{{font-family:'Cormorant Garamond',serif;font-size:18px;font-style:italic;color:rgba(251,247,236,0.6);max-width:820px;line-height:1.6;}}
  .count-strip{{padding:16px 60px;background:var(--surface);border-bottom:1px solid var(--border);font-family:'Outfit',sans-serif;font-size:12px;letter-spacing:0.12em;color:var(--text-muted);text-transform:uppercase;}}
  .count-strip strong{{color:var(--blue);}}
  main{{flex:1;padding:40px 60px 60px;max-width:1200px;margin:0 auto;width:100%;}}
  .sess-grid{{display:flex;flex-direction:column;gap:14px;}}
  .sess-card{{display:block;background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:20px 24px;text-decoration:none;color:var(--text);transition:border-color .15s, transform .15s;}}
  .sess-card:hover{{border-color:var(--blue);transform:translateY(-2px);}}
  .sess-card-head{{display:flex;align-items:center;gap:14px;margin-bottom:8px;flex-wrap:wrap;}}
  .sess-num{{font-family:'Outfit',sans-serif;font-size:10px;font-weight:700;letter-spacing:0.2em;color:var(--blue);background:var(--blue-light);border:1px solid var(--blue-border);padding:3px 10px;border-radius:10px;text-transform:uppercase;}}
  .sess-phase{{font-family:'Outfit',sans-serif;font-size:10px;font-weight:600;letter-spacing:0.14em;color:var(--text-muted);text-transform:uppercase;}}
  .sess-chip{{font-family:'Outfit',sans-serif;font-size:9px;font-weight:700;letter-spacing:0.16em;padding:2px 9px;border-radius:12px;text-transform:uppercase;border:1px solid;}}
  .sess-chip-done{{background:var(--green-light);color:var(--green);border-color:var(--green-border);}}
  .sess-title{{font-family:'Playfair Display',serif;font-size:22px;font-weight:600;color:var(--text);line-height:1.22;margin-bottom:6px;}}
  .sess-card:hover .sess-title{{color:var(--blue);}}
  .sess-preview{{font-family:'Cormorant Garamond',serif;font-size:16px;font-style:italic;color:var(--text-soft);line-height:1.55;margin-bottom:8px;}}
  .sess-meta{{font-family:'Outfit',sans-serif;font-size:11px;color:var(--text-muted);letter-spacing:0.06em;}}
  footer{{padding:18px 60px;border-top:1px solid var(--border);background:var(--surface);font-family:'Outfit',sans-serif;font-size:11px;letter-spacing:0.14em;color:var(--text-muted);text-transform:uppercase;text-align:center;}}
  footer span{{color:var(--blue);}}
  @media(max-width:640px){{
    header{{padding:32px 24px 24px;}}
    header h1{{font-size:32px;}}
    .count-strip{{padding:12px 24px;}}
    main{{padding:24px 20px 40px;}}
    .sess-card{{padding:16px 18px;}}
  }}
</style>
</head>
<body>
<header>
  <div class="breadcrumb">
    <a href="../index.html">Home</a>
    <span class="breadcrumb-sep">›</span>Socratic Sessions
  </div>
  <div class="eyebrow">Socratic Sessions · NSE7 Enterprise Firewall 7.6</div>
  <h1>Socratic <em>Sessions</em></h1>
  <p>Flat listing of all {n_total} sessions in the order they're meant to be studied. Every session naturally follows the previous one — you can also enter the story at any point.</p>
</header>
<div class="count-strip"><strong>{n_total}</strong> sessions · <strong>{n_done}</strong> completed · one continuous learning story</div>
<main>
  <div class="sess-grid">
    {"".join(cards)}
  </div>
</main>
<footer>NSE7 EF 7.6 <span>·</span> Socratic Curriculum <span>·</span> {n_total} sessions</footer>
</body>
</html>
"""
    out_path = SESSIONS_DIR / "index.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")

# ---------------------------------------------------------------------------
# LANDING PAGE (index.html) — one-stop front door to every hub
# ---------------------------------------------------------------------------

def render_landing(extras, completions, standalone_extras):
    n_sessions = len(SESSIONS)
    n_phases = len(PHASES)
    n_completed = sum(1 for v in completions.values() if v.get("has_complete"))

    def _count_kind(kind):
        session_count = sum(len(extras.get(s["num"], {}).get(kind, [])) for s in SESSIONS)
        standalone_count = sum(len(e[kind]) for e in standalone_extras)
        return session_count + standalone_count

    n_guides = _count_kind("guides")
    n_bites = _count_kind("bites")
    n_nibbles = _count_kind("nibbles")
    n_extras_total = n_guides + n_bites + n_nibbles

    tiles = [
        ("study-plan/index.html", "PLAN",      "chip-plan",     "Study Plan",              f"{n_sessions} sessions across {n_phases} phases — the full curriculum hub."),
        ("sessions/index.html",   "SESSIONS",  "chip-sessions", "Socratic Sessions",       f"Flat listing of all {n_sessions} sessions in order — one card each."),
        ("extras.html#bites",     "BITE",      "chip-bite",     "Bites",                   f"{n_bites} focused single-concept explainers."),
        ("extras.html#nibbles",   "NIBBLE",    "chip-nibble",   "Nibbles",                 f"{n_nibbles} short reference cards / cheat sheets."),
        ("completed-sessions.html", "COMPLETED", "chip-complete", "Completed Study Guides", f"{n_completed} of {n_sessions} sessions finished — polished HTML study guides."),
        ("labs/index.html",       "LABS",      "chip-labs",     "Hands-On Labs",           (f"{sum(1 for l in LABS if not l.get('concept_only') and not l.get('is_orientation'))} hands-on labs + orientation across the shared topology — Socratic predict → run → verify." if LABS else "Empty — feed a lab guide PDF and run /build-lab-plan.")),
        ("extras.html",           "ALL",       "chip-all",      "Extras (all)",            f"{n_extras_total} items — combined guides · bites · nibbles."),
    ]

    tiles_html = "".join(
        f'<a class="tile" href="{href}">'
        f'<span class="tile-chip {chip_class}">{chip}</span>'
        f'<span class="tile-title">{html_escape(title)}</span>'
        f'<span class="tile-desc">{html_escape(desc)}</span>'
        f'<span class="tile-arrow">→</span>'
        f'</a>'
        for href, chip, chip_class, title, desc in tiles
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NSE7 Enterprise Firewall 7.6 — Socratic Curriculum</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;0,700;0,800;1,400;1,500&family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg:#faf5e9; --surface:#fffdf5; --surface-2:#f5eed9;
    --border:#d4c89a; --border-dim:#ebe1c2;
    --text:#0a1838; --text-soft:#1e2f5a; --text-muted:#6b7794;
    --blue:#1e40af; --blue-vivid:#2563eb; --blue-light:#eff4fc; --blue-border:#b8cce8;
    --ink-dark:#0d1a3a; --ink-accent:#9bb8e6;
    --green:#1a7c4a; --green-light:#dff0e1; --green-border:#a7d8b0;
    --amber:#b45309; --amber-light:#fcf2c3; --amber-border:#f3d68a;
    --plum:#7c1a5f; --plum-light:#f7e5f0; --plum-border:#d8a7c5;
    --teal:#0f766e; --teal-light:#ccfbf1; --teal-border:#5eead4;
  }}
  *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
  html,body{{min-height:100vh;}}
  body{{font-family:'Cormorant Garamond',serif;background:var(--bg);color:var(--text);display:flex;flex-direction:column;}}
  header{{padding:56px 60px 40px;background:var(--ink-dark);color:#fbf7ec;}}
  .eyebrow{{display:inline-flex;align-items:center;gap:8px;background:rgba(155,184,230,0.1);border:1px solid rgba(155,184,230,0.28);padding:5px 14px;border-radius:20px;font-family:'Outfit',sans-serif;font-size:11px;color:var(--ink-accent);letter-spacing:0.12em;margin-bottom:16px;text-transform:uppercase;}}
  .dot-live{{width:6px;height:6px;background:var(--ink-accent);border-radius:50%;display:inline-block;animation:blink 2.4s ease-in-out infinite;}}
  @keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:0.3}}}}
  header h1{{font-family:'Playfair Display',serif;font-size:56px;font-weight:700;line-height:1.02;letter-spacing:-0.015em;margin-bottom:12px;}}
  header h1 em{{font-style:italic;font-weight:500;color:var(--ink-accent);}}
  header p{{font-family:'Cormorant Garamond',serif;font-size:19px;font-style:italic;color:rgba(251,247,236,0.6);max-width:760px;line-height:1.55;}}
  main{{flex:1;padding:48px 60px 72px;}}
  .tile-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px;max-width:1200px;margin:0 auto;}}
  .tile{{position:relative;display:flex;flex-direction:column;gap:12px;padding:26px 28px 30px;background:var(--surface);border:1px solid var(--border);border-radius:14px;text-decoration:none;color:var(--text);transition:transform .18s ease, box-shadow .18s ease, border-color .18s ease;overflow:hidden;}}
  .tile:hover{{transform:translateY(-2px);box-shadow:0 8px 24px -12px rgba(10,24,56,0.18);border-color:var(--blue);}}
  .tile-chip{{align-self:flex-start;font-family:'Outfit',sans-serif;font-size:10px;font-weight:700;letter-spacing:0.16em;padding:4px 10px;border-radius:12px;text-transform:uppercase;}}
  .chip-plan{{background:var(--blue-light);color:var(--blue);border:1px solid var(--blue-border);}}
  .chip-sessions{{background:var(--blue-light);color:var(--blue);border:1px solid var(--blue-border);}}
  .chip-complete{{background:var(--green-light);color:var(--green);border:1px solid var(--green-border);}}
  .chip-guide{{background:var(--green-light);color:var(--green);border:1px solid var(--green-border);}}
  .chip-bite{{background:var(--blue-light);color:var(--blue);border:1px solid var(--blue-border);}}
  .chip-nibble{{background:var(--amber-light);color:var(--amber);border:1px solid var(--amber-border);}}
  .chip-all{{background:var(--plum-light);color:var(--plum);border:1px solid var(--plum-border);}}
  .chip-labs{{background:var(--teal-light);color:var(--teal);border:1px solid var(--teal-border);}}
  .tile-title{{font-family:'Playfair Display',serif;font-size:26px;font-weight:700;color:var(--text);line-height:1.15;}}
  .tile-desc{{font-family:'Cormorant Garamond',serif;font-size:16px;color:var(--text-soft);line-height:1.55;}}
  .tile-arrow{{position:absolute;right:22px;bottom:20px;font-family:'Outfit',sans-serif;font-size:22px;color:var(--blue);transition:transform .18s ease;}}
  .tile:hover .tile-arrow{{transform:translateX(4px);}}
  footer{{padding:18px 60px;border-top:1px solid var(--border);background:var(--surface);font-family:'Outfit',sans-serif;font-size:11px;letter-spacing:0.14em;color:var(--text-muted);text-transform:uppercase;text-align:center;}}
  footer span{{color:var(--blue);}}
  @media(max-width:640px){{
    header{{padding:36px 24px 28px;}}
    header h1{{font-size:36px;}}
    header p{{font-size:16px;}}
    main{{padding:28px 20px 44px;}}
    .tile-grid{{grid-template-columns:1fr;gap:14px;}}
    .tile{{padding:22px 22px 26px;}}
    .tile-title{{font-size:22px;}}
    footer{{padding:14px 24px;}}
  }}
</style>
</head>
<body>
<header>
  <div class="eyebrow"><span class="dot-live"></span>Socratic Curriculum · NSE7 EF 7.6</div>
  <h1>NSE7 Enterprise <em>Firewall 7.6</em></h1>
  <p>One door to every study surface — the plan, the finished guides, and every extra you've built along the way.</p>
</header>
<main>
  <div class="tile-grid">
    {tiles_html}
  </div>
</main>
<footer>NSE7 EF 7.6 <span>·</span> Socratic Curriculum <span>·</span> {n_sessions} sessions <span>·</span> {n_completed}/{n_sessions} completed <span>·</span> {n_extras_total} extras</footer>
</body>
</html>
"""
    (ROOT / "index.html").write_text(html, encoding="utf-8")

# ---------------------------------------------------------------------------
# IMAGE PROMPTS FILE
# ---------------------------------------------------------------------------

def write_prompts_file():
    blocks = []
    blocks.append("NSE7 Enterprise Firewall 7.6 Socratic Curriculum — Image Prompts")
    blocks.append("=" * 60)
    blocks.append("")
    blocks.append("Style preamble (applied to every prompt below):")
    blocks.append("")
    blocks.append(STYLE_PREAMBLE)
    blocks.append("")
    blocks.append("=" * 60)
    blocks.append("")

    # Hub phase images
    for phase in PHASES:
        blocks.append(f"images/hub/phase-{phase['num']:02d}-{phase['slug']}.png")
        blocks.append("")
        blocks.append(phase["image_prompt"] + "\n\n" + STYLE_PREAMBLE)
        blocks.append("")
        blocks.append("=" * 60)
        blocks.append("")

    # Per-session hero images
    for s in SESSIONS:
        blocks.append(f"sessions/session-{s['num']:02d}-{s['slug']}/images/hero.png")
        blocks.append("")
        blocks.append(s["image_prompt"] + "\n\n" + STYLE_PREAMBLE)
        blocks.append("")
        blocks.append("=" * 60)
        blocks.append("")

    (IMAGES_DIR / "prompts.txt").write_text("\n".join(blocks), encoding="utf-8")

# ---------------------------------------------------------------------------
# FOLDER STRUCTURE
# ---------------------------------------------------------------------------

def ensure_image_folders():
    (IMAGES_DIR / "hub").mkdir(parents=True, exist_ok=True)
    for s in SESSIONS:
        (SESSIONS_DIR / f"session-{s['num']:02d}-{s['slug']}" / "images").mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    ensure_image_folders()

    # Discover post-completion artifacts once
    extras = discover_extras()
    completions = discover_completions()
    standalone_extras = discover_standalone_extras()

    for s in SESSIONS:
        render_session(s, extras=extras, completions=completions)

    render_study_plan_index(extras=extras, completions=completions, standalone_extras=standalone_extras)
    render_sessions_index(completions=completions)
    render_completed_hub(completions)
    render_extras_hub(extras, standalone_extras=standalone_extras)
    render_landing(extras, completions, standalone_extras)
    render_labs_hub()

    # Old root-level study-plan.html is superseded by study-plan/index.html.
    old_study_plan = ROOT / "study-plan.html"
    if old_study_plan.exists():
        os.remove(old_study_plan)
    for l in LABS:
        render_lab_page(l)
    normalize_sorted_breadcrumbs()
    normalize_page_transitions()
    write_prompts_file()

    n_extras = sum(len(items) for kinds in extras.values() for items in kinds.values())
    n_standalone = sum(len(e[k]) for e in standalone_extras for k in ("guides", "bites", "nibbles"))
    n_completed = sum(1 for v in completions.values() if v.get("has_complete"))
    n_summaries = sum(1 for v in completions.values() if v.get("has_summary"))

    print(f"Wrote study-plan/index.html")
    print(f"Wrote sessions/index.html (Socratic Sessions listing)")
    print(f"Wrote {len(SESSIONS)} session pages to sessions/session-NN-slug/index.html")
    print(f"Wrote images/prompts.txt with {len(PHASES) + len(SESSIONS)} prompts")
    print(f"Ensured images/hub/ and {len(SESSIONS)} per-session sessions/session-NN-slug/images/ folders")
    print(f"Wrote completed-sessions.html ({n_completed} completed, {n_summaries} summaries)")
    print(f"Wrote extras.html ({n_extras} session-linked + {n_standalone} standalone)")
    print(f"Wrote index.html (landing page)")
    report_completion_validation(completions)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
NSE7 Enterprise Firewall 7.6 Socratic Curriculum Generator.

Produces:
  - study-plan.html (hub: 8 phases + roadmap + objective map + journey narrative)
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
      <a href="../../study-plan.html">Curriculum</a>
      <span class="breadcrumb-sep">›</span>
      <a href="../../study-plan.html#phase-{phase_num_pad}">Phase {phase_num} — {phase_title_esc}</a>
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
        prev_href = "../../study-plan.html"
        prev_title = "NSE7 EF 7.6 Curriculum"
        prev_disabled = ""

    if next_s:
        next_label = f"Session {next_s['num']:02d}"
        next_href = sibling_session_href(next_s)
        next_title = html_escape(next_s["title"])
        next_disabled = ""
    else:
        next_label = "the Curriculum Hub"
        next_href = "../../study-plan.html"
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

def render_hub(extras=None, completions=None, standalone_extras=None):
    extras = extras or {}
    completions = completions or {}
    standalone_extras = standalone_extras or []
    completed_count = sum(1 for v in completions.values() if v.get("has_complete"))
    extras_exist = any(bool(v) for v in extras.values()) or bool(standalone_extras)
    has_extras = extras_exist
    # Phase sections
    phase_sections_html = []
    nav_tabs_html = []
    for phase in PHASES:
        nav_tabs_html.append(
            f'<a class="nav-tab" href="#phase-{phase["num"]:02d}">Phase {phase["num"]:02d}</a>'
        )

    # Build phase blocks
    for phase in PHASES:
        sessions_in_phase = [s for s in SESSIONS if s["phase"] == phase["num"]]
        cards = []
        for s in sessions_in_phase:
            obj_str = ", ".join(s["objectives"]) if s["objectives"] else "<em>story / transition</em>"
            cards.append(f"""
        <div class="session-card">
          <div class="session-card-num">SESSION {s['num']:02d}</div>
          <a class="session-card-title" href="sessions/{session_filename(s)}">{html_escape(s['title'])}</a>
          <div class="session-card-meta">{html_escape(s['duration'])} · Objectives: {obj_str}</div>
          <p class="session-card-why">{html_escape(s['why'].split('.')[0] + '.')}</p>
        </div>""")

        full_prompt = f"{phase['image_prompt']}\n\n{STYLE_PREAMBLE}"
        phase_sections_html.append(f"""
    <div class="section-block" id="phase-{phase['num']:02d}">
      <div class="section-label">PHASE {phase['num']:02d}</div>
      <h2>{html_escape(phase['title'].split(': ')[0])} — <em>{html_escape(phase['title'].split(': ', 1)[1] if ': ' in phase['title'] else phase['title'])}</em></h2>
      <div class="section-img-wrap">
        <img src="images/hub/phase-{phase['num']:02d}-{phase['slug']}.png" class="section-img"
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
            links.append(f'<a href="sessions/{session_filename(s)}">S{sn:02d}</a>')
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
                f'<tr><td>{s["num"]:02d}</td><td><a href="sessions/{session_filename(s)}">{html_escape(s["title"])}</a></td><td>{html_escape(s["duration"])}</td></tr>'
            )

    # Build left sidebar entries.
    # Structure: [collapse-toggle, Progress tab, Curriculum group, Reference group].
    # Both groups are independently collapsible; the whole sidebar is collapsible to a thin icon rail.
    side_entries = []

    # Top-level collapse button for the whole sidebar
    side_entries.append(
        '<button class="hub-side-collapse" id="hub-side-collapse" aria-label="Toggle sidebar">'
        '<span class="hub-side-collapse-chevron">«</span>'
        '<span class="hub-side-collapse-label">Collapse</span>'
        '</button>'
    )

    # How-to-Use tab — pinned, first-time onboarding for the Claude Project workflow
    side_entries.append(
        '<button class="hub-side-tab" data-target="how-to-use">'
        '<span class="hub-side-tab-icon">?</span>'
        '<span class="hub-side-tab-title">How to Use</span>'
        '</button>'
    )

    # Completed tab — pinned, external link to completed-sessions.html
    side_entries.append(
        f'<a class="hub-side-tab hub-side-tab-external" href="completed-sessions.html">'
        f'<span class="hub-side-tab-icon">✓</span>'
        f'<span class="hub-side-tab-title">Completed</span>'
        f'<span class="hub-side-badge">{completed_count}/{len(SESSIONS)}</span>'
        f'</a>'
    )

    # Progress tab — pinned, always visible (not inside a collapsible group)
    side_entries.append(
        '<button class="hub-side-tab" data-target="progress">'
        '<span class="hub-side-tab-icon">P</span>'
        '<span class="hub-side-tab-title">Progress</span>'
        '<span class="hub-side-badge" id="side-progress-badge">0/40</span>'
        '</button>'
    )

    # Curriculum group — 8 phases
    curriculum_items = []
    for phase in PHASES:
        n_sessions = sum(1 for s in SESSIONS if s["phase"] == phase["num"])
        short_title = phase["title"].split(": ", 1)[1] if ": " in phase["title"] else phase["title"]
        curriculum_items.append(
            f'<button class="hub-side-tab" data-target="phase-{phase["num"]:02d}">'
            f'<span class="hub-side-tab-icon">{phase["num"]:02d}</span>'
            f'<span class="hub-side-tab-title">Phase {phase["num"]:02d} — {html_escape(short_title)}</span>'
            f'<span class="hub-side-tab-sub">{n_sessions}</span>'
            f'</button>'
        )
    side_entries.append('<div class="hub-sidebar-divider"></div>')
    side_entries.append(
        '<div class="hub-sidebar-group" data-group="curriculum">'
        '<button class="hub-side-group-head" data-group-toggle="curriculum">'
        '<span class="hub-side-group-chevron">▾</span>'
        '<span class="hub-side-group-label">The Curriculum</span>'
        '</button>'
        '<div class="hub-sidebar-group-body">'
        + "".join(curriculum_items) +
        '</div>'
        '</div>'
    )

    # Reference group — Roadmap, Objective Map, Journey
    reference_items = [
        '<button class="hub-side-tab" data-target="roadmap"><span class="hub-side-tab-icon">R</span><span class="hub-side-tab-title">Roadmap</span></button>',
        '<button class="hub-side-tab" data-target="objective-map"><span class="hub-side-tab-icon">O</span><span class="hub-side-tab-title">Objective Map</span></button>',
        '<button class="hub-side-tab" data-target="journey"><span class="hub-side-tab-icon">J</span><span class="hub-side-tab-title">The Journey</span></button>',
    ]
    side_entries.append('<div class="hub-sidebar-divider"></div>')
    side_entries.append(
        '<div class="hub-sidebar-group" data-group="reference">'
        '<button class="hub-side-group-head" data-group-toggle="reference">'
        '<span class="hub-side-group-chevron">▾</span>'
        '<span class="hub-side-group-label">Reference</span>'
        '</button>'
        '<div class="hub-sidebar-group-body">'
        + "".join(reference_items) +
        '</div>'
        '</div>'
    )

    # Extras group — Guides / Bites / Nibbles anchors into extras.html (only when any extras exist)
    if has_extras:
        extras_items = [
            '<a class="hub-side-tab hub-side-tab-external" href="extras.html#guides"><span class="hub-side-tab-icon">G</span><span class="hub-side-tab-title">Guides</span></a>',
            '<a class="hub-side-tab hub-side-tab-external" href="extras.html#bites"><span class="hub-side-tab-icon">B</span><span class="hub-side-tab-title">Bites</span></a>',
            '<a class="hub-side-tab hub-side-tab-external" href="extras.html#nibbles"><span class="hub-side-tab-icon">N</span><span class="hub-side-tab-title">Nibbles</span></a>',
        ]
        side_entries.append('<div class="hub-sidebar-divider"></div>')
        side_entries.append(
            '<div class="hub-sidebar-group" data-group="extras">'
            '<button class="hub-side-group-head" data-group-toggle="extras">'
            '<span class="hub-side-group-chevron">▾</span>'
            '<span class="hub-side-group-label">Extras</span>'
            '</button>'
            '<div class="hub-sidebar-group-body">'
            + "".join(extras_items) +
            '</div>'
            '</div>'
        )

    sidebar_html = "\n        ".join(side_entries)

    # Per-phase checkbox blocks for the progress section
    progress_blocks = []
    for phase in PHASES:
        sessions_in_phase = [s for s in SESSIONS if s["phase"] == phase["num"]]
        rows = []
        for s in sessions_in_phase:
            rows.append(
                f'<label class="progress-row" data-session="{s["num"]}">'
                f'<input type="checkbox" class="progress-check" data-session="{s["num"]}">'
                f'<span class="progress-num">{s["num"]:02d}</span>'
                f'<a class="progress-title" href="sessions/{session_filename(s)}">{html_escape(s["title"])}</a>'
                f'<span class="progress-dur">{html_escape(s["duration"])}</span>'
                f'</label>'
            )
        progress_blocks.append(
            f'<div class="progress-phase"><div class="progress-phase-head">PHASE {phase["num"]:02d} — {html_escape(phase["title"])}'
            f' <span class="progress-phase-stats" data-phase="{phase["num"]}">0 / {len(sessions_in_phase)}</span></div>'
            f'{"".join(rows)}</div>'
        )
    progress_phase_html = "".join(progress_blocks)

    socratic_methodology_esc = html_escape(SOCRATIC_METHODOLOGY_TEXT)

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
  /* LAYOUT: left sidebar + right main pane */
  .hub-layout{{display:flex;align-items:flex-start;max-width:1440px;margin:0 auto;}}
  .hub-sidebar{{width:300px;flex-shrink:0;position:sticky;top:0;align-self:flex-start;height:100vh;overflow-y:auto;background:var(--surface);border-right:1px solid var(--border);padding:24px 16px 32px;display:flex;flex-direction:column;gap:4px;transition:width 0.18s ease, padding 0.18s ease;}}
  /* Top-level collapse toggle */
  .hub-side-collapse{{display:flex;align-items:center;gap:10px;width:100%;background:transparent;border:none;color:var(--text-muted);font-family:'Outfit',sans-serif;font-size:10px;font-weight:600;letter-spacing:0.14em;text-transform:uppercase;padding:6px 14px 12px;cursor:pointer;}}
  .hub-side-collapse:hover{{color:var(--text);}}
  .hub-side-collapse-chevron{{display:inline-block;font-size:14px;line-height:1;transition:transform 0.18s ease;}}
  /* Collapsible groups */
  .hub-sidebar-group{{display:flex;flex-direction:column;gap:4px;}}
  .hub-side-group-head{{display:flex;align-items:center;gap:8px;width:100%;background:transparent;border:none;color:var(--text-muted);font-family:'Outfit',sans-serif;font-size:9px;font-weight:700;letter-spacing:0.2em;text-transform:uppercase;padding:6px 14px;cursor:pointer;text-align:left;}}
  .hub-side-group-head:hover{{color:var(--text);}}
  .hub-side-group-chevron{{display:inline-block;font-size:10px;line-height:1;width:10px;text-align:center;transition:transform 0.15s ease;}}
  .hub-sidebar-group.group-collapsed .hub-side-group-chevron{{transform:rotate(-90deg);}}
  .hub-sidebar-group-body{{display:flex;flex-direction:column;gap:4px;}}
  .hub-sidebar-group.group-collapsed .hub-sidebar-group-body{{display:none;}}
  /* Tab icon (hidden by default; shown only when sidebar is collapsed) */
  .hub-side-tab-icon{{display:none;font-family:'Outfit',sans-serif;font-size:10px;font-weight:700;letter-spacing:0.04em;color:var(--text-muted);background:var(--surface-2);border:1px solid var(--border);border-radius:6px;padding:3px 0;min-width:32px;text-align:center;flex-shrink:0;}}
  .hub-side-tab.active .hub-side-tab-icon{{color:var(--blue);border-color:var(--blue);background:var(--blue-light);}}
  /* COLLAPSED sidebar — thin icon rail */
  .hub-sidebar.collapsed{{width:64px;padding:24px 6px 32px;}}
  .hub-sidebar.collapsed .hub-side-collapse{{justify-content:center;padding:6px 0 12px;}}
  .hub-sidebar.collapsed .hub-side-collapse-label{{display:none;}}
  .hub-sidebar.collapsed .hub-side-collapse-chevron{{transform:scaleX(-1);}}
  .hub-sidebar.collapsed .hub-side-group-head,
  .hub-sidebar.collapsed .hub-sidebar-divider,
  .hub-sidebar.collapsed .hub-sidebar-label{{display:none;}}
  /* When sidebar is collapsed, always show group bodies regardless of group-collapsed */
  .hub-sidebar.collapsed .hub-sidebar-group.group-collapsed .hub-sidebar-group-body{{display:flex;}}
  .hub-sidebar.collapsed .hub-side-tab{{justify-content:center;padding:8px 4px;border-radius:8px;border-left:none;}}
  .hub-sidebar.collapsed .hub-side-tab.active{{background:var(--blue-light);}}
  .hub-sidebar.collapsed .hub-side-tab-title,
  .hub-sidebar.collapsed .hub-side-tab-sub,
  .hub-sidebar.collapsed .hub-side-badge{{display:none;}}
  .hub-sidebar.collapsed .hub-side-tab-icon{{display:inline-flex;align-items:center;justify-content:center;}}
  .hub-sidebar-label{{font-family:'Outfit',sans-serif;font-size:9px;font-weight:700;letter-spacing:0.2em;text-transform:uppercase;color:var(--text-muted);padding:0 14px;margin-bottom:8px;}}
  .hub-sidebar-divider{{height:1px;background:var(--border-dim);margin:10px 14px;}}
  .hub-side-tab{{display:flex;align-items:center;gap:8px;width:100%;background:transparent;border:none;border-left:3px solid transparent;color:var(--text-soft);font-family:'Outfit',sans-serif;font-size:12px;font-weight:600;letter-spacing:0.06em;text-align:left;padding:10px 14px;cursor:pointer;border-radius:0 8px 8px 0;transition:background 0.15s, color 0.15s, border-color 0.15s;}}
  .hub-side-tab:hover{{background:var(--blue-glow);color:var(--text);}}
  .hub-side-tab.active{{background:var(--blue-light);color:var(--blue);border-left-color:var(--blue);}}
  .hub-side-tab-title{{flex:1;line-height:1.3;}}
  .hub-side-tab-sub{{font-family:'Outfit',sans-serif;font-size:10px;font-weight:600;color:var(--text-muted);letter-spacing:0.04em;}}
  .hub-side-tab.active .hub-side-tab-sub{{color:var(--blue);}}
  .hub-side-badge{{background:var(--blue);color:#fff;font-size:10px;font-weight:700;padding:2px 8px;border-radius:10px;letter-spacing:0.04em;font-family:'Outfit',sans-serif;}}
  .hub-side-tab.active .hub-side-badge{{background:var(--blue-deep);}}
  a.hub-side-tab{{text-decoration:none;}}
  .hub-side-tab-external:hover .hub-side-tab-title{{color:var(--blue);}}
  .hub-main{{flex:1;min-width:0;}}
  main{{margin:0;padding:0;}}
  .main-content{{padding:36px 48px 60px 48px;max-width:1080px;}}
  /* one-section-at-a-time view */
  .section-block{{display:none;}}
  .section-block.active-section{{display:block;}}
  @media(max-width:900px){{
    .hub-layout{{flex-direction:column;}}
    .hub-sidebar{{position:static;width:100%;height:auto;max-height:none;flex-direction:row;overflow-x:auto;overflow-y:hidden;border-right:none;border-bottom:1px solid var(--border);padding:10px 12px;gap:6px;}}
    .hub-sidebar.collapsed{{width:100%;padding:10px 12px;}}
    .hub-sidebar-label,.hub-sidebar-divider,.hub-side-collapse,.hub-side-group-head{{display:none;}}
    .hub-sidebar-group,.hub-sidebar-group-body{{display:contents;}}
    .hub-sidebar-group.group-collapsed .hub-sidebar-group-body{{display:contents;}}
    .hub-side-tab{{flex-shrink:0;border-left:none;border-bottom:3px solid transparent;border-radius:8px 8px 0 0;padding:8px 14px;white-space:nowrap;}}
    .hub-side-tab.active{{border-left-color:transparent;border-bottom-color:var(--blue);}}
    .main-content{{padding:24px 24px 40px;}}
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
  .progress-reset{{margin-left:auto;font-family:'Outfit',sans-serif;font-size:10px;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:var(--text-muted);background:transparent;border:1px solid var(--border);border-radius:6px;padding:5px 12px;cursor:pointer;}}
  .progress-reset:hover{{color:var(--text);border-color:var(--text);}}
  .progress-bar-wrap{{width:100%;height:8px;background:var(--surface-2);border-radius:8px;overflow:hidden;}}
  .progress-bar-fill{{height:100%;background:var(--blue);transition:width 0.25s ease;}}
  .progress-phases{{display:flex;flex-direction:column;gap:16px;}}
  .progress-phase{{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:12px 18px;}}
  .progress-phase-head{{font-family:'Outfit',sans-serif;font-size:11px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:var(--text);margin-bottom:8px;display:flex;justify-content:space-between;}}
  .progress-phase-stats{{font-weight:600;color:var(--blue);letter-spacing:0.06em;}}
  .progress-row{{display:flex;align-items:center;gap:12px;padding:6px 0;cursor:pointer;}}
  .progress-row.completed .progress-title{{text-decoration:line-through;color:var(--text-muted);}}
  .progress-check{{appearance:none;width:18px;height:18px;border:1.5px solid var(--border);border-radius:4px;cursor:pointer;flex-shrink:0;background:var(--surface);position:relative;}}
  .progress-check:hover{{border-color:var(--blue);}}
  .progress-check:checked{{background:var(--blue);border-color:var(--blue);}}
  .progress-check:checked::after{{content:'✓';position:absolute;color:#fff;font-size:13px;font-weight:700;top:-1px;left:3px;}}
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

<div class="hub-layout">

  <aside class="hub-sidebar" id="hub-sidebar">
    <div class="hub-sidebar-label">Navigate</div>
        {sidebar_html}
  </aside>

  <main class="hub-main">
  <div class="main-content">

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
          <p>Open the session you're about to study (for example, <a href="sessions/session-01-nse7-story-exam-map/index.html">Session 01</a>). Scroll to the <em>Session context — paste into your Claude NSE7 tutor</em> block near the bottom of the page, click <strong>Copy</strong>, and paste it into a fresh chat inside your Claude Project. That prompt hands Claude the exact scenario, objectives, and Socratic setup for the session, so the tutor immediately picks up the investigation where the story left off.</p>
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
          <span class="progress-count-block"><span id="progress-count">0</span> <em>of 40 complete</em></span>
          <span><span id="progress-pct">0%</span></span>
          <button class="progress-reset" onclick="resetProgress()">Reset progress</button>
        </div>
        <div class="progress-bar-wrap"><div class="progress-bar-fill" id="progress-fill" style="width:0%"></div></div>
      </div>
      <div class="progress-phases">
        {progress_phase_html}
      </div>
    </div>

{''.join(phase_sections_html)}

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
</div>

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

/* ── Section routing (left-sidebar single-pane view) ── */
const VALID_SECTIONS = new Set(['how-to-use','progress','phase-01','phase-02','phase-03','phase-04','phase-05','phase-06','phase-07','phase-08','roadmap','objective-map','journey']);
const DEFAULT_SECTION = 'how-to-use';
function showSection(id, opts) {{
  if (!VALID_SECTIONS.has(id)) id = DEFAULT_SECTION;
  document.querySelectorAll('.section-block').forEach(function(b) {{
    b.classList.toggle('active-section', b.id === id);
  }});
  document.querySelectorAll('.hub-side-tab').forEach(function(t) {{
    t.classList.toggle('active', t.dataset.target === id);
  }});
  /* Intentionally NO scroll — clicking a sidebar tab preserves the user's
     current scroll position in both the main pane and the document. */
  if (opts && opts.updateHash !== false) {{
    const newHash = '#' + id;
    if (location.hash !== newHash) history.pushState(null, '', newHash);
  }}
}}
document.querySelectorAll('.hub-side-tab').forEach(function(tab) {{
  tab.addEventListener('click', function(e) {{
    if (!tab.dataset.target) return;  /* external anchor (Completed / Extras) — let the browser navigate */
    e.preventDefault();
    showSection(tab.dataset.target);
  }});
}});
window.addEventListener('hashchange', function() {{
  const id = (location.hash || '#' + DEFAULT_SECTION).slice(1);
  showSection(id, {{updateHash: false}});
}});

/* Initial section from hash, or default */
(function() {{
  const initial = (location.hash || '#' + DEFAULT_SECTION).slice(1);
  if (!VALID_SECTIONS.has(initial)) {{
    history.replaceState(null, '', '#' + DEFAULT_SECTION);
    showSection(DEFAULT_SECTION, {{updateHash: false}});
  }} else {{
    showSection(initial, {{updateHash: false}});
  }}
}})();

/* ── Sidebar collapse + group collapse (persistent via localStorage) ── */
const SIDEBAR_KEY = 'nse7-ef-sidebar-collapsed';
const GROUP_KEY_PREFIX = 'nse7-ef-sidebar-group-';
const hubSidebar = document.getElementById('hub-sidebar');
const sidebarCollapseBtn = document.getElementById('hub-side-collapse');
function applySidebarCollapsed(collapsed) {{
  if (!hubSidebar) return;
  hubSidebar.classList.toggle('collapsed', collapsed);
  if (collapsed) localStorage.setItem(SIDEBAR_KEY, '1');
  else localStorage.removeItem(SIDEBAR_KEY);
}}
function applyGroupCollapsed(group, collapsed) {{
  const el = document.querySelector('.hub-sidebar-group[data-group="' + group + '"]');
  if (!el) return;
  el.classList.toggle('group-collapsed', collapsed);
  if (collapsed) localStorage.setItem(GROUP_KEY_PREFIX + group, '1');
  else localStorage.removeItem(GROUP_KEY_PREFIX + group);
}}
if (sidebarCollapseBtn) {{
  sidebarCollapseBtn.addEventListener('click', function() {{
    applySidebarCollapsed(!hubSidebar.classList.contains('collapsed'));
  }});
}}
document.querySelectorAll('.hub-side-group-head').forEach(function(head) {{
  head.addEventListener('click', function() {{
    const group = head.dataset.groupToggle;
    const el = document.querySelector('.hub-sidebar-group[data-group="' + group + '"]');
    if (!el) return;
    applyGroupCollapsed(group, !el.classList.contains('group-collapsed'));
  }});
}});
/* Apply persisted states immediately (default = expanded) */
if (localStorage.getItem(SIDEBAR_KEY) === '1') applySidebarCollapsed(true);
['curriculum','reference'].forEach(function(g) {{
  if (localStorage.getItem(GROUP_KEY_PREFIX + g) === '1') applyGroupCollapsed(g, true);
}});

/* ── Progress tracking ── */
const PROGRESS_KEY = 'nse7-ef-curriculum-progress';
function getProgress() {{
  try {{ return JSON.parse(localStorage.getItem(PROGRESS_KEY) || '[]'); }}
  catch(e) {{ return []; }}
}}
function saveProgress(arr) {{
  localStorage.setItem(PROGRESS_KEY, JSON.stringify(arr));
}}
function renderProgress() {{
  const done = new Set(getProgress());
  const total = 40;
  const count = done.size;
  const pct = Math.round((count / total) * 100);
  document.getElementById('progress-count').textContent = count;
  document.getElementById('progress-pct').textContent = pct + '%';
  document.getElementById('progress-fill').style.width = pct + '%';
  const badge = document.getElementById('side-progress-badge');
  if (badge) badge.textContent = count + '/' + total;
  document.querySelectorAll('.progress-check').forEach(function(cb) {{
    const n = Number(cb.dataset.session);
    cb.checked = done.has(n);
    cb.closest('.progress-row').classList.toggle('completed', done.has(n));
  }});
  document.querySelectorAll('.progress-phase-stats').forEach(function(el) {{
    const phase = Number(el.dataset.phase);
    const rows = el.closest('.progress-phase').querySelectorAll('.progress-check');
    let phaseDone = 0;
    rows.forEach(function(cb) {{ if (done.has(Number(cb.dataset.session))) phaseDone++; }});
    el.textContent = phaseDone + ' / ' + rows.length;
  }});
}}
function toggleSession(n, checked) {{
  const set = new Set(getProgress());
  if (checked) set.add(n); else set.delete(n);
  saveProgress(Array.from(set).sort((a, b) => a - b));
  renderProgress();
}}
function resetProgress() {{
  if (!confirm('Reset all session progress?')) return;
  saveProgress([]);
  renderProgress();
}}
document.querySelectorAll('.progress-check').forEach(function(cb) {{
  cb.addEventListener('change', function(e) {{
    e.stopPropagation();
    toggleSession(Number(cb.dataset.session), cb.checked);
  }});
}});
document.querySelectorAll('.progress-row').forEach(function(row) {{
  row.addEventListener('click', function(e) {{
    if (e.target.tagName === 'A' || e.target.tagName === 'INPUT') return;
    const cb = row.querySelector('.progress-check');
    cb.checked = !cb.checked;
    toggleSession(Number(cb.dataset.session), cb.checked);
  }});
}});
renderProgress();
</script>
</body>
</html>
"""

    (ROOT / "study-plan.html").write_text(hub_html, encoding="utf-8")

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
        f'<a href="study-plan.html">Curriculum</a>'
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
                ("Curriculum", "../../study-plan.html"),
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
                    ("Curriculum", "../../../study-plan.html"),
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
        ("study-plan.html", "PLAN",      "chip-plan",     "Study Plan",              f"{n_sessions} sessions across {n_phases} phases — the full curriculum hub."),
        ("completed-sessions.html", "COMPLETED", "chip-complete", "Completed Study Guides", f"{n_completed} of {n_sessions} sessions finished — polished HTML study guides."),
        ("extras.html#guides",  "GUIDE",   "chip-guide",   "Guides",                  f"{n_guides} long-form companion pages that dive deeper than a session can."),
        ("extras.html#bites",   "BITE",    "chip-bite",    "Bites",                   f"{n_bites} focused single-concept explainers."),
        ("extras.html#nibbles", "NIBBLE",  "chip-nibble",  "Nibbles",                 f"{n_nibbles} short reference cards / cheat sheets."),
        ("extras.html",         "ALL",     "chip-all",     "Extras (all)",            f"{n_extras_total} items — combined guides · bites · nibbles."),
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
  .chip-complete{{background:var(--green-light);color:var(--green);border:1px solid var(--green-border);}}
  .chip-guide{{background:var(--green-light);color:var(--green);border:1px solid var(--green-border);}}
  .chip-bite{{background:var(--blue-light);color:var(--blue);border:1px solid var(--blue-border);}}
  .chip-nibble{{background:var(--amber-light);color:var(--amber);border:1px solid var(--amber-border);}}
  .chip-all{{background:var(--plum-light);color:var(--plum);border:1px solid var(--plum-border);}}
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

    render_hub(extras=extras, completions=completions, standalone_extras=standalone_extras)
    render_completed_hub(completions)
    render_extras_hub(extras, standalone_extras=standalone_extras)
    render_landing(extras, completions, standalone_extras)
    normalize_sorted_breadcrumbs()
    write_prompts_file()

    n_extras = sum(len(items) for kinds in extras.values() for items in kinds.values())
    n_standalone = sum(len(e[k]) for e in standalone_extras for k in ("guides", "bites", "nibbles"))
    n_completed = sum(1 for v in completions.values() if v.get("has_complete"))
    n_summaries = sum(1 for v in completions.values() if v.get("has_summary"))

    print(f"Wrote study-plan.html")
    print(f"Wrote {len(SESSIONS)} session pages to sessions/session-NN-slug/index.html")
    print(f"Wrote images/prompts.txt with {len(PHASES) + len(SESSIONS)} prompts")
    print(f"Ensured images/hub/ and {len(SESSIONS)} per-session sessions/session-NN-slug/images/ folders")
    print(f"Wrote completed-sessions.html ({n_completed} completed, {n_summaries} summaries)")
    print(f"Wrote extras.html ({n_extras} session-linked + {n_standalone} standalone)")
    print(f"Wrote index.html (landing page)")
    report_completion_validation(completions)

if __name__ == "__main__":
    main()

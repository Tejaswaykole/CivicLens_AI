# CivicLens AI — Complaint Taxonomy & Annotation Guidelines

> **Status**: Provisional / Experimental  
> **Target Track**: AI/ML Track — Phase 1 & 2  
> **Review Requirement**: Subject to municipal stakeholder and administrative validation before production deployment.

---

## 1. Complaint Category Taxonomy

To enable reliable grievance classification and automated department routing, CivicLens AI adopts an initial five-category taxonomy tailored to common municipal public administration workflows.

### Summary Table

| Category | Primary Focus | Recommended Department | Example Scenarios |
| :--- | :--- | :--- | :--- |
| **Sanitation** | Solid waste management, street cleaning, garbage dumping, dead animal removal. | Department of Public Services / Solid Waste Management | Uncollected household garbage, overflow of public trash bins, illegal street dumping. |
| **Roads** | Physical carriageway, pavements, potholes, road cave-ins, traffic signs, lane markings. | Department of Public Works / Roads & Engineering | Deep potholes, broken divider curb, sinkhole on roadway, damaged traffic signage. |
| **Electricity** | Street lighting, power distribution infrastructure, hanging cables, blown transformers. | Electricity Distribution Board / Public Lighting Division | Dark street due to non-functioning lamps, sparking overhead wires, damaged feeder box. |
| **Water Supply** | Potable water delivery, water pipe bursts, low pressure, contamination, supply schedule. | Water Works / Municipal Water Supply & Sewerage Board | Ruptured underground main line gushing water, discolored/foul tap water, zero supply for 3 days. |
| **Public Health** | Disease vector breeding, sewage overflow, public toilets, biological/health hazards. | Department of Public Health & Preventive Sanitation | Open sewer stagnation causing mosquito infestation, hospital medical waste dumped in public alley. |

---

### Detailed Category Definitions, Inclusions & Exclusions

#### A. Sanitation
- **Description**: Management of urban solid waste, litter, collection logistics, and street hygiene.
- **Inclusions**:
  - Missed household waste collection rounds.
  - Overflowing municipal dustbins and community collection points.
  - Debris, bulk discarded furniture, construction rubbish in public passages.
  - Dead animal carcass disposal on streets.
- **Exclusions**:
  - Liquid sewage overflow or open drain contamination $\rightarrow$ Classify as **Public Health** or **Water Supply** (if entering drinking water lines).
  - Potholes filled with garbage $\rightarrow$ Classify as **Roads** if road integrity is the principal hazard, or **Sanitation** if clearing trash is the primary operational need.

#### B. Roads
- **Description**: Civil road infrastructure, pavements, traffic regulation devices, and pedestrian sidewalks.
- **Inclusions**:
  - Potholes, road surface erosion, crater formations on vehicular roads.
  - Damaged, missing, or fallen regulatory/warning road signs.
  - Broken footpath slabs, missing manhole covers on footpaths/road edges.
  - Missing or damaged guardrails, median barriers, and street speed breakers.
- **Exclusions**:
  - Non-functioning street lighting mounted on poles $\rightarrow$ Classify as **Electricity**.
  - Water accumulation on road due to burst pipe $\rightarrow$ Classify as **Water Supply**.

#### C. Electricity
- **Description**: Municipal electrical distribution, public illumination, overhead transmission safety, and junction boxes.
- **Inclusions**:
  - Street lights not turning on at night, or staying on during daytime.
  - Sparking, low-hanging, or snapped overhead power cables.
  - Exposed, broken, or submerged electrical junction boxes and distribution pillars.
  - Transformer oil leakage, buzzing, or localized blackout on public poles.
- **Exclusions**:
  - Private indoor household wiring issues (out of scope for municipal 311).
  - Broken traffic lights / signals without electrical fire risk $\rightarrow$ Route to Traffic/Roads division, but if live bare wires are exposed, cross-flag with **Electricity**.

#### D. Water Supply
- **Description**: Municipal drinking water pipeline network, distribution pressure, pipeline integrity, and potable water quality.
- **Inclusions**:
  - High-pressure water main bursts, pipe leaks causing street flooding or clean water waste.
  - Contaminated drinking water supply (muddy, turbid, foul odor, chemical taste).
  - No water supply, severe low pressure, erratic timing against published supply schedules.
  - Broken water meters, stolen air-release valves on municipal mains.
- **Exclusions**:
  - Stormwater drain siltation $\rightarrow$ Classify as **Sanitation** (clearing debris) or **Public Health** (if sewage stagnation occurs).
  - Standing rain puddles on roads without pipeline leak $\rightarrow$ Classify as **Roads** (poor drainage camber).

#### E. Public Health
- **Description**: Environmental health hazards, disease control, biological hazards, sanitation infrastructure failing into public health risks.
- **Inclusions**:
  - Overflowing manholes discharging raw blackwater/sewage into residential streets.
  - Open stagnant wastewater pools breeding mosquitoes (dengue/malaria risk).
  - Food safety complaints regarding unlicensed/unhygienic public street food preparation.
  - Biohazard waste, animal excrement accumulation near schools/hospitals.
- **Exclusions**:
  - Routine dry garbage accumulation $\rightarrow$ Classify as **Sanitation**.
  - Emergency medical assistance or ambulance dispatch $\rightarrow$ Out of scope for 311/CivicLens (immediate 108/112 emergency escalation).

---

### Ambiguous & Cross-Cutting Cases

| Ambiguous Scenario | Primary Category | Secondary / Cross-Department Concern | Rationale |
| :--- | :--- | :--- | :--- |
| **Burst water pipe flooding a potholed road** | **Water Supply** | Roads | Repairing the high-pressure water pipe must occur before civil road repair can commence. |
| **Raw sewage leaking into a potable water pipeline** | **Public Health** | Water Supply | Critical disease outbreak risk (cholera, typhoid); immediate public health intervention required. |
| **Low-hanging live wire touching tree branches above a footpath** | **Electricity** | Roads / Parks | Imminent electrocution hazard takes operational precedence. |
| **Missing manhole cover on a dark street** | **Roads** | Electricity | Primary hazard is fall/vehicle fatal accident; darkness is an environmental multiplier. |

---

## 2. Priority Annotation Guidelines

Priority assesses the **urgency of response**, determining operational triage and service level agreements (SLAs).

> [!IMPORTANT]
> **Priority is never inferred purely from the category name or simple keyword presence.** A pothole can be Low (shallow depression on an alleyway) or High (crater on a 60 km/h highway causing active vehicular accidents).

### Operational Priority Definitions

```
                     HIGH
         ┌─────────────────────────┐
         │ Immediate Danger to Life│
         │ Severe Health Outbreak  │
         │ Critical Infrastructure │
         └─────────────────────────┘
                      ▲
                      │ Escalation
         ┌─────────────────────────┐
         │ Significant Disruption  │
         │ Large Population Impact │
         │ Moderate Risk / Degrad. │
         └─────────────────────────┘
                   MEDIUM
                      ▲
                      │ Escalation
         ┌─────────────────────────┐
         │ Minor Inconvenience     │
         │ Isolated Individual Case│
         │ No Immediate Risk       │
         └─────────────────────────┘
                     LOW
```

### Criteria Breakdown

#### 1. High Priority (Target SLA: Immediate to 24 Hours)
- **Immediate Hazard to Human Life / Safety**:
  - Snapped live electrical wires hanging at pedestrian height.
  - Open, uncovered manholes on unlit arterial roadways.
  - Road cave-ins, deep sinkholes on high-speed or heavily congested roads.
- **Critical Contamination & Public Health Crisis**:
  - Sewage mixing into the community drinking water supply.
  - Chemical spills or medical biohazard waste dumped near residential areas or schools.
- **Complete Critical Infrastructure Failure**:
  - Water main burst cutting off water supply to an entire hospital, quarantine center, or major locality.

#### 2. Medium Priority (Target SLA: 2 to 4 Days)
- **Significant Service Disruption (No Immediate Life Threat)**:
  - Low water pressure or no water supply affecting a street or apartment block for over 24 hours.
  - Street lighting out across an entire residential block (increasing nighttime crime risk).
  - Large garbage dump overflow accumulating for over 3 days near commercial areas.
- **Traffic Impairment without Catastrophic Failure**:
  - Non-functioning traffic signal at a moderate-traffic intersection.
  - Substantial pothole on an inner-neighborhood street causing vehicles to brake abruptly.

#### 3. Low Priority (Target SLA: 5 to 10 Days)
- **Aesthetic or Minor Nuisance Issues**:
  - Faded zebra crossing or lane marking.
  - Single non-functioning street lamp on a well-illuminated avenue.
  - Stray litter or dry leaves on pedestrian footpath.
  - Broken bench or aesthetic damage to municipal park fence.
- **Isolated, Low-Impact Defects**:
  - Shallow surface gravel loss on a low-traffic dead-end lane.
  - Pre-scheduled request for bulky waste pickup (e.g., old sofa/mattress).

---

## 3. Human-in-the-Loop & Uncertainty Rules

1. **Experimental Nature**: All synthetic or automated priority labels are **suggestions** to assist human triage officers, never unreviewed ground truth.
2. **Ambiguity Escalation**: If a complaint contains ambiguous urgency indicators (e.g., "water looks dirty and child got sick"), the system must default to **Medium or High** (safety-first heuristic) and flag for immediate officer review.
3. **Audit Trail**: Every automated triage decision must output an inspectable `annotation_rationale` explaining which specific complaint factors influenced the suggestion.

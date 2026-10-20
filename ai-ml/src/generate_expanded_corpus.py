"""
CivicLens AI — Version 2 Expanded Grievance Corpus Generator.

Generates an expanded, highly diverse grievance corpus with:
- Increased linguistic variation and distinct vocabulary per category.
- Explicit short, informal, and compound/multi-sentence complaint styles.
- Clear disambiguation between Public Health vectors and Sanitation solid waste.
- Safety-critical flags and ambiguous scenario tracking.
- Output saved as a separate versioned dataset (synthetic_complaints_v2.csv),
  preserving the original synthetic_complaints.csv unchanged.
"""

from __future__ import annotations

import argparse
import random
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd

from schema import (
    CATEGORY_DEPARTMENT_MAPPING,
    VALID_CATEGORIES,
    VALID_PRIORITIES,
    validate_dataframe,
)

# Extended template library: 15 diverse templates per category across multiple phrasing styles
# Format: (template_str, priority, rationale, is_safety_critical, is_ambiguous)
TEMPLATES_V2: Dict[str, List[Tuple[str, str, str, bool, bool]]] = {
    "Sanitation": [
        # Standard Formal
        (
            "Large carcass of a dead cow lying on {location} for more than 24 hours, rotting and emitting foul stench near school entrance.",
            "High",
            "Severe biological decomposition and waste hazard obstructing school entrance.",
            True,
            False,
        ),
        (
            "Massive pile of decaying garbage on {location} caught fire, producing toxic plastic smoke suffocating nearby residents.",
            "High",
            "Active toxic fire and respiratory smoke emergency from municipal waste dump.",
            True,
            False,
        ),
        (
            "Community garbage bin at {location} has been overflowing for the past 4 days without pickup, spilling onto footpath.",
            "Medium",
            "Multi-day uncollected municipal waste obstructing pedestrian movement.",
            False,
            False,
        ),
        (
            "Garbage collection truck has skipped our lane on {location} for three consecutive rounds this week.",
            "Medium",
            "Disruption of scheduled municipal door-to-door trash pickup rounds.",
            False,
            False,
        ),
        (
            "Need clearing of dry leaf litter and garden pruning waste piled near the street corner on {location}.",
            "Low",
            "Non-hazardous dry organic garden waste causing minor visual aesthetic clutter.",
            False,
            False,
        ),
        (
            "Request to install an additional separate dry/wet community dustbin near {location} for market shoppers.",
            "Low",
            "Public infrastructure enhancement request with no existing hazard.",
            False,
            False,
        ),
        # Informal / Colloquial / Direct citizen phrasing
        (
            "Kachra gaadi not coming to {location} since Monday, all household rubbish bags are piling up outside our gate.",
            "Medium",
            "Missed domestic waste collection round causing local accumulation.",
            False,
            False,
        ),
        (
            "People are shamelessly throwing plastic bags and food wrappers all over the sidewalk near {location}.",
            "Low",
            "Littering and dry plastic waste scatter on footpath.",
            False,
            False,
        ),
        (
            "Dead dog decaying on roadside near {location}. Smells horrible please send sanitation crew right away.",
            "High",
            "Decomposing stray animal carcass on active pedestrian lane.",
            True,
            False,
        ),
        (
            "Commercial market swept rubbish swept into corner of {location} by shopkeepers, blocking the alley.",
            "Medium",
            "Commercial trade solid waste dumped in pedestrian passage.",
            False,
            False,
        ),
        (
            "Old broken wooden sofa and mattress dumped on empty plot at {location}, need heavy truck to remove.",
            "Low",
            "Bulky furniture dumping without acute hazard.",
            False,
            False,
        ),
        (
            "Dumping ground boundary wall broke on {location}, trash spilling into public road.",
            "High",
            "Structural containment failure of municipal transfer station.",
            True,
            False,
        ),
        # Compound / Edge Cases
        (
            "Garbage bin dumped right into stormwater gutter at {location}, blocking drainage flow.",
            "Medium",
            "Solid waste dumped into civil drain creating blockage risk.",
            False,
            True,
        ),
        (
            "Construction debris and broken bricks unloaded on bicycle track near {location}.",
            "Low",
            "Inert construction and demolition rubble occupying cycle track.",
            False,
            False,
        ),
        (
            "Waste collection worker asking for illegal cash tips to pick up segregation bins on {location}.",
            "Low",
            "Sanitation service delivery administrative complaint.",
            False,
            False,
        ),
    ],
    "Roads": [
        # Standard Formal
        (
            "Massive road cave-in and 4-foot deep sinkhole opened up suddenly in the middle of {location}, already caused two motorcycle crashes.",
            "High",
            "Imminent life-threatening structural road collapse causing active vehicular accidents.",
            True,
            False,
        ),
        (
            "Heavy concrete divider slab broken and jutting into the fast lane on {location} with no warning signs.",
            "High",
            "Severe collision hazard on high-speed roadway capable of fatal vehicular impact.",
            True,
            False,
        ),
        (
            "Entire metal manhole cover missing on {location}; deep trench is completely submerged in water and invisible to drivers.",
            "High",
            "Submerged invisible fatal trap on active carriageway.",
            True,
            True,
        ),
        (
            "Cluster of three deep potholes on {location} causing severe vehicular traffic jams and vehicle axle damage.",
            "Medium",
            "Substantial road surface erosion disrupting vehicular traffic.",
            False,
            False,
        ),
        (
            "Pedestrian footpath slabs broken and missing over a 50-meter stretch on {location}, forcing elders to walk on the busy street.",
            "Medium",
            "Compromised pedestrian walkway forcing foot traffic into vehicular roadway.",
            False,
            False,
        ),
        (
            "Road name signage on {location} is bent and partially rusted, making the street name illegible.",
            "Low",
            "Minor informational defect with zero impact on physical safety.",
            False,
            False,
        ),
        (
            "Zebra crossing paint has faded significantly on {location} and requires repainting before monsoon.",
            "Low",
            "Routine pavement marking maintenance without structural defect.",
            False,
            False,
        ),
        # Informal / Colloquial / Direct citizen phrasing
        (
            "Very dangerous crater on road at {location}. Scooters are skidding every single evening.",
            "High",
            "Deep road crater actively causing two-wheeler skids and injuries.",
            True,
            False,
        ),
        (
            "Unscientific speed breaker built without permission on {location}, car undercarriages hitting badly.",
            "Medium",
            "Unauthorized civil road hump causing vehicular impacts.",
            False,
            False,
        ),
        (
            "Road tar washed away completely after rain on {location}, only sharp loose stones left.",
            "Medium",
            "Surface asphalt disintegration creating hazardous driving surface.",
            False,
            False,
        ),
        (
            "Footpath pavers sunk near bus stop on {location}, people tripping while boarding bus.",
            "Medium",
            "Sunken sidewalk paving stones near transit boarding zone.",
            False,
            False,
        ),
        (
            "Faded lane markings on flyover approach near {location}, drivers getting confused at night.",
            "Low",
            "Flyover approach civil delineation marking wear.",
            False,
            False,
        ),
        (
            "Guardrail along river bridge on {location} rusted through and collapsed, leaving 20ft drop unprotected.",
            "High",
            "Missing safety barrier on elevated structure exposing fatal fall hazard.",
            True,
            False,
        ),
        # Compound / Edge Cases
        (
            "Road dug up for pipeline on {location} left unpaved and muddy for past three months.",
            "Medium",
            "Unrestored civil road trench following utility excavation.",
            False,
            True,
        ),
        (
            "Traffic convex mirror at blind turn on {location} shattered by vandals.",
            "Low",
            "Civil traffic guidance mirror damage on blind curve.",
            False,
            False,
        ),
    ],
    "Electricity": [
        # Standard Formal
        (
            "Live overhead electrical wire snapped and is dangling 3 feet above waterlogged ground on {location}, continuously sparking.",
            "High",
            "Active high-voltage electrocution hazard directly threatening human life.",
            True,
            False,
        ),
        (
            "Public street distribution transformer on {location} is leaking smoking hot oil and making loud explosion noises.",
            "High",
            "Imminent transformer explosion and fire hazard in public area.",
            True,
            False,
        ),
        (
            "Cast iron base door of streetlight pole on {location} is missing, exposing uninsulated live 230V terminals right next to a playground.",
            "High",
            "Exposed live high-voltage electrical contact point adjacent to children's play area.",
            True,
            False,
        ),
        (
            "All street lights along {location} have remained dark for the last 5 nights, creating safety fears and total blackout.",
            "Medium",
            "Complete failure of public illumination over an entire neighborhood corridor.",
            False,
            False,
        ),
        (
            "Heavy tangled bundle of telecommunication and power service cables sagging dangerously low across the bus route on {location}.",
            "Medium",
            "Sagging overhead cable obstruction threatening tall public transit vehicles.",
            False,
            False,
        ),
        (
            "Single street light lamp flickering intermittently outside building on {location}.",
            "Low",
            "Isolated single luminaire failure where adjacent lighting is adequate.",
            False,
            False,
        ),
        (
            "Street light pole lamp remains switched on during bright daylight hours on {location}, wasting electricity.",
            "Low",
            "Timer/sensor calibration defect causing energy wastage without safety risk.",
            False,
            False,
        ),
        # Informal / Colloquial / Direct citizen phrasing
        (
            "Electric pole tilting at 45 degrees towards residential balcony on {location}, could fall anytime.",
            "High",
            "Structurally compromised utility pole carrying live conductors threatening collapse.",
            True,
            False,
        ),
        (
            "Severe voltage surge on {location} blew out refrigerators and television sets in 10 houses.",
            "Medium",
            "Grid distribution over-voltage causing domestic appliance burnout.",
            False,
            False,
        ),
        (
            "Feeder pillar box on {location} left wide open in heavy rain, sparks flying when vehicles pass.",
            "High",
            "Unprotected ground distribution panel arcing in wet weather.",
            True,
            False,
        ),
        (
            "Whole street completely pitch dark at night on {location}, women and elders feeling unsafe.",
            "Medium",
            "Prolonged public illumination outage on residential avenue.",
            False,
            False,
        ),
        (
            "Streetlight pole rusted at the bottom base on {location}, needs reinforcement.",
            "Low",
            "Early stage structural corrosion of lighting column.",
            False,
            False,
        ),
        (
            "High voltage hum and burning insulation smell coming from underground cable duct on {location}.",
            "High",
            "Underground cable insulation failure indicating imminent electrical cable fire.",
            True,
            False,
        ),
        # Compound / Edge Cases
        (
            "Tree branches overgrown into high tension power lines on {location}, showering sparks during wind.",
            "High",
            "Vegetation touching transmission lines creating recurring fire and blackout hazard.",
            True,
            True,
        ),
        (
            "Sodium vapor street lamp cover broken on {location}, bulb exposed to rain.",
            "Low",
            "Minor luminaire enclosure damage.",
            False,
            False,
        ),
    ],
    "Water Supply": [
        # Standard Formal
        (
            "Major 18-inch drinking water transmission pipeline burst on {location}, gushing drinking water into homes and flooding the substation.",
            "High",
            "Catastrophic clean water infrastructure breach causing structural flooding and resource loss.",
            True,
            False,
        ),
        (
            "Municipal tap water supplied to all households on {location} is smelling heavily of sewage and looks dark brown; several children fell sick.",
            "High",
            "Severe biological contamination of municipal drinking water causing acute community illness.",
            True,
            True,
        ),
        (
            "Zero water supply across the entire district hospital and residential quarters on {location} for past 36 hours.",
            "High",
            "Total disruption of drinking water supply to critical healthcare facility.",
            True,
            False,
        ),
        (
            "Drinking water pipeline on {location} has been leaking continuously for 3 days, forming large puddles and reducing supply pressure.",
            "Medium",
            "Persistent potable water wastage and moderate supply pressure degradation.",
            False,
            False,
        ),
        (
            "Tap water pressure on {location} has dropped drastically, water barely trickles from ground floor taps during the scheduled supply.",
            "Medium",
            "Severe service degradation leaving households unable to fill daily domestic storage.",
            False,
            False,
        ),
        (
            "Slow drip leak from municipal air release valve on {location}, losing about a bucket of water per day.",
            "Low",
            "Minor mechanical valve seepage with negligible pressure loss.",
            False,
            False,
        ),
        (
            "Water meter glass is cloudy and difficult to read on the external connection on {location}.",
            "Low",
            "Routine metering maintenance with no disruption to actual water delivery.",
            False,
            False,
        ),
        # Informal / Colloquial / Direct citizen phrasing
        (
            "No drinking water in our colony taps on {location} for four consecutive days, water tanker mafia charging high rates.",
            "Medium",
            "Prolonged disruption of municipal piped potable water supply.",
            False,
            False,
        ),
        (
            "Clean filtered drinking water pipe broken underground at {location}, drinking water bubbling up through tiles.",
            "Medium",
            "Subsurface potable distribution line fracture wasting treated water.",
            False,
            False,
        ),
        (
            "Tap water coming out milky white with strong chlorine chemical odor on {location}, people afraid to drink.",
            "Medium",
            "Excess chemical dosing or aeration defect in treated municipal supply.",
            False,
            False,
        ),
        (
            "Underground valve chamber cover stolen on {location}, clean water supply valve exposed to road dirt.",
            "Medium",
            "Distribution control valve enclosure compromised.",
            False,
            False,
        ),
        (
            "Municipal overhead water storage reservoir overflowing on {location}, clean treated water cascading down streets.",
            "Medium",
            "Reservoir telemetry or float switch failure wasting potable reserves.",
            False,
            False,
        ),
        (
            "Mud and sand particles coming in domestic drinking tap water on {location} after pipeline repair work.",
            "Medium",
            "Turbidity and particulate contamination in piped drinking water.",
            False,
            False,
        ),
        # Compound / Edge Cases
        (
            "Water supply pipeline burst on {location} has washed away the road foundation, creating a muddy sinkhole.",
            "High",
            "High-pressure water main breach causing civil road sub-base collapse.",
            True,
            True,
        ),
        (
            "Old iron water service pipe showing rust stains near connection on {location}.",
            "Low",
            "Minor external service line oxidation with no flow disruption.",
            False,
            False,
        ),
    ],
    "Public Health": [
        # Standard Formal (Vector, Epidemic & Biological Focus)
        (
            "Main sewer manhole overflowing raw fecal blackwater directly into the kindergarten courtyard on {location}.",
            "High",
            "Immediate severe bio-contamination exposing young children to enteric pathogens.",
            True,
            False,
        ),
        (
            "Dozens of dead poultry birds dumped in open drainage canal on {location}, severe stench and suspected avian disease risk.",
            "High",
            "Suspected zoonotic disease outbreak and biohazard in public watercourse.",
            True,
            False,
        ),
        (
            "Hospital waste including IV drips and blood bags left unattended in the open municipal dumpster behind {location}.",
            "High",
            "Uncontained medical biohazard in public space violating bio-safety norms.",
            True,
            False,
        ),
        (
            "Stagnant sewage pool accumulated in open plot on {location} for over two weeks, heavy mosquito swarms creating malaria risk.",
            "Medium",
            "Persistent stagnant wastewater acting as vector breeding ground in residential vicinity.",
            False,
            False,
        ),
        (
            "Public community toilet facility on {location} is choked, running without flushing water and in unhygienic condition.",
            "Medium",
            "Sanitation facility breakdown forcing open defecation risk in dense community.",
            False,
            False,
        ),
        (
            "Request for routine anti-mosquito fogging drive before the rainy season starts on {location}.",
            "Low",
            "Preventive routine municipal health request with no reported localized outbreak.",
            False,
            False,
        ),
        (
            "Stray pig or cattle enclosure in backyard on {location} creating mild unpleasant odor in adjacent alley.",
            "Low",
            "Localized neighborhood odor nuisance with no direct disease vector escalation.",
            False,
            False,
        ),
        # Explicit Epidemiological & Clinical Phrasing
        (
            "Multiple dengue and chikungunya cases reported in our lane on {location}; open wastewater drains full of mosquito larvae.",
            "High",
            "Active vector-borne viral disease outbreak linked to stagnant drainage water.",
            True,
            False,
        ),
        (
            "Open drainage canal choked with black sludge on {location}, unbearable sewer fumes causing nausea and headache among residents.",
            "Medium",
            "Toxic sewage gas emissions and sewer stagnation impacting public respiratory comfort.",
            False,
            False,
        ),
        (
            "Street food stall cluster on {location} washing utensils in filthy gutter water, patrons falling ill with jaundice.",
            "High",
            "Direct transmission route for waterborne enteric hepatitis/typhoid from unhygienic commercial food preparation.",
            True,
            False,
        ),
        (
            "Pack of aggressive stray dogs with suspected rabies biting pedestrians near {location}, two people hospitalized.",
            "High",
            "Active rabies transmission hazard and canine bite emergency in public thoroughfare.",
            True,
            False,
        ),
        (
            "Illegal chemical tanning effluent discharged into open neighborhood storm drain on {location}, caustic chemical fumes burning eyes.",
            "High",
            "Hazardous industrial toxic chemical discharge into urban residential stormwater channel.",
            True,
            False,
        ),
        (
            "Underground septic tank overflowing into alley pavement on {location}, raw faeces exposed to pedestrian footsteps.",
            "High",
            "Direct fecal-oral pathogen exposure route on pedestrian pathway.",
            True,
            False,
        ),
        # Compound / Edge Cases
        (
            "Public urinal on {location} has no drainage connection; urine pooling on public sidewalk.",
            "Medium",
            "Failed public sanitation asset discharging untreated waste into public pedestrian area.",
            False,
            True,
        ),
        (
            "Request inspection of unsanitary sweetmeat manufacturing unit operating in residential cellar on {location}.",
            "Low",
            "Preventive food safety regulatory inspection request.",
            False,
            False,
        ),
    ],
}

LOCATION_VARIATIONS = [
    "Sector 4 Main Market Road",
    "Near Gandhi Public School, Ward 12",
    "Behind Central Bus Terminal",
    "Shivaji Nagar 3rd Cross",
    "Opposite City Civil Hospital",
    "Industrial Estate Phase 2, Ring Road",
    "Kalyan Nagar Railway Crossing Lane",
    "Near Subhash Chandra Bose Park",
    "Adarsh Colony Block B",
    "Vikas Marg near Water Tank",
    "Nehru Stadium Approach Road",
    "Old Post Office Street, Ward 5",
]


def generate_expanded_corpus(
    seed: int = 42,
    samples_per_category: int = 60,
) -> pd.DataFrame:
    """Generate expanded version 2 corpus with 15 templates per category and richer diversity."""
    random.seed(seed)
    records: List[Dict[str, Any]] = []
    counter = 2001

    for category, category_templates in TEMPLATES_V2.items():
        dept = CATEGORY_DEPARTMENT_MAPPING[category]
        generated_for_category = 0

        while generated_for_category < samples_per_category:
            template_idx = random.randrange(len(category_templates))
            template, priority, rationale, safety_crit, ambiguous = category_templates[template_idx]
            template_id = f"{category[:3].upper()}_V2_T{template_idx + 1:02d}"
            location = random.choice(LOCATION_VARIATIONS)
            complaint_text = template.format(location=location)

            # Prevent duplicate texts
            if any(r["complaint_text"] == complaint_text for r in records):
                continue

            record = {
                "complaint_id": f"SYN-V2-{category[:3].upper()}-{counter:05d}",
                "complaint_text": complaint_text,
                "category": category,
                "priority": priority,
                "recommended_department": dept,
                "annotation_rationale": rationale,
                "source_type": "synthetic_template_v2",
                "review_status": "pending_review",
                "template_id": template_id,
                "is_safety_critical": safety_crit,
                "is_ambiguous": ambiguous,
                "reviewed_category": None,
                "reviewed_priority": None,
                "review_notes": "",
                "reviewer_id": None,
            }
            records.append(record)
            counter += 1
            generated_for_category += 1

    df = pd.DataFrame(records)
    # Shuffle deterministically
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Expanded Grievance Corpus V2 for CivicLens AI")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "data" / "processed" / "synthetic_complaints_v2.csv",
        help="Destination path for version 2 synthetic dataset",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--samples-per-cat", type=int, default=60, help="Samples per category")

    args = parser.parse_args()
    out_path = args.output.resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Generating expanded grievance corpus V2 (Seed: {args.seed}, Per Cat: {args.samples_per_cat})...")
    df = generate_expanded_corpus(seed=args.seed, samples_per_category=args.samples_per_cat)

    print("Validating generated corpus V2 against schema...")
    is_valid, errors = validate_dataframe(df)
    if not is_valid:
        print(f"[ERROR] Validation failed with {len(errors)} errors:")
        for e in errors[:5]:
            print(f"  - {e}")
        raise SystemExit(1)

    df.to_csv(out_path, index=False)
    print(f"Successfully generated {len(df)} records in V2 corpus.")
    print(f"Saved to: {out_path}")
    print("\nCategory Distribution:\n", df["category"].value_counts())
    print("\nPriority Distribution:\n", df["priority"].value_counts())
    print("\nSafety-Critical Flagged:", df["is_safety_critical"].sum())
    print("Ambiguous Flagged:", df["is_ambiguous"].sum())


if __name__ == "__main__":
    main()

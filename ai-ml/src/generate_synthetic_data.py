"""
CivicLens AI — Reproducible Synthetic Grievance Corpus Generator.

Generates a balanced, realistic, clearly labeled synthetic dataset of public
grievance complaint narratives across five categories and three priority levels.
"""

from __future__ import annotations

import argparse
import random
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

from schema import (
    CATEGORY_DEPARTMENT_MAPPING,
    VALID_CATEGORIES,
    VALID_PRIORITIES,
    validate_dataframe,
)

# Seeded template dictionaries with operational context, realistic wording,
# varied severity, and genuine domain indicators.
# Form: (text_template, priority, rationale)
TEMPLATES: Dict[str, List[Tuple[str, str, str]]] = {
    "Sanitation": [
        # High Priority
        (
            "Large carcass of a dead cow lying on {location} for more than 24 hours, rotting and emitting foul stench near school entrance.",
            "High",
            "Severe biological contamination and decomposition hazard near children/school premises.",
        ),
        (
            "Medical waste including used syringes, blood-stained bandages, and chemical bottles dumped openly on {location}.",
            "High",
            "Hazardous bio-medical waste posing immediate risk of infectious disease transmission.",
        ),
        (
            "Massive pile of decaying garbage on {location} caught fire, producing toxic plastic smoke suffocating nearby residents.",
            "High",
            "Active toxic fire and respiratory health emergency from burning municipal waste dump.",
        ),
        # Medium Priority
        (
            "Community garbage bin at {location} has been overflowing for the past 4 days without pickup, spilling onto footpath.",
            "Medium",
            "Significant community waste accumulation obstructing pedestrian movement and attracting stray animals.",
        ),
        (
            "Garbage collection truck has skipped our lane on {location} for three consecutive rounds this week.",
            "Medium",
            "Multi-day disruption of scheduled municipal waste collection service affecting an entire street.",
        ),
        (
            "Fish and poultry shop vendors dumping organic waste openly by the roadside on {location}, attracting large packs of aggressive dogs.",
            "Medium",
            "Commercial organic dumping creating persistent nuisance and stray animal hazard.",
        ),
        # Low Priority
        (
            "Need clearing of dry leaf litter and garden waste piled near the street corner on {location}.",
            "Low",
            "Non-hazardous dry organic garden waste causing minor visual aesthetic clutter.",
        ),
        (
            "Small amount of construction gravel and plastic wrappers discarded on the sidewalk near {location}.",
            "Low",
            "Minor isolated dry litter without environmental or health hazard.",
        ),
        (
            "Request to install an additional separate dry/wet community dustbin near {location} for market shoppers.",
            "Low",
            "Routine public infrastructure enhancement request with no existing hazard.",
        ),
    ],
    "Roads": [
        # High Priority
        (
            "Massive road cave-in and 4-foot deep sinkhole opened up suddenly in the middle of {location}, already caused two motorcycle crashes.",
            "High",
            "Imminent life-threatening structural road collapse causing active vehicular accidents.",
        ),
        (
            "Heavy concrete divider slab broken and jutting into the fast lane on {location} with no warning signs.",
            "High",
            "Severe collision hazard on high-speed roadway capable of causing fatal vehicular impact.",
        ),
        (
            "Entire metal manhole cover missing on {location}; deep trench is completely submerged in water and invisible to drivers.",
            "High",
            "Submerged invisible fatal trap on active carriageway.",
        ),
        # Medium Priority
        (
            "Cluster of three deep potholes on {location} causing severe vehicular traffic jams and vehicle axle damage.",
            "Medium",
            "Substantial road surface erosion disrupting vehicular traffic and damaging vehicles.",
        ),
        (
            "Pedestrian footpath slabs broken and missing over a 50-meter stretch on {location}, forcing elders to walk on the busy street.",
            "Medium",
            "Compromised pedestrian walkway forcing foot traffic into vehicular roadway.",
        ),
        (
            "Speed breaker on {location} is completely unpainted with no advance signage, causing sudden emergency braking.",
            "Medium",
            "Unmarked civil road obstruction causing abrupt braking and moderate collision risk.",
        ),
        # Low Priority
        (
            "Road name signage on {location} is bent and partially rusted, making the street name illegible.",
            "Low",
            "Minor informational defect with zero impact on physical vehicle or pedestrian safety.",
        ),
        (
            "Zebra crossing paint has faded significantly on {location} and requires repainting before monsoon.",
            "Low",
            "Routine pavement marking maintenance without immediate structural road defect.",
        ),
        (
            "Slight surface asphalt roughness and loose fine gravel on the dead-end lane of {location}.",
            "Low",
            "Minor cosmetic surface wear on low-speed cul-de-sac lane.",
        ),
    ],
    "Electricity": [
        # High Priority
        (
            "Live overhead electrical wire snapped and is dangling 3 feet above waterlogged ground on {location}, continuously sparking.",
            "High",
            "Active high-voltage electrocution hazard directly threatening human life.",
        ),
        (
            "Public street distribution transformer on {location} is leaking smoking hot oil and making loud explosion noises.",
            "High",
            "Imminent transformer explosion and fire hazard in dense public area.",
        ),
        (
            "Cast iron base door of streetlight pole on {location} is missing, exposing uninsulated live 230V terminals right next to a playground.",
            "High",
            "Exposed live high-voltage electrical contact point adjacent to children's play area.",
        ),
        # Medium Priority
        (
            "All street lights along {location} have remained dark for the last 5 nights, creating safety fears and total blackout.",
            "Medium",
            "Complete failure of public illumination over an entire neighborhood corridor.",
        ),
        (
            "Heavy tangled bundle of telecommunication and power service cables sagging dangerously low across the bus route on {location}.",
            "Medium",
            "Sagging overhead cable obstruction threatening tall public transit vehicles.",
        ),
        (
            "Frequent voltage fluctuations on {location} causing recurring domestic equipment damage and erratic power trippings.",
            "Medium",
            "Power quality instability affecting multiple households across the local grid feeder.",
        ),
        # Low Priority
        (
            "Single street light lamp flickering intermittently outside building number 12 on {location}.",
            "Low",
            "Isolated single luminaire failure where adjacent streetlights provide sufficient illumination.",
        ),
        (
            "Street light pole lamp remains switched on during bright daylight hours on {location}, wasting electricity.",
            "Low",
            "Timer/sensor calibration defect causing energy wastage without public safety risk.",
        ),
        (
            "Protective plastic junction box cover is cracked on pole near {location}, though internal wires are still insulated.",
            "Low",
            "Minor physical cosmetic casing damage with no immediate live wire exposure.",
        ),
    ],
    "Water Supply": [
        # High Priority
        (
            "Major 18-inch drinking water transmission pipeline burst on {location}, gushing drinking water into homes and flooding the substation.",
            "High",
            "Catastrophic clean water infrastructure breach causing structural flooding and severe resource loss.",
        ),
        (
            "Municipal tap water supplied to all households on {location} is smelling heavily of sewage and looks dark brown; several children fell sick.",
            "High",
            "Severe biological contamination of municipal drinking water causing acute community illness.",
        ),
        (
            "Zero water supply across the entire district hospital and residential staff quarters on {location} for past 36 hours.",
            "High",
            "Total disruption of water supply to critical healthcare facility.",
        ),
        # Medium Priority
        (
            "Drinking water pipeline on {location} has been leaking continuously for 3 days, forming large puddles and reducing supply pressure.",
            "Medium",
            "Persistent clean water wastage and moderate supply pressure degradation across the street.",
        ),
        (
            "Tap water pressure on {location} has dropped drastically, water barely trickles from ground floor taps during the scheduled 1-hour supply.",
            "Medium",
            "Severe service degradation leaving multiple households unable to fill daily domestic storage.",
        ),
        (
            "Municipal water supply schedule not adhered to on {location}; water released at 2 AM without prior public notice.",
            "Medium",
            "Unannounced operational timing failure disrupting daily domestic life across the ward.",
        ),
        # Low Priority
        (
            "Slow drip leak from municipal air release valve on {location}, losing about a bucket of water per day.",
            "Low",
            "Minor mechanical valve seepage with negligible pressure loss.",
        ),
        (
            "Water meter glass is cloudy and difficult to read on the external connection on {location}.",
            "Low",
            "Routine metering maintenance with no disruption to actual water delivery.",
        ),
        (
            "Request for periodic water quality testing and TDS report for the community booster pump on {location}.",
            "Low",
            "Proactive informational service request with no reported contamination symptom.",
        ),
    ],
    "Public Health": [
        # High Priority
        (
            "Main sewer manhole overflowing raw fecal blackwater directly into the kindergarten courtyard on {location}.",
            "High",
            "Immediate severe bio-contamination directly exposing young children to pathogens.",
        ),
        (
            "Dozens of dead poultry birds dumped in open drainage canal on {location}, severe stench and suspected avian disease risk.",
            "High",
            "Suspected zoonotic disease outbreak and biohazard in public watercourse.",
        ),
        (
            "Hospital waste including IV drips and blood bags left unattended in the open municipal dumpster behind {location}.",
            "High",
            "Uncontained medical biohazard in public space violating biological safety norms.",
        ),
        # Medium Priority
        (
            "Stagnant sewage pool accumulated in open plot on {location} for over two weeks, heavy mosquito swarms creating malaria risk.",
            "Medium",
            "Persistent stagnant wastewater acting as vector breeding ground in residential vicinity.",
        ),
        (
            "Public community toilet facility on {location} is choked, running without flushing water and in unhygienic condition.",
            "Medium",
            "Sanitation facility breakdown forcing open defecation risk in dense community.",
        ),
        (
            "Street food stall cluster on {location} washing utensils in open drainage channel without proper hygiene safeguards.",
            "Medium",
            "Public health sanitation violation posing foodborne illness risk to patrons.",
        ),
        # Low Priority
        (
            "Request for routine anti-mosquito fogging drive before the rainy season starts on {location}.",
            "Low",
            "Preventive routine municipal service request with no reported localized outbreak.",
        ),
        (
            "Stray pig or cattle enclosure in backyard on {location} creating mild unpleasant odor in adjacent alley.",
            "Low",
            "Localized neighborhood odor nuisance with no direct disease vector escalation.",
        ),
        (
            "Public handwashing basin faucet in municipal park on {location} needs washer replacement.",
            "Low",
            "Minor amenity plumbing defect in recreational public space.",
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
]


def generate_synthetic_corpus(seed: int = 42, samples_per_category: int = 30) -> pd.DataFrame:
    """Generate a balanced, diverse synthetic grievance dataset with deterministic seeding."""
    random.seed(seed)
    records: List[Dict[str, str]] = []

    counter = 1001

    for category, category_templates in TEMPLATES.items():
        dept = CATEGORY_DEPARTMENT_MAPPING[category]
        generated_for_category = 0

        # Cycle through templates and vary locations and phrasing
        while generated_for_category < samples_per_category:
            template_idx = random.randrange(len(category_templates))
            template, priority, rationale = category_templates[template_idx]
            template_id = f"{category[:3].upper()}_T{template_idx + 1:02d}"
            location = random.choice(LOCATION_VARIATIONS)
            complaint_text = template.format(location=location)

            # Prevent duplicate texts within generated set
            if any(r["complaint_text"] == complaint_text for r in records):
                continue

            record = {
                "complaint_id": f"SYN-{category[:3].upper()}-{counter:05d}",
                "complaint_text": complaint_text,
                "category": category,
                "priority": priority,
                "recommended_department": dept,
                "annotation_rationale": rationale,
                "source_type": "synthetic_template",
                "review_status": "pending_review",
                "template_id": template_id,
            }
            records.append(record)
            counter += 1
            generated_for_category += 1

    df = pd.DataFrame(records)
    # Shuffle deterministically
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic grievance corpus for CivicLens AI")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "data" / "processed" / "synthetic_complaints.csv",
        help="Destination CSV path for synthetic complaints",
    )
    parser.add_argument("--seed", "-s", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument(
        "--samples-per-cat",
        type=int,
        default=30,
        help="Number of synthetic records per category",
    )

    args = parser.parse_args()
    output_path = args.output.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Generating synthetic grievance corpus (Seed: {args.seed}, Per Cat: {args.samples_per_cat})...")
    df = generate_synthetic_corpus(seed=args.seed, samples_per_category=args.samples_per_cat)

    print(f"Validating generated corpus against schema...")
    is_valid, errors = validate_dataframe(df)
    if not is_valid:
        print(f"[ERROR] Schema validation failed with {len(errors)} errors:")
        for err in errors[:10]:
            print(f"  - {err}")
        raise SystemExit(1)

    df.to_csv(output_path, index=False)
    print(f"Successfully generated and validated {len(df)} records.")
    print(f"Saved to: {output_path}")
    print("\nCategory counts:\n", df["category"].value_counts())
    print("\nPriority counts:\n", df["priority"].value_counts())


if __name__ == "__main__":
    main()

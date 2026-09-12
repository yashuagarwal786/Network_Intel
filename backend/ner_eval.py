"""Repeatable Evaluation Dataset and Benchmarking Suite for VEIL NER.

Compares spaCy models and hybrid architectural enhancements across
diverse fictional investigative texts with ground-truth entity labels.
"""
from typing import NamedTuple
import spacy

class LabeledEntity(NamedTuple):
    text: str
    kind: str  # Person, Organization, Location, Phone, Account, Vehicle, Money, Date

class EvalSample(NamedTuple):
    id: str
    text: str
    expected: list[LabeledEntity]

EVAL_DATASET: list[EvalSample] = [
    EvalSample(
        id="sample_01_briefing",
        text=(
            "Inspector questioned Raghav Malhotra regarding the suspicious account DEMO-A888. "
            "Eyewitness spotted Zoya Qureshi near the warehouse in Bengaluru on 15 August 2026. "
            "Financing was routed through Horizon Freight Solutions via phone +919876543210."
        ),
        expected=[
            LabeledEntity("Raghav Malhotra", "Person"),
            LabeledEntity("DEMO-A888", "Account"),
            LabeledEntity("Zoya Qureshi", "Person"),
            LabeledEntity("Bengaluru", "Location"),
            LabeledEntity("15 August 2026", "Date"),
            LabeledEntity("Horizon Freight Solutions", "Organization"),
            LabeledEntity("+919876543210", "Phone"),
        ]
    ),
    EvalSample(
        id="sample_02_surveillance",
        text=(
            "Informant confirmed Devansh Batra left the premises early morning in vehicle DEMO-VH-88. "
            "Later, Kabir Sethi met Meera Iyer at an office in Hyderabad. "
            "The shipment belonged to Meridian Exports Pvt Ltd and was valued at INR 250000.00."
        ),
        expected=[
            LabeledEntity("Devansh Batra", "Person"),
            LabeledEntity("DEMO-VH-88", "Vehicle"),
            LabeledEntity("Kabir Sethi", "Person"),
            LabeledEntity("Meera Iyer", "Person"),
            LabeledEntity("Hyderabad", "Location"),
            LabeledEntity("Meridian Exports Pvt Ltd", "Organization"),
            LabeledEntity("INR 250000.00", "Money"),
        ]
    ),
    EvalSample(
        id="sample_03_dispatch",
        text=(
            "Vikram Singh met Arjun Mehta near Jaipur Railway Station before contacting Apex Logistics. "
            "Suspect then coordinated with Kavya Rao in New Delhi regarding vehicle DEMO-VH-02. "
            "Amount reported was INR 150000.00 on 14 August 2026."
        ),
        expected=[
            LabeledEntity("Vikram Singh", "Person"),
            LabeledEntity("Arjun Mehta", "Person"),
            LabeledEntity("Jaipur Railway Station", "Location"),
            LabeledEntity("Apex Logistics", "Organization"),
            LabeledEntity("Kavya Rao", "Person"),
            LabeledEntity("New Delhi", "Location"),
            LabeledEntity("DEMO-VH-02", "Vehicle"),
            LabeledEntity("INR 150000.00", "Money"),
            LabeledEntity("14 August 2026", "Date"),
        ]
    ),
    EvalSample(
        id="sample_04_intercept",
        text=(
            "Case VEIL-DEMO-001. Operative tracked courier between Chandigarh and Kochi. "
            "Northstar Capital Services received wire transfer of INR 50000.00 to account DEMO-A101. "
            "Target used unlisted line +910000000303 to reach Priya Nair."
        ),
        expected=[
            LabeledEntity("VEIL-DEMO-001", "CaseIdentifier"),
            LabeledEntity("Chandigarh", "Location"),
            LabeledEntity("Kochi", "Location"),
            LabeledEntity("Northstar Capital Services", "Organization"),
            LabeledEntity("INR 50000.00", "Money"),
            LabeledEntity("DEMO-A101", "Account"),
            LabeledEntity("+910000000303", "Phone"),
            LabeledEntity("Priya Nair", "Person"),
        ]
    )
]

def run_evaluation(extractor_fn, name: str) -> dict:
    """Run extraction across the dataset and compute exact metrics."""
    total_expected = 0
    total_extracted = 0
    true_positives = 0
    missed: list[tuple[str, str, str]] = []  # (sample_id, text, kind)
    incorrect: list[tuple[str, str, str, str]] = []  # (sample_id, text, pred_kind, exp_kind_or_FP)

    for sample in EVAL_DATASET:
        preds = extractor_fn(sample.text)  # returns list of (text, kind)
        pred_dict = {p[0]: p[1] for p in preds}
        exp_dict = {e.text: e.kind for e in sample.expected}

        total_expected += len(sample.expected)
        total_extracted += len(preds)

        for exp_text, exp_kind in exp_dict.items():
            if exp_text in pred_dict:
                if pred_dict[exp_text] == exp_kind:
                    true_positives += 1
                else:
                    incorrect.append((sample.id, exp_text, pred_dict[exp_text], f"Expected {exp_kind}"))
            else:
                # Check case-insensitive / normalized match
                matched = False
                for p_text, p_kind in pred_dict.items():
                    if p_text.casefold() == exp_text.casefold():
                        matched = True
                        if p_kind == exp_kind:
                            true_positives += 1
                        else:
                            incorrect.append((sample.id, exp_text, p_kind, f"Expected {exp_kind}"))
                        break
                if not matched:
                    missed.append((sample.id, exp_text, exp_kind))

        # Check for false positives (extracted entities not in ground truth)
        exp_texts = {e.text.casefold() for e in sample.expected}
        for p_text, p_kind in preds:
            if p_text.casefold() not in exp_texts:
                incorrect.append((sample.id, p_text, p_kind, "False Positive (Unannotated / Erroneous)"))

    precision = true_positives / total_extracted if total_extracted > 0 else 0.0
    recall = true_positives / total_expected if total_expected > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "name": name,
        "total_expected": total_expected,
        "total_extracted": total_extracted,
        "true_positives": true_positives,
        "missed_count": len(missed),
        "missed": missed,
        "incorrect_count": len(incorrect),
        "incorrect": incorrect,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
    }

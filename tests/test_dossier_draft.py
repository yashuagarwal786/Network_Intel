import re
from pathlib import Path

def test_no_hardcoded_riverglass_or_accusatory_text_in_modal():
    modal_file = Path("frontend/src/components/CourtDossierModal.tsx")
    assert modal_file.exists(), "CourtDossierModal.tsx must exist"
    content = modal_file.read_text(encoding="utf-8")

    # Forbidden accusatory / guilt / operative terms
    forbidden_terms = [
        "ground operative",
        "target entity",
        "mastermind",
        "culprit",
        "criminal network",
        "probability of guilt",
        "established coordinated association",
        "Primary Key Intermediary",
        "STATUTORY CERTIFICATE",
        "Section 65B",
        "Section 63",
        "Bharatiya Sakshya",
        "CERTIFIED RECORD [SEAL]",
        "untampered",
    ]
    for term in forbidden_terms:
        assert term.lower() not in content.lower(), f"Found forbidden term '{term}' in CourtDossierModal.tsx"

    # Forbidden hard-coded identities / accounts
    forbidden_hardcoded = [
        "Rahul Kumar Sharma",
        "Vikram Singh",
        "Amit Verma",
        "DEMO-A17",
        "DEMO-A31",
        "+910000000204",
        "1,95,000",
    ]
    for identity in forbidden_hardcoded:
        assert identity not in content, f"Found hard-coded identity/data '{identity}' in CourtDossierModal.tsx"

    # Must contain neutral required phrasing
    assert "Investigation Analysis Draft" in content
    assert "requires human verification" in content.lower() or "human verification" in content.lower()
    assert "Not established from available records" in content
    assert 'aria-label="Close' in content

def test_network_workspace_dossier_button_label():
    ws_file = Path("frontend/src/components/NetworkWorkspace.tsx")
    content = ws_file.read_text(encoding="utf-8")
    assert "Sec 65B" not in content, "NetworkWorkspace.tsx must not reference Sec 65B"
    assert "Analysis Draft" in content or "Investigation Analysis Draft" in content

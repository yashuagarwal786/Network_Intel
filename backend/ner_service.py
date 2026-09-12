"""spaCy-based Named Entity Recognition service for free-text report ingestion.

This module loads the spaCy model once per process (singleton pattern).
It maps spaCy entity labels to the internal entity type vocabulary and
exposes a clean extraction function with structured provenance.

To use a different model, change DEFAULT_MODEL or pass model_name to extract().
The model must be downloaded separately:
    python -m spacy download en_core_web_sm
For a multilingual or stronger model:
    python -m spacy download xx_ent_wiki_sm   # multilingual
    python -m spacy download en_core_web_lg   # larger English model
"""
import logging
from typing import NamedTuple

logger = logging.getLogger(__name__)

# Default model. Swap this string to upgrade to a stronger or multilingual model.
DEFAULT_MODEL = 'en_core_web_sm'

import re

# Map spaCy entity labels to internal entity type vocabulary.
# Only labels listed here will be extracted; all others are silently skipped.
SPACY_LABEL_TO_KIND: dict[str, str] = {
    'PERSON': 'Person',
    'ORG':    'Organization',
    'GPE':    'Location',   # Geo-Political Entity (countries, cities, states)
    'LOC':    'Location',   # Non-GPE locations (mountain ranges, bodies of water)
    'FAC':    'Location',   # Facilities (airports, highways, bridges)
}

# Structured identifiers that belong strictly to deterministic regex parsing.
# Used for pre-masking spans so statistical NER never consumes sub-tokens (e.g. 'DEMO').
STRUCTURED_SPAN_PATTERNS = [
    re.compile(r'\+[0-9]{10,15}(?![0-9])'),
    re.compile(r'DEMO-A[0-9]{3,8}'),
    re.compile(r'DEMO-VH-[0-9]{2,4}'),
    re.compile(r'INR\s+[0-9]+(?:\.[0-9]{2})?'),
    re.compile(r'\d{4}-\d{2}-\d{2}(?:T[0-9:+-]+)?|\d{1,2}\s+August(?: 2026)?'),
    re.compile(r'VEIL-DEMO-[0-9]{3}'),
    re.compile(r'TX-[A-Z0-9-]+'),
    re.compile(r'CALL-[A-Z0-9-]+'),
]

# Generic role/category nouns commonly found in investigative prose.
# These must not be extracted as named entities (neither Person nor Organization).
INVESTIGATION_ROLES = {
    'suspect', 'operative', 'informant', 'handler', 'target', 'witness',
    'subject', 'caller', 'receiver', 'agent', 'courier', 'eyewitness',
    'depot', 'premises', 'officer', 'constable', 'inspector', 'individual'
}

# Corporate legal/trade suffixes for reliable organization disambiguation.
ORG_SUFFIXES = (
    'logistics', 'trading', 'services', 'exports', 'solutions',
    'enterprises', 'capital', 'pvt ltd', 'ltd', 'inc', 'corp', 'llp',
    'industries', 'technologies', 'holdings'
)

# Major geographical hubs to resolve GPE/ORG confusion on regional Indian entities.
INDIAN_CITIES = {
    'bengaluru', 'bangalore', 'hyderabad', 'mumbai', 'delhi', 'new delhi',
    'chandigarh', 'jaipur', 'kochi', 'cochin', 'kolkata', 'calcutta',
    'chennai', 'madras', 'pune', 'ahmedabad', 'surat', 'lucknow',
    'patna', 'indore', 'bhopal', 'nagpur', 'vadodara', 'agra',
    'nashik', 'varanasi', 'amritsar', 'guwahati', 'kanpur'
}


class ExtractedEntity(NamedTuple):
    """A single NER-extracted entity with provenance metadata."""
    raw_text:   str   # exact span text from the document
    normalized: str   # whitespace-collapsed, stripped
    kind:       str   # internal kind: Person / Organization / Location
    start_char: int   # character offset (start, inclusive) within the input text
    end_char:   int   # character offset (end, exclusive) within the input text
    spacy_label: str  # original spaCy label (e.g. 'PERSON', 'GPE')
    extraction_method: str  # spacy-ner or spacy-entity-ruler


# ---------------------------------------------------------------------------
# Module-level singleton state
# ---------------------------------------------------------------------------
_nlp = None          # loaded spaCy Language object, or None
_loaded_model: str | None = None   # model name that was successfully loaded
_load_error:   str | None = None   # error message from the last failed load attempt

RULER_PATTERNS = [
    {'label':'ORG','id':'generic-ruler-v1','pattern':[{'IS_TITLE':True,'OP':'+'},{'LOWER':{'IN':list(ORG_SUFFIXES)}}]},
    {'label':'FAC','id':'generic-ruler-v1','pattern':[{'IS_TITLE':True,'OP':'+'},{'LOWER':{'IN':['depot','yard','market','station','junction','warehouse','terminal']}}]},
    {'label':'PERSON','id':'generic-ruler-v1','pattern':[{'IS_TITLE':True},{'TEXT':{'REGEX':'^[A-Z]\\.?$'}}]},
]

def _add_ruler(nlp):
    if 'entity_ruler' in nlp.pipe_names:return nlp
    after='ner' if 'ner' in nlp.pipe_names else None
    ruler=nlp.add_pipe('entity_ruler',after=after,config={'overwrite_ents':False}) if after else nlp.add_pipe('entity_ruler',config={'overwrite_ents':False})
    ruler.add_patterns(RULER_PATTERNS)
    return nlp

def _activate_rule_fallback(error: str | None=None) -> bool:
    global _nlp,_loaded_model,_load_error
    try:
        import spacy
        nlp=spacy.blank('en')
        ruler=nlp.add_pipe('entity_ruler')
        ruler.add_patterns([
            *RULER_PATTERNS,
            {'label':'PERSON','id':'generic-ruler-v1','pattern':[{'IS_TITLE':True},{'IS_TITLE':True}]},
        ])
        _nlp=nlp;_loaded_model='entity-ruler-v1';_load_error=error
        return True
    except Exception:return False


def _ensure_loaded(model_name: str = DEFAULT_MODEL) -> bool:
    """Load the spaCy model if not already loaded.  Returns True on success."""
    global _nlp, _loaded_model, _load_error

    if _nlp is not None and _loaded_model in {model_name,'entity-ruler-v1'}:
        return True
    # If we already failed to load this model, don't retry every request.
    if _load_error is not None and _loaded_model == model_name:
        return _activate_rule_fallback(_load_error)

    try:
        import spacy  # noqa: PLC0415 – intentional lazy import
        _nlp = _add_ruler(spacy.load(model_name))
        _loaded_model = model_name
        _load_error = None
        logger.info('spaCy model "%s" loaded successfully.', model_name)
        return True
    except Exception as exc:  # noqa: BLE001
        _nlp = None;_load_error = str(exc);_loaded_model = model_name
        logger.warning(
            'spaCy model "%s" could not be loaded: %s  '
            '→ NER will fall back to whitelist extraction.',
            model_name, exc,
        )
        return _activate_rule_fallback(str(exc))


def reset_for_testing(
    mock_nlp=None,
    model_name: str | None = None,
    error: str | None = None,
) -> None:
    """Replace the singleton state for unit tests.  Not for production use."""
    global _nlp, _loaded_model, _load_error
    _nlp = mock_nlp
    _loaded_model = model_name or (DEFAULT_MODEL if mock_nlp is not None else None)
    _load_error = error


def is_available(model_name: str = DEFAULT_MODEL) -> bool:
    """Return True if the NER model is loaded and ready."""
    return _ensure_loaded(model_name)


def current_extractor_version(model_name: str = DEFAULT_MODEL) -> str:
    """Human-readable extractor identifier for provenance records."""
    if _nlp is not None and _loaded_model == 'entity-ruler-v1':
        return 'spacy-entity-ruler-v1'
    if _nlp is not None and _loaded_model == model_name:
        return f'spacy-{model_name}'
    return f'spacy-{model_name}-unavailable'


def extract(
    text: str,
    model_name: str = DEFAULT_MODEL,
) -> tuple[list[ExtractedEntity], str | None]:
    """Run NER on *text* and return (entities, error_message).

    On success:   error_message is None; entities is a deduplicated list.
    On failure:   entities is []; error_message describes why NER was skipped.

    Deduplication key: (casefold(normalized), kind).  When the same surface
    form appears more than once, only the first occurrence is kept so that
    downstream mention-ID hashing stays stable.
    """
    if not _ensure_loaded(model_name):
        return [], _load_error or f'Model "{model_name}" could not be loaded.'

    try:
        # Step 1: Pre-calculate structured identifier spans so NER never captures sub-tokens
        structured_spans: list[tuple[int, int]] = []
        for pattern in STRUCTURED_SPAN_PATTERNS:
            for match in pattern.finditer(text):
                structured_spans.append((match.start(), match.end()))

        doc = _nlp(text)  # type: ignore[misc]
        seen: set[tuple[str, str]] = set()
        results: list[ExtractedEntity] = []

        for ent in doc.ents:
            # Drop any entity that overlaps with structured identifier spans (e.g. 'DEMO' from 'DEMO-A888')
            if any(not (ent.end_char <= s_start or ent.start_char >= s_end) for s_start, s_end in structured_spans):
                continue

            raw_stripped = ent.text.strip(" .,:;'-_\"()")
            if not raw_stripped or len(raw_stripped) < 2:
                continue

            # Strip possessives: "Logistics'" -> "Logistics", "Sharma's" -> "Sharma"
            if raw_stripped.endswith("'s") or raw_stripped.endswith("’s"):
                raw_stripped = raw_stripped[:-2]
            elif raw_stripped.endswith("'") or raw_stripped.endswith("’"):
                raw_stripped = raw_stripped[:-1]

            normalized = ' '.join(raw_stripped.split())
            if not normalized or normalized.casefold() in INVESTIGATION_ROLES:
                continue

            kind = SPACY_LABEL_TO_KIND.get(ent.label_)
            if kind is None:
                continue

            # Contextual Harmonization Rules:
            # - Corporate suffixes (Logistics, Exports, Pvt Ltd) -> Organization
            if any(normalized.casefold().endswith(sfx) for sfx in ORG_SUFFIXES):
                kind = 'Organization'
            # - Major Indian cities -> Location
            elif normalized.casefold() in INDIAN_CITIES:
                kind = 'Location'

            dedup_key = (normalized.casefold(), kind)
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            # Compute exact character boundaries of the cleaned entity span
            offset_in_ent = ent.text.find(raw_stripped)
            start_char = ent.start_char + (offset_in_ent if offset_in_ent != -1 else 0)
            end_char = start_char + len(raw_stripped)

            results.append(ExtractedEntity(
                raw_text=raw_stripped,
                normalized=normalized,
                kind=kind,
                start_char=start_char,
                end_char=end_char,
                spacy_label=ent.label_,
                extraction_method='spacy-entity-ruler' if ent.ent_id_=='generic-ruler-v1' else 'spacy-ner',
            ))
        return results, None

    except Exception as exc:  # noqa: BLE001
        logger.error('NER extraction failed for text of length %d: %s', len(text), exc)
        return [], f'NER runtime error: {exc}'

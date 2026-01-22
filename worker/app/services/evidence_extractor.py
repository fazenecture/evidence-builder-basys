import re
from typing import Dict, List


class EvidenceExtractor:
    def extract(self, note_text: str) -> Dict:
        lines = note_text.split("\n")

        evidence = {
            "diagnosis": None,
            "conservative_therapy": None,
            "imaging_present": None,
            "functional_limitation": None,
            "missing_fields": [],
        }

        # Diagnosis
        diagnosis_sources = self._match_lines(
            lines, r"osteoarthritis"
        )

        if diagnosis_sources:
            evidence["diagnosis"] = {
                "value": "osteoarthritis",
                "confidence": 0.9,
                "source": diagnosis_sources,
            }
        else:
            evidence["missing_fields"].append("diagnosis")

        # Conservative Therapy
        therapy_sources = self._match_lines(
            lines, r"physiotherapy|physical therapy|NSAID|ibuprofen|naproxen"
        )

        therapy_types = []
        for src in therapy_sources:
            text = src["text_snippet"].lower()
            if "therapy" in text:
                therapy_types.append("physical_therapy")
            if "nsaid" in text or "ibuprofen" in text or "naproxen" in text:
                therapy_types.append("NSAIDs")

        if therapy_sources:
            evidence["conservative_therapy"] = {
                "attempted": True,
                "types": list(set(therapy_types)),
                "confidence": 0.85,
                "source": therapy_sources,
            }
        else:
            evidence["missing_fields"].append("conservative_therapy")

        # Imaging
        imaging_sources = self._match_lines(
            lines, r"x-ray|MRI|CT scan"
        )

        if imaging_sources:
            evidence["imaging_present"] = {
                "value": True,
                "confidence": 0.9,
                "source": imaging_sources,
            }
        else:
            evidence["missing_fields"].append("imaging")

        # Functional Limitation
        limitation_sources = self._match_lines(
            lines, r"difficulty walking|pain with daily activities|ADL"
        )

        if limitation_sources:
            evidence["functional_limitation"] = {
                "value": True,
                "confidence": 0.8,
                "source": limitation_sources,
            }
        else:
            evidence["missing_fields"].append("functional_limitation")

        return self._validate(evidence)

    # Helpers
    def _match_lines(self, lines: List[str], pattern: str) -> List[Dict]:
        matches = []
        for idx, line in enumerate(lines):
            if re.search(pattern, line, re.IGNORECASE):
                matches.append({
                    "line_number": idx + 1,
                    "text_snippet": line.strip(),
                })
        return matches

    def _validate(self, evidence: Dict) -> Dict:
        if "missing_fields" not in evidence:
            raise Exception("Invalid evidence structure")
        return evidence

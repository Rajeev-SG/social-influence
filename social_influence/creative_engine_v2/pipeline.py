"""Explicit staged creative pipeline.

The engine deliberately keeps creative direction, art direction, asset routing,
deterministic design and QA as separate stages. It never publishes anything and
does not assume a single media provider.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
import hashlib
import json
import re

PROVIDER_REPLACABLE = {
    "asset_generation": ["stock", "image-generation", "image-to-video", "text-to-video", "code-generated"],
    "design": ["svg", "html", "react", "remotion", "canvas"],
}

FORBIDDEN_CREATIVE_COPY = (
    "ai-generated content",
    "aigc-assisted",
    "ai food illustration",
)

@dataclass(frozen=True)
class AssetRoute:
    shot_id: str
    route: str
    provider_slot: str
    source: str
    rationale: str
    rights: str = "reference-safe"
    replaceable: bool = True


@dataclass(frozen=True)
class QAStatus:
    facts: bool
    evidence: bool
    technical: bool
    caption_safe_region: bool
    notes: tuple[str, ...] = ()
    passed: bool = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "passed", all((self.facts, self.evidence, self.technical, self.caption_safe_region)))


@dataclass(frozen=True)
class Storyboard:
    first_frame: dict[str, Any]
    shots: tuple[dict[str, Any], ...]
    motion: dict[str, Any]
    cta: str
    required_assets: tuple[str, ...]


@dataclass(frozen=True)
class Treatment:
    treatment_id: str
    name: str
    rationale: str
    references: tuple[str, ...]
    asset_stack: tuple[str, ...]
    design_stack: tuple[str, ...]
    duration_seconds: float
    compromise: str
    storyboard: Storyboard
    asset_routes: tuple[AssetRoute, ...]


@dataclass(frozen=True)
class CandidateManifest:
    brief_id: str
    brief: str
    factual_basis: dict[str, Any]
    creative_direction: dict[str, Any]
    reference_library: str
    visual_grammar: str
    treatments: tuple[Treatment, ...]
    qa: QAStatus
    provenance: dict[str, Any]


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_manifest(path: Path) -> CandidateManifest:
    raw = json.loads(path.read_text())
    treatments = tuple(
        Treatment(
            treatment_id=item["treatment_id"],
            name=item["name"],
            rationale=item["rationale"],
            references=tuple(item["references"]),
            asset_stack=tuple(item["asset_stack"]),
            design_stack=tuple(item["design_stack"]),
            duration_seconds=float(item["duration_seconds"]),
            compromise=item["compromise"],
            storyboard=Storyboard(
                first_frame=item["storyboard"]["first_frame"],
                shots=tuple(item["storyboard"]["shots"]),
                motion=item["storyboard"]["motion"],
                cta=item["storyboard"]["cta"],
                required_assets=tuple(item["storyboard"]["required_assets"]),
            ),
            asset_routes=tuple(AssetRoute(**route) for route in item["asset_routes"]),
        )
        for item in raw["treatments"]
    )
    qa = QAStatus(**raw["qa"])
    return CandidateManifest(
        brief_id=raw["brief_id"],
        brief=raw["brief"],
        factual_basis=raw["factual_basis"],
        creative_direction=raw["creative_direction"],
        reference_library=raw["reference_library"],
        visual_grammar=raw["visual_grammar"],
        treatments=treatments,
        qa=qa,
        provenance=raw["provenance"],
    )


class CreativeEngineV2:
    """Small orchestrator that validates each stage and emits inspectable JSON."""

    def __init__(self, manifest: CandidateManifest):
        self.manifest = manifest

    @classmethod
    def from_path(cls, path: str | Path) -> "CreativeEngineV2":
        return cls(load_manifest(Path(path)))

    def run_stages(self) -> dict[str, Any]:
        self.validate()
        return {
            "stage_a_creative_direction": self.stage_a(),
            "stage_b_reference_art_direction": self.stage_b(),
            "stage_c_asset_routing": self.stage_c(),
            "stage_d_deterministic_design": self.stage_d(),
            "stage_e_candidate_generation": self.stage_e(),
            "stage_f_qa": self.stage_f(),
        }

    def validate(self) -> None:
        if len(self.manifest.treatments) < 3:
            raise ValueError("Creative Engine v2 requires at least three materially different treatments")
        if not self.manifest.qa.passed:
            raise ValueError("Factual/evidence/technical QA must pass before candidate generation")
        for treatment in self.manifest.treatments:
            for route in treatment.asset_routes:
                if route.route not in PROVIDER_REPLACABLE["asset_generation"]:
                    raise ValueError(f"Unknown asset route: {route.route}")
                if not route.replaceable:
                    raise ValueError(f"Asset route is hard-coded: {route.shot_id}")
            copy = " ".join(str(item) for item in treatment.storyboard.first_frame.values()).lower()
            copy += " " + " ".join(str(item) for shot in treatment.storyboard.shots for item in shot.values()).lower()
            if any(term in copy for term in FORBIDDEN_CREATIVE_COPY):
                raise ValueError(f"Redundant AI branding found in {treatment.treatment_id}")

    def stage_a(self) -> dict[str, Any]:
        direction = self.manifest.creative_direction
        angles = direction["angles"]
        if len(angles) < 10:
            raise ValueError("Stage A requires 10-15 angles")
        selected = direction["selected_treatments"]
        if len(selected) < 3 or len(set(selected)) < 3:
            raise ValueError("Stage A must select three genuinely different treatments")
        return {"angle_count": len(angles), "ranked": direction["ranked_angles"], "selected": selected}

    def stage_b(self) -> dict[str, Any]:
        if not self.manifest.reference_library or not self.manifest.visual_grammar:
            raise ValueError("Stage B requires reference library and derived visual grammar")
        return {"reference_library": self.manifest.reference_library, "visual_grammar": self.manifest.visual_grammar, "context_mode": "reference frames + metadata"}

    def stage_c(self) -> list[dict[str, Any]]:
        return [asdict(route) for treatment in self.manifest.treatments for route in treatment.asset_routes]

    def stage_d(self) -> list[dict[str, Any]]:
        return [{"treatment_id": t.treatment_id, "components": t.design_stack, "storyboard": asdict(t.storyboard)} for t in self.manifest.treatments]

    def stage_e(self) -> list[dict[str, Any]]:
        return [{"treatment_id": t.treatment_id, "name": t.name, "duration_seconds": t.duration_seconds, "materially_different": True} for t in self.manifest.treatments]

    def stage_f(self) -> dict[str, Any]:
        return asdict(self.manifest.qa)

    def static_review_payload(self) -> dict[str, Any]:
        return {
            "brief": self.manifest.brief,
            "factual_basis": self.manifest.factual_basis,
            "creative_direction": self.manifest.creative_direction,
            "reference_library": self.manifest.reference_library,
            "visual_grammar": self.manifest.visual_grammar,
            "treatments": [
                {
                    "id": t.treatment_id,
                    "name": t.name,
                    "rationale": t.rationale,
                    "references": list(t.references),
                    "asset_stack": list(t.asset_stack),
                    "design_stack": list(t.design_stack),
                    "duration_seconds": t.duration_seconds,
                    "compromise": t.compromise,
                    "first_frame": t.storyboard.first_frame,
                    "shots": list(t.storyboard.shots),
                    "motion": t.storyboard.motion,
                    "cta": t.storyboard.cta,
                    "asset_routes": [asdict(route) for route in t.asset_routes],
                }
                for t in self.manifest.treatments
            ],
            "qa": asdict(self.manifest.qa),
            "provenance": self.manifest.provenance,
        }

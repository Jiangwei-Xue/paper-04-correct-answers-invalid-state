"""Native serialization fixtures used by the representation gate."""

from __future__ import annotations


def serialize(rep: str, positive: list[str], negative: list[str], ambiguous: list[str] | None = None) -> str:
    ambiguous = ambiguous or []
    if rep == "rolling_summary":
        claims = [f"{item} is active" for item in positive]
        claims += [f"{item} is revoked" for item in negative]
        claims += [f"{item} has conflicting status" for item in ambiguous]
        return "SUMMARY=" + "; ".join(claims)
    if rep == "visible_carry":
        note = [f"{item} is revoked" for item in negative]
        note += [f"{item} has conflicting status" for item in ambiguous]
        keep = positive + ambiguous
        return "VISIBLE_KEEP=" + ",".join(keep) + ("\nNOTE=" + "; ".join(note) if note else "")
    if rep == "ssr":
        out = positive + ambiguous
        no = negative + ambiguous
        return "OUT=" + ",".join(out) + ("\nNO=" + ",".join(no) if no else "")
    raise ValueError(rep)

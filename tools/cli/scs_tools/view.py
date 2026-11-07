"""Review package: a readable, self-contained view of a Domain or Project bundle for the people
who review and certify it (plan/0.8/bundle-review-process.md, phase 1).

The package is built mechanically from the bundle tree and the compiler's own output, so every
rule appears verbatim with its id and the exact line the AI receives. No AI writes any part of
it, and it holds no volatile content: the same source always produces the same bytes.

`build_view` returns the view as data (the shape a later RFC defines); `render_html` turns it
into one HTML file with no external assets.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml
from scs_validator.owners import needs_owner, owner_map

from scs_tools.compiler import compile_tree

VIEW_FORMAT = "0.1"
ITEM_KINDS = (("prohibitions", "prohibition"), ("directives", "directive"), ("facts", "fact"))
COMPILED_CONTENT = {"prohibitions", "directives", "facts", "summary"}
ITEM_FIELDS = {
    "prohibition": ("id", "kind", "subject", "instead", "cites", "derived_from"),
    "directive": ("id", "directive", "cites", "derived_from"),
    "fact": ("id", "fact", "cites", "derived_from"),
}


@dataclass
class Source:
    """One bundle tree to show, with what is known about its release."""

    tree: Any  # scs_validator.resolver.BundleTree
    workspace: Optional[Path] = None  # where intake.yaml lives
    manifest: Optional[Dict[str, Any]] = None  # the version manifest, when verified
    tag: Optional[str] = None


@dataclass
class ViewResult:
    view: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def _text(value: Any) -> str:
    return " ".join(str(value or "").split())


def _short(prefixed_id: str) -> str:
    return prefixed_id.rsplit(":", 1)[-1]


def _intake(workspace: Optional[Path]) -> Dict[str, Any]:
    """The workspace's intake record; for a release, the one committed with it."""
    if workspace is None or not (workspace / "intake.yaml").is_file():
        return {}
    try:
        data = yaml.safe_load((workspace / "intake.yaml").read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return {}
    return data if isinstance(data, dict) else {}


def _sources_by_id(data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Source documents and intake answers by id, from the intake record."""
    found: Dict[str, Dict[str, Any]] = {}
    for doc in data.get("source_documents") or []:
        if isinstance(doc, dict) and doc.get("id"):
            found[f"source:{doc['id']}"] = doc
    for answer in data.get("answers") or []:
        if isinstance(answer, dict) and answer.get("id"):
            found[f"intake:{answer['id']}"] = answer
    return found


def _derived_from(entries: Any, known: Dict[str, Dict[str, Any]]) -> List[str]:
    lines = []
    for entry in entries or []:
        if not isinstance(entry, dict):
            continue
        if entry.get("source"):
            key = f"source:{entry['source']}"
            doc = known.get(key, {})
            label = _text(doc.get("title")) or str(entry["source"])
            if doc.get("revision"):
                label += f" (rev {_text(doc['revision'])})"
            line = f"Source document: {label}"
        else:
            key = f"intake:{entry.get('intake')}"
            answer = known.get(key, {})
            question = _text(answer.get("question"))
            line = f"Intake answer {entry.get('intake')}" + (f": {question}" if question else "")
        if entry.get("locator"):
            line += f", {_text(entry['locator'])}"
        lines.append(line)
    return lines


def _release(source: Source, artifact: Dict[str, Any]) -> Dict[str, Any]:
    root = source.tree.root
    provenance = root.data.get("provenance") or {}
    release: Dict[str, Any] = {
        "version": artifact["version"],
        "draft": str(artifact["version"]).startswith("DRAFT"),
        "source_digest": artifact.get("source_digest"),
        "verified": bool(artifact.get("source_digest")),
    }
    manifest = source.manifest or {}
    approval = manifest.get("approval") or {}
    approved_by = approval.get("approved_by") or provenance.get("version_approved_by")
    approved_at = approval.get("approved_at") or provenance.get("version_approved_at")
    if approved_by:
        release["approved_by"] = _text(approved_by)
    if approved_at:
        release["approved_at"] = _text(approved_at)
    if approval.get("approval_notes"):
        release["approval_notes"] = _text(approval["approval_notes"])
    if manifest.get("release_date"):
        release["release_date"] = _text(manifest["release_date"])
    if source.tag:
        release["tag"] = source.tag
    return release


def _item(
    kind: str,
    entry: Dict[str, Any],
    compiled_id: str,
    compiled: Dict[str, str],
    known: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    item: Dict[str, Any] = {
        "kind": kind,
        "id": str(entry.get("id", "")),
        "compiled_id": compiled_id,
        "compiled": compiled.get(compiled_id),
    }
    if kind == "prohibition":
        item["subject"] = _text(entry.get("subject"))
        item["prohibition_kind"] = _text(entry.get("kind"))
        if entry.get("instead"):
            item["instead"] = _text(entry["instead"])
    else:
        item["text"] = _text(entry.get(kind))
    if entry.get("cites"):
        item["cites"] = [str(c) for c in entry["cites"]]
    derived = _derived_from(entry.get("derived_from"), known)
    if derived:
        item["derived_from"] = derived
    notes = {k: v for k, v in entry.items() if k not in ITEM_FIELDS[kind]}
    if notes:
        item["notes"] = notes
    return item


def _scd(scd: Any, bundle: str, compiled: Dict[str, str], known: Dict[str, Any]) -> Dict:
    data = scd.data
    content = data.get("content") if isinstance(data.get("content"), dict) else {}
    view: Dict[str, Any] = {
        "ref": scd.ref,
        "title": _text(data.get("title")) or _short(scd.ref),
        "version": _text(data.get("version")),
        "description": _text(data.get("description")),
        "summary": _text(content.get("summary")),
        "items": [],
    }
    for key, kind in ITEM_KINDS:
        for entry in content.get(key) or []:
            if isinstance(entry, dict):
                compiled_id = f"{bundle}/{_short(scd.ref)}/{entry.get('id', '')}"
                view["items"].append(_item(kind, entry, compiled_id, compiled, known))
    if data.get("cites"):
        view["cites"] = [str(c) for c in data["cites"]]
    relationships = [
        {"type": _text(r.get("type")), "target": _text(r.get("target"))}
        for r in data.get("relationships") or []
        if isinstance(r, dict)
    ]
    if relationships:
        view["relationships"] = relationships
    other = {k: v for k, v in content.items() if k not in COMPILED_CONTENT}
    if other:
        view["other_content"] = other
    provenance = data.get("provenance")
    if isinstance(provenance, dict) and provenance:
        view["provenance"] = {k: _text(v) for k, v in provenance.items()}
    return view


def _counts(items: List[Dict[str, Any]]) -> Dict[str, int]:
    return {kind: sum(1 for i in items if i["kind"] == kind) for _, kind in ITEM_KINDS}


def _owner(bundle: Dict[str, Any], holders: Dict[str, Dict[str, Any]]) -> Optional[Dict]:
    """The section's owner (D-92): its role and who holds it. None when the bundle holds no
    section of its own (the meta bundle); `role` or `person` None when not set."""
    if not needs_owner(bundle):
        return None
    role = _text(bundle.get("owner")) or None
    holder = holders.get(role, {}) if role else {}
    return {
        "role": role,
        "person": _text(holder.get("person")) or None,
        "title": _text(holder.get("title")) or None,
    }


def _layer(source: Source, role: str, include_cites: bool, allow_draft: bool) -> ViewResult:
    result = ViewResult()
    compiled = compile_tree(source.tree, allow_draft=allow_draft, include_cites=include_cites)
    result.warnings.extend(compiled.unreadable + compiled.warnings)
    if compiled.errors or compiled.artifact is None:
        result.errors.extend(compiled.errors)
        return result
    artifact = compiled.artifact
    lines = {r["id"]: r["rule"] for r in artifact["rules"]}
    lines.update({f["id"]: f["fact"] for f in artifact.get("facts") or []})

    tree = source.tree
    root = tree.root
    name = _short(root.id)
    intake = _intake(source.workspace)
    known = _sources_by_id(intake)
    holders = owner_map(intake)
    groups = []
    meta = []
    for bundle in tree.bundles:
        scds = [_scd(s, name, lines, known) for s in tree.scds if s.bundle_id == bundle.id]
        if bundle.type == "meta":
            # Meta SCDs are vocabulary; show only the ones that give the AI something.
            meta.append(f"{bundle.id}:{bundle.version}")
            scds = [s for s in scds if s["items"]]
        if not scds:
            continue
        items = [i for s in scds for i in s["items"]]
        groups.append(
            {
                "id": bundle.id,
                "type": bundle.type,
                "version": _text(bundle.version),
                "title": _text(bundle.data.get("title")) or _short(bundle.id),
                "description": _text(bundle.data.get("description")),
                "owner": _owner(bundle.data, holders),
                "counts": _counts(items),
                "scds": scds,
            }
        )
    items = [i for g in groups for s in g["scds"] for i in s["items"]]
    result.view = {
        "role": role,
        "id": root.id,
        "type": root.type,
        "title": _text(root.data.get("title")) or name,
        "description": _text(root.data.get("description")),
        "release": _release(source, artifact),
        "meta": meta,
        "identity_rule": lines.get(f"{name}/identity"),
        "counts": {
            **_counts(items),
            "concepts": len(groups),
            "scds": len([s for g in groups for s in g["scds"]]),
        },
        "groups": groups,
    }
    return result


def _summary_owner_line(total: int, unheld: int) -> str:
    if total == 1:
        if unheld:
            return "The one section has no one accountable for it."
        return "The one section has an accountable owner."
    if not unheld:
        return f"All {total} sections have an accountable owner."
    if unheld == 1:
        return f"1 of {total} sections has no one accountable for it."
    return f"{unheld} of {total} sections have no one accountable for them."


def _summary(layers: List[Dict[str, Any]]) -> List[str]:
    """The overview's plain-language summary, built from counts only."""

    def described(layer: Dict[str, Any]) -> str:
        c = layer["counts"]
        parts = [
            f"{c['prohibition']} prohibition{'s' if c['prohibition'] != 1 else ''}",
            f"{c['directive']} rule{'s' if c['directive'] != 1 else ''}",
            f"{c['fact']} fact{'s' if c['fact'] != 1 else ''}",
        ]
        return (
            f"{', '.join(parts)} in {c['scds']} document{'s' if c['scds'] != 1 else ''} "
            f"across {c['concepts']} concept{'s' if c['concepts'] != 1 else ''}"
        )

    root = layers[-1]
    kind = root["type"].capitalize()
    lines = [
        f"{kind} bundle {root['id']} version {root['release']['version']} gives the AI "
        f"{described(root)}."
    ]
    if len(layers) > 1:
        domain = layers[0]
        lines.append(
            f"It runs together with Domain bundle {domain['id']} version "
            f"{domain['release']['version']}, which applies to all work and adds "
            f"{described(domain)}. Both are shown here; the Domain's are marked as inherited."
        )
    elif root["type"] == "project":
        lines.append(
            "No released Domain was available, so rules this Project inherits from its Domain "
            "are not shown."
        )
    owned = [g["owner"] for g in root["groups"] if g["owner"] is not None]
    unheld = sum(1 for o in owned if not (o["role"] and o["person"]))
    if owned:
        lines.append(_summary_owner_line(len(owned), unheld))
    lines.append(
        "Prohibitions are absolute. Rules are instructions the AI follows. Facts are "
        "information it is given. Each item below shows its source text and the exact line "
        "the AI receives."
    )
    return lines


def build_view(
    root: Source,
    domain: Optional[Source] = None,
    include_cites: bool = True,
    allow_draft: bool = False,
) -> ViewResult:
    result = ViewResult()
    layers = []
    for source, role in ([(domain, "inherited")] if domain else []) + [(root, "root")]:
        layer = _layer(source, role, include_cites, allow_draft)
        label = "Domain" if role == "inherited" else source.tree.root.id
        result.warnings.extend(
            f"{label}: {w}" if role == "inherited" else w for w in layer.warnings
        )
        result.errors.extend(f"{label}: {e}" if role == "inherited" else e for e in layer.errors)
        if layer.view:
            layers.append(layer.view)
    if result.errors:
        return result
    result.view = {"view_format": VIEW_FORMAT, "summary": _summary(layers), "layers": layers}
    return result


# --- HTML ----------------------------------------------------------------------------------

CSS = """
:root{--bg:#fff;--fg:#1d1d1f;--muted:#5f6368;--line:#dadce0;--panel:#f6f7f9;
--accent:#1a5fb4;--no:#a51d2d;--no-bg:#fbeaec;--fact:#26662f;--warn-bg:#fff4ce;--warn:#7a5b00;
--code:#eef1f5}
@media (prefers-color-scheme: dark){:root{--bg:#16181c;--fg:#e8eaed;--muted:#9aa0a6;
--line:#3c4043;--panel:#1f2227;--accent:#8ab4f8;--no:#f28b82;--no-bg:#3a2224;--fact:#81c995;
--warn-bg:#3d3418;--warn:#fdd663;--code:#262a30}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 -apple-system,
"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
main{max-width:920px;margin:0 auto;padding:24px 16px 64px}
h1{font-size:1.6rem;margin:0 0 4px}h2{font-size:1.25rem;margin:40px 0 8px;
padding-bottom:4px;border-bottom:1px solid var(--line)}h3{font-size:1.05rem;margin:28px 0 4px}
a{color:var(--accent)}p{margin:6px 0}
.muted{color:var(--muted)}.small{font-size:.85rem}
code,.id{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.85em}
.id{background:var(--code);padding:1px 5px;border-radius:4px;white-space:nowrap}
.banner{padding:10px 14px;border-radius:6px;margin:12px 0;font-weight:600}
.banner.draft{background:var(--no-bg);color:var(--no)}
.banner.warn{background:var(--warn-bg);color:var(--warn)}
table.release{border-collapse:collapse;margin:12px 0;width:100%}
table.release th{text-align:left;font-weight:600;padding:5px 12px 5px 0;width:180px;
vertical-align:top;color:var(--muted)}
table.release td{padding:5px 0;word-break:break-all}
table.owners{border-collapse:collapse;width:100%;margin:8px 0}
table.owners th,table.owners td{text-align:left;padding:5px 12px 5px 0;
border-bottom:1px solid var(--line);vertical-align:top}
table.owners th{color:var(--muted);font-weight:600}
.ok{color:var(--fact);font-weight:600}.bad{color:var(--no);font-weight:600}
ul.tree{list-style:none;padding-left:0}ul.tree ul{list-style:none;padding-left:20px}
ul.tree li{margin:3px 0}
.tag{display:inline-block;font-size:.75rem;font-weight:600;padding:0 6px;border-radius:10px;
border:1px solid var(--line);color:var(--muted);margin-left:6px}
.tag.inherited{border-color:var(--accent);color:var(--accent)}
section.scd{border:1px solid var(--line);border-radius:8px;padding:4px 16px 12px;
margin:18px 0;break-inside:avoid-page}
.item{border-left:4px solid var(--line);padding:6px 12px;margin:12px 0;background:var(--panel);
border-radius:0 6px 6px 0}
.item.prohibition{border-left-color:var(--no)}.item.directive{border-left-color:var(--accent)}
.item.fact{border-left-color:var(--fact)}
.kind{font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.04em}
.prohibition .kind{color:var(--no)}.directive .kind{color:var(--accent)}
.fact .kind{color:var(--fact)}
.compiled{margin-top:6px;font-size:.9rem}
.compiled q{display:block;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
font-size:.85rem;background:var(--code);padding:6px 8px;border-radius:4px;quotes:none}
dl.meta{display:grid;grid-template-columns:max-content 1fr;gap:2px 12px;margin:8px 0;
font-size:.9rem}dl.meta dt{color:var(--muted)}dl.meta dd{margin:0}
pre{background:var(--code);padding:8px;border-radius:4px;overflow-x:auto;font-size:.8rem;
white-space:pre-wrap}
footer{margin-top:48px;border-top:1px solid var(--line);padding-top:8px}
@media print{body{font-size:11pt}a{color:inherit;text-decoration:none}
section.scd{border-color:#999}}
"""


def _e(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _anchor(role: str, ref: str) -> str:
    return f"{'d' if role == 'inherited' else 'p'}-" + re.sub(r"[^A-Za-z0-9_-]", "-", ref)


def _count_hint(counts: Dict[str, int]) -> str:
    parts = []
    for _, kind in ITEM_KINDS:
        n = counts[kind]
        if n:
            label = "rule" if kind == "directive" else kind
            parts.append(f"{n} {label}{'s' if n != 1 else ''}")
    return ", ".join(parts) or "no compiled items"


def _release_table(layer: Dict[str, Any]) -> str:
    r = layer["release"]
    rows = [
        ("Bundle", f"<span class=id>{_e(layer['id'])}</span> ({_e(layer['type'])})"),
        ("Version", _e(r["version"])),
    ]
    if r.get("source_digest"):
        rows.append(("Content digest", f"<code>{_e(r['source_digest'])}</code>"))
        rows.append(("Digest check", "<span class=ok>Matches the released version</span>"))
    elif not r["draft"]:
        rows.append(
            (
                "Digest check",
                "<span class=bad>Not verified: no version manifest with a "
                "content digest was found</span>",
            )
        )
    if r.get("approved_by"):
        when = f" on {_e(r['approved_at'])}" if r.get("approved_at") else ""
        rows.append(("Version approved by", f"{_e(r['approved_by'])}{when}"))
    if r.get("approval_notes"):
        rows.append(("Approval notes", _e(r["approval_notes"])))
    if r.get("release_date"):
        rows.append(("Released", _e(r["release_date"])))
    if r.get("tag"):
        rows.append(("Release tag", f"<code>{_e(r['tag'])}</code>"))
    body = "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in rows)
    return f"<table class=release>{body}</table>"


def _owner_text(owner: Optional[Dict[str, Any]]) -> str:
    """`VP Quality, Jane Doe <jane@...> (quality)`; flags a missing role or holder."""
    if owner is None:
        return ""
    if not owner["role"]:
        return "<span class=bad>No owner</span>"
    if not owner["person"]:
        return f"<span class=bad>No one holds the role {_e(owner['role'])}</span>"
    who = f"{owner['title']}, {owner['person']}" if owner["title"] else owner["person"]
    return f"{_e(who)} <span class=muted>({_e(owner['role'])})</span>"


def _owners_table(layer: Dict[str, Any]) -> str:
    rows = [
        f"<tr><td>{_e(g['title'])}</td><td>{_owner_text(g['owner'])}</td></tr>"
        for g in layer["groups"]
        if g["owner"] is not None
    ]
    if not rows:
        return ""
    return (
        "<h2>Section owners</h2><p class='muted small'>The person accountable for each section, "
        "who reviews and approves it, as recorded with this release.</p>"
        "<table class=owners><tr><th>Section</th><th>Owner</th></tr>" + "".join(rows) + "</table>"
    )


def _tree(layers: List[Dict[str, Any]]) -> str:
    out = ["<ul class=tree>"]
    for layer in layers:
        inherited = layer["role"] == "inherited"
        tag = "<span class='tag inherited'>inherited</span>" if inherited else ""
        out.append(
            f"<li><strong>{_e(layer['title'])}</strong> <span class=id>{_e(layer['id'])}</span> "
            f"{_e(layer['release']['version'])}{tag}<ul>"
        )
        for group in layer["groups"]:
            owner = _owner_text(group["owner"])
            out.append(
                f"<li>{_e(group['title'])} <span class='muted small'>"
                f"{_e(_count_hint(group['counts']))}</span>"
                + (f" <span class=small>Owner: {owner}</span>" if owner else "")
                + "<ul>"
            )
            for scd in group["scds"]:
                hint = _count_hint(_counts(scd["items"]))
                out.append(
                    f"<li><a href='#{_anchor(layer['role'], scd['ref'])}'>{_e(scd['title'])}"
                    f"</a> <span class='muted small'>{_e(hint)}</span></li>"
                )
            out.append("</ul></li>")
        out.append("</ul></li>")
    out.append("</ul>")
    return "".join(out)


def _list(values: List[str]) -> str:
    return ", ".join(f"<code>{_e(v)}</code>" for v in values)


def _item_html(item: Dict[str, Any]) -> str:
    kind = item["kind"]
    label = "Rule" if kind == "directive" else kind.capitalize()
    out = [
        f"<div class='item {kind}'><div><span class=kind>{label}</span> "
        f"<span class=id>{_e(item['id'])}</span></div>"
    ]
    if kind == "prohibition":
        out.append(
            f"<p><strong>Prohibited ({_e(item['prohibition_kind'])}):</strong> "
            f"{_e(item['subject'])}</p>"
        )
        if item.get("instead"):
            out.append(f"<p><strong>Use instead:</strong> {_e(item['instead'])}</p>")
    else:
        out.append(f"<p>{_e(item['text'])}</p>")
    meta = []
    if item.get("cites"):
        meta.append(("Cites", _list(item["cites"])))
    for line in item.get("derived_from") or []:
        meta.append(("From", _e(line)))
    for key, value in (item.get("notes") or {}).items():
        meta.append((_e(key.replace("_", " ").capitalize()), _e(_text(value))))
    if meta:
        out.append(
            "<dl class=meta>" + "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in meta) + "</dl>"
        )
    if item.get("compiled") and item["compiled"] == item.get("text"):
        out.append(
            f"<div class='compiled muted'>Given to the AI word for word as "
            f"<span class=id>{_e(item['compiled_id'])}</span></div>"
        )
    elif item.get("compiled"):
        out.append(
            f"<div class=compiled><span class=muted>What the AI receives "
            f"(<span class=id>{_e(item['compiled_id'])}</span>):</span>"
            f"<q>{_e(item['compiled'])}</q></div>"
        )
    out.append("</div>")
    return "".join(out)


def _scd_html(scd: Dict[str, Any], layer: Dict[str, Any], targets: Dict[str, str]) -> str:
    inherited = layer["role"] == "inherited"
    tag = "<span class='tag inherited'>inherited from the Domain</span>" if inherited else ""
    out = [
        f"<section class=scd id='{_anchor(layer['role'], scd['ref'])}'>"
        f"<h3>{_e(scd['title'])}{tag}</h3>"
        f"<p class=small><span class=id>{_e(scd['ref'])}</span>"
        + (f" version {_e(scd['version'])}" if scd["version"] else "")
        + "</p>"
    ]
    if scd["description"]:
        out.append(f"<p>{_e(scd['description'])}</p>")
    if scd["summary"]:
        out.append(f"<p class=muted>{_e(scd['summary'])}</p>")
    out.extend(_item_html(i) for i in scd["items"])
    if not scd["items"]:
        out.append(
            "<p class=muted>This document gives the AI no prohibitions, rules, or " "facts.</p>"
        )
    meta = []
    if scd.get("cites"):
        meta.append(("Cites", _list(scd["cites"])))
    for rel in scd.get("relationships") or []:
        target = rel["target"]
        link = (
            f"<a href='#{targets[target]}'>{_e(target)}</a>"
            if target in targets
            else f"<code>{_e(target)}</code>"
        )
        meta.append((_e(rel["type"].replace("_", " ")), link))
    for key, value in (scd.get("provenance") or {}).items():
        meta.append((_e(key.replace("_", " ").capitalize()), _e(value)))
    meta.append(("Included in", f"{_e(layer['id'])} {_e(layer['release']['version'])}"))
    out.append("<dl class=meta>" + "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in meta) + "</dl>")
    if scd.get("other_content"):
        dumped = yaml.safe_dump(scd["other_content"], sort_keys=False, allow_unicode=True, width=88)
        out.append(
            "<details><summary class=small>Other content in this document (for "
            "reviewers; not given to the AI)</summary>"
            f"<pre>{_e(dumped)}</pre></details>"
        )
    out.append("</section>")
    return "".join(out)


def render_html(view: Dict[str, Any]) -> str:
    layers = view["layers"]
    root = layers[-1]
    title = f"{root['title']} {root['release']['version']} review package"
    targets: Dict[str, str] = {}
    for layer in layers:
        for group in layer["groups"]:
            for scd in group["scds"]:
                targets.setdefault(scd["ref"], _anchor(layer["role"], scd["ref"]))
    out = [
        "<!doctype html><html lang=en><head><meta charset=utf-8>"
        "<meta name=viewport content='width=device-width,initial-scale=1'>"
        f"<title>{_e(title)}</title><style>{CSS}</style></head><body><main>",
        f"<p class='muted small'>Review package</p><h1>{_e(root['title'])}</h1>",
    ]
    if root["description"]:
        out.append(f"<p class=muted>{_e(root['description'])}</p>")
    if root["release"]["draft"]:
        out.append(
            "<div class='banner draft'>DRAFT: this bundle has not been released. "
            "This package is for preview only and cannot be certified.</div>"
        )
    elif not root["release"]["verified"]:
        out.append(
            "<div class='banner warn'>The content of this package could not be checked "
            "against a released version.</div>"
        )
    out.append(_release_table(root))
    out.append("<h2>Summary</h2>" + "".join(f"<p>{_e(s)}</p>" for s in view["summary"]))
    if len(layers) > 1:
        out.append("<h3>Inherited Domain</h3>" + _release_table(layers[0]))
    out.append(_owners_table(root))
    out.append("<h2>Contents</h2>" + _tree(layers))
    for layer in reversed(layers):
        inherited = layer["role"] == "inherited"
        heading = ("Inherited from the Domain: " if inherited else "") + layer["title"]
        out.append(f"<h2>{_e(heading)}</h2>")
        if layer.get("identity_rule"):
            out.append(
                f"<p class=small>The AI is also told: <q>{_e(layer['identity_rule'])}" "</q></p>"
            )
        for group in layer["groups"]:
            owner = _owner_text(group["owner"])
            out.append(
                f"<p class='muted small'>{_e(group['title'])}"
                + (f" &middot; Owner: {owner}" if owner else "")
                + "</p>"
            )
            out.extend(_scd_html(s, layer, targets) for s in group["scds"])
    out.append(
        "<footer class='muted small'>Generated by <code>scs view</code> from the bundle "
        f"source, view format {VIEW_FORMAT}. Every rule and fact is shown verbatim; nothing in "
        "this package is written by AI.</footer></main></body></html>\n"
    )
    return "".join(out)


def counts(view: Dict[str, Any]) -> Tuple[int, int, int]:
    """Prohibitions, rules, and facts of the root layer."""
    c = view["layers"][-1]["counts"]
    return c["prohibition"], c["directive"], c["fact"]

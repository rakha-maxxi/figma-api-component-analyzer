"""Component refactor analyzer built on top of Figma file JSON."""

from collections import Counter, defaultdict
from datetime import datetime, timezone
import math
import re
import uuid


NOISE_NAME_RE = re.compile(r"^(frame|group|rectangle|vector|line|content|text)\b", re.IGNORECASE)


def analyze_figma_file(file_data, meta, reference_file_data=None):
    raw_by_id = {}
    records = []
    local_component_ids = set()
    component_structure_signatures = set()
    reference_inventory = _build_reference_inventory(reference_file_data)

    def walk(node, parent_id=None, depth=0, page_name=None, path_parts=None):
        node_id = node.get("id", f"anon-{len(records)}")
        node_type = node.get("type", "UNKNOWN")
        name = node.get("name", node_type.title())
        raw_by_id[node_id] = node
        width, height = _node_size(node)
        current_path_parts = list(path_parts or [])
        if node_type != "DOCUMENT":
            current_path_parts.append(name)
        record = {
            "id": node_id,
            "name": name,
            "type": node_type,
            "parent_id": parent_id,
            "depth": depth,
            "page_name": page_name,
            "width": width,
            "height": height,
            "layout_mode": node.get("layoutMode", "NONE"),
            "component_id": node.get("componentId"),
            "layer_path": " / ".join(current_path_parts),
        }
        records.append(record)
        if node_type == "COMPONENT":
            local_component_ids.add(node_id)

        current_page_name = name if node_type == "CANVAS" else page_name
        for child in node.get("children", []) or []:
            walk(
                child,
                parent_id=node_id,
                depth=depth + 1,
                page_name=current_page_name,
                path_parts=current_path_parts,
            )

    walk(file_data.get("document", {}))
    counts = Counter(record["type"] for record in records)
    components = [record for record in records if record["type"] == "COMPONENT"]
    instances = [record for record in records if record["type"] == "INSTANCE"]
    known_component_inventory = _build_known_component_inventory(file_data, meta["file_key"], local_component_ids, raw_by_id)
    component_sources = _build_component_source_groups(instances, known_component_inventory)
    component_source_counts = Counter(item["component_source_type"] for item in component_sources for _ in range(item["occurrence_count"]))

    eligible_native = []
    signatures = defaultdict(list)
    node_metrics_cache = {}

    for record in records:
        raw = raw_by_id[record["id"]]
        record.update(_node_metrics(raw, node_metrics_cache))
        record["signature"] = _signature(raw, record)
        record["structure_signature"] = _structure_signature(record["signature"])
        if record["type"] == "COMPONENT":
            component_structure_signatures.add(record["structure_signature"])
        if _is_native_candidate(record, raw):
            eligible_native.append(record)
            signatures[record["signature"]].append(record)

    repeated_clusters = []
    for signature, members in signatures.items():
        if len(members) < 2:
            continue
        cluster = _build_cluster(
            signature,
            members,
            raw_by_id,
            component_structure_signatures,
            known_component_inventory,
            reference_inventory,
        )
        repeated_clusters.append(cluster)

    repeated_clusters.sort(key=lambda item: (item["promotion_score"], item["occurrence_count"]), reverse=True)

    promotion_candidates = [cluster for cluster in repeated_clusters if cluster["bucket"] == "promotion_ready"]
    existing_component_not_reused = [cluster for cluster in repeated_clusters if cluster["bucket"] == "existing_component_not_reused"]
    raw_duplicates = [cluster for cluster in repeated_clusters if cluster["bucket"] == "raw_duplicate"]
    low_value = [cluster for cluster in repeated_clusters if cluster["bucket"] == "low_value"]

    large_components = []
    for component in components:
        assessment = _assess_component_size(component, raw_by_id[component["id"]])
        if assessment["is_large"]:
            large_components.append({
                "node_id": component["id"],
                "node_name": component["name"],
                "layer_path": component["layer_path"],
                "page_name": component["page_name"],
                "classification": assessment["classification"],
                "complexity_score": assessment["complexity_score"],
                "complexity_breakdown": assessment["complexity_breakdown"],
                "child_count": component["child_count"],
                "text_descendants": component["text_descendants"],
                "semantic_regions": component["semantic_regions"],
                "recommendation_type": assessment["recommendation_type"],
                "recommendation": assessment["recommendation"],
                "reason": assessment["reason"],
            })

    cross_file_dependencies = sum(1 for instance in instances if instance.get("component_id") and instance["component_id"] not in local_component_ids)
    possible_detached = sum(cluster["occurrence_count"] for cluster in repeated_clusters if cluster["possible_detached"])
    native_candidate_count = len(eligible_native)
    instance_usage_rate = _safe_divide(len(instances), len(instances) + native_candidate_count)
    duplication_occurrences = sum(max(cluster["occurrence_count"] - 1, 0) for cluster in repeated_clusters)
    reuse_gap = 1 - instance_usage_rate
    duplication_burden = duplication_occurrences
    refactor_candidate_count = len(large_components) + len(promotion_candidates) + len(existing_component_not_reused)
    component_vs_native_ratio = _safe_divide(len(instances), native_candidate_count or 1)

    top_recommendations = _build_recommendations(large_components, existing_component_not_reused, promotion_candidates)

    return {
        "id": str(uuid.uuid4()),
        "meta": {
            "file_key": meta["file_key"],
            "file_name": file_data.get("name", meta["file_key"]),
            "project_name": meta.get("project_name") or "Unknown Project",
            "platform": meta.get("platform") or "Unknown Platform",
            "analyzed_at": datetime.now(timezone.utc).astimezone().isoformat(),
            "source": "demo" if meta["file_key"].lower() == "demo" else "figma",
            "reference_file_key": meta.get("reference_file_key") or "",
            "reference_file_name": reference_file_data.get("name", meta.get("reference_file_key", "")) if reference_file_data else "",
            "reference_compare_enabled": bool(reference_file_data),
        },
        "summary": {
            "component_usage_rate": round(instance_usage_rate, 4),
            "reuse_gap": round(reuse_gap, 4),
            "instance_count": len(instances),
            "local_instance_count": component_source_counts.get("local_file_instance", 0),
            "remote_instance_count": component_source_counts.get("remote_library_instance", 0),
            "remote_or_published_instance_count": component_source_counts.get("remote_or_published_instance", 0),
            "unknown_instance_count": component_source_counts.get("unknown_instance", 0),
            "native_candidate_count": native_candidate_count,
            "repeated_native_cluster_count": len(repeated_clusters),
            "promotion_candidate_count": len(promotion_candidates),
            "existing_component_not_reused_count": len(existing_component_not_reused),
            "large_component_count": len(large_components),
            "section_like_component_count": sum(1 for item in large_components if item["classification"] == "section_like_component"),
            "refactor_candidate_count": refactor_candidate_count,
            "possible_detached_pattern_count": possible_detached,
            "cross_file_component_dependency_count": cross_file_dependencies,
            "duplication_burden": duplication_burden,
            "component_vs_native_ratio": round(component_vs_native_ratio, 2),
        },
        "inventory": {
            "total_nodes": len(records),
            "total_components": len(components),
            "total_component_sets": counts.get("COMPONENT_SET", 0),
            "total_instances": len(instances),
            "total_frames": counts.get("FRAME", 0),
            "total_groups": counts.get("GROUP", 0),
        },
        "large_components": large_components,
        "component_sources": component_sources[:30],
        "promotion_candidates": promotion_candidates[:15],
        "existing_component_not_reused": existing_component_not_reused[:15],
        "raw_duplicates": raw_duplicates[:25],
        "low_value_repetition": low_value[:25],
        "recommendations": top_recommendations,
    }


def _build_recommendations(large_components, existing_component_not_reused, promotion_candidates):
    recommendations = []
    for item in large_components[:8]:
        recommendations.append({
            "priority": "high",
            "title": item["node_name"],
            "layer_path": item["layer_path"],
            "page_name": item["page_name"],
            "type": item["recommendation_type"],
            "recommendation": item["recommendation"],
            "reason": item["reason"],
        })
    for item in existing_component_not_reused[:8]:
        recommendations.append({
            "priority": "high" if item["confidence"] == "high" else "medium",
            "title": item["semantic_name"],
            "layer_path": item["sample_nodes"][0]["layer_path"] if item["sample_nodes"] else "",
            "page_name": item["sample_nodes"][0]["page_name"] if item["sample_nodes"] else "",
            "type": "existing_component_not_reused",
            "recommendation": item["recommendation"],
            "reason": item["reason"],
        })
    for item in promotion_candidates[:8]:
        recommendations.append({
            "priority": "medium" if item["confidence"] == "medium" else "high",
            "title": item["semantic_name"],
            "layer_path": item["sample_nodes"][0]["layer_path"] if item["sample_nodes"] else "",
            "page_name": item["sample_nodes"][0]["page_name"] if item["sample_nodes"] else "",
            "type": item["level"],
            "recommendation": item["recommendation"],
            "reason": item["reason"],
        })
    return recommendations[:12]


def _build_cluster(signature, members, raw_by_id, component_structure_signatures, known_component_inventory, reference_inventory):
    sample = members[0]
    role_tokens = sample["role_tokens"]
    semantic_name = _semantic_name(sample, role_tokens)
    level = _infer_level(sample)
    reference_match = (
        _match_known_component(sample, semantic_name, known_component_inventory)
        or _match_reference_component(sample, semantic_name, signature, reference_inventory)
    )
    confidence = _cluster_confidence(sample, len(members), semantic_name, reference_match)
    possible_detached = sample["structure_signature"] in component_structure_signatures
    promotion_score = _promotion_score(sample, len(members), confidence, level, reference_match)
    bucket = _cluster_bucket(sample, semantic_name, len(members), confidence, level, reference_match)
    recommendation, reason = _cluster_recommendation(sample, semantic_name, level, len(members), bucket, reference_match)
    return {
        "cluster_id": f"cluster-{abs(hash(signature))}",
        "semantic_name": semantic_name,
        "level": level,
        "occurrence_count": len(members),
        "confidence": confidence,
        "bucket": bucket,
        "possible_detached": possible_detached,
        "reference_match": reference_match,
        "recommendation": recommendation,
        "reason": reason,
        "sample_nodes": [
            {
                "node_id": member["id"],
                "node_name": member["name"],
                "page_name": member["page_name"],
                "layer_path": member["layer_path"],
            }
            for member in members[:5]
        ],
        "promotion_score": promotion_score,
    }


def _cluster_recommendation(sample, semantic_name, level, occurrence_count, bucket, reference_match):
    if bucket == "existing_component_not_reused":
        component_name = reference_match["component_name"]
        reference_name = reference_match.get("reference_file_name") or reference_match.get("source_label") or "known component source"
        return (
            f"Use existing {component_name} from {reference_name} instead of rebuilding this structure natively.",
            f"Pattern repeats {occurrence_count} times and matches an existing reusable component already visible from instance metadata.",
        )
    if bucket == "low_value":
        return "Ignore for now; repetition is too low-value for UI kit action.", "Pattern is mostly low-semantic or wrapper-only repetition."
    if level == "scaffold":
        return f"Refactor into {semantic_name.lower()} scaffold with slots for variable content.", f"Structure repeats {occurrence_count} times and behaves like a reusable shell."
    if level == "compound":
        return f"Extract as reusable {semantic_name.lower()} compound in the project UI kit.", f"Pattern repeats {occurrence_count} times with stable mid-level anatomy."
    if level == "pattern":
        return f"Keep local as pattern for now; extract smaller shells and compounds from {semantic_name.lower()}.", "Structure is repeated, but still reads as a larger feature composition."
    return f"Extract as reusable {semantic_name.lower()} component.", f"Pattern repeats {occurrence_count} times with stable small-unit anatomy."


def _promotion_score(sample, occurrence_count, confidence, level, reference_match):
    confidence_weight = {"low": 0.2, "medium": 0.6, "high": 1.0}[confidence]
    level_weight = {"atomic": 0.7, "compound": 0.95, "scaffold": 1.0, "pattern": 0.4}[level]
    stability = min(sample["semantic_regions"] / 3, 1.0)
    reference_bonus = 12 if reference_match else 0
    return round((min(occurrence_count, 12) / 12) * 50 + confidence_weight * 25 + level_weight * 15 + stability * 10 + reference_bonus, 1)


def _cluster_bucket(sample, semantic_name, occurrence_count, confidence, level, reference_match):
    if reference_match:
        return "existing_component_not_reused"
    if NOISE_NAME_RE.match(sample["name"]) and sample["semantic_regions"] <= 1:
        return "low_value"
    if semantic_name.startswith("Unnamed") and occurrence_count < 4:
        return "raw_duplicate"
    if confidence == "low":
        return "raw_duplicate"
    if level == "pattern" and occurrence_count < 4:
        return "raw_duplicate"
    return "promotion_ready"


def _cluster_confidence(sample, occurrence_count, semantic_name, reference_match=None):
    score = 0
    if reference_match:
        score += 2 if reference_match["match_type"] in {"signature", "structure_signature", "name", "known_component_name"} else 1
    if occurrence_count >= 4:
        score += 1
    if sample["semantic_regions"] >= 2:
        score += 1
    if not semantic_name.startswith("Unnamed"):
        score += 1
    if sample["meaningful_child_count"] >= 2:
        score += 1
    if score >= 4:
        return "high"
    if score >= 2:
        return "medium"
    return "low"


def _infer_level(record):
    roles = set(record["role_tokens"])
    if record["semantic_regions"] >= 4 or ("header" in roles and "content" in roles):
        return "pattern"
    if record["semantic_regions"] >= 3 or "section" in roles or "card" in roles:
        return "scaffold"
    if record["semantic_regions"] >= 2 or "metric" in roles or "chevron" in roles:
        return "compound"
    return "atomic"


def _semantic_name(record, role_tokens):
    name = record["name"].strip()
    lower = name.lower()
    roles = set(role_tokens)
    if "filter" in lower or "chip" in roles:
        return "Filter Chip Group"
    if "section" in lower or ("header" in roles and "button" in roles):
        return "Section Header with Action"
    if "dialog" in lower or "popup" in lower:
        return "Dialog Shell"
    if "card" in lower and "metric" in roles:
        return "Entity Summary Card"
    if "chevron" in roles and ("title" in roles or "subtitle" in roles):
        return "List Item with Chevron"
    if "metric" in roles and record["semantic_regions"] <= 2:
        return "Metric Pair"
    if "header" in roles and "content" in roles:
        return "Section Shell"
    if not NOISE_NAME_RE.match(name) and len(name) > 3:
        normalized = re.sub(r"\s+", " ", name).strip()
        if normalized:
            return normalized
    if record["semantic_regions"] >= 3:
        return "Unnamed Scaffold Pattern"
    if record["semantic_regions"] == 2:
        return "Unnamed Compound Pattern"
    return "Unnamed Atomic Pattern"


def _assess_component_size(record, raw):
    width, height = record["width"], record["height"]
    is_section_like = record["semantic_regions"] >= 3 and record["child_count"] >= 3 and width >= 240
    is_page_like = width >= 320 and height >= 520
    complexity_score = (
        record["child_count"] * 1.7
        + record["text_descendants"] * 0.7
        + record["semantic_regions"] * 4
        + max(record["depth"] - 1, 0) * 1.2
        + (6 if width >= 280 else 0)
        + (8 if height >= 280 else 0)
    )
    complexity_breakdown = {
        "children_score": round(record["child_count"] * 1.7, 1),
        "text_score": round(record["text_descendants"] * 0.7, 1),
        "region_score": round(record["semantic_regions"] * 4, 1),
        "depth_score": round(max(record["depth"] - 1, 0) * 1.2, 1),
        "width_bonus": 6 if width >= 280 else 0,
        "height_bonus": 8 if height >= 280 else 0,
    }
    is_large = complexity_score >= 28 or is_section_like or is_page_like
    classification = "large_component"
    recommendation_type = "review_component_scope"
    recommendation = "Review component scope; it is larger than a healthy reusable building block."
    reason = f"Complexity score {round(complexity_score, 1)} with {record['child_count']} children and {record['semantic_regions']} semantic regions."
    if is_page_like:
        classification = "page_like_component"
        recommendation_type = "downgrade_to_pattern"
        recommendation = "Treat this as pattern/reference instead of reusable component; extract header shells and smaller compounds."
        reason = f"Dimensions {int(width)}x{int(height)} and structure read like a page or major template block."
    elif is_section_like:
        classification = "section_like_component"
        recommendation_type = "decompose_to_scaffold"
        recommendation = "Refactor into section shell with title, action, and content slots."
        reason = f"Component behaves like a reusable section with {record['semantic_regions']} semantic regions and {record['child_count']} direct children."
    elif complexity_score >= 36:
        classification = "template_like_component"
        recommendation_type = "split_into_scaffold_and_compounds"
        recommendation = "Split this component into scaffold and smaller compounds; current scope is too content-specific."
        reason = f"High complexity score {round(complexity_score, 1)} suggests template-like behavior."
    return {
        "is_large": is_large,
        "classification": classification,
        "complexity_score": round(complexity_score, 1),
        "complexity_breakdown": complexity_breakdown,
        "recommendation_type": recommendation_type,
        "recommendation": recommendation,
        "reason": reason,
    }


def _signature(raw, record):
    child_roles = [_child_role(child) for child in raw.get("children", []) or []]
    child_roles = [role for role in child_roles if role != "decorative"]
    role_counts = Counter(child_roles)
    dominant = ",".join(sorted(set(child_roles))[:6]) or "none"
    return "|".join(
        [
            record["type"],
            record["layout_mode"],
            f"cc:{min(record['child_count'], 8)}",
            f"mc:{min(record['meaningful_child_count'], 8)}",
            f"sr:{min(record['semantic_regions'], 6)}",
            f"txt:{min(record['text_descendants'], 8)}",
            dominant,
            f"chev:{int('chevron' in role_counts)}",
            f"btn:{int('button' in role_counts)}",
        ]
    )


def _role_tokens(raw):
    return [_child_role(child) for child in raw.get("children", []) or [] if _child_role(child) != "decorative"]


def _semantic_region_count(raw):
    roles = []
    for child in raw.get("children", []) or []:
        role = _child_role(child)
        if role != "decorative":
            roles.append(role)
    return len(set(roles))


def _meaningful_child_count(raw):
    return sum(1 for child in raw.get("children", []) or [] if _child_role(child) != "decorative")


def _child_role(node):
    node_type = node.get("type", "")
    name = node.get("name", "").lower()
    if node_type in {"RECTANGLE", "ELLIPSE"} and not name:
        return "decorative"
    if any(token in name for token in ["chevron", "arrow", "next", "back"]):
        return "chevron"
    if any(token in name for token in ["button", "cta", "submit", "apply", "save", "lihat"]):
        return "button"
    if any(token in name for token in ["filter", "chip", "tab", "segment"]):
        return "chip"
    if any(token in name for token in ["header", "title"]):
        return "title"
    if any(token in name for token in ["subtitle", "caption", "label"]):
        return "subtitle"
    if any(token in name for token in ["value", "jumlah", "omzet", "scan", "target", "brand", "metric"]):
        return "metric"
    if any(token in name for token in ["dialog", "popup", "modal"]):
        return "dialog"
    if any(token in name for token in ["input", "field", "search"]):
        return "input"
    if any(token in name for token in ["card", "section", "content", "body"]):
        return "content"
    if any(token in name for token in ["icon", "avatar", "image", "photo"]) or node_type in {"ELLIPSE", "VECTOR"}:
        return "icon"
    if node_type == "TEXT":
        if re.search(r"\d", name):
            return "metric"
        return "text"
    if node_type in {"FRAME", "GROUP"}:
        if len(node.get("children", []) or []) <= 1:
            return "decorative"
        return "content"
    return "decorative"


def _is_native_candidate(record, raw):
    if record["type"] not in {"FRAME", "GROUP"}:
        return False
    if record["depth"] <= 2 and record["width"] >= 280 and record["height"] >= 420:
        return False
    if record["meaningful_child_count"] < 2:
        return False
    if record["semantic_regions"] < 2:
        return False
    return True


def _node_metrics(node, cache):
    node_key = node.get("id") or id(node)
    if node_key in cache:
        return cache[node_key]

    role_tokens = [_child_role(child) for child in node.get("children", []) or []]
    role_tokens = [role for role in role_tokens if role != "decorative"]
    text_descendants = 1 if node.get("type") == "TEXT" else 0
    for child in node.get("children", []) or []:
        text_descendants += _node_metrics(child, cache)["text_descendants"]

    metrics = {
        "child_count": len(node.get("children", []) or []),
        "text_descendants": text_descendants,
        "semantic_regions": len(set(role_tokens)),
        "meaningful_child_count": len(role_tokens),
        "role_tokens": role_tokens,
    }
    cache[node_key] = metrics
    return metrics


def _descendant_type_count(node, target_type):
    count = 1 if node.get("type") == target_type else 0
    for child in node.get("children", []) or []:
        count += _descendant_type_count(child, target_type)
    return count


def _node_size(node):
    bbox = node.get("absoluteBoundingBox") or {}
    return bbox.get("width", 0), bbox.get("height", 0)


def _safe_divide(a, b):
    return a / b if b else 0.0


def _build_reference_inventory(reference_file_data):
    if not reference_file_data:
        return None

    items = []

    def walk(node, parent_id=None, depth=0, page_name=None, path_parts=None):
        node_id = node.get("id", f"ref-{len(items)}")
        node_type = node.get("type", "UNKNOWN")
        name = node.get("name", node_type.title())
        current_path_parts = list(path_parts or [])
        if node_type != "DOCUMENT":
            current_path_parts.append(name)
        current_page_name = name if node_type == "CANVAS" else page_name

        if node_type == "COMPONENT":
            width, height = _node_size(node)
            metrics = _node_metrics(node, {})
            record = {
                "id": node_id,
                "name": name,
                "type": node_type,
                "parent_id": parent_id,
                "depth": depth,
                "page_name": current_page_name,
                "width": width,
                "height": height,
                "layout_mode": node.get("layoutMode", "NONE"),
                "layer_path": " / ".join(current_path_parts),
            }
            record.update(metrics)
            record["signature"] = _signature(node, record)
            record["structure_signature"] = _structure_signature(record["signature"])
            record["semantic_name"] = _semantic_name(record, record["role_tokens"])
            items.append(record)

        for child in node.get("children", []) or []:
            walk(
                child,
                parent_id=node_id,
                depth=depth + 1,
                page_name=current_page_name,
                path_parts=current_path_parts,
            )

    walk(reference_file_data.get("document", {}))

    by_signature = defaultdict(list)
    by_structure_signature = defaultdict(list)
    by_name = defaultdict(list)
    by_semantic_name = defaultdict(list)
    reference_file_name = reference_file_data.get("name", "")

    for item in items:
        ref_item = {
            "component_id": item["id"],
            "component_name": item["name"],
            "semantic_name": item["semantic_name"],
            "signature": item["signature"],
            "structure_signature": item["structure_signature"],
            "page_name": item["page_name"],
            "layer_path": item["layer_path"],
            "reference_file_name": reference_file_name,
        }
        by_signature[item["signature"]].append(ref_item)
        by_structure_signature[item["structure_signature"]].append(ref_item)
        by_name[_normalize_label(item["name"])].append(ref_item)
        by_semantic_name[_normalize_label(item["semantic_name"])].append(ref_item)

    return {
        "file_name": reference_file_name,
        "items": items,
        "by_signature": dict(by_signature),
        "by_structure_signature": dict(by_structure_signature),
        "by_name": dict(by_name),
        "by_semantic_name": dict(by_semantic_name),
    }


def _match_reference_component(sample, semantic_name, signature, reference_inventory):
    if not reference_inventory:
        return None

    if signature in reference_inventory["by_signature"]:
        match = reference_inventory["by_signature"][signature][0].copy()
        match["match_type"] = "signature"
        return match

    structure_signature = _structure_signature(signature)
    if structure_signature in reference_inventory["by_structure_signature"]:
        match = reference_inventory["by_structure_signature"][structure_signature][0].copy()
        match["match_type"] = "structure_signature"
        return match

    normalized_name = _normalize_label(sample["name"])
    if normalized_name and normalized_name in reference_inventory["by_name"]:
        match = reference_inventory["by_name"][normalized_name][0].copy()
        match["match_type"] = "name"
        return match

    normalized_semantic = _normalize_label(semantic_name)
    if normalized_semantic and normalized_semantic in reference_inventory["by_semantic_name"]:
        match = reference_inventory["by_semantic_name"][normalized_semantic][0].copy()
        match["match_type"] = "semantic_name"
        return match

    return None


def _build_known_component_inventory(file_data, current_file_key, local_component_ids, raw_by_id):
    by_name = defaultdict(list)
    by_semantic_name = defaultdict(list)
    by_component_id = {}
    file_components = file_data.get("components", {}) or {}
    current_file_name = file_data.get("name", current_file_key)

    for component_id, metadata in file_components.items():
        component_name = metadata.get("name") or raw_by_id.get(component_id, {}).get("name") or component_id
        source_type, source_label = _component_source_type(component_id, metadata, current_file_key, local_component_ids, current_file_name)
        item = {
            "component_id": component_id,
            "component_key": metadata.get("key", ""),
            "component_name": component_name,
            "component_source_type": source_type,
            "source_label": source_label,
            "source_file_key": metadata.get("file_key") or metadata.get("fileKey") or "",
            "remote": bool(metadata.get("remote")),
            "match_source": "file_component_metadata",
        }
        by_component_id[component_id] = item
        by_name[_normalize_label(component_name)].append(item)
        by_semantic_name[_normalize_label(component_name)].append(item)

    for component_id in local_component_ids:
        if component_id in by_component_id:
            continue
        raw_component = raw_by_id.get(component_id, {})
        component_name = raw_component.get("name", component_id)
        item = {
            "component_id": component_id,
            "component_key": "",
            "component_name": component_name,
            "component_source_type": "local_file_instance",
            "source_label": current_file_name,
            "source_file_key": current_file_key,
            "remote": False,
            "match_source": "local_component_node",
        }
        by_component_id[component_id] = item
        by_name[_normalize_label(component_name)].append(item)
        by_semantic_name[_normalize_label(component_name)].append(item)

    return {
        "by_component_id": by_component_id,
        "by_name": dict(by_name),
        "by_semantic_name": dict(by_semantic_name),
    }


def _build_component_source_groups(instances, known_component_inventory):
    groups = {}
    for instance in instances:
        component_id = instance.get("component_id") or ""
        source = known_component_inventory["by_component_id"].get(component_id) or {
            "component_id": component_id,
            "component_key": "",
            "component_name": component_id or "Unknown component",
            "component_source_type": "unknown_instance",
            "source_label": "Unknown source",
            "source_file_key": "",
            "remote": False,
            "match_source": "missing_component_metadata",
        }
        group_key = source.get("component_key") or source["component_id"] or source["component_name"]
        if group_key not in groups:
            groups[group_key] = {
                "component_id": source["component_id"],
                "component_key": source.get("component_key", ""),
                "component_name": source["component_name"],
                "component_source_type": source["component_source_type"],
                "source_label": source["source_label"],
                "source_file_key": source.get("source_file_key", ""),
                "remote": source.get("remote", False),
                "occurrence_count": 0,
                "sample_nodes": [],
            }
        groups[group_key]["occurrence_count"] += 1
        if len(groups[group_key]["sample_nodes"]) < 5:
            groups[group_key]["sample_nodes"].append({
                "node_id": instance["id"],
                "node_name": instance["name"],
                "page_name": instance["page_name"],
                "layer_path": instance["layer_path"],
            })

    return sorted(groups.values(), key=lambda item: item["occurrence_count"], reverse=True)


def _component_source_type(component_id, metadata, current_file_key, local_component_ids, current_file_name):
    source_file_key = metadata.get("file_key") or metadata.get("fileKey") or ""
    is_remote = bool(metadata.get("remote"))

    if component_id in local_component_ids:
        return "local_file_instance", current_file_name
    if source_file_key and source_file_key == current_file_key:
        return "local_file_instance", current_file_name
    if is_remote or (source_file_key and source_file_key != current_file_key):
        return "remote_library_instance", source_file_key or "Remote library"
    if metadata:
        return "remote_or_published_instance", source_file_key or "Published component"
    return "unknown_instance", "Unknown source"


def _match_known_component(sample, semantic_name, known_component_inventory):
    if not known_component_inventory:
        return None

    normalized_name = _normalize_label(sample["name"])
    if normalized_name and not NOISE_NAME_RE.match(sample["name"]) and normalized_name in known_component_inventory["by_name"]:
        match = known_component_inventory["by_name"][normalized_name][0].copy()
        match["match_type"] = "known_component_name"
        return match

    normalized_semantic = _normalize_label(semantic_name)
    if (
        normalized_semantic
        and not semantic_name.startswith("Unnamed")
        and normalized_semantic in known_component_inventory["by_semantic_name"]
    ):
        match = known_component_inventory["by_semantic_name"][normalized_semantic][0].copy()
        match["match_type"] = "known_component_semantic_name"
        return match

    return None


def _normalize_label(value):
    normalized = re.sub(r"[^a-z0-9]+", " ", (value or "").lower())
    return re.sub(r"\s+", " ", normalized).strip()


def _structure_signature(signature):
    return signature.split("|", 1)[1] if "|" in signature else signature

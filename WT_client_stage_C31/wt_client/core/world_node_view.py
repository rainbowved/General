from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional, Tuple

from wt_client.core.content_pack import ContentPack


@dataclass(frozen=True)
class NodeView:
    graph_id: str
    node_id: str
    ui: Dict[str, Any]
    raw_node: Dict[str, Any]


def _get_location(state: Mapping[str, Any]) -> Optional[Mapping[str, Any]]:
    w = state.get("world") if isinstance(state, Mapping) else None
    if isinstance(w, dict):
        ww = w.get("world")
        if isinstance(ww, dict):
            loc = ww.get("location")
            if isinstance(loc, dict):
                return loc
    return None


def _pick_graph_file(pack: ContentPack, graph_id: str) -> Optional[str]:
    gid = str(graph_id)
    if not gid:
        return None
    target_suffix = f"{gid}_graph.json"
    files = [f.replace("\\", "/") for f in pack.list_files()]
    exact = [f for f in files if f.endswith(target_suffix)]
    if exact:
        return sorted(exact, key=lambda s: (len(s), s))[0]
    # fallback: any *_graph.json containing the graph id token
    fuzzy = [f for f in files if f.endswith("_graph.json") and gid in f]
    if fuzzy:
        return sorted(fuzzy, key=lambda s: (len(s), s))[0]
    return None


def _find_node_in_graph(doc: Mapping[str, Any], node_id: str) -> Optional[Dict[str, Any]]:
    nodes = doc.get("nodes")
    if not isinstance(nodes, list):
        return None
    nid = str(node_id)
    for n in nodes:
        if not isinstance(n, dict):
            continue
        if str(n.get("node_id") or "") == nid:
            return dict(n)
    return None


def resolve_current_node_view(pack: ContentPack, state: Mapping[str, Any]) -> Optional[NodeView]:
    """Best-effort read-only node card resolver.

    Reads world graph JSON from the selected pack (db_bundle/content/world/*_graph.json)
    and extracts node['ui'] fields for the current location.

    This never mutates state and never evaluates mechanics.
    """

    loc = _get_location(state)
    if not loc:
        return None
    graph_id = str(loc.get("location_id") or "")
    node_id = str(loc.get("sub_id") or "")
    if not graph_id or not node_id:
        return None

    graph_file = _pick_graph_file(pack, graph_id)
    if not graph_file:
        return None

    doc = pack.load_json(graph_file)
    if not isinstance(doc, dict):
        return None
    node = _find_node_in_graph(doc, node_id)
    if not node:
        return None
    ui = node.get("ui")
    ui_dict: Dict[str, Any] = dict(ui) if isinstance(ui, dict) else {}
    return NodeView(graph_id=graph_id, node_id=node_id, ui=ui_dict, raw_node=node)

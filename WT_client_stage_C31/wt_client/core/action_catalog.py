from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Tuple

from wt_client.core.content_pack import ContentPack
from wt_client.core.node_interactions import NodeInteractions
from wt_client.core.world_resolver import WorldGraph, WorldResolverError
from wt_client.core.action_dispatcher import ActionDispatcher


class ActionCatalogError(RuntimeError):
    pass


@dataclass(frozen=True)
class ActionMeta:
    action_id: str
    group: str  # travel / explore / rest / service / other
    label: str
    description: str
    record_only: bool
    sources: Tuple[str, ...]


def _is_record_only(action_id: str) -> bool:
    # Single source of truth: ActionDispatcher capability declaration.
    return ActionDispatcher.is_record_only_node_action_id(action_id)


def _norm(s: str) -> str:
    return str(s).replace("\\", "/").lstrip("/")


def _group_for_action(action_id: str, sources: Tuple[str, ...]) -> str:
    aid = str(action_id)
    if aid in {"EXIT_CITY", "ENTER_CITY", "ENTER_TOWER"}:
        return "travel"
    if aid in {"REST", "CAMP_REST"}:
        return "rest"
    if aid in {"PROCEED"}:
        return "explore"
    # Heuristic: actions introduced by node services are usually "service".
    if any(s.startswith("service:") for s in sources):
        return "service"
    # A few obvious service-y ids (forward compatible).
    if any(tok in aid for tok in ("SHOP", "TRADE", "HEAL", "INN", "TAVERN", "SMITH", "BANK")):
        return "service"
    return "other"


class ActionCatalog:
    """Lists available node actions for a given (graph_id, node_id).

    Source of truth: specs/node_interactions.json.
    Read-only helper for UI (no new mechanics).
    """

    def __init__(self, pack: ContentPack) -> None:
        self._pack = pack
        self._spec = pack.load_json("specs/node_interactions.json")
        self._interactions = NodeInteractions(self._spec)
        self._graphs = self._load_world_graphs(pack)

        raw = self._spec.get("action_catalog") if isinstance(self._spec, dict) else None
        self._action_catalog: Dict[str, Any] = dict(raw) if isinstance(raw, dict) else {}

    @property
    def interactions(self) -> NodeInteractions:
        return self._interactions

    def list_actions(self, graph_id: str, node_id: str) -> List[ActionMeta]:
        gid = str(graph_id)
        nid = str(node_id)
        g = self._graphs.get(gid)
        if not g:
            raise ActionCatalogError(
                f"No world graph found for graph_id={gid}. Known graphs: {sorted(self._graphs.keys())}"
            )
        node = g.nodes_by_id.get(nid)
        if not node:
            raise ActionCatalogError(f"Node not found in graph {gid}: {nid}")

        resolved = self._interactions.resolve(node)
        out: List[ActionMeta] = []
        for aid in resolved.action_ids:
            srcs = tuple(resolved.sources.get(aid, []))
            label, desc = self._describe(aid)
            out.append(
                ActionMeta(
                    action_id=aid,
                    group=_group_for_action(aid, srcs),
                    label=label,
                    description=desc,
                    record_only=_is_record_only(aid),
                    sources=srcs,
                )
            )
        return out

    def is_record_only(self, action_id: str) -> bool:
        return _is_record_only(str(action_id))

    def _describe(self, action_id: str) -> Tuple[str, str]:
        """Return (label, description) with friendly fallbacks."""
        aid = str(action_id)
        it = self._action_catalog.get(aid)

        label = ""
        desc = ""

        if isinstance(it, str):
            label = it
        elif isinstance(it, dict):
            if isinstance(it.get("label_ru"), str) and it.get("label_ru"):
                label = str(it.get("label_ru"))
            elif isinstance(it.get("ru"), str) and it.get("ru"):
                label = str(it.get("ru"))
            elif isinstance(it.get("label"), str) and it.get("label"):
                label = str(it.get("label"))

            if isinstance(it.get("description_ru"), str) and it.get("description_ru"):
                desc = str(it.get("description_ru"))
            elif isinstance(it.get("description"), str) and it.get("description"):
                desc = str(it.get("description"))

        if not label:
            label = self._interactions.describe_action_ru(aid)
        if not desc:
            desc = ""
        return label, desc

    def _load_world_graphs(self, pack: ContentPack) -> Dict[str, WorldGraph]:
        db = pack.layout.db_bundle_dir
        if not db:
            raise ActionCatalogError("Pack layout has no db_bundle_dir; cannot locate world graphs")
        prefix = _norm(f"{db}/content/world/")
        graphs: Dict[str, WorldGraph] = {}
        for f in pack.list_files():
            rel = _norm(f)
            if not rel.startswith(prefix):
                continue
            if not rel.endswith("_graph.json"):
                continue
            doc = pack.load_json(rel)
            if not isinstance(doc, dict):
                continue
            try:
                g = WorldGraph.from_json(doc)
            except WorldResolverError:
                continue
            graphs.setdefault(g.graph_id, g)
        if not graphs:
            raise ActionCatalogError(f"No world graphs found under {prefix}")
        return graphs

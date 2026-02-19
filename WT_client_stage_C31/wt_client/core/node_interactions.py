from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Set, Tuple


class NodeInteractionsError(RuntimeError):
    pass


def _as_set(x: Any) -> Set[str]:
    if not x:
        return set()
    if isinstance(x, (list, tuple, set)):
        return {str(i) for i in x}
    return {str(x)}


@dataclass(frozen=True)
class ResolvedActions:
    node_type: str
    action_ids: List[str]
    sources: Dict[str, List[str]]  # action_id -> list of source strings


class NodeInteractions:
    """Interprets specs/node_interactions.json.

    Resolution algorithm (per spec):
      1) Determine node_type by first matching rule.
      2) Start with node_types[node_type].actions
      3) Add actions from service_to_actions for each node ui.services
      4) Deduplicate + stable priority ordering.
    """

    def __init__(self, spec: Mapping[str, Any]) -> None:
        self._spec = dict(spec)
        self._rules = list(self._spec.get("rules") or [])
        self._node_types: Dict[str, Any] = dict(self._spec.get("node_types") or {})
        self._service_to_actions: Dict[str, Any] = dict(self._spec.get("service_to_actions") or {})
        self._action_catalog: Dict[str, Any] = dict(self._spec.get("action_catalog") or {})
        self._priority_order: List[str] = list(self._spec.get("priority_order") or [])

        if not self._rules or not self._node_types:
            raise NodeInteractionsError("node_interactions spec is missing required fields (rules/node_types)")

        # Precompute rank for stable sorting.
        self._rank: Dict[str, int] = {aid: i for i, aid in enumerate(self._priority_order)}

    def describe_action_ru(self, action_id: str) -> str:
        it = self._action_catalog.get(action_id)
        if isinstance(it, dict) and "ru" in it:
            return str(it["ru"])
        return action_id

    def resolve(self, node: Mapping[str, Any]) -> ResolvedActions:
        node_type = self._resolve_node_type(node)
        base_actions = list((self._node_types.get(node_type) or {}).get("actions") or [])

        services = self._extract_services(node)
        sources: Dict[str, Set[str]] = {}
        actions: Set[str] = set()

        def _add(action_id: str, src: str) -> None:
            aid = str(action_id)
            actions.add(aid)
            sources.setdefault(aid, set()).add(src)

        for aid in base_actions:
            _add(aid, f"node_type:{node_type}")

        for svc in services:
            mapped = self._service_to_actions.get(svc)
            if not mapped:
                # Forward compatible: unknown services are ignored.
                continue
            for aid in list(mapped):
                _add(aid, f"service:{svc}")

        ordered = self._order_actions(actions)
        return ResolvedActions(
            node_type=node_type,
            action_ids=ordered,
            sources={k: sorted(list(v)) for k, v in sources.items()},
        )

    def _extract_services(self, node: Mapping[str, Any]) -> List[str]:
        ui = node.get("ui")
        if isinstance(ui, dict):
            sv = ui.get("services")
            if isinstance(sv, list):
                return [str(s) for s in sv]
        # Some future nodes might store services elsewhere.
        sv = node.get("services")
        if isinstance(sv, list):
            return [str(s) for s in sv]
        return []

    def _resolve_node_type(self, node: Mapping[str, Any]) -> str:
        for rule in self._rules:
            if not isinstance(rule, dict):
                continue
            node_type = rule.get("node_type")
            match = rule.get("match")
            if not node_type or not isinstance(match, dict):
                continue
            if self._match_node(match, node):
                return str(node_type)
        # Spec normally ends with defaults; if not found, fall back deterministically.
        return "UNKNOWN"

    def _match_node(self, match: Mapping[str, Any], node: Mapping[str, Any]) -> bool:
        # region
        m_region = match.get("region")
        if m_region is not None:
            if str(node.get("region")) != str(m_region):
                return False

        tags = _as_set(node.get("tags"))

        tags_any = match.get("tags_any")
        if tags_any is not None:
            if not (tags & _as_set(tags_any)):
                return False

        tags_all = match.get("tags_all")
        if tags_all is not None:
            if not _as_set(tags_all).issubset(tags):
                return False

        services = _as_set(self._extract_services(node))

        svc_any = match.get("services_any")
        if svc_any is not None:
            if not (services & _as_set(svc_any)):
                return False

        svc_all = match.get("services_all")
        if svc_all is not None:
            if not _as_set(svc_all).issubset(services):
                return False

        return True

    def _order_actions(self, action_ids: Iterable[str]) -> List[str]:
        # Stable ordering: by explicit priority_order first, then lexicographic.
        def key(aid: str) -> Tuple[int, int, str]:
            if aid in self._rank:
                return (0, self._rank[aid], "")
            return (1, 10**9, aid)

        return sorted({str(a) for a in action_ids}, key=key)

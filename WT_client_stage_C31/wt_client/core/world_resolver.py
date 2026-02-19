from __future__ import annotations

import copy
import hashlib
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Set, Tuple

from wt_client.core.content_pack import ContentPack
from wt_client.core.node_interactions import NodeInteractions


class WorldResolverError(RuntimeError):
    pass


def _sha16(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def _norm(s: str) -> str:
    return str(s).replace("\\", "/").lstrip("/")


@dataclass(frozen=True)
class WorldGraph:
    graph_id: str
    start_node_id: str
    nodes_by_id: Dict[str, Dict[str, Any]]
    adjacency: Dict[str, Set[str]]

    @staticmethod
    def from_json(doc: Mapping[str, Any]) -> "WorldGraph":
        graph_id = str(doc.get("graph_id") or "UNKNOWN")
        start_node_id = str(doc.get("start_node_id") or "")

        nodes_raw = doc.get("nodes")
        if not isinstance(nodes_raw, list):
            raise WorldResolverError(f"Invalid world graph {graph_id}: nodes must be a list")

        nodes_by_id: Dict[str, Dict[str, Any]] = {}
        for n in nodes_raw:
            if not isinstance(n, dict):
                continue
            nid = n.get("node_id")
            if not nid:
                continue
            nodes_by_id[str(nid)] = dict(n)

        edges_raw = doc.get("edges")
        if not isinstance(edges_raw, list):
            edges_raw = []

        adjacency: Dict[str, Set[str]] = {nid: set() for nid in nodes_by_id.keys()}
        for e in edges_raw:
            if not isinstance(e, dict):
                continue
            a = e.get("from")
            b = e.get("to")
            if not a or not b:
                continue
            a = str(a)
            b = str(b)
            if a in adjacency:
                adjacency[a].add(b)
            if e.get("bidirectional") and b in adjacency:
                adjacency[b].add(a)

        if not start_node_id and nodes_by_id:
            start_node_id = sorted(nodes_by_id.keys())[0]

        return WorldGraph(graph_id=graph_id, start_node_id=start_node_id, nodes_by_id=nodes_by_id, adjacency=adjacency)

    def neighbors(self, node_id: str) -> List[str]:
        return sorted(list(self.adjacency.get(str(node_id), set())))


class WorldResolver:
    """Resolves current node and available actions based on node_interactions + world graphs.

    Data sources:
      - specs/node_interactions.json
      - db_bundle*/content/world/*_graph.json

    State inputs (demo/SAVE):
      state['world']['world']['location'] = {region, location_id, sub_id, ...}
    """

    def __init__(self, pack: ContentPack) -> None:
        self._pack = pack
        self._interactions = NodeInteractions(pack.load_json("specs/node_interactions.json"))
        self._graphs = self._load_world_graphs(pack)

    @property
    def interactions(self) -> NodeInteractions:
        return self._interactions

    def get_current_node(self, state: Mapping[str, Any]) -> Dict[str, Any]:
        loc = self._get_location(state)
        graph = self._get_graph_for_location(loc)
        node_id = str(loc.get("sub_id") or graph.start_node_id)
        node = graph.nodes_by_id.get(node_id)
        if not node:
            raise WorldResolverError(f"Current node_id not found in graph {graph.graph_id}: {node_id}")
        return dict(node)

    def get_available_actions(self, node: Mapping[str, Any], state: Mapping[str, Any]) -> List[Dict[str, Any]]:
        # State is currently not used, but reserved for future gates (skills, flags, etc.)
        resolved = self._interactions.resolve(node)
        out: List[Dict[str, Any]] = []
        for aid in resolved.action_ids:
            out.append(
                {
                    "action_id": aid,
                    "label_ru": self._interactions.describe_action_ru(aid),
                    "sources": resolved.sources.get(aid, []),
                }
            )
        return out

    def get_neighbors(self, state: Mapping[str, Any]) -> List[str]:
        """Return reachable neighbor node_ids from the current node (within the current graph)."""
        loc = self._get_location(state)
        graph = self._get_graph_for_location(loc)
        cur_node_id = str(loc.get("sub_id") or graph.start_node_id)
        return graph.neighbors(cur_node_id)

    def get_node_by_id(self, state: Mapping[str, Any], node_id: str) -> Dict[str, Any]:
        """Fetch a node by id within the current location graph."""
        loc = self._get_location(state)
        graph = self._get_graph_for_location(loc)
        nid = str(node_id)
        node = graph.nodes_by_id.get(nid)
        if not node:
            raise WorldResolverError(f"Node not found in graph {graph.graph_id}: {nid}")
        return dict(node)

    def get_graph_start(self, graph_id: str) -> str:
        """Return start_node_id for a world graph (by location_id/graph_id)."""
        gid = str(graph_id)
        g = self._graphs.get(gid)
        if not g:
            raise WorldResolverError(f"No world graph found for graph_id={gid}. Known graphs: {sorted(self._graphs.keys())}")
        return str(g.start_node_id)

    def move(self, to_node_id: str, state: Mapping[str, Any], ts: Optional[str] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Move within the current graph.

        Returns: (new_state, move_event)
        """
        loc = self._get_location(state)
        graph = self._get_graph_for_location(loc)
        cur_node_id = str(loc.get("sub_id") or graph.start_node_id)
        to_node_id = str(to_node_id)

        if to_node_id not in graph.nodes_by_id:
            raise WorldResolverError(f"Unknown destination node_id for graph {graph.graph_id}: {to_node_id}")

        neigh = graph.adjacency.get(cur_node_id, set())
        if to_node_id not in neigh:
            raise WorldResolverError(
                f"Move blocked: no edge {cur_node_id} -> {to_node_id} in graph {graph.graph_id}"
            )

        new_state = copy.deepcopy(dict(state))
        new_loc = self._get_location(new_state)
        from_loc = {
            "region": new_loc.get("region"),
            "location_id": new_loc.get("location_id"),
            "sub_id": new_loc.get("sub_id"),
        }
        new_loc["sub_id"] = to_node_id
        to_loc = {
            "region": new_loc.get("region"),
            "location_id": new_loc.get("location_id"),
            "sub_id": new_loc.get("sub_id"),
        }

        move_event = {
            "event_id": f"MV_{_sha16(f'{from_loc}->{to_loc}')}",
            "ts": ts or "0",
            "type": "WORLD_MOVE",
            "payload": {"from": from_loc, "to": to_loc},
        }
        return new_state, move_event

    def build_action_event(
        self,
        action_id: str,
        state: Mapping[str, Any],
        args: Optional[Mapping[str, Any]] = None,
        ts: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a minimal action-request event suitable for TURNPACK delta_events."""
        loc = self._get_location(state)
        payload = {
            "action_id": str(action_id),
            "at": {
                "region": loc.get("region"),
                "location_id": loc.get("location_id"),
                "sub_id": loc.get("sub_id"),
            },
            "args": dict(args) if isinstance(args, Mapping) else {},
        }
        return {
            "event_id": f"ACT_{_sha16(str(payload))}",
            "ts": ts or "0",
            "type": "action.request",
            "payload": payload,
        }

    # --- internals ---
    def _get_location(self, state: Mapping[str, Any]) -> Dict[str, Any]:
        w = state.get("world") if isinstance(state, Mapping) else None
        if isinstance(w, dict) and "world" in w and isinstance(w.get("world"), dict):
            ww = w.get("world")
            loc = ww.get("location")
            if isinstance(loc, dict):
                return loc
        raise WorldResolverError("State does not contain world.world.location")

    def _get_graph_for_location(self, loc: Mapping[str, Any]) -> WorldGraph:
        graph_id = loc.get("location_id")
        if not graph_id:
            raise WorldResolverError("Location is missing location_id; cannot select world graph")
        gid = str(graph_id)
        g = self._graphs.get(gid)
        if not g:
            raise WorldResolverError(f"No world graph found for location_id={gid}. Known graphs: {sorted(self._graphs.keys())}")
        return g

    def _load_world_graphs(self, pack: ContentPack) -> Dict[str, WorldGraph]:
        db = pack.layout.db_bundle_dir
        if not db:
            raise WorldResolverError("Pack layout has no db_bundle_dir; cannot locate world graphs")
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
            g = WorldGraph.from_json(doc)
            # If duplicated ids exist, keep the first in deterministic order.
            graphs.setdefault(g.graph_id, g)
        if not graphs:
            raise WorldResolverError(f"No world graphs found under {prefix}")
        return graphs

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..models import ExecutionStatus, SessionState, StateNode

_logger = logging.getLogger(__name__)


class StateGraph:
    def __init__(self, session: SessionState):
        self.session = session
        self.nodes_by_id: Dict[str, StateNode] = {node.node_id: node for node in session.nodes}

    def add_node(self, node_id: str, label: str, inputs: Optional[Dict[str, Any]] = None) -> StateNode:
        node = StateNode(node_id=node_id, label=label, inputs=inputs or {})
        self.session.nodes.append(node)
        self.nodes_by_id[node_id] = node
        self.session.updated_at = datetime.utcnow()
        _logger.debug("Added node %s to state graph", node_id)
        return node

    def set_current_node(self, node_id: str) -> None:
        self.session.current_node = node_id
        self.session.updated_at = datetime.utcnow()
        _logger.debug("Current node set to %s", node_id)

    def update_node_output(self, node_id: str, output: Dict[str, Any]) -> None:
        node = self.nodes_by_id[node_id]
        node.outputs.update(output)
        node.trace.append(f"Output updated at {datetime.utcnow().isoformat()}")
        self.session.updated_at = datetime.utcnow()

    def start_node(self, node_id: str) -> None:
        node = self.nodes_by_id[node_id]
        node.status = ExecutionStatus.RUNNING
        node.started_at = datetime.utcnow()
        node.trace.append("Started execution")
        self.session.status = ExecutionStatus.RUNNING
        self.session.updated_at = datetime.utcnow()
        _logger.info("Started node %s", node_id)

    def complete_node(self, node_id: str, output: Optional[Dict[str, Any]] = None) -> None:
        node = self.nodes_by_id[node_id]
        if output:
            node.outputs.update(output)
        node.status = ExecutionStatus.COMPLETED
        node.finished_at = datetime.utcnow()
        node.trace.append("Completed execution")
        self.session.status = ExecutionStatus.RUNNING
        self.session.updated_at = datetime.utcnow()
        _logger.info("Completed node %s", node_id)

    def fail_node(self, node_id: str, reason: str) -> None:
        node = self.nodes_by_id[node_id]
        node.status = ExecutionStatus.FAILED
        node.trace.append(f"Failed: {reason}")
        node.finished_at = datetime.utcnow()
        self.session.status = ExecutionStatus.FAILED
        self.session.updated_at = datetime.utcnow()
        _logger.warning("Node %s failed: %s", node_id, reason)

    def get_pending_nodes(self) -> List[StateNode]:
        return [node for node in self.session.nodes if node.status == ExecutionStatus.PENDING]

    def to_dict(self) -> Dict[str, Any]:
        return self.session.model_dump()

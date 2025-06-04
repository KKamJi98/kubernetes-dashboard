"""Tests for the collectors module."""

import unittest
from unittest.mock import MagicMock, patch

from kubernetes_dashboard.collectors import (_get_cluster_events, _get_pod_logs,
                                           _node_metrics, _non_running_pods,
                                           _non_running_pods_list, _recent_restarts,
                                           _total_pods, collect)


class TestCollectors(unittest.TestCase):
    """Test cases for the collectors module."""

    @patch("kubernetes_dashboard.collectors.api_for")
    def test_get_pod_logs(self, mock_api_for):
        """Test _get_pod_logs function."""
        # Mock 설정
        mock_core = MagicMock()
        mock_core.read_namespaced_pod_log.return_value = "test log"
        mock_api_for.return_value = (mock_core, None)
        
        # 함수 호출
        result = _get_pod_logs("test-cluster", "test-pod", "default", "container", 100)
        
        # 결과 확인
        self.assertEqual(result, "test log")
        mock_core.read_namespaced_pod_log.assert_called_once_with(
            name="test-pod", namespace="default", container="container", tail_lines=100
        )

    @patch("kubernetes_dashboard.collectors.api_for")
    def test_get_cluster_events(self, mock_api_for):
        """Test _get_cluster_events function."""
        # Mock 설정
        mock_core = MagicMock()
        mock_event = MagicMock()
        mock_event.type = "Normal"
        mock_event.reason = "Created"
        mock_event.message = "Created pod"
        mock_event.last_timestamp = None
        mock_event.event_time = None
        mock_event.involved_object.kind = "Pod"
        mock_event.involved_object.name = "test-pod"
        
        mock_events = MagicMock()
        mock_events.items = [mock_event]
        mock_core.list_event_for_all_namespaces.return_value = mock_events
        mock_api_for.return_value = (mock_core, None)
        
        # 함수 호출
        result = _get_cluster_events("test-cluster")
        
        # 결과 확인
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["cluster"], "test-cluster")
        self.assertEqual(result[0]["type"], "Normal")
        self.assertEqual(result[0]["reason"], "Created")
        self.assertEqual(result[0]["object"], "Pod/test-pod")
        self.assertEqual(result[0]["message"], "Created pod")
        
        mock_core.list_event_for_all_namespaces.assert_called_once_with(limit=100)

    @patch("kubernetes_dashboard.collectors._get_cluster_events")
    @patch("kubernetes_dashboard.collectors._recent_restarts")
    @patch("kubernetes_dashboard.collectors._node_metrics")
    @patch("kubernetes_dashboard.collectors._total_pods")
    @patch("kubernetes_dashboard.collectors._non_running_pods_list")
    def test_collect(self, mock_non_running_pods_list, mock_total_pods, 
                    mock_node_metrics, mock_recent_restarts, mock_get_cluster_events):
        """Test collect function."""
        # Mock 설정
        mock_non_running_pods_list.side_effect = [
            [{"cluster": "cluster1", "pod": "pod1"}],
            [{"cluster": "cluster2", "pod": "pod2"}]
        ]
        mock_total_pods.side_effect = [10, 20]
        mock_node_metrics.side_effect = [
            [{"cluster": "cluster1", "node": "node1"}],
            [{"cluster": "cluster2", "node": "node2"}]
        ]
        mock_recent_restarts.side_effect = [
            [{"cluster": "cluster1", "pod": "pod1"}],
            [{"cluster": "cluster2", "pod": "pod2"}]
        ]
        mock_get_cluster_events.side_effect = [
            [{"cluster": "cluster1", "type": "Normal"}],
            [{"cluster": "cluster2", "type": "Warning"}]
        ]
        
        # 함수 호출
        result = collect(("cluster1", "cluster2"))
        
        # 결과 확인
        self.assertEqual(result["total_pods"], 30)
        self.assertEqual(result["non_running_total"], 2)
        self.assertEqual(len(result["non_running_pods"]), 2)
        self.assertEqual(len(result["node_metrics"]), 2)
        self.assertEqual(len(result["recent_restarts"]), 2)
        self.assertEqual(len(result["events"]), 2)


if __name__ == "__main__":
    unittest.main()

"""Tests for the kube_client module."""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from kubernetes_dashboard.kube_client import (
    api_for,
    is_running_in_kubernetes,
    load_kubeconfig_from_secret,
)


class TestKubeClient(unittest.TestCase):
    """Test cases for the kube_client module."""

    def setUp(self):
        # 각 테스트 전에 api_for 캐시 초기화
        api_for.cache_clear()

    @patch("kubernetes_dashboard.kube_client.api_for.cache_clear")
    @patch("kubernetes_dashboard.kube_client.is_running_in_kubernetes")
    @patch("kubernetes_dashboard.kube_client.load_kubeconfig_from_secret")
    @patch("kubernetes_dashboard.kube_client.config")
    def test_api_for_local_env(self, mock_config, mock_load_secret, mock_is_k8s, _):
        """Test api_for function in local environment."""
        # 로컬 환경 시뮬레이션
        mock_is_k8s.return_value = False

        # 함수 호출
        api_for("test-context")

        # 로컬 kubeconfig 로드 확인
        mock_config.load_kube_config.assert_called_once_with(context="test-context")
        mock_load_secret.assert_not_called()

    @patch("kubernetes_dashboard.kube_client.api_for.cache_clear")
    @patch("kubernetes_dashboard.kube_client.is_running_in_kubernetes")
    @patch("kubernetes_dashboard.kube_client.load_kubeconfig_from_secret")
    @patch("kubernetes_dashboard.kube_client.config")
    def test_api_for_k8s_env_with_secret(
        self, mock_config, mock_load_secret, mock_is_k8s, _
    ):
        """Test api_for function in Kubernetes environment with secret."""
        # Kubernetes 환경 시뮬레이션
        mock_is_k8s.return_value = True
        mock_load_secret.return_value = "/tmp/kubeconfig"

        # 함수 호출
        api_for("test-context")

        # Secret에서 kubeconfig 로드 확인
        mock_load_secret.assert_called_once()
        mock_config.load_kube_config.assert_called_once_with(
            config_file="/tmp/kubeconfig", context="test-context"
        )

    @patch("kubernetes_dashboard.kube_client.api_for.cache_clear")
    @patch("kubernetes_dashboard.kube_client.is_running_in_kubernetes")
    @patch("kubernetes_dashboard.kube_client.load_kubeconfig_from_secret")
    @patch("kubernetes_dashboard.kube_client.config")
    def test_api_for_k8s_env_without_secret(
        self, mock_config, mock_load_secret, mock_is_k8s, _
    ):
        """Test api_for function in Kubernetes environment without secret."""
        # Kubernetes 환경 시뮬레이션 (Secret 없음)
        mock_is_k8s.return_value = True
        mock_load_secret.return_value = None

        # 함수 호출
        api_for("test-context")

        # Secret 로드 실패 시 기본 kubeconfig 사용 확인
        mock_load_secret.assert_called_once()
        mock_config.load_kube_config.assert_called_once_with(context="test-context")

    @patch("os.path.exists")
    def test_is_running_in_kubernetes(self, mock_exists):
        """Test is_running_in_kubernetes function."""
        # Kubernetes 환경 시뮬레이션
        mock_exists.return_value = True
        self.assertTrue(is_running_in_kubernetes())

        # 로컬 환경 시뮬레이션
        mock_exists.return_value = False
        self.assertFalse(is_running_in_kubernetes())

    @patch("kubernetes_dashboard.kube_client.config")
    @patch("kubernetes_dashboard.kube_client.client")
    @patch("kubernetes_dashboard.kube_client.base64")
    @patch("kubernetes_dashboard.kube_client.open")
    def test_load_kubeconfig_from_secret(
        self, mock_open, mock_base64, mock_client, mock_config
    ):
        """Test load_kubeconfig_from_secret function."""
        # Mock 설정
        mock_v1 = MagicMock()
        mock_client.CoreV1Api.return_value = mock_v1

        mock_secret = MagicMock()
        mock_secret.data = {"kubeconfig": "encoded_data"}
        mock_v1.read_namespaced_secret.return_value = mock_secret

        mock_base64.b64decode.return_value = b"kubeconfig_data"

        # 임시 파일 경로 시뮬레이션
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch(
                "kubernetes_dashboard.kube_client.tempfile.gettempdir",
                return_value=temp_dir,
            ):
                result = load_kubeconfig_from_secret("test-secret", "test-namespace")

                # 함수 호출 확인
                mock_config.load_incluster_config.assert_called_once()
                mock_v1.read_namespaced_secret.assert_called_once_with(
                    "test-secret", "test-namespace"
                )
                mock_base64.b64decode.assert_called_once_with("encoded_data")

                # 결과 확인
                self.assertEqual(result, f"{temp_dir}/kubeconfig")
                mock_open.assert_called_once()


if __name__ == "__main__":
    unittest.main()

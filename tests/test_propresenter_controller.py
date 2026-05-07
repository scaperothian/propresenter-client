"""
Unit tests for ProPresenterController
"""

import pytest
from unittest.mock import patch, MagicMock
from propresenter_slides.main import ProPresenterController


class TestProPresenterController:
    """Test suite for ProPresenterController"""

    @pytest.fixture
    def controller(self):
        """Create a controller instance for testing"""
        return ProPresenterController(host="localhost", port=1025, timeout=5)

    def test_controller_initialization(self):
        """Test that controller initializes with correct parameters"""
        controller = ProPresenterController(host="test.host", port=9999, timeout=10)
        assert controller.host == "test.host"
        assert controller.port == 9999
        assert controller.timeout == 10
        assert controller.base_url == "http://test.host:9999"

    def test_controller_default_parameters(self):
        """Test that controller uses correct default parameters"""
        controller = ProPresenterController()
        assert controller.host == "localhost"
        assert controller.port == 1025
        assert controller.timeout == 5
        assert controller.base_url == "http://localhost:1025"

    @patch("propresenter_slides.main.requests.request")
    def test_get_status_success(self, mock_request, controller):
        """Test successful status retrieval"""
        mock_response = MagicMock()
        mock_response.text = '{"currentSlide": 0}'
        mock_response.json.return_value = {"currentSlide": 0}
        mock_request.return_value = mock_response

        result = controller.get_status()

        assert result == {"currentSlide": 0}
        mock_request.assert_called_once_with(
            "GET",
            "http://localhost:1025/v1/status/slide",
            timeout=5
        )

    @patch("propresenter_slides.main.requests.request")
    def test_next_slide_success(self, mock_request, controller):
        """Test successful next slide trigger"""
        mock_response = MagicMock()
        mock_response.text = ""
        mock_response.json.side_effect = ValueError()  # Empty response
        mock_request.return_value = mock_response

        result = controller.next_slide()

        assert result is True
        mock_request.assert_called_once_with(
            "GET",
            "http://localhost:1025/v1/presentation/active/next/trigger",
            timeout=5
        )

    @patch("propresenter_slides.main.requests.request")
    def test_previous_slide_success(self, mock_request, controller):
        """Test successful previous slide trigger"""
        mock_response = MagicMock()
        mock_response.text = ""
        mock_response.json.side_effect = ValueError()  # Empty response
        mock_request.return_value = mock_response

        result = controller.previous_slide()

        assert result is True
        mock_request.assert_called_once_with(
            "GET",
            "http://localhost:1025/v1/presentation/active/previous/trigger",
            timeout=5
        )

    @patch("propresenter_slides.main.requests.request")
    def test_go_to_slide_success(self, mock_request, controller):
        """Test successful go to slide"""
        mock_response = MagicMock()
        mock_response.text = ""
        mock_response.json.side_effect = ValueError()  # Empty response
        mock_request.return_value = mock_response

        result = controller.go_to_slide(3)

        assert result is True
        mock_request.assert_called_once_with(
            "GET",
            "http://localhost:1025/v1/presentation/active/3/trigger",
            timeout=5
        )

    @patch("propresenter_slides.main.requests.request")
    def test_request_failure(self, mock_request, controller):
        """Test handling of request failures"""
        import requests
        mock_request.side_effect = requests.RequestException("Connection refused")

        result = controller.get_status()

        assert result is None

    @patch("propresenter_slides.main.requests.request")
    def test_request_with_empty_response(self, mock_request, controller):
        """Test handling of empty responses from trigger endpoints"""
        mock_response = MagicMock()
        mock_response.text = ""
        mock_response.raise_for_status()
        mock_request.return_value = mock_response

        result = controller._request("GET", "v1/presentation/active/next/trigger")

        assert result == {}

    @patch("propresenter_slides.main.requests.request")
    def test_request_with_json_response(self, mock_request, controller):
        """Test handling of JSON responses"""
        mock_response = MagicMock()
        mock_response.text = '{"data": "value"}'
        mock_response.json.return_value = {"data": "value"}
        mock_request.return_value = mock_response

        result = controller._request("GET", "v1/status/slide")

        assert result == {"data": "value"}

    @patch("propresenter_slides.main.requests.request")
    def test_get_active_presentation_success(self, mock_request, controller):
        """Test successful retrieval of active presentation"""
        mock_response = MagicMock()
        mock_response.text = '{"uuid": "123", "name": "Presentation 1"}'
        mock_response.json.return_value = {"uuid": "123", "name": "Presentation 1"}
        mock_request.return_value = mock_response

        result = controller.get_active_presentation()

        assert result == {"uuid": "123", "name": "Presentation 1"}
        mock_request.assert_called_once_with(
            "GET",
            "http://localhost:1025/v1/presentation/active",
            timeout=5
        )

    @patch("propresenter_slides.main.requests.request")
    def test_get_active_playlist_success(self, mock_request, controller):
        """Test successful retrieval of active playlist"""
        mock_response = MagicMock()
        mock_response.text = '{"id": "playlist1", "name": "Main Playlist"}'
        mock_response.json.return_value = {"id": "playlist1", "name": "Main Playlist"}
        mock_request.return_value = mock_response

        result = controller.get_active_playlist()

        assert result == {"id": "playlist1", "name": "Main Playlist"}
        mock_request.assert_called_once_with(
            "GET",
            "http://localhost:1025/v1/playlist/active",
            timeout=5
        )

    @patch("propresenter_slides.main.requests.request")
    def test_ensure_presentation_active_already_active(self, mock_request, controller):
        """Test ensure_presentation_active when presentation is already active"""
        mock_response = MagicMock()
        mock_response.text = '{"uuid": "123", "name": "Presentation 1"}'
        mock_response.json.return_value = {"uuid": "123", "name": "Presentation 1"}
        mock_request.return_value = mock_response

        result = controller.ensure_presentation_active()

        assert result is True
        # Should only call get_active_presentation
        assert mock_request.call_count == 1

    @patch("propresenter_slides.main.requests.request")
    def test_ensure_presentation_active_activates_playlist_first(self, mock_request, controller):
        """Test ensure_presentation_active activates first presentation in active playlist"""
        # First call (get_active_presentation) returns None
        mock_response_none = MagicMock()
        mock_response_none.text = ""
        mock_response_none.json.side_effect = ValueError()

        # Second call (get_active_playlist) returns playlist with presentation
        mock_response_playlist = MagicMock()
        mock_response_playlist.text = '{"presentation": "pres1"}'
        mock_response_playlist.json.return_value = {"presentation": "pres1"}

        # Third call (trigger first presentation) succeeds
        mock_response_success = MagicMock()
        mock_response_success.text = ""
        mock_response_success.raise_for_status()

        mock_request.side_effect = [mock_response_none, mock_response_playlist, mock_response_success]

        result = controller.ensure_presentation_active()

        assert result is True
        assert mock_request.call_count == 3

    @patch("propresenter_slides.main.requests.request")
    def test_ensure_presentation_active_fallback_to_focused(self, mock_request, controller):
        """Test ensure_presentation_active falls back to focused presentation"""
        # First call (get_active_presentation) returns None
        mock_response_none = MagicMock()
        mock_response_none.text = ""
        mock_response_none.json.side_effect = ValueError()

        # Second call (get_active_playlist) returns None
        mock_response_playlist_none = MagicMock()
        mock_response_playlist_none.text = ""
        mock_response_playlist_none.json.side_effect = ValueError()

        # Third call (trigger focused presentation) succeeds
        mock_response_success = MagicMock()
        mock_response_success.text = ""
        mock_response_success.raise_for_status()

        mock_request.side_effect = [mock_response_none, mock_response_playlist_none, mock_response_success]

        result = controller.ensure_presentation_active()

        assert result is True
        assert mock_request.call_count == 3

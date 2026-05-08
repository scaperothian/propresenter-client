"""
Unit tests for ProPresenterController
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from propresenter_slides.main import ProPresenterController, interactive_prompt, load_config_file


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
            "http://localhost:1025/v1/presentation/active/2/trigger",
            timeout=5
        )

    @patch("propresenter_slides.main.requests.request")
    def test_go_to_slide_first_slide_success(self, mock_request, controller):
        """Test first slide uses API index 0 when given 1"""
        mock_response = MagicMock()
        mock_response.text = ""
        mock_response.json.side_effect = ValueError()  # Empty response
        mock_request.return_value = mock_response

        result = controller.go_to_slide(1)

        assert result is True
        mock_request.assert_called_once_with(
            "GET",
            "http://localhost:1025/v1/presentation/active/0/trigger",
            timeout=5
        )

    def test_get_slide_position_returns_1_indexed(self, controller):
        """Test slide position is returned in 1-indexed form"""
        controller.get_status = MagicMock(return_value={"currentSlide": 2, "slideCount": 3})

        assert controller.get_slide_position() == (3, 3)

    @patch("builtins.input", side_effect=["n", "q"])
    @patch("builtins.print")
    def test_interactive_prompt_next_at_last_slide(self, mock_print, mock_input, controller):
        """Test that 'n' at last slide does not move forward"""
        controller.get_status = MagicMock(return_value={"currentSlide": 2, "slideCount": 3})
        controller.next_slide = MagicMock(return_value=True)

        interactive_prompt(controller)

        mock_print.assert_any_call("Cannot go beyond the last slide. Prompt attempted to go beyond the last slide.")
        controller.next_slide.assert_not_called()

    @patch("builtins.input", side_effect=["b", "q"])
    @patch("builtins.print")
    def test_interactive_prompt_previous_at_first_slide(self, mock_print, mock_input, controller):
        """Test that 'b' at first slide does not move backward"""
        controller.get_status = MagicMock(return_value={"currentSlide": 0, "slideCount": 3})
        controller.previous_slide = MagicMock(return_value=True)

        interactive_prompt(controller)

        mock_print.assert_any_call("Cannot go before the first slide. Prompt attempted to go beyond the first slide.")
        controller.previous_slide.assert_not_called()

    @patch("builtins.input", side_effect=["5", "q"])
    @patch("builtins.print")
    def test_interactive_prompt_number_beyond_last_slide(self, mock_print, mock_input, controller):
        """Test a numeric slide request beyond the last slide is blocked"""
        controller.get_status = MagicMock(return_value={"currentSlide": 1, "slideCount": 3})
        controller.go_to_slide = MagicMock(return_value=True)

        interactive_prompt(controller)

        mock_print.assert_any_call("Cannot go beyond the last slide. Prompt attempted to go beyond the last slide.")
        controller.go_to_slide.assert_not_called()

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
    def test_get_library_default_success(self, mock_request, controller):
        """Test successful retrieval of Default library contents"""
        mock_response = MagicMock()
        mock_response.text = '{"items": [{"uuid": "abc", "name": "Hello World"}]}'
        mock_response.json.return_value = {"items": [{"uuid": "abc", "name": "Hello World"}]}
        mock_request.return_value = mock_response

        result = controller.get_library_default()

        assert result == {"items": [{"uuid": "abc", "name": "Hello World"}]}
        mock_request.assert_called_once_with(
            "GET",
            "http://localhost:1025/v1/library/Default",
            timeout=5
        )

    def test_find_presentation_uuid_by_name(self, controller):
        """Test presentation lookup in Default library response"""
        library_data = {
            "items": [
                {"uuid": "123", "name": "The Great Song"},
                {"uuid": "456", "name": "Another Track"}
            ]
        }

        result = controller.find_presentation_uuid_by_name("great", library_data)

        assert result == "123"

    def test_find_presentation_uuid_by_name_returns_none(self, controller):
        """Test missing presentation lookup returns None"""
        library_data = {
            "items": [
                {"uuid": "123", "name": "The Great Song"}
            ]
        }

        result = controller.find_presentation_uuid_by_name("missing", library_data)

        assert result is None

    @patch("propresenter_slides.main.requests.request")
    def test_activate_presentation_success(self, mock_request, controller):
        """Test successful presentation activation by UUID"""
        mock_response = MagicMock()
        mock_response.text = ""
        mock_response.json.side_effect = ValueError()
        mock_request.return_value = mock_response

        result = controller.activate_presentation("123")

        assert result is True
        mock_request.assert_called_once_with(
            "GET",
            "http://localhost:1025/v1/presentation/123/trigger",
            timeout=5
        )

    @patch("propresenter_slides.main.requests.request")
    def test_activate_first_playlist_presentation_success(self, mock_request, controller):
        """Test successful activation of first playlist presentation"""
        mock_response = MagicMock()
        mock_response.text = ""
        mock_response.json.side_effect = ValueError()
        mock_request.return_value = mock_response

        result = controller.activate_first_playlist_presentation("Service")

        assert result is True
        mock_request.assert_called_once_with(
            "GET",
            "http://localhost:1025/v1/playlist/Service/0/trigger",
            timeout=5
        )

    @patch("propresenter_slides.main.requests.request")
    def test_get_library_success(self, mock_request, controller):
        """Test successful retrieval of a named library"""
        mock_response = MagicMock()
        mock_response.text = '{"items": [{"uuid": "abc", "name": "Hello World"}]}'
        mock_response.json.return_value = {"items": [{"uuid": "abc", "name": "Hello World"}]}
        mock_request.return_value = mock_response

        result = controller.get_library("Default")

        assert result == {"items": [{"uuid": "abc", "name": "Hello World"}]}
        mock_request.assert_called_once_with(
            "GET",
            "http://localhost:1025/v1/library/Default",
            timeout=5
        )

    def test_load_config_file_reads_yaml(self, tmp_path):
        """Test that YAML config values load from presentation.config"""
        config_file = tmp_path / "presentation.config"
        config_file.write_text(
            "host: config.local\nport: 1234\nlibrary: MyLibrary\nplaylist: MyPlaylist\nlog-level: INFO\n"
        )

        config = load_config_file(config_file)

        assert config == {
            "host": "config.local",
            "port": 1234,
            "library": "MyLibrary",
            "playlist": "MyPlaylist",
            "log-level": "INFO"
        }

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

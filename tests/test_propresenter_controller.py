"""
Unit tests for ProPresenterController
"""

import pytest
from unittest.mock import patch, MagicMock
from propresenter_client.main import ProPresenterController, interactive_prompt


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

    @patch("propresenter_client.main.requests.request")
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

    @patch("propresenter_client.main.requests.request")
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

    @patch("propresenter_client.main.requests.request")
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

    @patch("propresenter_client.main.requests.request")
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

    @patch("propresenter_client.main.requests.request")
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

    @patch("propresenter_client.main.requests.request")
    def test_request_failure(self, mock_request, controller):
        """Test handling of request failures"""
        import requests
        mock_request.side_effect = requests.RequestException("Connection refused")

        result = controller.get_status()

        assert result is None

    @patch("propresenter_client.main.requests.request")
    def test_request_with_empty_response(self, mock_request, controller):
        """Test handling of empty responses from trigger endpoints"""
        mock_response = MagicMock()
        mock_response.text = ""
        mock_response.raise_for_status()
        mock_request.return_value = mock_response

        result = controller._request("GET", "v1/presentation/active/next/trigger")

        assert result == {}

    @patch("propresenter_client.main.requests.request")
    def test_request_with_json_response(self, mock_request, controller):
        """Test handling of JSON responses"""
        mock_response = MagicMock()
        mock_response.text = '{"data": "value"}'
        mock_response.json.return_value = {"data": "value"}
        mock_request.return_value = mock_response

        result = controller._request("GET", "v1/status/slide")

        assert result == {"data": "value"}

    @patch("propresenter_client.main.requests.request")
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

    @patch("propresenter_client.main.requests.request")
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

    @patch("propresenter_client.main.requests.request")
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

    @patch("propresenter_client.main.requests.request")
    def test_activate_first_library_presentation_success(self, mock_request, controller):
        """Test successful activation of first library presentation"""
        mock_response = MagicMock()
        mock_response.text = ""
        mock_response.json.side_effect = ValueError()
        mock_request.return_value = mock_response

        result = controller.activate_first_library_presentation("Default")

        assert result is True
        mock_request.assert_called_once_with(
            "GET",
            "http://localhost:1025/v1/library/Default/0/trigger",
            timeout=5
        )

    @patch("propresenter_client.main.requests.request")
    def test_get_presentation_details_success(self, mock_request, controller):
        """Test successful retrieval of presentation details by UUID"""
        mock_response = MagicMock()
        mock_response.text = '{"uuid": "7A465FF0-FF42-4785-82F1-5CF0DC136BAE", "name": "Mary Long"}'
        mock_response.json.return_value = {"uuid": "7A465FF0-FF42-4785-82F1-5CF0DC136BAE", "name": "Mary Long"}
        mock_request.return_value = mock_response

        result = controller.get_presentation_details("7A465FF0-FF42-4785-82F1-5CF0DC136BAE")

        assert result == {"uuid": "7A465FF0-FF42-4785-82F1-5CF0DC136BAE", "name": "Mary Long"}
        mock_request.assert_called_once_with(
            "GET",
            "http://localhost:1025/v1/presentation/7A465FF0-FF42-4785-82F1-5CF0DC136BAE",
            timeout=5
        )

    @patch("propresenter_client.main.requests.request")
    def test_get_presentation_details_failure(self, mock_request, controller):
        """Test failed retrieval of presentation details returns None"""
        import requests
        mock_request.side_effect = requests.RequestException("Connection refused")

        result = controller.get_presentation_details("7A465FF0-FF42-4785-82F1-5CF0DC136BAE")

        assert result is None

    @patch("propresenter_client.main.requests.request")
    def test_get_slide_index_integer_response(self, mock_request, controller):
        """Test slide index when API returns a bare integer"""
        mock_response = MagicMock()
        mock_response.text = "2"
        mock_response.json.return_value = 2
        mock_request.return_value = mock_response

        result = controller.get_slide_index()

        assert result == 2
        mock_request.assert_called_once_with(
            "GET",
            "http://localhost:1025/v1/presentation/slide_index",
            timeout=5,
            params={"chunked": "false"},
        )

    @patch("propresenter_client.main.requests.request")
    def test_get_slide_index_dict_response(self, mock_request, controller):
        """Test slide index when API returns a dict with slideIndex key"""
        mock_response = MagicMock()
        mock_response.text = '{"slideIndex": 3}'
        mock_response.json.return_value = {"slideIndex": 3}
        mock_request.return_value = mock_response

        result = controller.get_slide_index()

        assert result == 3

    @patch("propresenter_client.main.requests.request")
    def test_get_slide_index_presentation_index_shape(self, mock_request, controller):
        """Test slide index from PP7 presentation_index response shape"""
        payload = {
            "presentation_index": {
                "index": 2,
                "presentation_id": {
                    "uuid": "7A465FF0-FF42-4785-82F1-5CF0DC136BAE",
                    "name": "The Pledge",
                    "index": 19,
                },
            }
        }
        mock_response = MagicMock()
        mock_response.text = str(payload)
        mock_response.json.return_value = payload
        mock_request.return_value = mock_response

        result = controller.get_slide_index()

        assert result == 2

    @patch("propresenter_client.main.requests.request")
    def test_get_slide_index_failure(self, mock_request, controller):
        """Test slide index returns None on request failure"""
        import requests
        mock_request.side_effect = requests.RequestException("Connection refused")

        result = controller.get_slide_index()

        assert result is None

    @patch("propresenter_client.main.requests.request")
    def test_get_slide_index_chunked(self, mock_request, controller):
        """Test slide index passes chunked=true when requested"""
        mock_response = MagicMock()
        mock_response.text = "1"
        mock_response.json.return_value = 1
        mock_request.return_value = mock_response

        controller.get_slide_index(chunked=True)

        mock_request.assert_called_once_with(
            "GET",
            "http://localhost:1025/v1/presentation/slide_index",
            timeout=5,
            params={"chunked": "true"},
        )

    @patch("propresenter_client.main.requests.request")
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


class TestFindSlides:
    """Tests for ProPresenterController.find_slides — multi-group flattening."""

    def test_single_group_returns_all_slides(self):
        details = {"presentation": {"groups": [{"slides": [{"text": "a"}, {"text": "b"}]}]}}
        result = ProPresenterController.find_slides(details)
        assert result == [{"text": "a"}, {"text": "b"}]

    def test_multiple_groups_are_flattened(self):
        details = {
            "presentation": {
                "groups": [
                    {"slides": [{"text": "verse 1"}]},
                    {"slides": [{"text": "verse 2"}, {"text": "verse 3"}]},
                ]
            }
        }
        result = ProPresenterController.find_slides(details)
        assert result == [{"text": "verse 1"}, {"text": "verse 2"}, {"text": "verse 3"}]

    def test_first_group_empty_text_still_finds_later_groups(self):
        details = {
            "presentation": {
                "groups": [
                    {"slides": [{"text": ""}]},          # title/image slide
                    {"slides": [{"text": "Mary long"}]}, # content slide
                ]
            }
        }
        result = ProPresenterController.find_slides(details)
        assert len(result) == 2
        assert result[1]["text"] == "Mary long"

    def test_returns_empty_list_when_no_slides(self):
        assert ProPresenterController.find_slides({}) == []
        assert ProPresenterController.find_slides([]) == []

    def test_flat_slides_key_at_top(self):
        details = {"slides": [{"text": "only slide"}]}
        result = ProPresenterController.find_slides(details)
        assert result == [{"text": "only slide"}]

    def test_non_dict_non_list_returns_empty(self):
        assert ProPresenterController.find_slides("not a dict") == []
        assert ProPresenterController.find_slides(42) == []

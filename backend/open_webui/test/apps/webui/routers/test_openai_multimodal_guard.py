from open_webui.routers.openai import is_vision_model_id, payload_has_image_input


def test_payload_has_image_input_for_message_part():
    payload = {
        'messages': [
            {
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': 'Что на картинке?'},
                    {'type': 'image_url', 'image_url': {'url': 'https://example.com/cat.png'}},
                ],
            }
        ]
    }

    assert payload_has_image_input(payload) is True


def test_payload_has_image_input_for_file_attachment():
    payload = {'messages': [{'role': 'user', 'content': 'Что на картинке?'}]}
    metadata = {'files': [{'id': 'img-1', 'type': 'image', 'content_type': 'image/png'}]}

    assert payload_has_image_input(payload, metadata) is True


def test_is_vision_model_id_detects_vl_models():
    assert is_vision_model_id('qwen2.5-vl') is True
    assert is_vision_model_id('cotype-pro-vl-32b') is True
    assert is_vision_model_id('mws-gpt-alpha') is False

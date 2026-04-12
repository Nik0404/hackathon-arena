from open_webui.utils.middleware import (
    detect_auto_route,
    score_model_for_auto_route,
    select_auto_route_model,
)


def test_detect_auto_route_image_generation_intent_sets_feature():
    form_data = {
        'messages': [{'role': 'user', 'content': 'Нарисуй постер для хакатона в стиле retro-future'}],
    }
    metadata = {}

    route = detect_auto_route(form_data, metadata)

    assert route['route'] == 'image_generation'
    assert route['reason'] == 'image_generation_intent'
    assert form_data['features']['image_generation'] is True


def test_detect_auto_route_switches_to_vision_for_image_input():
    form_data = {
        'messages': [
            {
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': 'Что изображено на этой картинке?'},
                    {'type': 'image_url', 'image_url': {'url': 'https://example.com/cat.png'}},
                ],
            }
        ],
    }
    metadata = {}

    route = detect_auto_route(form_data, metadata)

    assert route['route'] == 'vision'
    assert route['reason'] == 'image_input'


def test_detect_auto_route_switches_to_vision_for_image_file_attachment():
    form_data = {
        'messages': [{'role': 'user', 'content': 'Что на этой картинке?'}],
        'files': [{'id': 'img-1', 'type': 'image', 'name': 'cat.png', 'content_type': 'image/png'}],
    }
    metadata = {}

    route = detect_auto_route(form_data, metadata)

    assert route['route'] == 'vision'
    assert route['reason'] == 'image_input'


def test_detect_auto_route_switches_to_files_for_file_input():
    form_data = {
        'messages': [{'role': 'user', 'content': 'Сделай краткое summary по вложенному PDF'}],
        'files': [{'id': 'file-1', 'type': 'file', 'name': 'brief.pdf', 'content_type': 'application/pdf'}],
    }
    metadata = {}

    route = detect_auto_route(form_data, metadata)

    assert route['route'] == 'files'
    assert route['reason'] == 'file_input'


def test_detect_auto_route_enables_web_search_for_url():
    form_data = {
        'messages': [{'role': 'user', 'content': 'Изучи эту ссылку и найди ключевые факты: https://example.com'}],
    }
    metadata = {}

    route = detect_auto_route(form_data, metadata)

    assert route['route'] == 'web'
    assert route['reason'] == 'url_in_message'
    assert form_data['features']['web_search'] is True


def test_select_auto_route_model_prefers_vision_candidate():
    models = {
        'text-model': {
            'id': 'text-model',
            'name': 'Text Pro',
            'owned_by': 'openai',
            'info': {'meta': {'capabilities': {'file_context': True}}},
        },
        'vision-model': {
            'id': 'qwen-vl',
            'name': 'Qwen VL',
            'owned_by': 'openai',
            'info': {'meta': {'capabilities': {'file_context': True}}},
        },
    }

    selected_model_id = select_auto_route_model(models, ['text-model', 'vision-model'], 'vision', 'text-model')

    assert selected_model_id == 'vision-model'


def test_score_model_for_auto_route_prefers_web_capability():
    web_model = {
        'id': 'research-model',
        'name': 'Research Assistant',
        'owned_by': 'openai',
        'info': {'meta': {'capabilities': {'web_search': True}}},
    }
    plain_model = {
        'id': 'plain-model',
        'name': 'Plain Chat',
        'owned_by': 'openai',
        'info': {'meta': {'capabilities': {}}},
    }

    assert score_model_for_auto_route(web_model, 'web') > score_model_for_auto_route(plain_model, 'web')



def test_get_timelines():
    # it overrides defaults with custom params:
    default_params = {"count": 200}
    request_params = {"count": 1}
    request_params = {**default_params, **request_params}
    assert request_params["count"] == 1

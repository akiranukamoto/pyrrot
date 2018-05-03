import os

import pytest

import main


@pytest.fixture
def client():
    def make_client(path):
        app = main.create_app(debug=True)
        main._read_configs(app, path)
        return app.test_client()

    yield make_client


@pytest.fixture
def url_example_example():
    return os.path.join(os.path.dirname(__file__), "../examples/example.yaml")


@pytest.fixture
def url_example_header():
    return os.path.join(os.path.dirname(__file__), "../examples/example_header.yaml")


@pytest.fixture
def url_example_body():
    return os.path.join(os.path.dirname(__file__), "../examples/example_body.yaml")


@pytest.fixture
def url_example_query():
    return os.path.join(os.path.dirname(__file__), "../examples/example_query.yaml")


@pytest.fixture
def url_example_path():
    return os.path.join(os.path.dirname(__file__), "../examples/example_path.yaml")

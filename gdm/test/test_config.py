"""Unit tests for the `config` module."""
# pylint: disable=no-self-use,redefined-outer-name

import pytest

from gdm.config import Config, load

from .conftest import FILES


class TestConfig:

    def test_init_defaults(self):
        """Verify a configuration has a default filename and location."""
        config = Config('mock/root')

        assert 'mock/root' == config.root
        assert 'gdm.yml' == config.filename
        assert 'gdm_sources' == config.location
        assert [] == config.sources

    def test_init_filename(self):
        """Verify the filename can be customized."""
        config = Config('mock/root', 'mock.custom')

        assert 'mock.custom' == config.filename
        assert 'gdm_sources' == config.location

    def test_init_location(self):
        """Verify the location can be customized."""
        config = Config('mock/root', location='.gdm')

        assert 'gdm.yml' == config.filename
        assert '.gdm' == config.location

    def test_path(self):
        """Verify a configuration's path is correct."""
        config = Config('mock/root')

        assert "mock/root/gdm.yml" == config.path

    @pytest.mark.integration
    def test_install_and_list(self):
        """Verify the correct dependencies are installed."""
        config = Config(FILES)

        count = config.install_deps()
        assert 7 == count

        deps = list(config.get_deps())
        assert 7 == len(deps)
        assert 'https://github.com/jacebrowning/gdm-demo' == deps[0][1]
        assert 'eb37743011a398b208dd9f9ef79a408c0fc10d48' == deps[0][2]
        assert 'https://github.com/jacebrowning/gdm-demo' == deps[1][1]
        assert 'ddbe17ef173538d1fda29bd99a14bab3c5d86e78' == deps[1][2]
        assert 'https://github.com/jacebrowning/gdm-demo' == deps[2][1]
        assert 'fb693447579235391a45ca170959b5583c5042d8' == deps[2][2]
        assert 'https://github.com/jacebrowning/gdm-demo' == deps[3][1]
        # master branch always changes --------------------- deps[3][2]
        assert 'https://github.com/jacebrowning/gdm-demo' == deps[4][1]
        # master branch always changes --------------------- deps[4][2]
        assert 'https://github.com/jacebrowning/gdm-demo' == deps[5][1]
        assert '7bd138fe7359561a8c2ff9d195dff238794ccc04' == deps[5][2]
        assert 'https://github.com/jacebrowning/gdm-demo' == deps[6][1]
        assert '2da24fca34af3748e3cab61db81a2ae8b35aec94' == deps[6][2]


class TestLoad:

    def test_load_from_directory_with_config_file(self):
        config = load(FILES)

        assert None is not config

    def test_load_from_directory_without_config_file(self, tmpdir):
        tmpdir.chdir()

        config = load()

        assert None is config

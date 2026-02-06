"""Tests for generator.config.validate_config."""

import copy

import pytest

from generator.config import ConfigError, validate_config


class TestValidateConfig:
    def test_valid_config_passes(self, sample_config):
        result = validate_config(copy.deepcopy(sample_config))
        assert result["username"] == "galaxy-dev"
        assert result["profile"]["name"] == "Nyx Orion"

    def test_username_required(self, sample_config):
        cfg = copy.deepcopy(sample_config)
        del cfg["username"]
        with pytest.raises(ConfigError, match="username"):
            validate_config(cfg)

    def test_username_empty_string(self, sample_config):
        cfg = copy.deepcopy(sample_config)
        cfg["username"] = "   "
        with pytest.raises(ConfigError, match="username"):
            validate_config(cfg)

    def test_profile_name_required(self, sample_config):
        cfg = copy.deepcopy(sample_config)
        cfg["profile"]["name"] = ""
        with pytest.raises(ConfigError, match="profile.name"):
            validate_config(cfg)

    def test_galaxy_arms_must_be_nonempty_list(self, sample_config):
        cfg = copy.deepcopy(sample_config)
        cfg["galaxy_arms"] = []
        with pytest.raises(ConfigError, match="galaxy_arms"):
            validate_config(cfg)

    def test_galaxy_arm_without_name(self, sample_config):
        cfg = copy.deepcopy(sample_config)
        cfg["galaxy_arms"] = [{"color": "synapse_cyan"}]
        with pytest.raises(ConfigError, match="name is required"):
            validate_config(cfg)

    def test_galaxy_arm_without_color(self, sample_config):
        cfg = copy.deepcopy(sample_config)
        cfg["galaxy_arms"] = [{"name": "Frontend"}]
        with pytest.raises(ConfigError, match="color is required"):
            validate_config(cfg)

    def test_project_arm_index_invalid(self, sample_config):
        cfg = copy.deepcopy(sample_config)
        cfg["projects"] = [{"repo": "user/repo", "arm": 99}]
        with pytest.raises(ConfigError, match="arm must be an integer"):
            validate_config(cfg)

    def test_invalid_hex_color_in_theme(self, sample_config):
        cfg = copy.deepcopy(sample_config)
        cfg["theme"] = {"void": "not-a-color"}
        with pytest.raises(ConfigError, match="valid hex color"):
            validate_config(cfg)

    def test_theme_override_merges_with_defaults(self, sample_config):
        cfg = copy.deepcopy(sample_config)
        cfg["theme"] = {"void": "#112233"}
        result = validate_config(cfg)
        assert result["theme"]["void"] == "#112233"
        assert result["theme"]["synapse_cyan"] == "#00d4ff"  # default preserved

    def test_defaults_applied_for_optional_fields(self, sample_config):
        cfg = copy.deepcopy(sample_config)
        del cfg["stats"]
        del cfg["languages"]
        del cfg["theme"]
        result = validate_config(cfg)
        assert "metrics" in result["stats"]
        assert "exclude" in result["languages"]
        assert "void" in result["theme"]

    def test_config_not_dict_fails(self):
        with pytest.raises(ConfigError, match="dict"):
            validate_config("not a dict")

    def test_config_none_fails(self):
        with pytest.raises(ConfigError, match="dict"):
            validate_config(None)

class ProviderError(Exception):
    """A safe provider-facing failure that can be translated for customers."""


class ProviderConfigurationError(ProviderError):
    """A live provider integration is enabled without its required configuration."""

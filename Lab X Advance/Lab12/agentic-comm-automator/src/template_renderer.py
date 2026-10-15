"""Tiny template renderer: '{placeholder}' / '{value:.2f}' filled from a context dict."""
import string

from .utils import setup_logging

logger = setup_logging(__name__)


class TemplateRenderer:
    """Renders str.format-style templates using a dictionary context."""

    def render(self, template_string, context):
        """Return the rendered string. Raises ValueError if a field is missing/invalid."""
        if template_string is None:
            return ""
        try:
            return string.Formatter().vformat(template_string, (), context)
        except (KeyError, IndexError, AttributeError) as e:
            logger.error(f"Missing/invalid template field {e!r} in template: {template_string!r}")
            raise ValueError(f"Missing/invalid template field: {e}") from e
        except ValueError as e:
            logger.error(f"Bad template format ({e}) in template: {template_string!r}")
            raise

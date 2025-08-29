import json
import os
import html
from typing import Any, Dict, List

from docutils import nodes
from docutils.parsers.rst import Directive, directives


class LecoDataViewerNode(nodes.General, nodes.Element):
    """Custom node for the LECO JSON viewer."""

    pass


def html_visit_leco_data_viewer(self, node) -> None:
    """Visit function for HTML output."""
    # Properly escape the JSON data for HTML attributes
    escaped_data = html.escape(node.attributes["data"], quote=True)
    classes = ",".join(node.attributes["classes"])

    self.body.append(f"<p>{node.attributes['title']}</p>")
    self.body.append(
        f"<div class='{classes}' "
        f"data-sdv='{escaped_data}' "
        f"data-expand={node.attributes['expand']}> </div>"
    )


def html_depart_leco_data_viewer(self, node) -> None:
    """Depart function for HTML output."""
    pass


class LecoDataViewerDirective(Directive):
    """Directive for displaying JSON data with reference resolution."""

    has_content = True
    optional_arguments = 1
    final_argument_whitespace = True

    option_spec = {
        "file": directives.unchanged,
        "data": directives.unchanged,
        "title": directives.unchanged,
        "expand": directives.flag,
    }

    def run(self) -> List[nodes.Node]:
        """Process the directive and return the node."""
        env = self.state.document.settings.env
        data_string = "\n".join(self.content)

        data_expand = True if self.options.get("expand", False) is None else False

        # Process data with reference resolution
        processed_data_string = self.process_data(data_string, env)

        container = nodes.container(classes=["sphinx-data-viewer"])
        data_container = LecoDataViewerNode(classes=["sdv-data"])
        data_container["data"] = processed_data_string
        data_container["expand"] = data_expand
        data_container["title"] = self.options.get("title", "")

        container.append(data_container)

        return [container]

    def process_data(self, data_string: str, env) -> str:
        """Process data by resolving JSON Schema references."""
        from sphinx_ext.json_ref_resolver import JSONRefResolver

        # Handle data from content
        if data_string.strip():
            try:
                data_obj = json.loads(data_string)
                resolved_obj = JSONRefResolver.resolve_refs(data_obj)
                return json.dumps(resolved_obj)
            except json.JSONDecodeError:
                pass

        # Handle data option
        data_option = self.options.get("data", None)
        if data_option and data_option in env.config["data_viewer_data"]:
            data_obj = env.config["data_viewer_data"][data_option]
            resolved_obj = JSONRefResolver.resolve_refs(data_obj)
            return json.dumps(resolved_obj)

        # Handle file option
        file_option = self.options.get("file", None)
        if file_option:
            if not os.path.isabs(file_option):
                source = self.state.document.current_source
                if source:
                    file_dir = os.path.dirname(source)
                    file_option = os.path.join(file_dir, file_option)
            try:
                with open(file_option) as file_obj:
                    data_obj = json.load(file_obj)
                    resolved_obj = JSONRefResolver.resolve_refs(data_obj)
                    return json.dumps(resolved_obj)
            except (IOError, json.JSONDecodeError):
                pass

        # Return original data if processing failed
        return data_string


def setup(app) -> Dict[str, Any]:
    """Setup function for the Sphinx extension."""
    app.add_node(
        LecoDataViewerNode,
        html=(html_visit_leco_data_viewer, html_depart_leco_data_viewer),
    )
    app.add_directive("leco-json-viewer", LecoDataViewerDirective)

    return {
        "version": "0.1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }

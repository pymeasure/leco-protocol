from typing import Any


class JSONRefResolver:
    """Utility class for resolving JSON Schema $ref references."""

    @staticmethod
    def resolve_refs(obj: Any, root: Any = None) -> Any:
        """
        Resolve JSON Schema $ref references in an object.

        Args:
            obj: The object to resolve references in
            root: The root object for resolving references (defaults to obj)

        Returns:
            Object with all $ref references resolved
        """
        if root is None:
            root = obj

        if isinstance(obj, list):
            return [JSONRefResolver.resolve_refs(item, root) for item in obj]
        elif isinstance(obj, dict):
            # Check if this is a reference
            if (
                "$ref" in obj
                and isinstance(obj["$ref"], str)
                and obj["$ref"].startswith("#/")
            ):
                # Resolve internal reference
                path = obj["$ref"][2:].split("/")
                target = root
                for segment in path:
                    if isinstance(target, dict) and segment in target:
                        target = target[segment]
                    else:
                        # Reference not found, return original
                        return obj
                # Recursively resolve references in the resolved object
                return JSONRefResolver.resolve_refs(target, root)
            else:
                # Recursively process all properties
                return {
                    key: JSONRefResolver.resolve_refs(value, root)
                    for key, value in obj.items()
                }
        return obj

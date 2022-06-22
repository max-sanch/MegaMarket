def deep_sort_children(node):
	if node.get("children"):
		node["children"].sort(key=lambda x: x["id"])

		for child in node["children"]:
			deep_sort_children(child)
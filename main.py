from graph.builder import graph


state = {
    "repo_url": input("Repository URL : "),
    "repo_path": None,
    "source_files": [],
    "current_file": None,
    "reviews": [],
}

result = graph.invoke(state)

print()

print("Files Found :")

for file in result["source_files"]:
    print(file)

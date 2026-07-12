from graph.builder import graph


def main():

    print("=" * 60)
    print("               GitInsight AI")
    print("=" * 60)

    repo_url = input("\nGitHub Repository URL : ").strip()

    if not repo_url:
        print("\nRepository URL cannot be empty.")
        return

    initial_state = {
        "repo_url": repo_url,
        "repo_path": None,

        "source_files": [],
        "current_file": None,
        "current_index": 0,

        "chunk_reviews": [],
        "reviews": {},

        "final_review": "",
        "report_path": None,
    }

    try:

        print("\nStarting Repository Analysis...\n")

        result = graph.invoke(initial_state)

        print("\n" + "=" * 60)
        print("Repository Review Completed Successfully!")
        print("=" * 60)

        print(f"\nMarkdown Report : {result['report_path']}")

    except KeyboardInterrupt:

        print("\n\nReview cancelled by user.")

    except Exception as e:

        print("\nRepository Review Failed!")
        print(f"Reason : {e}")


if __name__ == "__main__":
    main()
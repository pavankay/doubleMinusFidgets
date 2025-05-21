import os
import fnmatch
import argparse


def parse_gitignore(gitignore_path):
    if not os.path.exists(gitignore_path):
        return []

    with open(gitignore_path, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]


def should_ignore(path, ignore_patterns, root):
    rel_path = os.path.relpath(path, root)
    return any(fnmatch.fnmatch(rel_path, pattern) for pattern in ignore_patterns) or '.git' in rel_path.split(os.sep)


def generate_directory_tree(root_dir, output_file):
    gitignore_path = os.path.join(root_dir, '.gitignore')
    ignore_patterns = parse_gitignore(gitignore_path)
    ignored_items = []

    def walk(directory, prefix=""):
        filepaths = sorted(os.listdir(directory))
        tree_lines = []
        file_contents = []

        for i, filepath in enumerate(filepaths):
            is_last = i == len(filepaths) - 1
            full_path = os.path.join(directory, filepath)
            rel_path = os.path.relpath(full_path, root_dir)

            if should_ignore(full_path, ignore_patterns, root_dir):
                ignored_items.append(rel_path)
                continue

            if os.path.isdir(full_path):
                tree_lines.append(prefix + ("└── " if is_last else "├── ") + filepath + "/")
                sub_tree, sub_contents = walk(full_path, prefix + ("    " if is_last else "│   "))
                tree_lines.extend(sub_tree)
                file_contents.extend(sub_contents)
            else:
                tree_lines.append(prefix + ("└── " if is_last else "├── ") + filepath)
                if filepath.endswith(('.py', '.html')):
                    file_contents.append(f"\n{'=' * 80}\n{rel_path}\n{'=' * 80}\n")
                    try:
                        with open(full_path, 'r', encoding='utf-8') as file:
                            file_contents.append(file.read())
                    except Exception as e:
                        file_contents.append(f"Error reading file: {str(e)}")
                    file_contents.append(f"\n{'=' * 80}\n")

        return tree_lines, file_contents

    if os.path.exists(output_file):
        print(f"Warning: {output_file} already exists and will be overwritten.")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"{root_dir}/\n")
        tree, contents = walk(root_dir)
        for line in tree:
            f.write(line + "\n")
        for content in contents:
            f.write(content + "\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("Ignored files and folders:\n")
        for item in ignored_items:
            f.write(f"- {item}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a directory tree with file contents')
    parser.add_argument('-d', '--directory',
                        default=os.getcwd(),
                        help='Directory to analyze (default: current working directory)')
    parser.add_argument('-o', '--output',
                        default="directory_tree.txt",
                        help='Output file name (default: directory_tree.txt)')

    args = parser.parse_args()

    generate_directory_tree(args.directory, args.output)
    print(f"Directory tree and file contents have been written to {args.output}")

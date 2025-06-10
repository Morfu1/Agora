import os
import frontmatter
import markdown
from datetime import datetime

def get_post_slug(filename):
    """
    Generates a slug from a filename.
    e.g., 'sample-post.md' -> 'sample-post'
    """
    return os.path.splitext(os.path.basename(filename))[0]

def parse_blog_post(file_path):
    """
    Parses a single blog post file.

    Args:
        file_path (str): The full path to the .md file.

    Returns:
        dict: A dictionary containing metadata, HTML content, slug, and TOC,
              or None if parsing fails.
    """
    try:
        post = frontmatter.load(file_path)

        if isinstance(post.metadata.get('date'), str):
            try:
                post.metadata['date'] = datetime.strptime(post.metadata['date'], "%B %d, %Y")
            except ValueError:
                print(f"Warning: Could not parse date string '{post.metadata['date']}' in {file_path}. Leaving as string.")

        md_parser = markdown.Markdown(extensions=['toc', 'fenced_code', 'tables', 'extra'])
        html_content = md_parser.convert(post.content)
        toc_html = getattr(md_parser, 'toc', '')

        return {
            'metadata': post.metadata,
            'html_content': html_content,
            'slug': get_post_slug(file_path),
            'toc': toc_html
        }
    except Exception as e:
        print(f"Error parsing blog post {file_path}: {e}")
        return None

def get_all_blog_posts(posts_dir='blog_posts'):
    """
    Scans a directory for .md files, parses them, and returns a list of posts.

    Args:
        posts_dir (str): The directory containing markdown blog posts.

    Returns:
        list: A list of parsed post dictionaries.
    """
    all_posts = []
    if not os.path.isdir(posts_dir):
        print(f"Warning: Blog posts directory '{posts_dir}' not found.")
        return all_posts

    for filename in os.listdir(posts_dir):
        if filename.endswith('.md'):
            file_path = os.path.join(posts_dir, filename)
            parsed_post = parse_blog_post(file_path)
            if parsed_post:
                all_posts.append(parsed_post)

    try:
        all_posts.sort(key=lambda p: p['metadata'].get('date', datetime.min) if isinstance(p['metadata'].get('date'), datetime) else datetime.min, reverse=True)
    except Exception as e:
        print(f"Warning: Could not sort posts by date due to an error: {e}. Posts will be unsorted.")

    return all_posts

def get_post_by_slug(slug, posts_dir='blog_posts'):
    """
    Finds a single blog post by its slug.

    Args:
        slug (str): The slug of the post to find.
        posts_dir (str): The directory containing markdown blog posts.

    Returns:
        dict: The parsed post dictionary if found, otherwise None.
    """
    # A more optimized version might avoid calling get_all_blog_posts()
    # if performance becomes an issue, e.g., by directly looking for slug.md.
    # However, for a small number of posts, this is acceptable.
    # posts = get_all_blog_posts(posts_dir) # This would re-parse all files
    # for post in posts:
    #     if post['slug'] == slug:
    #         return post
    # return None

    # More direct approach:
    expected_filename = f"{slug}.md"
    file_path = os.path.join(posts_dir, expected_filename)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return parse_blog_post(file_path)
    return None


if __name__ == '__main__':
    print("--- Testing blog_utils.py ---")

    posts = get_all_blog_posts()

    print(f"\nFound {len(posts)} post(s).")

    if posts:
        first_post = posts[0]
        print("\n--- Data for the first post (from get_all_blog_posts) ---")
        print(f"Title: {first_post['metadata'].get('title')}")
        print(f"Slug: {first_post['slug']}")
        print(f"Date: {first_post['metadata'].get('date')}")

        toc_preview = first_post.get('toc', '')
        if isinstance(toc_preview, str):
            toc_preview = (toc_preview[:200] + '...') if len(toc_preview) > 200 else toc_preview
        print(f"\nTable of Contents HTML (Preview):\n{toc_preview}")

        html_preview = first_post.get('html_content', '')
        if isinstance(html_preview, str):
            html_preview = (html_preview[:300] + '...') if len(html_preview) > 300 else html_preview
        print(f"\nHTML Content (Preview):\n{html_preview}")

        print("\n--- Testing get_post_by_slug ---")
        if first_post:
            slug_to_test = first_post['slug']
            print(f"Attempting to fetch post with slug: '{slug_to_test}'")
            single_post = get_post_by_slug(slug_to_test)
            if single_post:
                print(f"Successfully fetched post: {single_post['metadata'].get('title')}")
                assert single_post['slug'] == slug_to_test
            else:
                print(f"Error: Could not fetch post with slug: '{slug_to_test}'")

        print("\nAttempting to fetch non-existent post with slug: 'non-existent-slug'")
        non_existent_single_post = get_post_by_slug('non-existent-slug')
        if non_existent_single_post is None:
            print("Correctly returned None for a non-existent slug.")
        else:
            print(f"Error: Expected None for non-existent slug, but got: {non_existent_single_post}")


    print("\n--- Testing with a non-existent directory (get_all_blog_posts) ---")
    non_existent_posts = get_all_blog_posts(posts_dir='non_existent_blog_dir')
    print(f"Found {len(non_existent_posts)} post(s) in non_existent_blog_dir.")

    print("\n--- End of blog_utils.py test ---")

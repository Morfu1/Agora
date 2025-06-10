## Blog Management

To add a new blog post to the website, follow these steps:

1.  **Create a new Markdown file** (with a `.md` extension) in the `blog_posts` directory (located in the root of the project). For example, `my-new-post.md`. The filename (without the extension) will be used to generate the URL slug for the post (e.g., `/blog/my-new-post`).

2.  **Add Frontmatter:** At the very beginning of your Markdown file, include a YAML frontmatter block enclosed by triple-dashed lines (`---`). This block contains metadata for your post. Here's an example of the required and recommended fields:

    ```yaml
    ---
    title: "Your Amazing Blog Post Title"
    date: "Month Day, Year"  # e.g., "October 27, 2023" - this format is preferred for date sorting
    author: "Your Name"
    featuredImage: "URL_to_your_featured_image.jpg" # Optional: URL for an image to display at the top
    categories: [PrimaryCategory, SecondaryCategory] # Optional: A list of categories
    tags: ["keyword1", "relevant_tag", "another_one"] # Optional: A list of tags
    metaDescription: "A short, compelling description of your post for SEO and previews."
    ---
    ```

3.  **Write Your Content:** Below the frontmatter, write your blog post content using standard Markdown syntax.

    *   Headings (e.g., `## Section Title`, `### Subsection`) will be used to automatically generate a Table of Contents for your post.
    *   You can use all standard Markdown features like lists, bold, italics, links, images, blockquotes, code blocks, etc.

Once you add the file and push the changes (if using a version control system integrated with Vercel or a similar hosting platform), the website should automatically pick up the new post and display it on the blog index page and its own dedicated page.

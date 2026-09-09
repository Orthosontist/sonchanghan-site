# Website operations

## Publishing

The existing production site is `https://drsonchanghan.com`, backed by the GitHub `main` branch and Netlify. Keep the existing domain and Google Search Console verification DNS records.

## Blog synchronization

- `.github/workflows/sync-blog.yml` runs daily at 23:17 UTC (08:17 Korea time the next day), or through GitHub Actions → Sync Naver blog articles → Run workflow. Scheduled jobs may start late.
- `python -m pip install -r scripts/requirements.txt` then `python scripts/sync_blog.py` refreshes public posts exposed by the Naver RSS feed.
- Full public `PostView.naver` bodies are sanitized into static `journal/<post-id>.html` pages. Paragraphs, highlights, tables, links and images are retained; active scripts and unsupported embeds are removed. Images remain on Naver's public image servers.
- The ten manually edited numbered articles and existing impacted-molar article keep their established URLs and contents. `LEGACY` maps their original Naver post IDs. They are not overwritten automatically.
- `SKIP` preserves the previously withheld resident-seminar post and excludes the duplicate biography and empty introductory post.
- Already imported posts stay in the archive after they leave the RSS feed. Edits are checked while posts remain in the feed. Deletions on Naver do not automatically delete the local archive.
- A failed body fetch or parser check preserves the last saved page and fails the job before the commit step. Check the Actions log if updates stop.
- `/consultation/`, `/cases/`, article metadata, and `sitemap.xml` update together. Personal posts are excluded from navigation and indexing. A changed commit triggers the existing Netlify Git deployment.

## Search

Each indexed article has an HTML body, its own canonical URL, answer-first summary, author credentials, publication/update dates, source link, image metadata and category-aware structured data. Existing URLs are preserved. These enable discovery but do not guarantee indexing or AI citations.

After deployment, resubmit `https://drsonchanghan.com/sitemap.xml` in the already verified Google Search Console property. Reconfirm the physician's affiliation when the fellowship ends; no clinic opening claims are currently promoted on the homepage.
# Four-page site structure

The primary navigation is Home `/`, Doctor `/doctor/`, Consultation Journal
`/consultation/`, and Clinical Cases `/cases/`. Presentation templates live in
`scripts/site_pages.py`, with shared responsive styles in `site.css`.
`python scripts/rebuild_site.py` regenerates all four pages and applies the shared
navigation to public articles without changing their existing URLs or clinical
body content. The blog sync workflow also stages the generated doctor page.
`index-redesign.html` is the retained older, noindex design, not the current home.

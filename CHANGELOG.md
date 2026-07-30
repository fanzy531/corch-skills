# Changelog

## 1.2.0 (2026-07-30)

### Added
- User interaction flow: guide to get Application Password, category selection, confirmation before publish
- Output mode fallback when auth not provided

### Changed
- Publish step now requires user confirmation before POST

---

## 1.1.0 (2026-07-30)

### Changed
- Removed "Output plain text pieces" and "Deliver" steps — metadata now goes through API payload ACF fields
- Simplified workflow: Generate HTML → Publish / Output

### Added
- corch-hub skill added to repo

---

## 1.0.0 (2026-07-30)

### Added
- corch-digest skill: read, digest, rewrite articles from URLs
- Inline-style self-contained HTML output
- Publish to WordPress voice CPT via /clab/v1/publish-voice
- Application Password + fallback auth
- voice_category selection (5 fixed categories)

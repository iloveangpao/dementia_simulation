# ADR-0001: Documentation Stack (MkDocs + Material + mkdocstrings)

* **Status**: Accepted
* **Date**: 2024-01-15
* **Deciders**: Development Team

## Context and Problem Statement

The Dementia Simulation project needs comprehensive, maintainable, and user-friendly documentation that covers multiple audiences (users, developers, contributors) and multiple content types (tutorials, API reference, architecture explanations). The documentation should be:

- Easy to write and maintain (Markdown-based)
- Auto-generate API documentation from code
- Support diagrams and interactive elements
- Deploy automatically to GitHub Pages
- Follow documentation best practices (Diátaxis framework)

## Decision Drivers

* **Maintainability**: Documentation should be easy to update and keep in sync with code
* **Automation**: API docs should auto-generate from Python docstrings
* **User Experience**: Clean, searchable, responsive design
* **Developer Experience**: Simple authoring workflow, local preview
* **Cost**: Free/open-source solution preferred
* **CI/CD Integration**: Seamless deployment to GitHub Pages
* **Diagram Support**: Native support for Mermaid diagrams
* **Framework Alignment**: Support for Diátaxis documentation framework

## Considered Options

### Option 1: MkDocs + Material Theme + mkdocstrings

Static site generator with Material theme and Python docstring plugin.

**Components**:
- MkDocs: Static site generator
- Material theme: Modern, feature-rich theme
- mkdocstrings: Auto-generate API docs from docstrings
- Mermaid: Diagram support

### Option 2: Sphinx + Read the Docs

Traditional Python documentation stack.

**Components**:
- Sphinx: Python documentation generator
- Read the Docs theme: Classic documentation theme
- autodoc: Auto-generate from docstrings
- Read the Docs: Free hosting

### Option 3: Docusaurus

React-based documentation framework from Meta.

**Components**:
- Docusaurus: Modern doc site generator
- React-based: Interactive components
- Versioning: Built-in version management
- Search: Algolia integration

### Option 4: GitBook

Commercial documentation platform with free tier.

**Components**:
- GitBook: Hosted platform
- WYSIWYG editor: Non-technical friendly
- Collaboration: Built-in review workflow
- Integrations: GitHub sync

## Decision Outcome

**Chosen option**: "Option 1: MkDocs + Material + mkdocstrings"

### Justification

MkDocs with Material theme and mkdocstrings best meets our requirements:

1. **Markdown-native**: Easy to write and maintain
2. **Excellent API docs**: mkdocstrings generates beautiful API reference from Python docstrings
3. **Material theme**: Modern, responsive, feature-rich (navigation tabs, search, dark mode)
4. **Mermaid support**: Native diagram rendering
5. **GitHub Pages**: Simple deployment with GitHub Actions
6. **Active community**: Well-maintained, extensive plugins
7. **Diátaxis-friendly**: Structure naturally supports Diátaxis categories
8. **Fast**: Static site with instant search
9. **Open source**: No vendor lock-in
10. **Python ecosystem**: Natural fit for Python project

### Positive Consequences

* ✅ **Automated API docs**: Changes to code docstrings automatically update documentation
* ✅ **Beautiful UI**: Material theme provides professional, modern design
* ✅ **Fast development**: Simple Markdown authoring with hot reload (`mkdocs serve`)
* ✅ **SEO-friendly**: Static HTML with good search engine optimization
* ✅ **Version control**: Documentation lives in repo alongside code
* ✅ **Extensible**: Rich plugin ecosystem for future needs
* ✅ **No build complexity**: Simple `mkdocs build` command
* ✅ **Free hosting**: GitHub Pages at no cost

### Negative Consequences

* ⚠️ **Learning curve**: Team needs to learn MkDocs + YAML configuration
* ⚠️ **Plugin dependencies**: Reliance on third-party plugins (mkdocstrings, mermaid)
* ⚠️ **Limited interactivity**: Static site, not SPA (but sufficient for docs)
* ⚠️ **Docstring quality**: Requires well-written Google/NumPy-style docstrings
* ⚠️ **Build time**: Large sites can have slow builds (not an issue yet)

## Pros and Cons of the Options

### Option 1: MkDocs + Material + mkdocstrings

**Pros**:
- ✅ Markdown-based authoring
- ✅ Excellent Material theme (navigation, search, responsive)
- ✅ mkdocstrings auto-generates API docs
- ✅ Mermaid diagram support
- ✅ Simple GitHub Actions deployment
- ✅ Fast local development (`mkdocs serve`)
- ✅ Active community and plugins
- ✅ Python-native tooling

**Cons**:
- ❌ Requires learning MkDocs config
- ❌ Plugin dependency (mkdocstrings)
- ❌ Static site (no interactive features)

### Option 2: Sphinx + Read the Docs

**Pros**:
- ✅ Traditional Python docs standard
- ✅ Mature, stable toolchain
- ✅ Free Read the Docs hosting
- ✅ Powerful cross-referencing
- ✅ Multi-format output (HTML, PDF, ePub)

**Cons**:
- ❌ Steeper learning curve (reStructuredText)
- ❌ Dated default theme
- ❌ More complex configuration
- ❌ Slower build times
- ❌ Less modern UX

### Option 3: Docusaurus

**Pros**:
- ✅ Modern React-based framework
- ✅ Interactive components possible
- ✅ Built-in versioning
- ✅ Algolia search integration
- ✅ Great for multi-version docs

**Cons**:
- ❌ JavaScript/React dependency (not Python-native)
- ❌ More complex setup (Node.js, npm)
- ❌ Overkill for current needs
- ❌ No native Python API doc generation
- ❌ Heavier build process

### Option 4: GitBook

**Pros**:
- ✅ WYSIWYG editor (non-technical friendly)
- ✅ Hosted platform (no infrastructure)
- ✅ Built-in collaboration
- ✅ Nice UI

**Cons**:
- ❌ Vendor lock-in
- ❌ Limited free tier
- ❌ Less control over design/structure
- ❌ No auto-generation from code
- ❌ Requires external sync with repo

## Implementation

### Tech Stack

```yaml
# mkdocs.yml
site_name: Dementia Simulation Documentation
theme:
  name: material
  features:
    - navigation.tabs
    - navigation.sections
    - search.suggest
    - content.code.copy

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          options:
            docstring_style: google
            show_source: true

markdown_extensions:
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
```

### Directory Structure

```
docs/
├── index.md                    # Landing page
├── tutorials/                  # Learning-oriented
│   ├── quickstart.md
│   ├── run-local.md
│   └── build-index.md
├── how-to/                     # Problem-oriented
│   ├── add-dataset.md
│   ├── add-model.md
│   └── enable-faiss.md
├── reference/                  # Information-oriented
│   ├── api/
│   └── modules/
├── explanation/                # Understanding-oriented
│   ├── architecture.md
│   ├── data-pipeline.md
│   └── personas.md
└── decisions/                  # ADRs
    └── ADR-0001-docs-stack.md
```

### Deployment

GitHub Actions workflow (`.github/workflows/docs.yml`):

```yaml
name: Deploy Docs
on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - run: pip install mkdocs-material mkdocstrings[python]
      - run: mkdocs gh-deploy --force
```

## Links

* Related: [Diátaxis Framework](https://diataxis.fr/)
* Related: [MkDocs Material](https://squidfunk.github.io/mkdocs-material/)
* Related: [mkdocstrings](https://mkdocstrings.github.io/)
* Related: [MADR Template](https://adr.github.io/madr/)

## Notes

### Future Considerations

- **Versioning**: If multi-version docs needed, consider mike plugin
- **Search**: If advanced search needed, consider Algolia integration
- **Analytics**: Consider adding Google Analytics or similar
- **PDF generation**: Can add pdf-export plugin if needed
- **i18n**: Material theme supports multiple languages if needed

### Alternatives Revisited

We can revisit this decision if:

- Team grows significantly and needs more collaboration features → Consider GitBook
- Need interactive tutorials → Consider Docusaurus
- Documentation grows to 1000+ pages → Re-evaluate build performance
- Need enterprise features → Consider commercial doc platforms

### Migration Path

If we need to migrate from MkDocs:

- **To Sphinx**: Content mostly compatible (Markdown → reStructuredText)
- **To Docusaurus**: Markdown compatible, need React wrapper
- **To GitBook**: Can import Markdown directly

Low migration risk due to Markdown-based content.

# Tutorials

Welcome to the tutorials section! These step-by-step guides will help you learn the Dementia Simulation platform from scratch.

## 📚 Available Tutorials

### [Quickstart Guide](quickstart.md)

Get up and running with the Dementia Simulation platform in just a few minutes. This tutorial covers:

- Installing dependencies
- Running your first simulation
- Understanding the basic workflow

**Time**: ~10 minutes  
**Level**: Beginner

---

### [Run Locally](run-local.md)

Complete guide to setting up the entire system on your local machine. You'll learn:

- Environment configuration
- Database setup
- Running different interfaces (Streamlit, CLI, API)
- Troubleshooting common issues

**Time**: ~30 minutes  
**Level**: Beginner to Intermediate

---

### [Build Index](build-index.md)

Learn how to create and manage the document search index. This covers:

- Document preprocessing
- Building FAISS index
- Testing search functionality
- Understanding TF-IDF vs semantic search

**Time**: ~20 minutes  
**Level**: Intermediate

## 🎯 Learning Path

We recommend following the tutorials in this order:

1. **Quickstart** → Get familiar with the basics
2. **Run Locally** → Set up your development environment
3. **Build Index** → Create your knowledge base

## 📖 What's Next?

After completing these tutorials, check out:

- **[How-to Guides](../how-to/index.md)** - Solve specific problems
- **[Explanation](../explanation/index.md)** - Understand the system design
- **[Reference](../reference/index.md)** - Explore the API documentation

## 💡 Tutorial Tips

!!! tip "Prerequisites"
    All tutorials assume you have:
    
    - Python 3.10 or higher installed
    - Basic command line knowledge
    - Git installed (for cloning the repository)

!!! note "Getting Help"
    If you get stuck, check the [Troubleshooting](#troubleshooting) section in each tutorial or visit our [GitHub Issues](https://github.com/iloveangpao/dementia_simulation/issues).

## 🐛 Troubleshooting

Common issues across tutorials:

### Python Version Issues

Ensure you're using Python 3.10 or higher:

```bash
python --version
```

### Dependency Installation Failures

Try upgrading pip first:

```bash
pip install --upgrade pip
```

### Port Already in Use

If port 8000 or 8501 is already in use, you can specify a different port:

```bash
# For API server
uvicorn dementia_simulation.api.server:app --port 8001

# For Streamlit
streamlit run frontend/streamlit_app.py --server.port 8502
```

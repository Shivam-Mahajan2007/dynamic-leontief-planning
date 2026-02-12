# Step-by-Step Guide: Setting Up Your GitHub Repository

## Part 1: Create the Repository Structure

### 1. Create Local Project Folder

```bash
mkdir dynamic-leontief-planning
cd dynamic-leontief-planning
```

### 2. Organize Files into Folders

Create the following structure:

```
dynamic-leontief-planning/
├── README.md                  # Rename README_GITHUB.md to this
├── LICENSE
├── CITATION.cff
├── .gitignore
├── CONTRIBUTING.md
├── requirements.txt
│
├── code/
│   ├── main.py
│   ├── config.yaml
│   ├── data_loader.py
│   ├── model.py
│   ├── plotting.py
│   └── __init__.py           # Empty file
│
├── data/
│   ├── README.md             # Use DATA_README.md
│   ├── Spanish_A-matrix.xlsx
│   ├── Value_added.xlsx
│   └── Consumption_and_total_production.xlsx
│
├── examples/
│   ├── basic_simulation.py   # Use basic_example.py
│   └── README.md             # Create: "See basic_simulation.py for minimal example"
│
└── paper/
    └── manuscript.pdf        # Your PDF
```

### 3. Create Empty __init__.py

```bash
cd code
touch __init__.py
cd ..
```

## Part 2: Initialize Git Repository

### 1. Initialize Git

```bash
git init
```

### 2. Add All Files

```bash
git add .
```

### 3. Make First Commit

```bash
git commit -m "Initial commit: Dynamic IO planning model v1.0.0"
```

## Part 3: Create GitHub Repository

### Option A: Using GitHub Website

1. Go to https://github.com
2. Click the **"+"** in top right → **"New repository"**
3. Fill in:
   - **Repository name:** `dynamic-leontief-planning`
   - **Description:** "Dynamic Input–Output Planning Model with Price Feedback"
   - **Public** (recommended for academic work)
   - **Do NOT** initialize with README (you already have one)
4. Click **"Create repository"**

### Option B: Using GitHub CLI

```bash
gh repo create dynamic-leontief-planning --public --source=. --remote=origin
```

## Part 4: Push to GitHub

### 1. Link Local Repository to GitHub

```bash
# Replace 'yourusername' with your actual GitHub username
git remote add origin https://github.com/yourusername/dynamic-leontief-planning.git
```

### 2. Push Code

```bash
git branch -M main
git push -u origin main
```

## Part 5: Get a DOI with Zenodo

### 1. Link GitHub to Zenodo

1. Go to https://zenodo.org
2. Sign in with GitHub
3. Go to https://zenodo.org/account/settings/github/
4. Find your repository and toggle it **ON**

### 2. Create a Release

On GitHub:
1. Go to your repository
2. Click **"Releases"** → **"Create a new release"**
3. Fill in:
   - **Tag:** `v1.0.0`
   - **Title:** `v1.0.0 - Initial Release`
   - **Description:**
     ```
     First public release of the Dynamic Input–Output Planning Model.
     
     Accompanies the paper:
     Mahajan, S., & Singh, A. (2025). "On a Dynamic Input–Output Framework 
     for Price-Feedback-Based Production Planning."
     
     Features:
     - Full implementation of dynamic planning algorithm
     - Spanish IO data (2022, 64 sectors)
     - Complete reproducibility of paper results
     - Mean absolute output gap: 1.56%
     ```
4. Click **"Publish release"**

### 3. Get Your DOI

1. Go back to Zenodo (https://zenodo.org/account/settings/github/)
2. Your release should appear - click it
3. Copy the DOI badge
4. Update your README with the DOI

## Part 6: Update README with DOI

```bash
# Edit README.md and replace:
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)

# With your actual DOI from Zenodo
```

Then commit and push:
```bash
git add README.md
git commit -m "Add Zenodo DOI"
git push
```

## Part 7: Add to Your Paper

Update your manuscript with:

### Data Availability Statement
```
Code and data are available at: 
https://github.com/yourusername/dynamic-leontief-planning
DOI: 10.5281/zenodo.XXXXXXX
```

### Computational Details (in Methods or Appendix)
```
All simulations were performed using Python 3.9 on a standard laptop 
(Intel i5, 8GB RAM). Complete code, data, and documentation are available 
at https://github.com/yourusername/dynamic-leontief-planning with DOI 
10.5281/zenodo.XXXXXXX. Runtime for the 64-sector, 60-month simulation 
is approximately 2 minutes.
```

## Part 8: Optional Enhancements

### Add GitHub Topics

On your repository page:
1. Click the gear icon next to "About"
2. Add topics: `input-output-analysis`, `economic-planning`, `leontief-model`, `computational-economics`, `python`

### Add Repository Description

In the same "About" section:
- Description: "Dynamic Input–Output Planning Model with Price Feedback"
- Website: Link to your paper when published

### Create GitHub Pages (Optional)

For a nice project website:
```bash
# In your repo settings, enable GitHub Pages
# Choose source: main branch, /docs folder (or use README)
```

### Add Badges to README

```markdown
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
```

## Part 9: Test Everything

### Clone in a New Location

```bash
cd ~/Desktop
git clone https://github.com/yourusername/dynamic-leontief-planning.git test-clone
cd test-clone
pip install -r requirements.txt
python code/main.py
```

If this works, your repository is ready!

## Troubleshooting

### Problem: Git push rejected

```bash
# Pull first
git pull origin main --rebase
git push
```

### Problem: File too large

GitHub has a 100MB file limit. If your data files are too large:
1. Use Git LFS: `git lfs install`
2. Or: Store data on Zenodo/figshare and link to it

### Problem: Can't find modules

Make sure `__init__.py` exists in the `code/` directory.

## Checklist

Before announcing your repository:

- [ ] README.md is clear and comprehensive
- [ ] LICENSE file is present
- [ ] All code runs without errors
- [ ] Data files are included (or linked if too large)
- [ ] Paper PDF is in `paper/` folder
- [ ] CITATION.cff has correct information
- [ ] Zenodo DOI is obtained and added to README
- [ ] Repository topics are added
- [ ] Example code runs successfully
- [ ] requirements.txt is complete

## Next Steps

After your repository is live:

1. **Share it:**
   - Include link in paper submission
   - Tweet about it
   - Add to your website/CV
   - Submit to relevant mailing lists

2. **Maintain it:**
   - Respond to issues
   - Accept pull requests
   - Update if you find bugs
   - Add new features from future work

3. **Archive it:**
   - Create new Zenodo versions for updates
   - Keep the v1.0.0 version stable (don't delete or force-push)

## Need Help?

- **GitHub Guides:** https://guides.github.com/
- **Zenodo Help:** https://help.zenodo.org/
- **Git Tutorial:** https://git-scm.com/docs/gittutorial

Congratulations on making your research reproducible! 🎉

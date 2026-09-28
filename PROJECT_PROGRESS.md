# MLSD DVC Project - Progress and Remaining Plan

Last updated: 2026-09-28

## 1. Project Summary

This project is an inventory restocking system built for the DS-4491 Machine
Learning Systems Design course. A tabular Q-learning agent decides how many
units a shop should order each day.

DVC manages the data, model, parameters, metrics, plots, and pipeline so the
complete experiment can be reproduced on another computer.


Project locations:

- Feast GitHub: `https://github.com/Az-main/Q-learning-MLSD-Project-Feast`
- Feast DagsHub: `https://dagshub.com/Az-main/Q-learning-MLSD-Project-Feast`
- Feast workspace: `D:\DVC Project Feast`
- Feast local DVC backup: `D:\dvcstore-feast`
- Original mandatory GitHub: `https://github.com/Az-main/Q-learning-MLSD-Project`
- Original mandatory DagsHub: `https://dagshub.com/Az-main/Q-learning-MLSD-Project`
- Original stable folder: `D:\DVC Project`
- Friend's laptop clone: `D:\MLSD\Q-learning-MLSD-Project`

## 2. Dataset and Model

### Dataset

- Source: Kaggle Store Item Demand Forecasting Challenge
- Selected data: store 1 and item 1
- Size: 1,826 daily rows from 2013 through 2017
- Training period: 2013-2015
- Online stream period: 2016
- Test period: 2017
- `tools/get_data.py` can generate synthetic data when Kaggle data is unavailable.

### Model

- Model: tabular Q-learning
- State space: 168 states
- State values: stock bucket, day of week, and demand trend
- Actions: order 0, 10, 20, or 40 units
- Main model output: `models/q_table.json`
- Evaluation compares Q-learning with several simple ordering policies.

### Bonus Components

The following bonus components have been implemented:

- River incremental learning
- ADWIN data-drift detection
- ADWIN concept-drift detection
- Automatic retraining after detected drift
- Comparison with drift response enabled and disabled
- Feast offline feature store
- Feast online feature store
- Historical and online feature retrieval
- Feature-based Q-learning order recommendations

## 3. DVC Pipeline

The project contains the following pipeline stages:

```text
data/raw/sales.csv.dvc -> prepare -> train -> evaluate

prepare + train -> online_drift
prepare + train -> feast_serve
```

| Stage | Purpose | Main outputs |
|---|---|---|
| `prepare` | Cleans and splits data chronologically | train, stream, and test Parquet files |
| `train` | Trains the Q-learning agent | Q-table, training metrics, and training plot |
| `evaluate` | Tests and compares policies | evaluation metrics and policy comparison plot |
| `online_drift` | Runs online learning and drift response | drift metrics and online-drift plot |
| `feast_serve` | Retrieves offline and online features | Feast metrics and order recommendations |

The pipeline can be inspected and reproduced with:

```powershell
dvc status
dvc dag
dvc repro
dvc metrics show
dvc plots show
```

## 4. Work Completed

### Environment and Repository Setup

- Created Python 3.11 virtual environments.
- Installed the packages from `requirements.txt`.
- Installed Feast 0.65.0 from `requirements-feast.txt`.
- Initialized Git and DVC.
- Added the project files and ignore rules.
- Pushed the repository to GitHub.
- Added a detailed README containing all required sections.

### Data Versioning

- Added `data/raw/sales.csv` to DVC.
- Confirmed that Git tracks `sales.csv.dvc` instead of the large CSV.
- Confirmed that DVC stores files by content hash in `.dvc/cache`.
- Created `D:\dvcstore` as a local backup remote.
- Connected the project to a shared DagsHub DVC remote.
- Made the DagsHub remote named `origin` the default DVC remote.
- Pushed the required data and model artifacts to DagsHub.
- Successfully restored the files on another laptop with `dvc pull`.

Current DVC remote arrangement:

```text
localremote -> D:\dvcstore-feast
origin      -> https://dagshub.com/Az-main/Q-learning-MLSD-Project-Feast.dvc
```

### Main Pipeline

- Ran the `prepare`, `train`, `evaluate`, and `online_drift` stages.
- Generated `dvc.lock` with dependency, parameter, and output hashes.
- Verified that unchanged stages are skipped by `dvc repro`.
- Ran the smoke tests successfully.
- Generated the required metrics and plots.

### Model Results

| Policy | Total reward | Service level | Stockout rate | Average leftover |
|---|---:|---:|---:|---:|
| Q-learning | 18,197.3 | 0.860 | 0.466 | 3.92 |
| Recent-average order | 16,589.1 | 0.887 | 0.337 | 26.47 |
| Always order 20 | 15,258.0 | 0.866 | 0.381 | 27.75 |
| Random policy | 12,979.6 | 0.813 | 0.268 | 27.28 |

The Q-learning policy produced the highest total reward and kept significantly
less unused inventory than the comparison policies.

### Drift Experiment

Both experiment modes were preserved separately.

| Metric | Response enabled | Response disabled |
|---|---:|---:|
| Average reward before drift | 44.07 | 43.84 |
| Average reward after drift | 51.51 | 13.66 |
| Online total reward | 17,498.2 | 10,493.5 |
| Retraining events | 3 | 0 |

The similar before-drift results make the comparison fair. After the simulated
demand increase, automatic retraining substantially improved performance.

The final configuration uses:

```yaml
drift:
  respond: true
```

### Feast Feature Store

Feast 0.65.0 was installed and tested in an isolated Python 3.11 environment.

The `feast_serve` stage:

1. Creates historical feature data in Parquet format.
2. Registers the `store_item` entity.
3. Registers the `demand_features` feature view.
4. Retrieves point-in-time historical features.
5. Confirms that Feast values match the source data.
6. Materializes the latest values into a SQLite online store.
7. Retrieves online features for store 1 and item 1.
8. Uses the features and Q-table to recommend order quantities.

The Feast validation produced:

| Result | Value |
|---|---|
| Historical rows retrieved | 5 |
| Historical values match source | True |
| Feature view state | `AVAILABLE_ONLINE` |
| Store-item ID | 1001 |
| Latest day of week | 6 |
| Latest rolling demand | 17.57 |
| Latest demand trend | 1 |
| Recommended order with stock 0 | 10 |
| Recommended order with stock 20 | 10 |
| Recommended order with stock 60 | 0 |

Generated registry, SQLite, and Feast Parquet files are stored under
`feature_repo/data/` and are ignored by Git because they can be regenerated.

### Collaboration Setup

- Connected the GitHub repository to DagsHub.
- Added the friend as a collaborator on GitHub and DagsHub.
- Installed Python, Git, DVC, and the dependencies on the friend's laptop.
- Cloned the project on the laptop.
- Configured the friend's own DagsHub credentials locally.
- Confirmed that `.dvc/config.local` is ignored by Git.
- Successfully ran `dvc pull` on the laptop.
- Successfully ran `dvc status` and the smoke tests on the laptop.
- Successfully created and pushed a collaboration test branch.
- Used a pull request to merge the drift-comparison work.

Access tokens are never committed. Each collaborator uses their own token in
their local `.dvc/config.local` file.

## 5. Course Requirement Status

| Requirement | Status | Evidence |
|---|---|---|
| Data preparation | Complete | `prepare` stage |
| Model training | Complete | `train` stage |
| Model evaluation | Complete | `evaluate` stage |
| Suitable dataset and model | Complete | Demand dataset and Q-learning agent |
| Reproducible DVC pipeline | Complete | `dvc.yaml` and `dvc.lock` |
| DVC command knowledge | Implemented | Commands documented and tested |
| Clean GitHub repository | Complete | Shared GitHub repository |
| Complete README | Complete | All required sections included |
| Reproduction on another machine | Complete | Laptop setup and DVC pull passed |
| River online learning bonus | Complete | Used by `online_drift` |
| Drift detection bonus | Complete | ADWIN data and concept drift |
| Drift response bonus | Complete | Automatic retraining and comparison |
| Feast bonus | Complete | Offline, online, and materialization verified |

All mandatory requirements and the River, drift-detection, drift-response, and
Feast bonus components have been implemented successfully.

## 6. Remaining Work

### Final Reproducibility Check

After the Feast branch is merged, verify the final project on the PC and laptop:

```powershell
git switch main
git pull
python -m pip install -r requirements.txt
python -m pip install -r requirements-feast.txt
dvc pull
dvc status
dvc repro
python tests\smoke_test.py
git status
```

Expected results:

- DVC reports that the pipeline is up to date.
- The smoke tests pass.
- Git reports a clean working tree.
- `feast_serve` appears in `dvc dag`.
- `demand_features` appears as `AVAILABLE_ONLINE`.

### Viva Preparation

Practice running and explaining:

```powershell
dvc status
dvc repro
dvc dag
dvc metrics show
dvc push
dvc pull
```

Be ready to explain:

- The difference between Git and DVC
- The purpose of `dvc.yaml`, `dvc.lock`, and `params.yaml`
- How DVC decides which stage must rerun
- What happens when data or parameters change
- How another person reproduces the project
- Batch learning compared with online learning
- How River performs incremental learning
- Data drift compared with concept drift
- How ADWIN detects changes
- How the system responds to drift
- Offline and online Feast stores
- Historical and online feature retrieval
- Feast materialization
- Project limitations and simulated drift

### Presentation Preparation

- Capture a clear screenshot of `dvc dag`.
- Capture the policy comparison plot.
- Capture both drift-response plots.
- Show the Feast feature view as `AVAILABLE_ONLINE`.
- Show the GitHub repository and DagsHub storage.
- Prepare a short pipeline architecture slide.
- Practice one complete live demonstration.

## 7. Collaboration Workflow

Before starting work:

```powershell
git switch main
git pull
dvc pull
git switch -c username/short-task-name
```

After completing work:

```powershell
dvc repro
dvc push
git status
git add .
git commit -m "Describe the change"
git push -u origin HEAD
```

Then create a pull request, review the changes, merge into `main`, and delete
the completed branch.

Avoid editing the same files on both computers at the same time.

## 8. Current Overall Status

- Mandatory project requirements: complete
- Original GitHub and DagsHub setup: complete
- Original project reproduction on the friend's laptop: complete
- Multi-user collaboration test: complete
- Q-learning pipeline: complete
- River online learning bonus: complete
- Drift detection and response bonus: complete
- Separate drift comparison evidence: complete
- Feast feature-store bonus: complete
- Separate Feast GitHub repository: complete
- Separate Feast DagsHub storage: complete
- Separate Feast local backup: complete
- Final Feast reproducibility verification: remaining
- Friend collaboration setup for Feast repository: remaining
- Viva and presentation practice: remaining

The mandatory project and the Feast-enhanced project are stored independently.
The implementation and repository separation are complete. The remaining work
is final reproducibility verification, collaborator setup, viva practice, and
presentation preparation.
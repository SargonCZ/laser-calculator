# laser-calculator

## Local development setup

The instructions below presume you have cloned this git repository you are in a command line
(¨`bash`, `cmd` etc.) in the root directory of this project.

### conda environment

For the first time, create a new `laser-calculator` conda environment with necessary packages using
```
conda env create -f environment.yaml
```

This environment must be updated when the `environment.yaml` file changes using
```
conda env update -f environment.yaml
```

Every time you are working on the project, activate the environment using
```
conda activate laser-calculator
```

This is especially useful for local development.

# lifetime_trends

A model created for the publication "Long-term lifetime trends of large appliances since the introduction in Norwegian households" in the Journal of Industrial Ecology. The model estimates the mean lifetime assuming a constant or logistic function to describe how the Weibull scale parameter of the lifetime distribution varied in time. 

Author: Kamila Krych, Norwegian University of Science and Technology

## Setup

1. Create Python environment
2. Install ODYM

### Create Python environment

Create a Python environment in conda or similar using the `environment.yml` file.

### Install ODYM

In the parent directory of your lifetime_trends folder, clone GitHub repository containing the ODYM framework: https://github.com/IndEcol/ODYM. The code requires the ODYM_Classes.py file located in the odym/odym/modules folder. 

## Repository's structure
The repository contains the following files:
1. Data input file `data.xlsx`.
2. Jupyter Notebooks with Python scripts. The files need to be executed in the given order. It is not necessary to run the first file, unless the underlying raw data has been changed, or processed data has been deleted from the data.xlsx file. 
	- `1_preprocessing.ipynb`: scripts preprocessing raw data;
	- `2_preliminary_analysis_global.ipynb`: scripts performing the preliminary analysis, where all the model parameters are varied to identify the critical ones (global uncertainty and sensitivity analysis);
	- `3a_analysis_constant.ipynb`: scripts performing the final analysis with a constant lifetime assumption;
	- `3b_analysis_logistic.ipynb`: scripts performing the final analysis with a logistic lifetime assumption;
	- `4_figures.ipynb`: scripts creating figures and analyzing the results.
3. Python files with functions and classes supporting the calculations:
	- `timeseriessegments.py`: a class assisting in dividing the time series into segments with independent uncertainty information;
	- `funct.py`: all other supporting functions.
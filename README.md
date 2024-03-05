# lifetime_trends

A model created for the publication "Long-term lifetime trends of large appliances since the introduction in Norwegian households" in the Journal of Industrial Ecology. The model estimates the mean lifetime assuming a constant or logistic function to describe how the Weibull scale parameter of the lifetime distribution varied in time. 

Author: Kamila Krych, Norwegian University of Science and Technology

## Setup

1. Create Python environment
2. Install ODYM

### Create Python environment

Create a Python environment in conda or similar, either using the environment.yml file or using the following dependencies:
- numpy
- pandas
- openpyxl
- ipykernel
- matplotlib
- seaborn
- scipy
- salib

### Install ODYM

In the parent directory of your lifetime_trends folder, clone GitHub repository containing the ODYM framework: https://github.com/IndEcol/ODYM. The code requires the ODYM_Classes.py file located in the odym/odym/modules folder. 
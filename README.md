
# ptbfla
Python Test Bed for Federated Learning Algorithms (PTB-FLA)

PTB-FLA team: Miroslav Popovic, Marko Popovic, Ivan Kastelan, Miodrag Djukic

Project description:
For the introduction to PTB-FLA, including the examples 1, 2, and 3, see [ZINC 2023 paper](https://arxiv.org/abs/2305.20027).
For the development paradigm, including the examples 4 and 5, see [ECBS 2023 paper 1](https://arxiv.org/abs/2310.05102).
For the formal verification of PTB-FLA generic algorithms, see [ECBS 2023 paper 2](https://arxiv.org/abs/2306.14529).

Warning: this project is work in progress.

## Quick installation on Windows:
1. Clone the ptbfla project into the directory src
2. Create the venv: `py -m venv venv_ptbfla`
3. Activate the `venv_ptbfla`: `venv_ptbfla\Scripts\activate`
4. PIP-install the package `ptbfla_pkg` ("-e" means editable install): `py -m pip install -e src`
5. Run example 1: `launch src\examples\example1_fedd_mean.py 3 id 0`

Notes:
- If for some reason you want to uninstall the pacakage, type: `pip uninstall venv_ptbfla`
- To deactivate the `venv_ptbfla` on Windows type: `venv_ptbfla\Scripts\deactivate.bat`

## Quick installation on Ubuntu:
1. Clone the ptbfla project into the directory src
2. Create the venv: `python3 -m venv venv_ptbfla`
3. Source the `venv_ptbfla`: `source venv_ptbfla/bin/activate`
4. PIP-install the package `ptbfla_pkg` ("-e" means editable install): `python3 -m pip install -e src`
5. Run example 1: `launch src/examples/example1_fedd_mean.py 3 id 0`

Note: To deactivate the `venv_ptbfla` on Ubuntu type: `deactivate`

## Additional installation steps for Examples 4 and 5 on Windows:
1. If not already acive, activate the `venv_ptbfla`: `venv_ptbfla\Scripts\activate`
2. Upgrade PIP: `py -m pip install --upgrade pip`
3. PIP-install the package numpy: `py -m pip install numpy`
4. PIP-install the package pandas: `py -m pip install pandas`
5. PIP-install the package matplotlib: `py -m pip install matplotlib`
6. PIP-install the package scikit-learn: `py -m pip install -U scikit-learn`
7. Chage directory to examples: `cd src\examples`
8. Run example 4: `launch example4_logistic_regression.py 3 id 2`
9. Run example 5: `launch example5_dec_log_regression.py 2 id`

## Additional installation steps for Examples 4 and 5 on Ubuntu:
1. If not already sourced, source the `venv_ptbfla`: `source venv_ptbfla/bin/activate`
2. Upgrade PIP: `python3 -m pip install --upgrade pip`
3. PIP-install the package numpy: `python3 -m pip install numpy`
4. PIP-install the package pandas: `python3 -m pip install pandas`
5. PIP-install the package matplotlib: `python3 -m pip install matplotlib`
6. PIP-install the package scikit-learn: `python3 -m pip install -U scikit-learn`
7. Chage directory to examples: `cd src/examples`
8. Run example 4: `launch example4_logistic_regression.py 3 id 2`
9. Run example 5: `launch example5_dec_log_regression.py 2 id`

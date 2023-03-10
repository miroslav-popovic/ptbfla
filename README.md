# ptbfla
Python Test Bed for Federated Learning Algorithms (PTB-FLA)

PTB-FLA team: Miroslav Popovic, Marko Popovic, Ivan Kastelan, Miodrag Djukic

TODO: Project description.
Warning: this project is work in progress.

## Qick installation on Windows:
1. Clone the ptbfla project into the directory src
2. Create the venv: `py -m venv venv_ptbfla`
3. Activate the `venv_ptbfla`: `venv_ptbfla\Scripts\activate`
4. PIP-install the package `ptbfla_pkg` ("-e" means editable install): `py -m pip install -e src`
5. Run example 1: `launch src\examples\example1_fedd_mean.py 3 id 0`

Notes:
- If for some reason you want to uninstall the pacakage, type: `pip uninstall venv_ptbfla`
- To deactivate the `venv_ptbfla` on Windows type: `venv_ptbfla\Scripts\deactivate.bat`

## Qick installation on Ubuntu:
1. Clone the ptbfla project into the directory src
2. Create the venv: `python3 -m venv venv_ptbfla`
3. Source the `venv_ptbfla`: `source venv_ptbfla/bin/activate`
4. PIP-install the package `ptbfla_pkg` ("-e" means editable install): `python3 -m pip install -e src`
5. Run example 1: `launch src/examples/example1_fedd_mean.py 3 id 0`

Note: To deactivate the `venv_ptbfla` on Ubuntu type: `deactivate`


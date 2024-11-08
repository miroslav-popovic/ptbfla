# ptbfla

The package ptbfla comprises the following two FL frameworks:

1. Python TestBed for Federated Learning Algorithms (PTB-FLA) on a localhost.
2. MicroPython testbed for Federated Learning Algorithms (MPT-FLA) on a (W)LAN of PCs and IoTs like RPi Pico W boards.

Project team: Miroslav Popovic, Marko Popovic, Ivan Kastelan, Miodrag Djukic.

Project description:

1. For the introduction to PTB-FLA, including the examples 1, 2, and 3, see [ZINC 2023 paper](https://arxiv.org/abs/2305.20027).
2. For the development paradigm, including the examples 4 and 5, see [ECBS 2023 paper 1](https://arxiv.org/abs/2310.05102).
3. For the formal verification of PTB-FLA generic algorithms, see [ECBS 2023 paper 2](https://arxiv.org/abs/2306.14529).
4. For the introduction to MPT-FLA, and the "mp*async*" examples, see the [paper](https://arxiv.org/abs/2405.09423) and the [video](https://www.youtube.com/watch?v=QQJ-xs7ZG30).

Directories (under the directory src):

- ptbfla_pkg: PTB-FLA (ptbfla.py, mpapi.py), MPT-FLA (mp_async_ptbfla.py, mp_async_mpapi.py), launcher.py (shared by both).
- examples: both PTB-FLA examples (without the prefix "mp*async*") and MPT-FLA (with the prefix).
- examples*rp2_board: the modules config.py and main.py to install on RPi Pico W boards to run "mp_async*" examples.

Notes on launching the examples:

- Remember to change the working directory to "src/examples".
- You must replace the IP addresses in the launch commands for the "mp*async*" examples with your IP address!
- When running PTB-FLA apps on Windows with many instances e.g., ODTS for 170 satellites (launch example6_odts.py 170 id 1 25), Windows may start protecting itself by throwing the exception "WinError 10061" to some of the processes, this is as expected, PTB-FLA should be able to cope with this and make the recovery, you should not do anything but be patient and wait.

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

## Distributed Launcher for MPT-FLA

If you wish to make MPT-FLA application testing on multiple PCs easier, see the Distributed Launcher for MPT-FLA [repository](https://github.com/LinguineP/distributedLauncher)

## PTB-FLA Babel adapter

 If you wish to use PTB-FLA accross multiple devices, see the PTB-FLA plug in adapter for Babel [repository](https://github.com/LinguineP/PTB-FLA_BabelAdapter)

# Project viewer

## Default install instructions

1. Clone the repository:

        git clone https://github.com/yohanboniface/piati.git

2. Change into the directory and create a `virtualenv` with python3.3:

        cd piati
        virtualenv -p python3.3 ./pyenv
        source ./pyenv/bin/activate

3. Install requirements:

        pip install -r requirements.txt

4. Fetch the data:

        python run.py fetch

5. Run the server to check you're happy with everything:

        python run.py serve --debug

6. Once you're happy, build the static site:

        python run.py build


## Customize the dataset

Just create a python settings file, using the `piati/default_settings.py` as
model (you should override only the needed keys). Then either create a env var:

    export PIATI_SETTINGS=path.to.settings

or use the command line `--settings=path.to.settings` on all the commands.

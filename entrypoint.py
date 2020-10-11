import sys
import yaml
import os
import json
import tempfile
import subprocess
import shutil
from loguru import logger
import tempfile
import subprocess
from jinja2 import Environment, PackageLoader, select_autoescape
import glob
from shutil import copyfile

def execute(bashCommand):
    logger.debug(f"bashCommand={bashCommand}")

    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    logger.debug(f"output={output}")
    logger.debug(f"error={error}")

    return output

def copy_files():
    """
        Parse user yaml and copy files to temp directory
    """
    current_work_directory = os.getcwd()
    dataset_file_in_yaml = [ x for x in os.environ.get('INPUT_FILES').split("\n")]
    logger.info(f"dataset_file_in_yaml={dataset_file_in_yaml}")
    FILE_PATH= os.environ.get('GITHUB_WORKSPACE')

    for dataset_file in dataset_file_in_yaml :
        logger.debug(f"dataset_file={dataset_file}")
        # We have to explode * expressions
        expanded_dataset_files = glob.glob(f"{FILE_PATH}/{dataset_file}")
        for expanded_dataset_file in expanded_dataset_files  :
            # If file already is there, we do not copy it
            file_not_exists_on_dst = not os.path.exists(expanded_dataset_file.split("/")[-1])
            if file_not_exists_on_dst :
                src = expanded_dataset_file
                dst = current_work_directory + "/" + os.path.basename(expanded_dataset_file) )
                logger.info(f"copy {src} to {dst}")
                shutil.copy(src,dst)

                logger.info(f"file {expanded_dataset_file}")

    logger.success(glob.glob(current_work_directory + "/" +'*'))
    return

def prepare_job():
    """
        Prepare temp dir
    """
    dirpath = tempfile.mkdtemp()
    os.chdir(dirpath)

    #kaggle datasets status jaimevalero/covid19-madrid

    INPUT_ID = os.environ.get('INPUT_ID')
    result = execute(f" kaggle datasets status {INPUT_ID}")
    logger.debug(f"result for {INPUT_ID} is result={result}")

    has_to_create_new_dataset = not "ready" in str(result)

    if has_to_create_new_dataset:
        env = Environment(
            loader=PackageLoader('templates'),
            autoescape=select_autoescape(['html', 'xml'])
        )
        template = env.get_template('templates/dataset-metadata.j2')

        INPUT_ID = os.environ.get('INPUT_ID')
        REPO_NAME= os.environ.get('GITHUB_REPOSITORY').split("/")[-1]
        TITLE = os.environ.get('INPUT_TITLE',REPO_NAME)
        logger.debug(f"INPUT_ID={INPUT_ID}, INPUT_TITLE={INPUT_TITLE}")

        outputText = template.render(INPUT_ID=INPUT_ID, INPUT_TITLE=INPUT_TITLE)
        with open("dataset-metadata.json", "w") as fh:
            fh.write(outputText)
        with open("dataset-metadata.json", 'r') as fin:
            logger.debug(fin.read())


    return
# Resolve if dataset has to be created

# Prepare temp dirname

# Prepare filenames

# PRepare

# prepare meta json if no
def print_files():
    """
        Helper function to know where are my files.
        Just for debug
    """

    for dirname, _, filenames in os.walk('/'):
        for filename in filenames:
            print(os.path.join(dirname, filename))
    return

def print_environment():
    """
        Helper function to know where are my variables.
        Just for debug
    """
    variables_functions = [dir(), globals() , locals()]
    for func in variables_functions:
        logger.debug( func)
    # Print environment varriables
    for key in os.environ.keys():
        valor=os.environ[key]
        logger.debug(f"llave {key} : {valor}")
    return

@logger.catch
def main():
    logger.info("Start")
    #print_files()
    print_environment()

    prepare_job()
    copy_files()

    logger.info("info")
    return

if __name__ == '__main__':
    main()

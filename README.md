# asf_jupyter_notebook_testing
OpenSARlabs notebook testing module and notebook test scripts

The tests are designed to be run in an instance of OpenSARlab.

	First, go to https://opensarlab.asf.alaska.edu/, login, and start a server.

	Open a terminal and clone the repo into /home/joyvan with the following command:

	git clone https://github.com/ASFOpenSARlab/opensarlab-notebook_testing.git opensarlab-notebook_testing

A .netrc file is required for some of the notebooks that are run by the test script.
The .netrc file can be generated by navigating to the opensarlab-notebook_testing directory, running the notebook make_netrc.ipynb and entering valid Earthdata credentials.

To do a test run against production OSL, you should be in the 'master' branch of /home/jovyan/notebooks and the 'main' branch of /home/jovyan/conda_environments.

If a feature branch of notebooks or conda_environments needs to be tested, switch into that branch before running the mamba_test_driver.sh script.



To run the test script manually, I like to use the following command so runtime errors are recorded:

	cd /home/jovyan/opensarlab-notebook_testing

	source mamba_test_driver.sh 2> errors.txt

Then, check the report in /home/jovyan/opensarlab-notebook_testing/reports for lines that do not include 'PASSED'.

Investigate any tests that resulted in 'FAILED' or 'EXCEPTION'.

Note: It is ofter useful to run individual test scripts. To do so, the appropriate conda environment must be installed and activated.

For example, from a terminal:

	cd to /home/jovyan/opensarlab-notebook_testing/
	
	conda activate /home/jovyan/.local/envs/rtc_analysis
	
	python3 Test_Ecosystems_Ex1.py


Alternatively, the test script can be set up to run on a cron in an instance of OSL running in Amazon Workspace.
Setup for cron to run mamba_test_driver.sh (Note: This requires sudo access in OSL):

1) Start an instance of OpenSarlabs in Amazon Workspace (this is necessarry to keep the instance open through internet outages and other interruptions).
2) Open a terminal in OSL
3) mkdir /home/joyvan/opensarlab-notebook_testing/keep_OSL_alive
4) sudo apt update
5) sudo apt-get install cron
6) sudo service cron start
7) crontab -e
8) Enter the following in the crontab:

DATEVAR=date +%Y%m%d_%H%M%S

*/30 * * * * echo $(date)  > /home/jovyan/opensarlab-notebook_testing/keep_OSL_alive/keep_alive$($DATEVAR).log 2>&1

PATH=/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/opt/conda/bin

SHELL=/bin/bash

25 14 * * * source /home/jovyan/opensarlab-notebook_testing/mamba_test_driver.sh > /dev/null 2>&1

01 15 * * * /usr/bin/find /home/jovyan/opensarlab-notebook_testing/reports -name "*.txt" -type f -mtime +7 -delete

20 15 * * * /usr/bin/find /home/jovyan/opensarlab-notebook_testing/keep_OSL_alive -name "keep_alive*" -type f -mtime +0 -delete

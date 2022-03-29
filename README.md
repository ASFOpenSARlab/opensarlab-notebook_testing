# asf_jupyter_notebook_testing
OpenSARlabs notebook testing module and notebook test scripts

Clone the repo into /home/joyvan

git clone https://github.com/ASFOpenSARlab/opensarlab-notebook_testing.git opensarlab-notebook_testing


The test suite requires the following directories and files to be set up:


/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev

/home/jovyan/opensarlab-notebook_testing/notebook_testing_logs

/home/jovyan/opensarlab-notebook_testing/notebook_testing_logs/old_logs

cd /home/jovyan/opensarlab-notebook_testing/notebook_testing_logs/old_logs/

touch test.log

/home/jovyan/opensarlab-notebook_testing/reports

/home/jovyan/opensarlab-notebook_testing/keep_OSL_alive



To run the test script manually, I like to use the following command so runtime errors are recorded:

cd /home/jovyan/opensarlab-notebook_testing

source mamba_test_driver.sh 2> errors.txt


Setup for cron to run mamba_test_driver.sh (Note: This requires sudo access in OSL):

1) Start an instance of OpenSarlabs in Amazon Workspace (this is necessarry to keep the instance open through internet outages and other interruptions).
2) Open a terminal in OSL
3) sudo apt update
4) sudo apt-get install cron
5) sudo service cron start
6) crontab -e
7) Enter the following in the crontab:

DATEVAR=date +%Y%m%d_%H%M%S

*/30 * * * * echo $(date)  > /home/jovyan/opensarlab-notebook_testing/keep_OSL_alive/keep_alive$($DATEVAR).log 2>&1

PATH=/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/opt/conda/bin

SHELL=/bin/bash

25 14 * * * source /home/jovyan/opensarlab-notebook_testing/mamba_test_driver.sh > /dev/null 2>&1

01 15 * * * /usr/bin/find /home/jovyan/opensarlab-notebook_testing/reports -name "*.txt" -type f -mtime +7 -delete

20 15 * * * /usr/bin/find /home/jovyan/opensarlab-notebook_testing/keep_OSL_alive -name "keep_alive*" -type f -mtime +0 -delete

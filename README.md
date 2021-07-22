# asf_jupyter_notebook_testing
OpenSARlabs notebook testing module and notebook test scripts

The test suite requires the following directories to be set up:
/home/jovyan/opensarlab-notebook_testing/notebook_testing_dev
/home/jovyan/opensarlab-notebook_testing/notebook_testing_logs
/home/jovyan/opensarlab-notebook_testing/notebook_testing_logs/old_logs
/home/jovyan/opensarlab-notebook_testing/reports

Setup for cron to run test_driver.sh (Note: This requires sudo access in OSL):
1) Start an instance of OpenSarlabs in Amazon Workspace (this is necessarry to keep the instance open through internet outages and other interruptions).
2) Open a terminal in OSL
3) sudo apt update
4) sudo apt-get install cron
5) sudo service cron start
6) crontab -e
7) Enter the following in the crontab:
# Write a file every 30 minutes to keep OSL instance active
DATEVAR=date +%Y%m%d_%H%M%S
*/30 * * * * echo $(date)  >> /home/jovyan/opensarlab-notebook_testing/keep_OSL_alive/keep_alive$($DATEVAR).log 2>&1
# Remove the keep alive log files that are more than 1 day old
45 11 * * * find /home/jovyan/opensarlab-notebook_testing/keep_OSL_alive -name  "keep_alive*.log" -type f -mtime +1 -delete
# Run the test script every day at 10:05 AM UT (05 10 * * *) Switched to 45 10 * * * today
PATH=/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/opt/conda/bin
SHELL=/bin/bash
45 10 * * * source /home/jovyan/opensarlab-notebook_testing/test_driver.sh > /dev/null 2>&1
# Delete reports more than 7 days old
01 0 * * * /usr/bin/find /home/jovyan/opensarlab-notebook_testing/reports -name "*.txt" -type f -mtime +7 -delete

# **ASF Jupyter Notebook Testing**

This repository entails a notebook testing module and a notebook test scripts OpenSARlabs. 

The tests are designed to be run in an instance of OpenSARlab.

### _Table of Contents_

1. [**Getting Started**](#getting-started)
2. [**Running Test (Auto)**](#running-test-auto)
	- [**Generate `.netrc` File**](#generate-netrc-file)
---

## **Getting Started**
---

Before running the test scripts, you will need to setup an environment.

_Prerequisite: You will need to install Git. Refer to the [official documentation](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) for how to install Git on your system._

To setup the environment, follow these steps:

1. **Go to [OpenSARLab](https://opensarlab.asf.alaska.edu/)**.
	1. If this is your first time, sign up for an account.
	2. If you have an account, sign in.
	3. Once you're in start the OSL server.

2. **Clone repository in your OSL account**.
	1. Open a terminal in your OSL account.
	2. Make sure that you're on the following path: `/home/joyvan`.
	3. Run the following commands to clone the `opensarlab-notebook_testing` repository:

	``` bash
	git clone https://github.com/ASFOpenSARlab/opensarlab-notebook_testing.git opensarlab-notebook_testing
	```

	_**Note: Clone via `HTTPS` instead of `ssh`.**_

---

## **Running Test (Auto)**
---

This section will introduce users to running automated test scripts.

### **Generate `.netrc` File**
---

Before running the automated tests, you will need to generate a *`.netrc` file. Below are the steps on how to generate the `.netrc` file.

![nav to `opensarlab-notebook_testing`](img/test_script_osl-test-nav.PNG)

1. First, you will need to navigate to the `opensarlab-notebook_testing` directory via the left-hand panel. 


![find and open `.netrc`](img/test_script_osl-make_netrc.PNG)

2. Once you're in the cloned repository, locate the `make_netrc.ipynb` and open the notebook.

![run `make_netrc.ipynb`](img/test_script_osl-cred.PNG)

3. Run the `make_netrc.ipynb` notebook and enter valid [Earthdata](https://www.earthdata.nasa.gov/) credentials.

_*Note: A `.netrc` file is required for some of the notebooks that are run by the test script._


---

To do a test run against production OSL, you should be in the `master` branch of `/home/jovyan/notebooks` and the `main` branch of `/home/jovyan/conda_environments`.

If a feature branch of notebooks or conda_environments needs to be tested, switch into that branch before running the `mamba_test_driver.sh` script.


---

To run the test script manually, I like to use the following command so runtime errors are recorded:

	cd /home/jovyan/opensarlab-notebook_testing

	source mamba_test_driver.sh 2> errors.txt
	
If the test script fails to complete, check /home/jovyan/opensarlab-notebook_testing/errors.txt to figure out what went wrong.

The test script should run to completion. When it finishes, check the report in /home/jovyan/opensarlab-notebook_testing/reports for lines that do not include 'PASSED'.

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

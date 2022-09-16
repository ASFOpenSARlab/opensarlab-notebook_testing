# **ASF Jupyter Notebook Testing**

This repository entails a notebook testing module and a notebook test scripts OpenSARlabs. 

The tests are designed to be run in an instance of OpenSARlab.

### _Table of Contents_

1. [**Getting Started**](#getting-started)
2. [**OSL Configuration**](#osl-configuration)
	- [Generate `.netrc` File](#generate-netrc-file)
	- [Testing Preparation](#testing-preparation)
3. [**Utilizing Test Script**](#utilizing-test-script)
	- [Running a Test Script](#running-a-test-script)
	- [Test Results](#test-results)
4. [**Individual Test**](#individual-test)
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

## **OSL Configuration**
---

This section will introduce users to setup a testing environment in OpenSARLab.

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

### **Testing Preparation**

---

To use a test script in OSL, make sure that the directory you are going to test is in the right branch.

#### **Testing on Production**

This test script will allow you to test two of our main directories: `notebooks` and the `conda_environments`.

To do a test run against production OSL, make sure that you are in:

- `master` branch of `/home/jovyan/notebooks` 
- `main` branch of `/home/jovyan/conda_environments`

#### **Testing New Features**

If you happen to add new features on a separate branch, make sure to switch to that branch before testing `notebooks` or the `conda_environments`.

*Example:*

Let's say that you have a new branch called `insar_update`, where it has additional packages included in your `conda_environments/Environment_Configs/insar_analysis_env.yml`.

In order to test this, you will need to first switch into `insar_update` branch in `/home/jovyan/conda_environments` with following command:

``` bash
git checkout insar_update
```

Once you are in the correct branch, you should be able to run your test script.

---

## **Utilizing Test Script**

---

In this section, we will introduce you to running a test script.

---

### **Running a Test Script**

---

To run the test script manually, use the following commands so the runtime errors are recorded:

``` bash
# command 1: Change into test 
cd /home/jovyan/opensarlab-notebook_testing

# command 2: Run test script; record its result
source mamba_test_driver.sh 2> errors.txt
```

---	

### **Test Results**

---

#### **Test Script Failure**

If the test script fails to complete, check the generated log file located here: 

``` bash
/home/jovyan/opensarlab-notebook_testing/errors.txt
```
Inspect `errors.txt` to determine what went wrong.

#### **Test Script Completion**

The test script should run to completion. When it finishes, check the following location for the report:

``` bash
/home/jovyan/opensarlab-notebook_testing/reports
```


When looking at the report, you will need to look for lines that do not include `'PASSED'`.

Investigate any tests that resulted in `'FAILED'` or `'EXCEPTION'`.

---

## **Individual Test**

---

It is often useful to run individual test scripts. To do so, the appropriate conda environment must be installed and activated.

_Example_

Run the following commands on terminal:

``` bash
# command 1: Move into testing repo
cd /home/jovyan/opensarlab-notebook_testing/

# command 2: Activate proper conda environment
conda activate /home/jovyan/.local/envs/rtc_analysis

# commaned 3: Manually run python test script
python3 Test_Ecosystems_Ex1.py
```


Alternatively, the test script can be set up to run on a cron in an instance of OSL running in Amazon Workspace.
Setup for cron to run `mamba_test_driver.sh` (Note: This requires `sudo` access in OSL):

1) Start an instance of OpenSarlabs in Amazon Workspace (this is necessarry to keep the instance open through internet outages and other interruptions).
2) Open a terminal in OSL
3) Run the following commands:
``` bash
# command 1: Make new directory 
mkdir /home/joyvan/opensarlab-notebook_testing/keep_OSL_alive

# command 2: Update everything you have
sudo apt update

# command 3: Install cron
sudo apt-get install cron

# command 4: Activate cron
sudo service cron start

# command Use cron
crontab -e
```
4) Enter the following in the crontab:

``` bash
DATEVAR=date +%Y%m%d_%H%M%S

*/30 * * * * echo $(date)  > /home/jovyan/opensarlab-notebook_testing/keep_OSL_alive/keep_alive$($DATEVAR).log 2>&1

PATH=/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/opt/conda/bin

SHELL=/bin/bash

25 14 * * * source /home/jovyan/opensarlab-notebook_testing/mamba_test_driver.sh > /dev/null 2>&1

01 15 * * * /usr/bin/find /home/jovyan/opensarlab-notebook_testing/reports -name "*.txt" -type f -mtime +7 -delete

20 15 * * * /usr/bin/find /home/jovyan/opensarlab-notebook_testing/keep_OSL_alive -name "keep_alive*" -type f -mtime +0 -delete
```
# SPORTS INVENTORY

SPORTS INVENTORY is a web applicationd build to act as one stop to view different sports and equipment required for that particular sport. A user can register into the application using google auth or G signin and add new sports and their equipments or edit their exisiting information.

-----------------------------------------------------------------
## INTRODUCTION:
* The application is built using python micro web framework - FLask, for database connection and maintainence used SQL ALchemy, Google OAuth2.0 for authentication and authorization. 
-------------------------------------------------------------------

## TO RUN APP LOCALLY:
* The project comes with VM file which has python, oauth, http libraries to run the web application.You can install [vagrant](https://www.vagrantup.com/) and [virtualbox](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1), here.
* Install git bash from https://git-scm.com/downloads based on your OS. (For windows git provides git bash to do unix shell).
-------------------------------------------------------------------
### STEPS TO CONFIGURE VM
1. Clone this project.
2. Navigate to downloaded project folder in your system using terminal/ git bash for windows.
3. In project you will find a vagrant file which is used to configure VM. 
#### NOTE: (vagrant file is important to configure/interact with VM).
4. Follow below steps to setup and use VM.
   * Start up virtual machine using vagrant up.
   * Once up to log into newly installed VM using vagrant ssh.

#### RUN APPLICATION
* After logging into vm,
  1. Navigate to catalog folder.
  2. Run "python database_setup.py" to create database setup locally.
  3. Run "python application.py" to run our web application, which runs on localhost:8000 by default.

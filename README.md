## Youtube Watchman - Personalized Dashboard Application

### 📝 Quick Notes

* How to run(_for development or local testing_):
    * Clone the repo
    * Create python virtual environment
    * Install backend packages using `pip install my-requirements.txt` also `dot-env` for .flaskenv files
    * Install frontend packages using your favourite package manager inside the `frontend` folder
    * Create env files `.env` and `.flaskenv`(_If want to run flask using `flask run`_) for backend also add client_secret files in root directory(this is problem, I have mentioned in next point).(Note for me- what environment variables are required to run, I will tell later. Also, separate, local and deployed env variables files so that same source code, with changed env. variables run different environments)
    * Create env file for frontend, add client_id of your google console application. (Note for me- make global env file from which frontend and backend could pick variables, as they are common to both, so why create separately for them)
    * Start backend and frontend servers and enjoy...

* Use `main` branch for development
    * Includes `frontend` folder for frontend development
* Use `deploy` branch for deployment
    * Contains `.ebextensions` folder for aws-EBS deployment
    * Consider looking at `aws-deploy.txt` for instructions

* Tip: 
    * Consider having seperate env files for development and deployment
    * Roughly, dev env file would contain db and website details of `localhost` and deploy env file would
        contain deployed db and website environments(_shh.. its a top secret_ :) )

* Lastly, feel free to report improvements through issues or PR tab. Most probably, I respond within 1-2 days. Also, don't forget to star this repo. if you find this interesting. 

__Happy coding :)__
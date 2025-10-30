# Week 2: Shifting to backend development via Flask

**Summary:**  
- Built a basic backend for Filefly to use in the web app stage
- Refined code for further adaptibility and compatibility while running and (possibly) sharing


*Wednesday, 10/29/2025*, _6:58 PM_

"Traceback (most recent call last):
  File "c:\Users\yodiw\Workspace\Filefly\backend\main.py", line 271, in <module>
    with open("config.json", "r") as f:
FileNotFoundError: [Errno 2] No such file or directory: 'config.json'"
-- Filefly

The above error is me trying to get config.json to behave itself so that its list of watch_folders can be imported into main.py without having to hard code anything. For now, the watch_folders will be Downloads and Documents, but later on, the user can probably ask the backend to include other folders as well. Speaking of backend, the target for this week has to be the Flask API that I'm going to try to turn Filefly into. Afterwards, anything is possible. Filefly could either be a web application complete with a browser extension or an automated daemon that does the heavy lifting even when you're not thinking about it!

So as of right now, I'm focusing on the OOP principles that I've learned by trying to refine a draft for a load_config method that I made to remove these issues. I'm also moving everything into the backend movement that's upcoming, so I'm going to definitely reframe my existing logic to keep in touch with that.

# Steps of This Week

1. Create and design a /backend directory (later to be equipped with core methods, API calls, and more) to group backend-related files and reframe automation for a daemon-like approach.
2. Draft a bare-minimum version of the Flask API backend.
3. Start writing a requirements.txt file that can notify other users, should there be any, of any essential libraries that Filefly uses to sort the system's files.

I tried to run an updated version of the code that would import and otherwise initiate the config.json for main.py's assorted lists. When I stumbled upon this, however, I did a double take from how it needed a surefire way to scan for config.json consistent in the DownloadsHandler() class as well - especially if we were going to import this to any app at all - since consistency is key for these types of applications.

"Traceback (most recent call last):
  File "c:\Users\yodiw\Workspace\Filefly\backend\main.py", line 300, in <module>
    event_handler = DownloadsHandler()
  File "c:\Users\yodiw\Workspace\Filefly\backend\main.py", line 97, in __init__
    with open("config.json") as f:
FileNotFoundError: [Errno 2] No such file or directory: 'config.json'"

The error took me to line 97, where the config.json importing method was still the same as if the new config handling method didn't exist. Luckily, I dove deeper into config handling (learning config for the load_config method's purposes taught me a good amount of json) and was able to replace

    with open("config.json", "r") as f:

    config = json.load(f)

with

    config = load_config()

    watch_folders = config["watch_folders"]

and it ended up being just what the doctor ordered. Filefly actually pops off when it comes to a multitasking approach to files - renaming, moving, tracking and extracting files all at once - and it reminds me why its current mind could go literally _anywhere._ The current backend logic was working out amazingly so far, and we could now move into the scalability portion of the backend - sponsored (with documentation instead of money) by Flask.

(go to https://flask.palletsprojects.com/en/stable to pick up YOUR Flask documentation **today!**)

```
Filefly/
│
├── backend/
│   ├── main.py               # my file watcher logic
│   ├── config.json
│   └── app.py                # new Flask backend (we’ll start this)
│
└── web/
    ├── static/               # (optional later) JS, CSS, etc.
    └── templates/            # HTML pages
```
^ Concept folder structure for Filefly

Drafting the Flask automation backend taught me quite a few key ideas about Flask's simple yet powerful backend endpoints:

- Flask(__name__) (The core of Flask, creating the app.)
- @app.route("/status") (Defines a _route_ — a web address that triggers a function.)
- jsonify(...) (Sends Python data as JSON (so browsers & APIs can read it).)
- threading.Thread(...) (Lets Flask and Filefly run at the same time. )
- debug=True (Enables auto-reload when you change code (only in dev mode).)

This subtle start had gotten my toes dipped in the waters of backend development, and it's going to prove useful no matter what I choose to do next. In fact, as I'm typing this sentence, I'm thinking about the applications of using Flask, PostgreSQL, Pandas and/or Matplitlib in tandem to shape a complex backend - next steps could include the frontend in the web folder, too.

A requirements.txt file is a list of requires libraries that a program needs in order to run properly. For example, you need gas from your local gas station, a (legally bought) car, car keys, and a driver's license of some sort in order to drive a car; all of the prerequisites are the "requirements.txt" of driving. My requirements.txt will be able to rely on the following libraries to be installed on the system so that the core logic in main.py can run smoothly with the rest of the backend:

- Flask (core)
- Watchdog (core)
- py7zr (utility and file handling)

**Review of concepts (AEM) on this week's changes:**

- Abstraction: Focuses on the bigger picture via hardcoding removal in main.py. Improvements could be made in app.py's scripting basics and methods in order to point to routing's applications as opposed to routing's complexities (which could be useful if I were to call app.py's methods from another file). 7/10.
- Encapsulation: Great usage of OOP in implementing essential methods in main.py AND app.py. Improvements could be made in allowing main.py to be more easily imported later. 9/10.
- Modularity: The changes this week were great in organizing the frontend and backend for the first time. Improvements could be made in implementing Flask itself (perfect for a later episode). 8/10.

**Possible future focuses:**
- Start touching up the frontend for the Flask web application
- Use JSON logs (learning more JSON) to promote logging and transparency as Filefly logs what it does
- Use either Pandas or matplotlib to display analytics - some retrospective, some in real-time - which provide insight to the user

### Reflections & Takeaways
- Flask is a simple yet powerful backend development tool that allows developers to demo their website's overall backend capabilities before deployment.
- Hardcoded statements in multifaceted projects does more harm than good - replace these with adaptible files and methods instead.
- A requirements.txt file is a great way to simplify the deployment phase of your project, even if you start writing it up before then.

Overall, this week was pivotal in organizing the project for the first time. The main.py file was freed of certain hardcoded statements, a basic backend was created and proved to be working, and a requirements.txt file was created and started up for future reference in allowing other users in the future to use my project. This was overall a successful week in my learnings as well, and learning about Flask's many basic capabilities and commands had me remembering for at least half the time how much I still have to learn - and I pursue it! This is not to say that it's all downhill from here, but it _is_ to say that I'm ready for the mountain ahead. At the end of the day, planting Filefly's flag on the peak of the summit will definitely be worth all of the nerdiness (occasional or constant - you decide). Filefly, sign this one off.

```
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.1.159:5000
Press CTRL+C to quit
```
-- Filefly, **10/29/2025,** _9:06 PM_

Warm regards, and God bless you,

^ OtterShot
# Week 3: Developing a backend in more depth

**Summary:**
- Started up an idea of how I want the frontend and backend to work together later
- Migrated the previous print() logging messages to messages using the built-in logging library

*Friday, 11/7/2025*, _3:17 PM_

```
def get_safe_path(dest_folder, filename):
    path = Path(filename) suffixes = path.suffixes # e.g. ['.tar', '.gz']
    ext = "".join(suffixes).lower() # ".tar.gz"
    name = path.name[:-len(ext)] if ext else path.name # Filename without ALL suffixes; strips ALL suffixes, not just one

    counter = 0
    while True:
        suffix = f"({counter})" if counter > 0 else ""
        new_dest_path = os.path.join(dest_folder, f"{name}{suffix}{ext}")

        # Check case-insensitively to avoid false collisions
        if os.path.basename(new_dest_path).lower() not in {f.lower() for f in os.listdir(dest_folder)}:
            return new_dest_path # found a safe, unused name
            counter += 1
```
-- Filefly, _backend/main.py_

I was preparing my pupils for a staring contest with the block of code you just saw.

So if I wasn't blinking, then now you know why. If you noticed differences in this get_safe_path() compared to the previous one, then your eyes must have been looking while I was so focused on staring! I was attempting to fix a petty bug in the file renaming part of the method since EVERY SINGLE file that was entered inside of the process to be downloaded and moved was instantly getting a timestamp no matter what. Every single file.pdf would become file(1).pdf, even with no duplicates whatsoever. This is where I had to look closer in the if statement driving this, and I found my problem there. The condition was making it such that the file was being downloaded into the same destination folder, so at the time of the check, the code sees the perfectly harmless pre-move and marks every file as a collision waiting to happen. I was able to fix this by updating the conditional logic as such - based on the following previous insight inside of the former get_safe_path():

"The new_dest_path declared and initialized in the while loop uses string concatenation to map suffixes to file types, because certain file extensions such as .tar.gz have multiple dots. The while loop's os.path.join() usage can be corroborated with ext's declaration and initialization earlier on in this method, in the sense that both are joining matching suffixes together in order to properly associate files with these file types."
-- Me, _pre-week1 while drafting the project_

The description above was probably ANOTHER TANGENT, because I realized that I had added the documents folder to be one of my watch folders. HOWEVER, I had only intended the Documents folder to be used as a watch folder if users drag and dropped their heaps of files inside of the downloads folder itself instead of its subdirectories! (The Downloads folder basically never has any subdirectories if it's managing files and not the sorting of multiple folders, and the documents folder was made to allow Filefly to move files inside of the subdirectories with users leaving their files "at the door.") With this crucial eureka (now I know where the head lightbulbs come from) I hurried to main.py and edited its recursion call:

```
    watch_folders = [os.path.expanduser(path) for path in config.get("watch_folders", ["~/Downloads", "~/Documents"])] # Default watch directories listed; can be expanded in config.json
    event_handler = DownloadsHandler()
    observer = Observer()
    for folder in watch_folders:
        os.makedirs(folder, exist_ok=True)  # Create folder if missing
        observer.schedule(event_handler, path=folder, recursive=False)
```  
Now that recursive=False, subdirectories will be ignored by the observer.

So now I had a smarter timestamping algo on top of a destination folder awareness and case-insensitivity that I acquired on the way there. In other words,
Job well done - bug well patched. (^_^)
Which leads us to this week's round of bug fixes, building and learning. Still got those observational eyes? Lookie here - just let me go blink for a second - 

# Steps of This Week

1. Fix bugs inside main.py that may degrade how Filefly performs as a daemon (._.)
2. Start developing a basic version of the frontend (.html, .css) to see how both the front and back work together (-_-)
3. Learn how to move into JSON logging (._.)

So when I use Filefly, the introductory bug was definitely the main beef that I had going on as of writing this. Since that's over, however, we should move into how the entire project functions as a daemon. Since the goal of this is to get this into the background of people's computers, we would need to stabilize the log messages and reform the file timestamping so that we could do this. Along with the get_safe_path, I tried to implement the following so that file names would reserve and the timestamping error from before doesn't happen again:

```
try:
    with open(safe_path, "xb") as f:
        pass  # reserve the filename atomically
    except FileExistsError:
    # Another process created the same file — regenerate a new safe path
        safe_path = get_safe_path(dest_folder, filename)
```

There was still another problem, though - anytime the code inside of the try/except block ran, a NameError would pop up because i was referencing safe_path before assignment if I was putting it before the while True: loop. Luckily, I found that the problem wasn't outside the box, it was inside the loop, so I indented the try/except atomic creation snippet into while True. Inside the while True: loop, and situated in get_safe_path(), small yet consistent and powerful changes started to take place.

Speaking of small changes, I was able to build a place for Flask (last week) to run when I deploy Filefly for the public. The backend so far is already promising to do some great things, and I can't wait to see how this goes along with the _frontend_, since they both go hand-in-hand for web applications. The actor-director relationship between the frontend-backend is a real thing, and I started to get both sides of the same coin by drafting a simple styles.css for the website to develop a starter color scheme of sorts:

```
/* Body styling */
body {
    font-family: Arial, sans-serif; /* Sets a basic font */
    margin: 20px; /* Adds space around the content */
    background-color: #f0f0f0; /* Sets a light gray background */
}

/* Heading styling */
h1 {
    color: #333; /* Dark gray color for the heading */
    text-align: center; /* Centers the heading text */
}

/* Paragraph styling */
p {
    color: #666; /* Lighter gray color for paragraphs */
    line-height: 1.6; /* Improves readability of text */
}
```

I imported the changes reflected here into a starting html file:

```
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Filefly | Fly through file management</title>
    <!-- Link to your external CSS file -->
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <h1>Filefly</h1>
    </header>
    <main>
        <p>Welcome to your file management solution!</p>
    </main>
    <footer>
        <p>&copy; 2025 My Basic Website</p>
    </footer>
</body>
</html>
```

The crucial setup allowed so that any time I ever want to work on either the frontend or the backend, I can jump straight to learning. This is going to be crucial later, and the project's potential role is really starting to make sense, especially with _app.py_'s improved presence:

```
# Made by Yodahe Wondimu
# Welcome to the backend of Filefly.
# The stage sets, and the curtains are pulled aside...

from flask import Flask, jsonify, render_template, send_from_directory
import threading
import time
import json
import os

# Create Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")

# Load config file
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("[Notice] config.json not found, using default watch folders (Downloads & Documents)")
        return {"watch_folders": ["~/Downloads", "~/Documents"]}

config = load_config()

# Runtime status
filefly_status = {
    "active": True,
    "watched_folders": config.get("watch_folders", []),
    "moved_files": 23 # Placeholder value, change to 0 when implementing script.js
}
...
```

Run app.py on the first try, and the result is...
not a drumroll, it's this:

```
Traceback (most recent call last):
  File "C:\Users\yodiw\Workspace\Filefly\.venv\lib\site-packages\flask\app.py", line 1536, in __call__
    return self.wsgi_app(environ, start_response)
  ...
jinja2.exceptions.TemplateNotFound: index.html
```

What should all of this mean? I wasn't sure. But I was willing to find out. (I'm talking to you, _bugs._) After digging on the link **https://www.pythonanywhere.com/forums/topic/29069** out of curiosity, they highlighted something about Flask that was definitely worth noting:

"render_template does not take a file path. It takes a template name. Then Flask looks for that template in the template search path. Make sure that you've set the template search directory correctly (i.e. with an absolute path) using the template_folder argument when you create your Flask object: https://flask.palletsprojects.com/en/1.1.x/api/#application-object"
-- glenn, _pythonanywhere.com_

Thank you, glenn! So what the forum was telling me was that I had to go in and tell app.py to expect the static files to come from a certain folder, in this case the new one named "static". On top of this, we don't even need a templates folder yet until we use React/JS for the _dynamic_ frontend, and I was just aiming to get a _static_ frontend going so that I could learn from mistakes like this.

NEVER MIND (>_<), it needs a templates folder. (TemplateNotFound)

NEVER MIND AGAIN (TemplateNotFound) (ಠ_ಠ), it also needs the folders reframed so that there’s maximum consistency between directories. I had to move quite a few folders around (keep in mind that this project is a _FILE MANAGEMENT_ DAEMON) to get what Flask was looking for just right, and I had to think real hard when I got the same TemplateNotFound error a few times afterwards - "Wait, so index.html is supposed to be in a separate folder from styles.css?" - and got a file structure that worked. I mean, am I the _only_ person that sees the irony in repetitively moving files inside of a program designed to repetitively move files?

After contemplating whether I should get Filefly to basically move its own files, I realized that I had a very up-to-date communication system down, especially when I get to learn React/JS later (more documentation, yay!). The next thing on our agenda was learning how to do logging with JSON, which basically meant that I had to convert all of the print messages in main.py previously used for debugging into plausible logs that would simulate how it would actually log as a daemon.

In other words,
The first change was to increment the moved file count whenever a file is moved and update it on the dashboard.
The second one was communicating the runtime status and logs through JSON.

For the first one, a new update_status_file() universal method was made so that the main.py could interpret a new runtime_status.json file:
```
STATUS_FILE = os.path.join(os.path.dirname(__file__), "runtime_status.json")

def update_status_file(moved_files_count):
    status_data = {
        "active": True,
        "watched_folders": watch_folders,
        "moved_files": moved_files_count
    }
    with open(STATUS_FILE, "w") as f:
        json.dump(status_data, f, indent=4)
```

Other changes were made in other files just so that runtime_status.json would be initialized if not already, and that it could be set up to update in real-time later. But for now, check out this new logging configuration!

```
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("filefly.log"),  # saves logs to a file
        logging.StreamHandler()              # also prints to console
    ]
)
logger = logging.getLogger(__name__)
```

I learned that the logging library is able to save logs to a dedicated file and print the logs to the console for extended readability. With all of this in mind, you could probably tell that this was a very busy day in the program's development, but it was well worth it for the sake of initializing what will very well be a daemon one day. I can rank the AEM principles based on today’s changes:

- Abstraction

The bigger picture was well completed here. Smart variable usage and a file architecture that both me and Flask were happy with meant that my project would definitely be able to prove itself as a daemon later. However, there seems to be a lot of mumbo-jumbo concerning some of the library intricacies that I've looked through during my debugging endeavors, and I'll be sure to clear those up to focus on a state of making as well as learning.

*8/10*

- Encapsulation

Classes and methods are working hand in hand right now, just as the frontend-backend relationship is going. Today was a lot of getting beaten down by errors and dusting off my shoulders via relevant solutions, so at least I know that the logging has gone according to plan. I would encourage myself to keep files safe from each other as the project grows in complexity, though, especially to prevent any race conditions that could dismantle how Filefly works as a potential daemon.

*7/10*

- Modularity

My files and changes are well sorted now, with everything being within easy reach and a standard architecture being crucial to keep imports, reads, and writes in check. However, one thing that I have to manage right now is the version control, so that each branch is able to carry out its desired commits without muddling up GitHub, so I'm going to have to work on my version control skills a bit more - especially if I get this thing deployed.

*6/10*

**Potential Focuses for Next Week:**
- Refine the frontend by getting _styles.css_ to import and be used perfectly every time
- Manage the version control of my project so that main and logs can display their changes correctly without errors that may occur when I merge branches
- Fix errors in my dashboard that could pop up from edge cases or redundant logic, and integrate analytics into it afterwards


### Reflections and Takeaways
- Learned to implement newfound libraries inside of my project while protecting it from potential race conditions
- Learned how React looks for and uses static and template files in order to build a dashboard
- Logger is a tool for both users and developers - users and developers can understand what the code did and improve the code based upon insights

Today was a great day in terms of learning, but it was SURE a lot to take in at once! I'm going to have to break apart the "why" behind things in future reviews, along with getting my AEM score up so that Filefly can become more streamlined and unified in its approach to files. So if anyone reading this is asking why I didn't restate the dashboard logic in a cleaner way while I was already at it, then we can simply lead them to look back at how much better my project has already gotten. Filefly, sign this one off.

```
2025-11-07 18:18:37,494 [INFO] Now watching ['C:\\Users\\yodiw/Downloads', 'C:\\Users\\yodiw/Documents'] for new files... (Ctrl+C to stop)
```
-- Filefly, _filefly.log_

Warm regards, and God bless you,

^ Yodahe
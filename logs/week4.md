# Week 4: Building up the web interface and stability

**Summary:**
- Refined the backend to keep the web dashboard accurate and reliable
- Improved the program's tracking of dashboard info

*Friday, 11/14/2025*, _5:12 PM_

```
base_dir = os.path.dirname(os.path.abspath(__file__))
```

-- Filefly, _web/app.py_

One thing that makes Filefly special is that it is able to extract the truth on files. Currently, it is able to use a web dashboard to display its stats on the folders being watched, the amount of files moved, etc. As of right now, however, certain work could be done in order to keep this accuracy throughout the entire repo. What I was trying to implement, for instance, was a status file after the base_dir initialization, which would make it so that the web dashboard and the daemon itself wouldn't pull their data from different places. What I wanted to learn this week was how to make it so that I could make sure that both pull this definition from the same places. After remembering that I had a handy os.path.join() method available to use, I got to work and defined the status_file:

```
status_file = os.path.join(base_dir, "runtime_status.json")
```

Now that that's down, app.py can make sure that it pulls its status updates from the same place as main.py. Good work so far!

# Steps of This Week

1. Improve overall stability and reliability of the web dashboard
2. Refine the temp file tracking process in core logic
3. Improve the core logic of status_files (it's almost like I was foreshadowing!)

As of writing above, I had simply wanted to work towards something small that could combine with other small changes to bring results. Slow change is steady change, especially with a system like the current one. What I definitely want to work towards, however, is the sleek backend - keeping its dashboard reliable is going to be great for bringing other systems into using Filefly later. The problem with this, however, is that the dashboard doesn't always look the cleanest so far. Most of the time, it pulls two headings with stats instead of just one, and it can definitely confuse the user (I know I would be confused). In order to fix this, I looked into index.html and app.py to see what they were each calling for the dashboard and saw one call to displaying a status on index.html:

```
<body>
    <h1>Filefly Daemon Dashboard</h1>
    <p>Status: {{ 'Active' if status.active else 'Inactive' }}</p>
    <p>Files moved: <span id="moved-files">0</span></p>
    <p>Watching: <span id="watched-folders"></span></p>


    <!-- JS goes here -->
    <script src="{{ url_for('static', filename='script.js') }}"></script>

    <script>
    async function refreshStatus() {
        const response = await fetch('/status');
        const data = await response.json();
        
        document.getElementById('moved-files').textContent = data.moved_files;
        document.getElementById('watched-folders').textContent = data.watched_folders.join(', ');
        document.getElementById('status-active').textContent = data.active ? "Active" : "Inactive";
    }

    // Update every 5 seconds
    setInterval(refreshStatus, 5000);

    // Also run once immediately
    refreshStatus();
</script>
```

When compared to the one on app.py for reading the status:

```
def read_status():
    if os.path.exists(status_file):
        with open(status_file, "r") as f:
            return json.load(f)
    return {"active": False, "watched_folders": [], "moved_files": 0}
```

I tried to think about how I would go about this. Flask isn't a library that I'm too familiar with, but I did realize one thing about index.html - why was it there? We did not need a second section that would import the dashboard automatically, since Filefly's app.py already does this. Remember what I said about small changes? That really highlights one thing that I like about the project's design structure so far - in between scrolling through documentations trying to see which section will assist me and asking ChatGPT to quiz me on my own code, the best solutions are the simple ideas. Upon realizing this, I tore down the second section so that only one dashboard shows. The final, single-dashboard script section reads as follows, shortly after reframing the HTML to only call the JS that would update the dashboard:

```
<script src="{{ url_for('static', filename='script.js') }}"></script>

    <script>
    async function refreshStatus() {
        const response = await fetch('/status');
        const data = await response.json();

        document.getElementById('moved-files').textContent = data.moved_files;
        document.getElementById('watched-folders').textContent =
            data.watched_folders.join(', ');
        document.getElementById('status-active').textContent =
            data.active ? "Active" : "Inactive";
    }

    setInterval(refreshStatus, 5000);
    refreshStatus();
    </script>
```

So now only one dashboard, an accurate one at that, is ready for usage. Another thing that I've been thinking of is this core logic - since working on that status files pulled from two sources is squashing two bugs with one fix.

Next up was refining this logic by rephrasing certain methods (such as the one below) inside the DownloadsHandler class in main.py, just so that I could know what to work on later. It was fairly straightforward - just detecting more temporary download file extensions and restabilizing so that the code can still work for personal use (making Filefly one of the most automated things on my computer now).
```
def on_deleted(self, event):
        if event.is_directory:
            return

        path = event.src_path

        if self.is_temp_path(path):
            logger.info(f"Ignoring temp file delete: {path}")
            return

        if self.was_recent_auto(path):
            logger.info(f"Ignoring auto-move delete event: {path}")
            return

        if path in self.moved_files:
            return
        
        if path in self.active_files:
            logger.warning(f"File manually removed mid-process: {path}")
            self.active_files.discard(path)
            self.update_file_event(path, "manual")
            return

        logger.warning(f"File manually deleted or displaced: {path}")
        self.update_file_event(path, "manual")

```

Much easier to work with, especially for the download processes used by Chrome and Opera. The final reflections are as follows, as I've taken a step back so that I could understand how files work together. Here is the final file structure as an appendix for the file syncing improvements made this week. Take a look! (^_^)


```
project/
│
├── app.py
├── daemon.py
│
├── templates/
│   └── dashboard.html
│
└── static/
    ├── style.css
    └── script.js
```

Time to get to the AEM principles, based on this week's calm set of foundations:

- Abstraction

The bigger picture of some possible next steps is dependent on whether or not I get other changes out. I am relying on my code to be stable for the next set of changes, since they can be crucial in refining the current files into something that could be usable in the future.

*7/10*

- Encapsulation

The sections are going well right now. The status updates being called correctly definitely removed potential race conditions - a pretty big win for a daemon in a week - but I would also want to work on making sure that .html and .css call each other effectively.

*8/10*

- Modularity

The architecture hasn't changed and is remaining stable. However, certain future changes such as dark mode will require a lot more learning about underlying interactions between files and libraries, so I will need to push this project outside of its comfort zone more and more each week.

*6/10*

**Potential Focuses for Next Week:**
- Focus on making light mode and dark mode something that users can toggle between
- Patch log messages that still log certain downloaded files as "manually deleted or displaced" even after checking for temp files
- Clean up app.py a little bit so that it can display additional stats and insights as necessary


### Reflections and Takeaways
- A clean architecture allows you to save a lot of time debugging when moving forward, because each section is in its proper place
- Learned how powerful the simple solution is when solving a problem
- HTML, CSS and JS are a powerful trinity of web development - learn these, and you know how to connect files together as an added bonus

I liked the changes made today, because they really highlighted how great Filefly would be as a daemon. In future weeks, I can start to push this project outside of its comfort zone more and more, perhaps in one subject field per week or so, so that it can accomplish more things. Little changes are big changes, because they bring consistent growth that I can't wait to see. (That's just one of the extra perks of having no deadline!) Filefly, sign this one off.

```
<script>
    // auto-refresh status
    async function refreshStatus() {
      const res = await fetch("/status");
      const data = await res.json();
      document.getElementById("moved-files").textContent = data.moved_files;
      document.getElementById("watched-folders").textContent = data.watched_folders.join(', ');
      document.getElementById("status-active").textContent = data.active ? "Active" : "Inactive";
    }

    setInterval(refreshStatus, 5000);
    refreshStatus();
  </script>
```
-- Filefly, _index.html_

Warm regards, and God bless you,

^ OtterShot
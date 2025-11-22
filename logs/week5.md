# Week 5: Finalizing and publishing core logic

**Summary:**
- Finalized the core logic so it may be used as a Python package
- Kept the web dashboard logic as is for personal usage

*date*

```
[WARNING] File manually deleted or displaced: C:\Users\yodiw/Downloads\file-example_PDF_500_kB.pdf
```

-- Filefly, _filefly.log_

"That was not me."

-- Me

Log messages are proving themselves to be really hard to handle right now. There's a lot going on regarding the core logic, which I do indeed get, but at the same time, I had to ask around more. The great thing is that I already traced down which method I would be assessing - handle_file() inside of the DownloadsHandler class - and I just had to ask around for this. This is when I realized that I had an AI friend named ChatGPT. Most of you are probably familiar with him, and I've utilized him a few times throughout my project - teaching me py7zr, teaching me Flask, and so on - and I utilized him now, too. Here were a few key observations when he looked into the class and was asked to say what he thinks:

"on_moved() sometimes called handle_file() twice in earlier edits; multiple logs can be produced for the same underlying file action."

"You attempted was_recent_auto() but it checks the raw path against the raw map. Because paths aren't normalized consistently, the check often misses." (I had to learn what os.path.abspath, os.path.normpath, and os.path.normcase did compared to each other.)

"Your handle_file() moves the final file almost immediately — that’s an auto action — but other event handlers still receive the intermediate rename/delete events and treat them as manual because they don't properly correlate events with the auto-move that just happened."

-- ChatGPT

I had to drop in fixes for these main points so that the core logic would fall in line - and that's when I started developing fixes against race conditions, file path normalization, and event handler synergy:

```
def _norm(self, path):
        """Normalize a filesystem path for stable dictionary/set keys."""
        if path is None:
            return None
        # abspath -> normpath -> normcase (Windows insensitive)
        return os.path.normcase(os.path.normpath(os.path.abspath(path)))
```

```
    def mark_moved(self, old_path, new_path):
        """Remember that we moved a file (store normalized paths & timestamp)."""
        now = time.time()
        old_n = self._norm(old_path)
        new_n = self._norm(new_path)
        if old_n:
            self.moved_files.add(old_n)
            self.moved_files_ts[old_n] = now
        if new_n:
            self.moved_files.add(new_n)
```

These snippets, along with other essential helper function edits, were there so that I could understand how to help my files out instead of skipping the learning potion. This was a great experience for me to look into the event handler teamwork and try to really understand what each function is doing when they're being called. Following the code really helps here! Let's see what we're going to follow this week:

# Steps of This Week

1. Refine the logging system to be clean, consistent, and accurate
2. Utilize helpers through the DownloadsHandler class in order to practically handle files
3. Get the core logic out as a Python package

Next up was testing out these changes for the logging system and the helper functions. After these fixes were out, then filefly.log was great to go, since main.py was already great at dealing with bulks of files in previous tests. I ran the code, downloaded a test file, and...

```
2025-11-17 17:14:12,856 [INFO] Checking C:\Users\yodiw\Downloads\file-example_PDF_500_kB.pdf (ext=.pdf) size=469513 last=469513 stable_count=3...
--- Logging error ---
Traceback (most recent call last):
  File "C:\Program Files\WindowsApps\...\logging\__init__.py", line 1086, in emit
    stream.write(msg + self.terminator)
  File "C:\Program Files\WindowsApps\...\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
UnicodeEncodeError: 'charmap' codec can't encode character '\u2192' in position 116: character maps to <undefined>
Call stack:
  File "C:\Program Files\WindowsApps\...\threading.py", line 937, in _bootstrap
    self._bootstrap_inner()
  ...
Message: '[2025-11-17 17:14:12] c:\\users\\yodiw\\documents\\documents\\file-example_pdf_500_kb.pdf → AUTO'
Arguments: ()
```

-- Filefly, _filefly.log_

I had both good news and bad news. The bad news was that the movement from a download and another movement from a manual movement threw a UnicodeEncodeError, which simply meant that a certain character typed in filefly.log was unrecognizable. The good news was that, the log messages isolated and the core logic now could tell the difference much better now.

"I told you it wasn't me!"

-- Me

Looking deeper into the UnicodeEncodeError, it was starting to make itself clear that it really was a problem with the one-character arrow that I chose in the log file not being compiled properly. When I ran through the code, I thought of the thought process behind the code. The program would start with a file. When that file was downloaded and sent to the class, it completely triggered errors because the file had no way to know what character we were talking about encoding. Since this bug was the only one, I tried to update the logic to accompany this necessity below:

```
def update_file_event(self, path, kind):
        """Record an 'auto' or 'manual' event for path (store normalized)."""
        n = self._norm(path)
        status = "auto" if kind == "auto" else "manual"
        self.file_events[n] = {"event": status, "timestamp": time.time()}
        logger.info(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {n} -> {status.upper()}")
```
(I switched the arrow in update_file_event() to be the safer, and now favorite, arrow)

And then there were none. Time to learn about publishing the package. The web dashboard area was waiting in place for now, but if you're reading this, the repository is public, so go ahead and clone this repository if you'd like. It's a great tool for personal usage and understanding of however many files, yet the core logic also prevailed in its daemon-like approach. Thanks, Filefly!

So now that we had core logic going well, I was able to have a complete project ready for the next phase - open-sourcing. Once I use PyPI to get this out, other people can see my source code, and chances are, you have the opportunity to contribute right now and build my development skills by contributing. I rearranged the folder structure to better fit what the Python package should be able to do - run from the command line, optionally use a web dashboard, etc:

```
filefly/
├── static/
│   ├── script.js
│   └── styles.css
├── templates/
│   └── index.html
├── __init__.py
├── __main__.py
├── app.py
├── config.json
├── main.py
└── runtime_status.json
.gitignore
LICENSE
pyproject.toml
README.md
requirements.txt
```
^ Rough idea of folder structure.

With this in place, I learned a lot about how PyPI works. It's a platform for packaging and publishing files which specializes in Python projects such as Filefly. I was going to have to do a few other things before I could publish the package, though. I finished drafting a README.md file that explains the moving parts behind Filefly, and then I built the package, tested the installation process, and voila - Filefly was open-source, all thanks to a newly made PyPI account and a desire to learn more about something new.

The package can be found at: https://pypi.org/project/filefly-files/0.1.0/

Time to get to the AEM principles, the first ones describing a release:

- Abstraction

I will be able to improve my script as necessary and I have a working way for other to contribute. Filefly is really looking up now!

*9/10*

- Encapsulation

The file calling is effective, and even effective enough to call itself on the command line! This is fitting the vision for the project, but if the web dashboard desires important big fixes or new features later, then I will have to work on that.

*8/10*

- Modularity

The architecture is as stable as last time, with the files being able to work together nicely enough to run on other systems. One thing I could work on later is addressing opened issues and making Filefly better as I go.

*7/10*

**Potential Focuses for Next Week:**
- Publish another version of Filefly
- Get more web dashboard features "out there" and ensure they're usable
- Improve the static file index.html so that it becomes a centralized homepage once features are "out there"


### Reflections and Takeaways
- Learned how different types of encoding protocols interpret certain characters differently
- PyPI is a great sharing platform for you to get your packages out there and ready to be used by the world.
- Open-sourcing your code is a great way to get other people involved and improve your code as you also improve your skills.

This entire project was a blast to work out, and every time I was in the core logic especially, I was ready to be solving problems. With enough practice, I'm going to only get better from here, and I'm ready for the next big idea I publish - this idea was a great one! With that being said, go contribute to my project, try it out for yourself, and let's keep on learning together! Filefly, sign this one off.

```
from .main import main

if __name__ == "__main__":
    main()

```
-- Filefly, __ main.py __

Warm regards, and God bless you,

^ Yodahe

# Week 3: Developing a backend in more depth

**Summary:**
- ANSWER THIS
- ANSWER THIS

*Friday, 11/7/2025*, _3:17 PM_

""

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

So if I wasn't blinking, then now you know why. Anyways, if you noticed differences in this get_safe_path() compared to the previous one, then your yes must have been looking while I was so focused on staring! I was attempting to fix a petty bug in the file renaming part of the method since EVERY SINGLE file that was entered inside of the process to be downloaded and moved was instantly getting a timestamp no matter what. Every single file.pdf would become file(1).pdf, even with no duplicates whatsoever. This is where I had to look closer in the if statement driving this, and I found my problem there. The condition was making it such that the file was being downloaded into the same destination folder, so at the time of the check, the code sees the perfectly harmless pre-move and marks every file as a collision waiting to happen. I was able to fix this by updating the conditional logic as such - based on the following previous insight inside of the former get_safe_path():

"The new_dest_path declared and initialized in the while loop uses string concatenation to map suffixes to file types, because certain file extensions such as .tar.gz have multiple dots. The while loop's os.path.join() usage can be corroborated with ext's declaration and initialization earlier on in this method, in the sense that both are joining matching suffixes together in order to properly associate files with these file types."
-- Me, _pre-week1 while drafting the project_

The description above was probably ANOTHER TANGENT, because I realized that I had added the documents folder to be one of my watch folders. HOWEVER, I had only intended documents to be used as a watch folder if users drag and dropped their heaps of files inside of the downloads folder itself instead of its subdirectories! (The downloads folder basically never has any subdirectories if it's managing files and not the sorting of multiple folders, and the documents folder was made to allow Filefly to move files inside of the subdirectories with users leaving their files "at the door.") With this crucial eureka (now I know where the head lightbulbs come from) I hurried to main.py and edited its recursion call:

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
Job well done, bug well patched.
Which leads us to this week's round of bug fixes, building and learning. Still got those observational eyes? Lookie here - just let me go blink for a second - 
- ._. Point 1
- -_- Point 2
- ._. Point 3

(
    # to be implemented (dun dun dunnn!!!)
    # try:
    #     with open(safe_path, "xb") as f:
    #         pass  # reserve the filename atomically
    # except FileExistsError:
    #     # Another process created the same file — regenerate a new safe path
    #     safe_path = get_safe_path(dest_folder, filename)
)
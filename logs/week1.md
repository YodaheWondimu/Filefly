# Week 1: Starting revision stage, checking over current draft

**Summary:**  
- Revising Filefly’s codebase using OOP design principles (abstraction, encapsulation, modularity)
- Assessed each aspect and planned improvements for scalability and user accessibility


*Friday, 10/24/2025*, _10:10 PM_

"[Info] Now watching ['C:\\Users\\yodiw/Downloads'] for new files...
(Ctrl+C to stop)"
-- Filefly

I'm looking through my code right now. I started this project as a simple main.py script which was able to organize my downloads, since I was bored with choosing a certain day of every month and treating it like laundry day for all of my missed work. Right-clicking a file, using ctrl+x, navigating to the desired folder, using ctrl+v, and repeating the process for what would sometimes be for dozens of files on end is tiring at best and mind-numbing at worst. I thought to myself that there's got to be an easier way - and humanity deserves one - and that's how Filefly was made. I named it "Filefly" as a tribute to Fireflies, which are going to go extinct after this generation. I wanted to make this the best tribute possible, so starting from the beginning of the school year, up until now, I've been hard at work developing what I believed to be one of my most creative projects that I've ever written, especially during that blessed September stretch of learning all of those libraries that I needed to know. I can't believe that it's already been 2 months of this project being written little by little, but now here we are.

Now, I'm looking at next steps that would be able to make this project much more usable in practice. The three principles of developing software from the ground up are what I like to call "AEM", because calling them this weird acronym means that you remember to "AEM" for their bullseye. On top of that, my AP Java class is teaching me how to use Object-Oriented Programming (OOP) to my advantage (therefore making it hands-down my favorite class), which I also tried to implement in this project. Each week that I work on these devlogs is a report card of sorts, and I'm using it to document what I do and don't find in my project to look for next steps (and maybe change the world with this?).

# Steps of This Week

1. Identify and assess Filefly's implementation of modularity.
2. Identify and assess Filefly's implementation of abstraction.
3. Identify and assess Filefly's implementation of encapsulation.

These 3 traits are genuine guidelines that I want to look up to, and they were even neat enough for universities like MIT, Harvard and Stanford to feature in _their_ curriculums. Sweet!

### **Abstraction:**

Allows developers to hide complex implementation details/mumbo-jumbo in order to focus on what sections of code actually do. All programmers, at least the ones with only 24 hours a day, want to implement multiple sections of code in lieu of each other in order to focus on the bigger picture. This was the hardest one for me to fully understand, because when I first heard the definition while reading "Breaking And Entering: The Extraordinary Story of a Hacker Called 'Alien'," (which was so insightful in assisting my projects now,) I wondered why complexity would be hidden if the point of debugging was to check over every detail. But then I fully got the grasp when I tried to imagine what this would be like, which made me realize that hiding the details may be worse in the _short run_ (when you're just starting a big picture), but will still be worth it in the _long run_ (when you have all of these moving parts to your work). I experienced this firsthand during the prior development of Filefly, when the humble main.py file and its trusty config.json went from just an initial commit to ALMOST 300 LINES OF CODE. I had to learn quickly that every single method had to be able to carry out its designed purposes with efficiency while interacting with other parts of the project as necessary. To sum all of this up, a lack of abstraction would start to paint the Mona Lisa by learning how to create paint, change it to it the desired color, and put it on the paint pallete. Abstraction allows developers to focus on outcomes rather than implementation details — much like an artist focusing on the composition rather than the chemistry behind the paint.

### **Encapsulation:**

Bundles attributes to the methods that operate on them. This goes back to OOP, because as I said before about what AP Java is teaching a lot of, it's the art of taking both data and predefined actions and encouraging them to use the buddy system. The added benefit of tying these features to each other is that it allows your code to be extra secure. Against hackers? Not necessarily. Against itself? Yes. Let me explain (in Java terms). When an object is instantiated from a class, that object will be created with the class's predefined attributes and methods. The class keeps the attributes to itself and only gives them to objects that are made with that class, and the class keeps the attributes to itself automatically because they can only be called on instances of the class to begin with, with the exception of static methods, which do not need an instance of the class in order to run. Remember, though, we do not need to think through the case where the methods are static, because we are in OOP, which is primarily objects made from classes that use methods to act on attributes. When these classes gatekeep against themselves, it prevents other classes from accidentally touching something that doesn't belong to it, which would be breaking the buddy system that each class unwrittenly agrees to. Encapsulation means making sure that each class listens to this pact by setting class variables as inaccessible if you're just using it willy-nilly, and keeping the software safe from itself.

### **Modularity:**

Defines how well I compartmentalize my programs into clearly defined sections that interact with each other without fully depending on each other to work. In other words, this trait judges how well I turn an empty apartment building into a building with a main lobby, an elevator, a staircase, and apartments. Each section of the building is clearly defined, has their own responsibilities, and can function independently while interacting with other sections for added convenience. Take a fire, for example. **0h nOOOoOO! A fiRe11!!!!!!** _Please exit calmly through the stairwell. Do not use elevators,_ the alarm announces. In this case, even when the elevator stops becoming a viable option completely, resources are distributed to another place and people take the stairs instead. The stairs can carry out their intended function, has distinct responsibilities and abilities, and does not depend on the elevator for survival. Furthermore, we can say that if someone is moving into their apartment for the first time and has loads of luggage to carry, they will want to take the elevator in order to be able to lift all of their luggage out of their room while using less time and energy. The elevator carries out its function effectively (does a better job) timely (saves time) and efficiently (saves energy); its distinct responsibilites are perfect for the tenants moving in and it functions without needing help from the stairs. Modularity, especially through OOP, is a great way to organize your code so that each compartment is so clearly defined and efficient on their own that you're so close to color-coding some of the files in your repositories.

So now that we have an idea on what each of the 3 principles means, we can start to grade my draft based on how well it carries out these procedures. The three principles of software development I call ‘AEM’ — Abstraction, Encapsulation, and Modularity — because you should always 'AEM' for their bullseye. On top of these will be subtopics that I can use to automatically detect which sector of traits has any given bug that I'm trying to fix, which are mainly just how each of the main topics go hand-in-hand with each other, along with how well I may have implemented OOP in the changes of that week.

- Abstraction

After a thorough scan of main.py, I found that the heart of the program - the DownloadsHandler class - is already doing a stellar job at organizing all methods into their own respective functions without focusing too much on the technical talk. Abstraction is just one of those things that you have to wait and look for as you add more files, so my program already does well enough right now in the way methods are introduced and used throughout the project. One thing that I could work on, however, is starting to get Filefly out as a either a web application or a Python package distribution so that the big picture of my project doesn't waste any potential by giving its potential to a single line that says observer.join().

*8/10*

- Encapsulation

main.py does a great job at both creating class variables and defining methods that will be used later on in the project via bundling. A lot has to be done here if I start to use the class in multiple python files, but other than that, it works great at what it does with the DownloadsHandler class. one thing that it could work on is using a gatekeep mechanism to keep the two universal methods in main.py, handle_archive() and get_safe_path(), safe from any unwanted touchy feely from other .py files that could be made.

*8/10*

- Modularity

One thing that I thank past me for doing is keeping my code in sections that may look jumbled to some that read it, although I know where everything is. I definitely know where each module of sorts is located in my program as of currently, but debugging has been fairly slow so far because of the lack of tool implementation when I debug. I could work on this by adding tools to check for overall efficiency, which could help a bunch when I assess the asymptotic notation of my program (future episode?) and I could include a dev mode and/or settings mode where the user can look at additional metrics which could prove handy. (psst, matplotlib, you could be the one to take this job offer!)

*7/10*

The scores were as accurate as I deemed fair since my next steps are to turn this project into something feasible that lands on other computers instead of only my own.

**Next Week’s Focus:**
- Build website framework
- Analyze time complexity
- Add additional settings and user friendliness via a dev mode and/or settings mode

### Reflections & Takeaways
- Learned to identify abstraction in practice, not just theory.
- Encapsulation protects internal logic, even from my own debugging mistakes.
- Modularity will make scaling Filefly (to a package or web app) much easier later on.

It's crazy to think that this has only been 2 months of my work, and it's already gaining momentum. These logs will prove invaluable in sharing my thought processes and acquired skills with all of you, and it's great to have people in for the ride as I learn by doing. This is preparation to solve some of the world's hardest problems, which is making those hours on end of learning, writing, debugging, repeat, all worth it. With an AP Java classroom that is nothing short of inspiring, and an untapped potential to bring a new idea into the world, Filefly is ready for the next revisions to come (the word "website" sounds pretty impactful right now). If there was something more to say for this last line, then I couldn't quite find it. Filefly, sign this one off.

"Traceback (most recent call last):
  File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.9_3.9.3568.0_x64__qbz5n2kfra8p0\lib\threading.py", line 980, in _bootstrap_inner
    self.run()
  ...
AttributeError: 'DownloadsHandler' object has no attribute 'moved_files_ts'"

-- Filefly, _about 3 weeks ago_

"Oh, error on line 980, sure, let me just check through my-I DON'T EVEN HAVE 250 LINES OF CODE YET."
-- Me, _also 3 weeks ago_

(I traced the issue to an uninitialized attribute in the DownloadsHandler class and created a default dictionary setup to prevent AttributeErrors from happening again.)

Warm regards, and God bless you,

^ OtterShot
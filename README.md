# MQL5Comp

A Sublime Text 3 plugin for building MetaTrader's MQL projects from a Linux system.  


### Requirements  

On Linux:  
Sublime Text 3.x  
Wine (Windows compatibility software)  
smbclient
(Metatrader id running on wine - use local copy mode)

On Windows:  
Metatrader


### Plugin Manual Install  

Copy the `MQL5Comp.sublime-package` from this repo's build directory into your Sublime Text "Installed Packages" location. 
It should be at `~/.config/sublime-text-3/Installed Packages/`  
  
or  

Clone MQL5Comp:
`git clone http://github.com/curvian/MQL5Comp`  
Create package dir & copy contents of MQL5Comp/src into it:
`mkdir ~/.config/sublime-text-3/Packages/MQL5Comp`
`cp -r MQL5Comp/src/* ~/.config/sublime-text-3/Packages/MQL5Comp`  
  
or  
  
Install with Package Manager (Not yet available)  



### Usage  


#### 1. Prepare MQL Project

It is important to get the directory structure right for the project.  

Inside your sublime project directory must exist a source directory with any name of your choice ("src", or "my_expert", anything) and specified in your `.sublime-project` file, along with all the other settings.

From there a specific structure must be maintained for the metatrader compiler to work correctly, and for the files to be installed/copied correctly.  


1. Create your project directory structure as follows:
```
    MyExpertProject/
        MyExpert.sublime-project
        MyExpertSource/
            metaeditor.exe
            MQL4/
                Experts/
                    MyExpert.mq4
                Indicators/
                Scripts/
                Include/
                Libraries/
```

2. Copy your compiler (metaeditor.exe, for instance) from the Metatrader program on Windows to the root of your source directory, as shown above.  

3. From this repo, in the support directory, open `example.sublime-project`  
Read the comments inside and copy the relevant settings to your own `MyProject.sublime-project` file. 

4. Make sure to create the windows share of your Metatrader application data or program root (depending where your data is located)
This will make sense when you edit your project file settings as specified in `example.sublime-project`


#### 2. Usage - Build Project

If all is set up correctly, all you have to do is hit <kbd>ctrl</kbd>+<kbd>B</kbd> to build the current mq4 file open in Sublime Text.

The first time MQL5Comp build command is run it will check for the relevant drive mapping in wine and create it if it does not exist.  

After a successful build, the compiled ex4 file can be found in the relevant `Experts`, `Scripts`, or `Indicators` directory on your 
Windows machine running Metatrader platform (as well as in your source location) and should be loadable as usual.


### Plugin Development  

See support/dev/ location for simple plugin development helpers  



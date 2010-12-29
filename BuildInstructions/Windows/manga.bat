set PIP=c:\python27\pyInstaller-1.5-rc1\

python %PIP%Makespec.py --onefile --console --upx --tk --icon=./Icon/Manga_icon_2.ico manga.py 
python %PIP%Build.py manga.spec 

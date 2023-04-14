echo off
pip install requests==2.25.0
pip install beautifulsoup4==4.9.3
pip install lxml==4.6.2
pip install randominfo==2.0.2
pip install yattag==1.14.0
pip install transliterate==1.10.2



pyinstaller --clean --hidden-import=pyttsx3.drivers --hidden-import=pyttsx3.drivers.sapi5 --onefile --noconsole --i RusSmSbot.ico RusSmsbot.py

del /s /q /f build.spec
rmdir /s /q __pycache__
rmdir /s /q build

exit

если вы используете установку из файла requirements.txt то добавте его в верху под 
строчкой pip install transliterate==1.10.2

pip install -r requirements.txt


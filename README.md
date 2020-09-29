# PyMemory
<b>(Derzeit nicht möglich da pip in Docker die Abhängigkeiten nicht herunterlädt.)</b><br>
Um das Projekt mit Docker zu starten:

```
docker build . --tag pymemory
docker run pymemory
```

Um das Projekt selbst zu starten:

Windows:
```
pip install -r requirements.txt
python PyMemory.py
```
Fedora:
```
python3 -m pip install pyperclip
dnf install python3-pygame python3-tkinter
pip install -r requirements.txt
python PyMemory.py
```

Im Spiel PyMemory geht es darum sich verschiedene Karten zu merken.
Es gibt zu jedem Bild ein Paar. 
Das Spiel besteht aus einem quadratischen Spielfeld, die Karten sind verdeckt hinzulegen.
Eine Runde besteht aus dem zufälligen Umdrehen von zwei verdeckten Karten. 
Falls diese das gleiche Bild besitzen, so bleiben sie umgedreht.
Wenn alle Karten umgedeckt wurden, gilt das Spiel als beendet.

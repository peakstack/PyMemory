# PyMemory

Um das Projekt mit Docker zu starten:

```
docker build --tag the-pymemory
docker run --name pymemory the-pymemory
```

Um das Projekt selbst zu starten:
```
pip install -r requirements.txt
python ./MemoryGame.py
```

Im Spiel PyMemory geht es darum sich verschiedene Karten zu merken.
Es gibt zu jedem Bild ein Paar. 
Das Spiel besteht aus einem quadratischen Spielfeld, die Karten sind verdeckt hinzulegen.
Eine Runde besteht aus dem zufälligen Umdrehen von zwei verdeckten Karten. 
Falls diese das gleiche Bild besitzen, so bleiben sie umgedreht.
Wenn alle Karten umgedeckt wurden, gilt das Spiel als beendet.

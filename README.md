# Semantic Science Project (SSP)

## Architektur
Derzeit läuft jeden Morgen das fetch_and_store_updates.py skript und schreibt die tagesaktuellen Publikationen in eine SQLite Datenbank.
Ein weiterer Service, der Telegram-Bot, holt sich mit einem kleinen zeitlichen Abstand die neuen Publikationen aus der Datenbank, 
erzeugt daraus eine Telegram-Nachricht und versendet diese an die entsprechenden Zielkanäle.
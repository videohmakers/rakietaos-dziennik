# Dziennik pokładowy rakietaOS – wersja publiczna

Strona: https://rakietaos.monikabochynska.pl (GitHub Pages)

## Co tu jest
- `index.html` – strona w stylu rakietaOS, czyta `data.json`. Na górze pliku blok `RAKIETAOS_CONFIG` z adresem formularza listy oczekujących i linkiem do polityki prywatności.
- `data.json` – publiczne dane dziennika. Generuje go automat o 21:00, nie edytuj ręcznie.
- `etapy/` – zdjęcia etapów pokazywane w dniach lotu.
- `tools/export.py` – zamienia zrzut bazy prywatnego dziennika w `data.json`. Pomija dni i wpisy z `private: true` oraz wszystko, co wspomina Rakietę Biznesu Live.
- `CNAME` – domena dla GitHub Pages.

## Wieczorna aktualizacja (21:00)
1. Pobierz kolekcje `entries` i `days` z prywatnego dziennika do katalogu `zrzut/` (ArtifactData, list, out_dir).
2. `python3 tools/export.py zrzut data.json`
3. Skopiuj nowe obrazy etapów z artefaktu do `etapy/`, jeśli są.
4. Commit i push na gałąź `main`. Strona odświeża się sama w ciągu 1–2 minut.

## Zmiana MailerLite na Easytools
Podmień `formAction` w `RAKIETAOS_CONFIG` na adres formularza z Easytools i dopasuj nazwy pól (`fields[email]`, `fields[name]`) do tych, których oczekuje Easytools.

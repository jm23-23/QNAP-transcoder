🎬 QNAP Intel HW Transcoder (x265/HEVC)

Lekki i wydajny kontener Docker z interfejsem webowym (Streamlit), umożliwiający sprzętowe kodowanie wideo za pomocą FFmpeg oraz technologii Intel QuickSync (VAAPI). Projekt zoptymalizowany pod serwery QNAP (np. seria TS-x53D).
✨ Główne funkcje

    Sprzętowa akceleracja: Wykorzystanie układu graficznego procesorów Intel do kodowania x265 (HEVC), co minimalizuje obciążenie procesora.

    Inteligentny File Browser: Przeglądanie struktury folderów NAS-a bezpośrednio w przeglądarce.

    Filtrowanie śmieci: Automatyczne ukrywanie folderów systemowych QNAP (np. @Recycle, @__thumb).

    Zachowanie jakości: Automatyczne kopiowanie ścieżek audio (PL/ENG) oraz napisów bez ich ponownego kodowania.

    Podgląd na żywo: Pasek postępu, liczba klatek na sekundę (FPS) oraz szacowany czas zakończenia.

🛠 Wymagania sprzętowe

    Serwer QNAP z procesorem Intel wspierającym QuickSync/VAAPI.

    Zainstalowana aplikacja Container Station.

🚀 Instalacja i uruchomienie
1. Budowanie obrazu (jeśli posiadasz kod źródłowy)

Pobierz pliki do jednego folderu na NAS-ie, przejdź do niego w terminalu (SSH) i wykonaj:
Bash

docker build -t qnap-transcoder .

2. Uruchomienie kontenera (CLI - Zalecane)

Najpewniejszym sposobem na uruchomienie z obsługą akceleracji sprzętowej jest użycie terminala. Podmień ścieżki /share/... na swoje własne foldery.
Bash

docker run -d \
  --name ffmpeg-ui \
  --device /dev/dri:/dev/dri \
  -p 8501:8501 \
  -v /share/Filmy:/data/input \
  -v /share/Public/Output:/data/output \
  --restart unless-stopped \
  qnap-transcoder

Wyjaśnienie parametrów:

    --device /dev/dri:/dev/dri: Udostępnia układ graficzny Intel procesora kontenerowi (kluczowe dla prędkości!).

    -p 8501:8501: Port, na którym dostępny będzie interfejs webowy.

    -v /data/input: Folder, w którym znajdują się Twoje filmy źródłowe.

    -v /data/output: Folder, w którym zostaną zapisane gotowe pliki.

🖥 Instrukcja obsługi

    Otwórz przeglądarkę i wpisz adres: http://IP_TWOJEGO_NAS:8501.

    Nawigacja: Klikaj w foldery, aby przejść do podkatalogów. Użyj przycisku "W górę", aby wrócić.

    Wybór: Wybierz plik wideo z listy (widoczny będzie jego rozmiar).

    Ustawienia: W panelu bocznym wybierz jakość (domyślnie 25). Pamiętaj: niższa wartość = lepsza jakość, ale większy plik.

    Start: Kliknij przycisk "Uruchom kodowanie sprzętowe".

    Finał: Gotowy plik znajdziesz w folderze wyjściowym z przyrostkiem _HEVC.mkv.

📝 Uwagi techniczne

    Format wyjściowy: Aplikacja wymusza kontener .mkv, aby zachować kompatybilność z wieloma ścieżkami audio i napisami.

    Audio/Napisy: Skrypt automatycznie próbuje odnaleźć ścieżki w języku polskim i angielskim. Jeśli ich nie ma, po prostu je pomija.

    Wydajność: Dzięki VAAPI, procesor (CPU) powinien pozostać na niskim poziomie obciążenia (zazwyczaj <20%), podczas gdy układ GPU wykonuje całą pracę.

    Autor: Przygotowano w ramach konfiguracji dedykowanej dla QNAP TS-453D.
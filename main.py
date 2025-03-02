import cv2
import numpy as np

input_path = "input.mp4"
output_path = "stabilized.mp4"

# Video öffnen
cap = cv2.VideoCapture(input_path)
fps = cap.get(cv2.CAP_PROP_FPS)
w   = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h   = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# VideoWriter für Ausgabevideo konfigurieren (Codec mp4v für .mp4-Datei)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

# Ersten Frame lesen (Referenzframe)
ret, ref_frame = cap.read()
if not ret:
    print("Video konnte nicht gelesen werden.")
    exit()

# In Graustufen umwandeln für Feature-Detection
ref_gray = cv2.cvtColor(ref_frame, cv2.COLOR_BGR2GRAY)

# ORB Feature-Detektor initialisieren (z.B. 500 Features)
orb = cv2.ORB_create(nfeatures=500)

# ORB-Features im Referenzframe erkennen und Deskriptoren berechnen
kp_ref, des_ref = orb.detectAndCompute(ref_gray, None)

# Matcher für ORB-Deskriptoren (Brute-Force mit Hamming-Distanz)
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)

frame_idx = 1  # Frame-Zähler (Start bei 1, da 0 der Referenzframe ist)
while True:
    ret, frame = cap.read()
    if not ret:
        break  # Ende erreicht

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    kp_cur, des_cur = orb.detectAndCompute(gray, None)

    # Features matchen (jeweils 2 nächste Nachbarn für Ratio-Test)
    matches = bf.knnMatch(des_ref, des_cur, k=2)
    good_matches = []
    for m, n in matches:
        if m.distance < 0.7 * n.distance:  # Lowe's Ratio-Test
            good_matches.append(m)

    if len(good_matches) < 4:
        # Falls zu wenige Matches gefunden werden, Originalframe verwenden
        print(f"Warnung: Zu wenige Matches in Frame {frame_idx}, keine Stabilisierung.")
        out.write(frame)
    else:
        # Korrespondenzpunkte aus den Matches extrahieren
        ref_pts = np.float32([ kp_ref[m.queryIdx].pt for m in good_matches ])
        cur_pts = np.float32([ kp_cur[m.trainIdx].pt for m in good_matches ])

        # Homographie berechnen (mit RANSAC zur Robustheit)
        H, mask = cv2.findHomography(cur_pts, ref_pts, cv2.RANSAC)

        # Frame mittels Homographie-Matrix zum Referenzblickwinkel transformieren
        stabilized_frame = cv2.warpPerspective(frame, H, (w, h))

        # Transformierten Frame zum Output-Video hinzufügen
        out.write(stabilized_frame)
    frame_idx += 1

# Schleife beendet: alle Frames verarbeitet

# Ressourcen freigeben
cap.release()
out.release()
print("Stabilisierung abgeschlossen. Ausgabe gespeichert unter:", output_path)

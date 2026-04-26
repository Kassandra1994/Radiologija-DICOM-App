# Radiologija-DICOM-App


Aplikacija za upravljanje podacima o pacijentima i pregled DICOM medicinskih snimaka.

## Funkcionalnosti
- **Evidencija pacijenata:** Dodavanje, izmena i brisanje podataka o pacijentima.
- **Upravljanje snimanjima:** Unos novih radioloških snimanja (CT, MR, XR, PET).
- **DICOM Viewer:** Prikaz i pregled DICOM datoteka i čitanje metapodataka iz snimaka.

## Tehnologije
- **Python 3.x**
- **Tkinter** (za grafički interfejs)
- **pydicom** (za obradu DICOM fajlova)
- **Pillow (PIL)** (za prikaz slika)

## Kako pokrenuti aplikaciju
1. Instalirajte potrebne biblioteke:
   ```bash
   pip install pydicom Pillow
2. Pokrenuti glavnu skriptu
   python radiologija_gui.py

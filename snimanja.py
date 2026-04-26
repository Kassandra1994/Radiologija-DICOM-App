from pacijenti_podaci import *
from tkinter import *
from PIL import Image, ImageTk
from tkinter import messagebox
import datetime
from tkinter.ttk import Combobox
import pydicom
from tkinter import filedialog


class ProzorSnimanje(Toplevel):

    def pretraga(self):
        indeks_pacijenta = self.__odaberi_pacijenta_combobox.current()
        indeks_snimka = self.__snimanja_combobox.current()
        pacijent = self.__odaberi_pacijente[indeks_pacijenta]
        snimak = self.__vrste_snimaka[indeks_snimka]

        nadjena_snimanja = []

        if indeks_pacijenta == 0 and indeks_snimka == 0:
            return self.__podaci.snimanja
        elif indeks_pacijenta != 0 and indeks_snimka != 0:
            for snimanje in self.__podaci.snimanja:
                if pacijent == snimanje.pacijent.prezime + ' ' + snimanje.pacijent.ime and snimak == snimanje.tip:
                    nadjena_snimanja.append(snimanje)
            return nadjena_snimanja
        elif indeks_snimka == 0:
            for snimanje in self.__podaci.snimanja:
                if pacijent == snimanje.pacijent.prezime + ' ' + snimanje.pacijent.ime:
                    nadjena_snimanja.append(snimanje)
            return nadjena_snimanja
        elif indeks_pacijenta == 0:
            for snimanje in self.__podaci.snimanja:
                if snimak == snimanje.tip:
                    nadjena_snimanja.append(snimanje)
            return nadjena_snimanja

    def popuni_listbox_snimanjima(self):
        self.__snimanja_listbox.delete(0, END)
        sortirana_snimanja = sorted(self.pretraga(), key=lambda snimanje:snimanje.datum_i_vreme)
        for snimanje in sortirana_snimanja:
            self.__snimanja_listbox.insert(END, snimanje.datum_i_vreme.strftime('%d.%m.%Y. %H:%M:%S'))

    def popuni_labele_podacima(self, snimanja):
        self.__pacijent_labela['text'] = snimanja.pacijent.prezime + ' ' + snimanja.pacijent.ime
        self.__datum_i_vreme_labela['text'] = snimanja.datum_i_vreme.strftime('%d.%m.%Y. %H:%M:%S')
        self.__vrsta_snimaka_labela['text'] = snimanja.tip
        self.__lekar_labela['text'] = snimanja.lekar
        self.__putanja_labela['text'] = snimanja.snimak

    def promena_selekcije_u_listboxu(self, event=None):

        if not self.__snimanja_listbox.curselection():
            self.komanda_ocisti()
            return

        indeks = self.__snimanja_listbox.curselection()[0]
        snimanje = sorted(self.pretraga(), key=lambda snimanje:snimanje.datum_i_vreme)[indeks]
        self.popuni_labele_podacima(snimanje)

        self.__button_obrisi['state'] = NORMAL
        self.__button_izmeni['state'] = NORMAL
        self.__button_ocisti['state'] = NORMAL
        self.__button_dicom['state'] = NORMAL

    def komanda_ocisti(self):
        self.__pacijent_labela['text'] = ''
        self.__datum_i_vreme_labela['text'] = ''
        self.__vrsta_snimaka_labela['text'] = ''
        self.__lekar_labela['text'] = ''
        self.__putanja_labela['text'] = ''

        self.__snimanja_listbox.selection_clear(0, END)

        self.__button_obrisi['state'] = DISABLED
        self.__button_izmeni['state'] = DISABLED
        self.__button_ocisti['state'] = DISABLED
        self.__button_dicom['state'] = DISABLED

        self.__odaberi_pacijenta_combobox.current(0)
        self.__snimanja_combobox.current(0)
        self.popuni_listbox_snimanjima()

    def komanda_obrisi(self):
        odgovor = messagebox.askquestion('Upozorenje','Da li ste sigurni da želite da obrišete snimanje?')
        if odgovor == 'no':
            return

        indeks = self.__snimanja_listbox.curselection()[0]
        snimanje_za_brisanje = sorted(self.pretraga(), key=lambda snimanje:snimanje.datum_i_vreme)[indeks]
        self.__podaci.obrisi_snimanje(snimanje_za_brisanje)

        self.config(cursor='wait')
        self.__podaci.sacuvaj_se()
        self.config(cursor='')

        self.__snimanja_listbox.delete(indeks)
        self.__snimanja_listbox.selection_set(indeks)
        self.promena_selekcije_u_listboxu()

        self.__odaberi_pacijenta_combobox.current(0)
        self.__snimanja_combobox.current(0)
        self.popuni_listbox_snimanjima()

    def komanda_izmeni(self):
        indeks = self.__snimanja_listbox.curselection()[0]
        snimanje = sorted(self.pretraga(), key=lambda snimanje:snimanje.datum_i_vreme)[indeks]

        izmeni_snimanje_prozor = IzmeniSnimanjeProzor(self, self.__podaci, snimanje)
        self.wait_window(izmeni_snimanje_prozor)

        if izmeni_snimanje_prozor.otkazan:
            return

        self.__snimanja_listbox.delete(indeks)
        self.__snimanja_listbox.insert(indeks, snimanje.datum_i_vreme.strftime('%d.%m.%Y. %H:%M:%S'))
        self.__snimanja_listbox.selection_set(indeks)
        self.promena_selekcije_u_listboxu()

    def komanda_dodaj(self):
        self.__snimanja_combobox.current(0)
        self.__odaberi_pacijenta_combobox.current(0)

        self.komanda_ocisti()

        dodaj_snimanje_prozor = DodajSnimanjeProzor(self, self.__podaci)
        self.wait_window(dodaj_snimanje_prozor)

        if dodaj_snimanje_prozor.otkazan:
            return

        snimak = self.__podaci.snimanja[-1]
        indeks = sorted(self.__podaci.snimanja, key=lambda snimanje:snimanje.datum_i_vreme).index(snimak)
        self.__snimanja_listbox.insert(indeks, snimak.datum_i_vreme.strftime('%d.%m.%Y. %H:%M:%S'))
        self.__snimanja_listbox.selection_set(indeks)
        self.promena_selekcije_u_listboxu()

    def komanda_dicom(self):
        try:
            staza_do_datoteke = self.__putanja_labela.cget('text')
            if staza_do_datoteke != '':
                dataset = pydicom.dcmread(staza_do_datoteke, force=True)
            else:
                messagebox.showerror('Greška', 'Staza do datoteke nije uneta!')

            indeks = self.__snimanja_listbox.curselection()[0]
            trenutno_snimanje = sorted(self.pretraga(), key=lambda snimanje:snimanje.datum_i_vreme)[indeks]

            trenutni_pacijent = trenutno_snimanje.pacijent

            DICOMProzor(self, dataset, trenutni_pacijent, trenutno_snimanje)
        except Exception as ex:
            print()
            print(ex)
            messagebox.showwarning('Upozorenje', 'Snimak nije pronađen!')



    def komanda_povratak(self):
        self.destroy()

    def __init__(self, master, podaci, indeks):
        super().__init__(master)
        self.__indeks = indeks
        self.__podaci = podaci

        self.__snimanja_listbox = Listbox(self, activestyle='none', exportselection=False)
        self.__snimanja_listbox.pack(side=LEFT, fill=BOTH, expand=1)
        self.__snimanja_listbox.bind('<<ListboxSelect>>', self.promena_selekcije_u_listboxu)

        self.__snimanja_frame = Frame(self, borderwidth=2, relief='ridge', padx=10, pady=10)
        self.__snimanja_frame.pack(side=RIGHT, fill=BOTH, expand=1)

        self.__odaberi_pacijente = ['Odaberi pacijenta']
        sortirani_pacijenti = sorted(self.__podaci.pacijenti, key=lambda pacijent:pacijent.prezime)
        for pacijent in sortirani_pacijenti:
            self.__odaberi_pacijente.append(pacijent.prezime + ' ' + pacijent.ime)

        self.__odaberi_pacijenta_combobox = Combobox(self.__snimanja_frame, state="readonly", value=self.__odaberi_pacijente)
        self.__odaberi_pacijenta_combobox.current(indeks)
        self.__odaberi_pacijenta_combobox.bind('<<ComboboxSelected>>', lambda _: self.popuni_listbox_snimanjima())

        self.__vrste_snimaka = ['Odaberi tip snimanja',
                          'Kompjuterska tomografija (CT)',
                          'Magnetnorezonantna angiografija (MRA)',
                          'Magnetna rezonanca (MR)',
                          'Pozitronska emisiona tomografija (PET)',
                          'Rendgenski zraci (XR)',
                          'Mamografija'
                                ]

        self.__snimanja_combobox = Combobox(self.__snimanja_frame, state="readonly", value=self.__vrste_snimaka, width=40)
        self.__snimanja_combobox.current(0)
        self.__snimanja_combobox.bind('<<ComboboxSelected>>', lambda _: self.popuni_listbox_snimanjima())

        self.__pacijent_labela = Label(self.__snimanja_frame)
        self.__datum_i_vreme_labela = Label(self.__snimanja_frame)
        self.__vrsta_snimaka_labela = Label(self.__snimanja_frame)
        self.__lekar_labela = Label(self.__snimanja_frame)
        self.__putanja_labela = Label(self.__snimanja_frame)


        self.__button_ocisti = Button(self.__snimanja_frame, text='Očisti', width=10, command=self.komanda_ocisti, state=DISABLED)
        self.__button_obrisi = Button(self.__snimanja_frame, text='Obriši', width=10, command=self.komanda_obrisi, state=DISABLED)
        self.__button_dodaj = Button(self.__snimanja_frame, text='Dodaj', width=10, command=self.komanda_dodaj)
        self.__button_dicom = Button(self.__snimanja_frame, text='Otvori DICOM', command=self.komanda_dicom, state=DISABLED)
        self.__button_izmeni = Button(self.__snimanja_frame, text='Izmeni', width=10, command=self.komanda_izmeni, state=DISABLED)
        self.__button_povratak = Button(self.__snimanja_frame, text='Povratak', width=10, command=self.komanda_povratak)

        red = 0
        self.__odaberi_pacijenta_combobox.grid(row=red, sticky=E)
        red += 1
        Label(self.__snimanja_frame, text='Pacijent:').grid(row=red, sticky=E)
        red += 1
        Label(self.__snimanja_frame, text='Datum i vreme:').grid(row=red, sticky=E)
        red += 1
        Label(self.__snimanja_frame, text='Tip snimanja:').grid(row=red, sticky=E)
        red += 1
        Label(self.__snimanja_frame, text='Lekar:').grid(row=red, sticky=E)
        red += 1
        Label(self.__snimanja_frame, text='Putanja do datoteke:').grid(row=red, sticky=E)

        red = 0
        kolona = 1
        self.__snimanja_combobox.grid(row=red, column=kolona, sticky=W)
        red += 1
        self.__pacijent_labela.grid(row=red, column=kolona, sticky=W)
        red += 1
        self.__datum_i_vreme_labela.grid(row=red, column=kolona, sticky=W)
        red += 1
        self.__vrsta_snimaka_labela.grid(row=red, column=kolona, sticky=W)
        red += 1
        self.__lekar_labela.grid(row=red, column=kolona, sticky=W)
        red += 1
        self.__putanja_labela.grid(row=red, column=kolona, sticky=W)
        red += 1
        self.__button_ocisti.grid(row=red, column=kolona, sticky=E)
        red += 1
        self.__button_dicom.grid(row=red, column=kolona, sticky=E)
        kolona += 1
        red -= 1
        self.__button_dodaj.grid(row=red, column=kolona, sticky=W)
        kolona += 1
        self.__button_izmeni.grid(row=red, column=kolona, sticky=W)
        kolona -= 1
        red += 1
        self.__button_obrisi.grid(row=red, column=kolona, sticky=W)
        kolona += 1
        self.__button_povratak.grid(row=red, column=kolona, sticky=W)

        self.popuni_listbox_snimanjima()

        self.title('Lista snimanja')
        self.iconbitmap('radiology.ico')

        self.update_idletasks()
        sirina = self.winfo_width()
        visina = self.winfo_height()
        self.minsize(sirina, visina)

        self.transient(master)
        self.focus_force()
        self.grab_set()

class DodajProzor(Toplevel):

    def pacijent_validacija(self):
        indeks = self.__pacijent_combobox.current()
        if indeks < 0:
            messagebox.showerror('Greška', 'Nijedan pacijent nije označen!')
            return None

        pacijent = sorted(self.__podaci.pacijenti, key=lambda pacijent:pacijent.prezime)[indeks]

        return pacijent

    def datum_i_vreme_validacija(self, pacijent):
        try:
            godina = self.__datum_godina.get()
            mesec = self.__datum_mesec.get()
            dan = self.__datum_dan.get()
            sat = self.__datum_sat.get()
            minut = self.__datum_minut.get()
            sekund = self.__datum_sekund.get()
            datum_i_vreme = datetime.datetime(godina, mesec, dan, sat, minut, sekund)

            if pacijent.datum_rodjenja < datum_i_vreme.date() < datetime.date.today():
                return datum_i_vreme
            else:
                messagebox.showerror('Greška', 'Niste uneli validan datum!')
                return None
        except TclError:
            messagebox.showerror('Greška', 'Niste uneli validan datum!')
            return None

    def lekar_validacija(self):
        lekar = self.__lekar.get()
        if lekar == '':
            messagebox.showerror('Greška', 'Unesite ime i prezime lekara!')
            return None
        return lekar

    def izvestaj_validacija(self):
        izvestaj = self.__izvestaj.get()
        if izvestaj == '':
            messagebox.showerror('Greška', 'Unesite izveštaj!')
            return None
        return izvestaj

    def tip_snimanja_validacija(self):
        indeks = self.__tip_combobox.current()
        if indeks < 0:
            messagebox.showerror('Greška', 'Vrsta snimaka nije označena!')
            return None
        vrste_snimaka = ['Kompjuterska tomografija (CT)',
                         'Magnetnorezonantna angiografija (MRA)',
                         'Magnetna rezonanca (MR)',
                         'Pozitronska emisiona tomografija (PET)',
                         'Rendgenski zraci (XR)',
                         'Mamografija'
                         ]
        tip_snimka = vrste_snimaka[indeks]
        return tip_snimka
    
    def snimak_validacija(self):
        snimak = self.__putanja.get()
        if snimak == '': # Proveravamo string iz StringVar-a, a ne Label objekat
             messagebox.showerror('Greška', 'Izaberite putanju do snimka!')
        return None
        return snimak

    """def snimak_validacija(self):
        snimak = self.__putanja.get()
        if self.__putanja_label == '':
            messagebox.showerror('Greška', 'Izaberite putanju do snimka!')
        return snimak """

    def komanda_potvrdi(self):

        self.config(cursor='wait')
        self.__podaci.sacuvaj_se()
        self.config(cursor='')

        self.__otkazan = False

        self.destroy()

    def komanda_povratak(self):
        self.destroy()

    def putanja_do_datoteke(self):
        staza_do_datoteke = filedialog.askopenfilename(
            title="Otvaranje",
            filetypes=[("All files", "*.*"), ("DICOM files", "*.dcm")])
        if staza_do_datoteke:
            self.__button_otvori['state'] = NORMAL
            self.__putanja.set(staza_do_datoteke)

    def podledaj_snimak(self):
        try:
            staza_do_datoteke = self.__putanja.get()
            if staza_do_datoteke != '':
                dataset = pydicom.dcmread(staza_do_datoteke, force= True)
            else:
                messagebox.showerror('Greška', 'Unesite putanju do datoteke!')
            DICOM(self, dataset)
        except Exception as ex:
            print()
            print(ex)
            messagebox.showwarning('Upozorenje', 'Snimak nije pronađen!')

    def __init__(self, master, podaci):
        super().__init__(master)

        self.__dataset = None
        self.__staza_do_datoteke = ''

        self.__podaci = podaci

        self.__otkazan = True

        self.__snimanja_frame = Frame(self, borderwidth=2, relief='ridge', padx=10, pady=10)
        self.__snimanja_frame.pack(fill=BOTH, expand=1)

        self.__pacijent = StringVar(master)
        self.__lekar = StringVar(master)
        self.__izvestaj = StringVar(master)
        self.__datum_dan = IntVar(master)
        self.__datum_mesec = IntVar(master)
        self.__datum_godina = IntVar(master)
        self.__datum_sat = IntVar(master)
        self.__datum_minut = IntVar(master)
        self.__datum_sekund = IntVar(master)
        self.__putanja = StringVar(master)

        self.__lekar_entry = Entry(self.__snimanja_frame, width=20, textvariable=self.__lekar)
        self.__izvestaj_entry = Entry(self.__snimanja_frame, width=20, textvariable=self.__izvestaj)
        self.__datum_dan_spinbox = Spinbox(self.__snimanja_frame, width=5, from_=1, increment=1, to=31, textvariable=self.__datum_dan)
        self.__datum_mesec_spinbox = Spinbox(self.__snimanja_frame, width=5, from_=1, increment=1, to=12, textvariable=self.__datum_mesec)
        self.__datum_godina_spinbox = Spinbox(self.__snimanja_frame, width=5, from_=1900, increment=1, to=datetime.date.today().year, textvariable=self.__datum_godina)
        self.__datum_sat_spinbox = Spinbox(self.__snimanja_frame, width=5, from_=0, increment=1, to=23, textvariable=self.__datum_sat)
        self.__datum_minut_spinbox = Spinbox(self.__snimanja_frame, width=5, from_=0, increment=1, to=59, textvariable=self.__datum_minut)
        self.__datum_sekund_spinbox = Spinbox(self.__snimanja_frame, width=5, from_=0, increment=1, to=59, textvariable=self.__datum_sekund)
        self.__putanja_label = Label(self.__snimanja_frame, textvariable=self.__putanja, state=DISABLED)

        pacijenti = []
        sortirani_pacijenti = sorted(self.__podaci.pacijenti, key=lambda pacijent: pacijent.prezime)
        for pacijent in sortirani_pacijenti:
            pacijenti.append(pacijent.prezime + ' ' + pacijent.ime)

        self.__pacijent_combobox = Combobox(self.__snimanja_frame, state="readonly", value=pacijenti)
        if len(pacijenti) > 0:
            self.__pacijent_combobox.current(0)

        self.__vrste_snimaka = ['Kompjuterska tomografija (CT)',
                                'Magnetnorezonantna angiografija (MRA)',
                                'Magnetna rezonanca (MR)',
                                'Pozitronska emisiona tomografija (PET)',
                                'Rendgenski zraci (XR)',
                                'Mamografija'
                                ]

        self.__tip_combobox = Combobox(self.__snimanja_frame, state="readonly", width=40, value=self.__vrste_snimaka)
        if len(self.__vrste_snimaka) > 0:
            self.__tip_combobox.current(0)

        self.__button_potvrdi = Button(self.__snimanja_frame, text='', width=10, command=self.komanda_potvrdi)
        self.__button_povratak = Button(self.__snimanja_frame, text='Povratak', width=10, command=self.komanda_povratak)
        self.__button_putanja = Button(self.__snimanja_frame, text='...', width=3, command=self.putanja_do_datoteke)
        self.__button_otvori = Button(self.__snimanja_frame, text='Otvori', width=10, command=self.podledaj_snimak, state=DISABLED)

        red = 0
        Label(self.__snimanja_frame, text='Pacijent').grid(row=red, sticky=E)
        red += 1
        Label(self.__snimanja_frame, text='Datum i vreme:').grid(row=red, sticky=E)
        red += 1
        Label(self.__snimanja_frame, text='Ime i prezime lekara:').grid(row=red, sticky=E)
        red += 1
        Label(self.__snimanja_frame, text='Izveštaj:').grid(row=red, sticky=E)
        red += 1
        Label(self.__snimanja_frame, text='Tip snimanja:').grid(row=red, sticky=E)
        red += 1
        Label(self.__snimanja_frame, text='Putanja do datoteke:').grid(row=red, sticky=E)

        red = 0
        kolona = 1
        self.__pacijent_combobox.grid(row=red, column=kolona, sticky=W)
        red += 1
        self.__datum_dan_spinbox.grid(row=red, column=kolona, sticky=E)
        kolona += 1
        self.__datum_mesec_spinbox.grid(row=red, column=kolona, sticky=W)
        kolona += 1
        self.__datum_godina_spinbox.grid(row=red, column=kolona, sticky=W)
        kolona += 1
        self.__datum_sat_spinbox.grid(row=red, column=kolona, sticky=W)
        kolona += 1
        self.__datum_minut_spinbox.grid(row=red, column=kolona, sticky=W)
        kolona += 1
        self.__datum_sekund_spinbox.grid(row=red, column=kolona, sticky=W)
        red += 1
        kolona = 1
        self.__lekar_entry.grid(row=red, column=kolona, sticky=W)
        red += 1
        self.__izvestaj_entry.grid(row=red, column=kolona, sticky=W)
        red += 1
        self.__tip_combobox.grid(row=red, column=kolona, sticky=W)
        red += 1
        self.__putanja_label.grid(row=red, column=kolona, sticky=W)
        kolona += 1
        self.__button_putanja.grid(row=red, column=kolona, sticky=W)
        kolona += 1
        self.__button_otvori.grid(row=red, column=kolona, sticky=W)
        red += 1
        self.__button_potvrdi.grid(row=red, column=kolona, sticky=E)
        kolona = 2
        self.__button_povratak.grid(row=red, column=kolona, sticky=W)

        self.iconbitmap('radiology.ico')
        self.title('Dodavanje snimanja')

        self.update_idletasks()
        sirina = self.winfo_width()
        visina = self.winfo_height()
        self.minsize(sirina, visina)

        self.transient(master)
        self.focus_force()
        self.grab_set()

    @property
    def otkazan(self):
        return self.__otkazan
    @property
    def datum_godina(self):
        return self.__datum_godina
    @property
    def datum_mesec(self):
        return self.__datum_mesec
    @property
    def datum_dan(self):
        return self.__datum_dan
    @property
    def datum_sat(self):
        return self.__datum_sat
    @property
    def datum_minut(self):
        return self.__datum_minut
    @property
    def datum_sekund(self):
        return self.__datum_sekund
    @property
    def lekar(self):
        return self.__lekar
    @property
    def izvestaj(self):
        return self.__izvestaj
    @property
    def putanja(self):
        return self.__putanja
    @property
    def button_potvrdi(self):
        return self.__button_potvrdi
    @property
    def button_otvori(self):
        return self.__button_otvori
    @property
    def pacijent_combobox(self):
        return self.__pacijent_combobox
    @property
    def tip_combobox(self):
        return self.__tip_combobox
    @property
    def vrste_snimaka(self):
        return self.__vrste_snimaka

class DodajSnimanjeProzor(DodajProzor):

    def komanda_potvrdi(self):

        pacijent = self.pacijent_validacija()
        if not pacijent:
            return

        indeks = self.pacijent_combobox.current()
        trenutni_pacijent = sorted(self.__podaci.pacijenti, key=lambda pacijent: pacijent.prezime)[indeks]

        datum_i_vreme = self.datum_i_vreme_validacija(trenutni_pacijent)
        if not datum_i_vreme:
            return
        lekar = self.lekar_validacija()
        if not lekar:
            return
        izvestaj = self.izvestaj_validacija()
        if not izvestaj:
            return
        tip_snimka = self.tip_snimanja_validacija()
        if not tip_snimka:
            return
        snimak = self.snimak_validacija()
        if not snimak:
            return

        self.__podaci.dodaj_snimak(snimak)
        snimanje = Snimanje(pacijent, datum_i_vreme, tip_snimka, izvestaj, lekar, snimak)
        self.__podaci.dodaj_snimanje(snimanje)


        super().komanda_potvrdi()

    def __init__(self, master, podaci):

        super().__init__(master, podaci)

        self.__podaci = podaci

        self.button_potvrdi['text'] = 'Dodaj'
        self.title('Dodaj snimanje')
        self.iconbitmap('radiology.ico')


class IzmeniSnimanjeProzor(DodajProzor):

    def komanda_potvrdi(self):

        pacijent = self.pacijent_validacija()
        if not pacijent:
            return

        indeks = self.pacijent_combobox.current()
        trenutni_pacijent = sorted(self.__podaci.pacijenti, key=lambda pacijent: pacijent.prezime)[indeks]

        datum_i_vreme = self.datum_i_vreme_validacija(trenutni_pacijent)
        if not datum_i_vreme:
            return
        lekar = self.lekar_validacija()
        if not lekar:
            return
        izvestaj = self.izvestaj_validacija()
        if not izvestaj:
            return
        tip_snimka = self.tip_snimanja_validacija()
        if not tip_snimka:
            return
        snimak = self.snimak_validacija()
        if not snimak:
            return

        self.__snimanje.pacijent = pacijent
        self.__snimanje.lekar = lekar
        self.__snimanje.datum_i_vreme = datum_i_vreme
        self.__snimanje.izvestaj = izvestaj
        self.__snimanje.tip = tip_snimka
        self.__snimanje.snimak = snimak

        super().komanda_potvrdi()

    def __init__(self, master, podaci, snimanje):

        super().__init__(master, podaci)

        self.__snimanje = snimanje
        self.__podaci = podaci

        self.lekar.set(snimanje.lekar)
        self.datum_godina.set(snimanje.datum_i_vreme.year)
        self.datum_mesec.set(snimanje.datum_i_vreme.month)
        self.datum_dan.set(snimanje.datum_i_vreme.day)
        self.datum_sat.set(snimanje.datum_i_vreme.hour)
        self.datum_minut.set(snimanje.datum_i_vreme.minute)
        self.datum_sekund.set(snimanje.datum_i_vreme.second)
        self.izvestaj.set(snimanje.izvestaj)
        self.putanja.set(snimanje.snimak)

        pacijenti = []
        for pacijent in podaci.pacijenti:
            pacijenti.append(pacijent.prezime + ' ' + pacijent.ime)
        sortirani_pacijenti = sorted(pacijenti, key=lambda pacijent: pacijent[0])

        for indeks in range(len(sortirani_pacijenti)):
            pacijent = sortirani_pacijenti[indeks]
            if pacijent == snimanje.pacijent.prezime + ' ' + snimanje.pacijent.ime:
                self.pacijent_combobox.current(indeks)
                break

        snimanja = self.vrste_snimaka
        for indeks in range(len(snimanja)):
            snimak = snimanja[indeks]
            if snimak == snimanje.tip:
                self.tip_combobox.current(indeks)
                break

        self.button_otvori['state'] = NORMAL
        self.button_potvrdi['text'] = 'Izmeni'
        self.title('Izmeni snimanje')
        self.iconbitmap('radiology.ico')

class DICOM(Toplevel):

    def __init__(self, master, dataset):

        super().__init__(master)

        self.__dataset = dataset

        self.__slika_label = Label(self)
        self.__slika_label.pack(side=LEFT, expand=1)

        pixel_array = self.__dataset.pixel_array
        pil_slika = Image.fromarray(pixel_array)
        slika = ImageTk.PhotoImage(pil_slika)
        self.__slika_label['image'] = slika
        self.__slika_label.image = slika

        self.iconbitmap('radiology.ico')
        self.title('Snimak')

        self.update_idletasks()
        sirina = self.winfo_width()
        visina =self.winfo_height()
        self.minsize(sirina, visina)

        self.transient()
        self.grab_set()
        self.focus_force()

class DICOMProzor(Toplevel):

    def komanda_povratak(self):
        self.destroy()

    def __init__(self, master, dataset, pacijent, snimanje):

        super().__init__(master)

        self.__dataset = dataset
        self.__pacijent = pacijent
        self.__snimanje = snimanje

        self.__dataset.PatientName = self.__pacijent.prezime + ' ' + self.__pacijent.ime
        self.__dataset.PatientID = self.__pacijent.lbo
        self.__dataset.PatientBirthDate = self.__pacijent.datum_rodjenja.strftime('%Y%m%d')
        self.__dataset.DateTime = self.__snimanje.datum_i_vreme.strftime('%Y%m%d%H%M%S')
        self.__dataset.Modality = self.__snimanje.tip
        self.__dataset.StudyDescription = self.__snimanje.izvestaj
        self.__dataset.ReferringPhysicianName = self.__snimanje.lekar

        self.__slika_label = Label(self)
        self.__slika_label.pack(side=LEFT, expand=1)
        pil_slika = pydicom_PIL.get_PIL_image(self.__dataset)
        slika = ImageTk.PhotoImage(pil_slika)
        self.__slika_label['image'] = slika
        self.__slika_label.image = slika

        self.__dicom_frame = Frame(self, borderwidth=2, relief='ridge', padx=10, pady=10)
        self.__dicom_frame.pack(fill=BOTH, expand=1)

        self.__button_povratak = Button(self.__dicom_frame, text='Povratak', width=10, command=self.komanda_povratak)

        red = 1
        Label(self.__dicom_frame, text='Patient ID:').grid(row=red, sticky=E)
        red += 1
        Label(self.__dicom_frame, text='Patient’s Name:').grid(row=red, sticky=E)
        red += 1
        Label(self.__dicom_frame, text='Patient’s Birth Date:').grid(row=red, sticky=E)
        red += 1
        Label(self.__dicom_frame, text='Datum:').grid(row=red, sticky=E)
        red += 1
        Label(self.__dicom_frame, text='Modality:').grid(row=red, sticky=E)
        red += 1
        Label(self.__dicom_frame, text='Study Description:').grid(row=red, sticky=E)
        red += 1
        Label(self.__dicom_frame, text='Referring Physician’s Name:').grid(row=red, sticky=E)

        kolona = 1
        red = 1
        Label(self.__dicom_frame, text=self.__dataset.PatientID).grid(row=red, column=kolona, sticky=W)
        red += 1
        Label(self.__dicom_frame, text=self.__dataset.PatientName).grid(row=red, column=kolona, sticky=W)
        red += 1
        Label(self.__dicom_frame, text=self.__dataset.PatientBirthDate).grid(row=red, column=kolona, sticky=W)
        red += 1
        Label(self.__dicom_frame, text=self.__dataset.DateTime).grid(row=red, column=kolona, sticky=W)
        red += 1
        Label(self.__dicom_frame, text=self.__dataset.Modality).grid(row=red, column=kolona, sticky=W)
        red += 1
        Label(self.__dicom_frame, text=self.__dataset.StudyDescription).grid(row=red, column=kolona, sticky=W)
        red += 1
        Label(self.__dicom_frame, text=self.__dataset.ReferringPhysicianName).grid(row=red, column=kolona, sticky=W)
        red += 1
        self.__button_povratak.grid(row=red, column=kolona, sticky=W)

        self.iconbitmap('radiology.ico')
        self.title('Snimak')

        self.update_idletasks()
        sirina = self.winfo_width()
        visina = self.winfo_height()
        self.minsize(sirina, visina)

        self.transient()
        self.focus_force()
        self.grab_set()
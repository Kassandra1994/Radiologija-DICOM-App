from pacijenti_podaci import *
from tkinter import *
from PIL import Image, ImageTk
from tkinter import messagebox
import datetime
from snimanja import *


class RadiologijaProzor(Tk):

    def komanda_prikaz_pacijenata(self):
        prozor_prikaz_pacijenata = ProzorPrikazPacijenata(self, self.__podaci)
        self.wait_window(prozor_prikaz_pacijenata)

    def komanda_prikaz_snimanja(self):
        prozor_prikaz_snimanja = ProzorSnimanje(self, self.__podaci, 0)
        self.wait_window(prozor_prikaz_snimanja)

    def komanda_izlaz(self):
        odgovor = messagebox.askquestion('Izlaz', 'Da li ste sigurni da želite da napustite aplikaciju?')
        if odgovor == 'no':
            return

        self.destroy()

    def __init__(self, podaci):
        super().__init__()

        self.__podaci = podaci

        slika = ImageTk.PhotoImage(Image.open('radiologija_slika.png'))
        self.__slika_label = Label(self, image=slika)
        self.__slika_label.image = slika
        self.__slika_label['image'] = slika
        self.__slika_label.grid()

        meni_bar = Menu(self)

        datoteka_meni = Menu(meni_bar, tearoff=0)
        datoteka_meni.add_command(label='Izlaz', command=self.komanda_izlaz)
        meni_bar.add_cascade(label='Datoteka', menu=datoteka_meni)

        podaci_meni = Menu(meni_bar, tearoff=0)
        podaci_meni.add_command(label='Prikaz pacijenata', command=self.komanda_prikaz_pacijenata)
        podaci_meni.add_command(label='Prikaz snimanja', command=self.komanda_prikaz_snimanja)
        meni_bar.add_cascade(label='Podaci', menu=podaci_meni)

        self.config(menu=meni_bar)

        self.protocol('WM_DELETE_WINDOW', self.komanda_izlaz)

        self.iconbitmap('radiology.ico')
        self.title('Radiologija')

        self.update_idletasks()
        sirina = self.winfo_width()
        visina = self.winfo_height()
        self.minsize(sirina, visina)

        self.transient()
        self.grab_set()
        self.focus_force()


class ProzorPrikazPacijenata(Toplevel):

    def pretrazi_pacijente(self, pretraga):
        pacijenti = []
        for pacijent in self.__podaci.pacijenti:
            if pretraga.upper() in pacijent.ime.upper() or pretraga.upper() in pacijent.prezime.upper():
                pacijenti.append(pacijent)
        return pacijenti

    def popuni_listbox_pacijentima(self, event):
        self.komanda_ocisti()
        self.__pacijenti_listbox.delete(0, END)
        sortirani_pacijenti = sorted(self.pretrazi_pacijente(self.__pretrazi_pacijente_entry.get()), key=lambda pacijent:pacijent.prezime)
        for pacijent in sortirani_pacijenti:
            self.__pacijenti_listbox.insert(END, pacijent.prezime + ' ' + pacijent.ime)

    def popuni_labele_podacima(self, pacijenti):
        self.__lbo_labela['text'] = pacijenti.lbo
        self.__ime_labela['text'] = pacijenti.ime
        self.__prezime_labela['text'] = pacijenti.prezime
        self.__datum_rodjenja_labela['text'] = pacijenti.datum_rodjenja.strftime('%d.%m.%Y.')

    def promena_selekcije_u_listboxu(self, event=None):
        if self.__pretrazi_pacijente.get() == '':
            if not self.__pacijenti_listbox.curselection():
                self.komanda_ocisti()
                return

            indeks = self.__pacijenti_listbox.curselection()[0]
            pacijent = sorted(self.__podaci.pacijenti, key=lambda pacijent: pacijent.prezime)[indeks]
            self.popuni_labele_podacima(pacijent)

            self.__button_obrisi['state'] = NORMAL
            self.__button_izmeni['state'] = NORMAL
            self.__button_ocisti['state'] = NORMAL
            self.__button_prikaz_snimanja['state'] = NORMAL
        else:
            if not self.__pacijenti_listbox.curselection():
                self.komanda_ocisti()
                return

            indeks = self.__pacijenti_listbox.curselection()[0]
            pacijent = \
                sorted(self.pretrazi_pacijente(self.__pretrazi_pacijente.get()), key=lambda pacijent: pacijent.prezime)[
                    indeks]
            self.popuni_labele_podacima(pacijent)

            self.__button_obrisi['state'] = NORMAL
            self.__button_izmeni['state'] = NORMAL
            self.__button_ocisti['state'] = NORMAL
            self.__button_prikaz_snimanja['state'] = NORMAL

    def komanda_ocisti(self):
        self.__lbo_labela['text'] = ''
        self.__ime_labela['text'] = ''
        self.__prezime_labela['text'] = ''
        self.__datum_rodjenja_labela['text'] = ''

        self.__pacijenti_listbox.selection_clear(0, END)

        self.__button_obrisi['state'] = DISABLED
        self.__button_izmeni['state'] = DISABLED
        self.__button_ocisti['state'] = DISABLED
        self.__button_prikaz_snimanja['state'] = DISABLED

    def komanda_obrisi(self):
        odgovor = messagebox.askquestion('Upozorenje',
                                         'Brisanjem pacijenta brišu se sva njihova snimanja.\nDa li ste sigurni da želite da obrišete pacijenta?')
        if odgovor == 'no':
            return

        indeks = self.__pacijenti_listbox.curselection()[0]
        pacijent_za_brisanje = sorted(self.pretrazi_pacijente(self.__pretrazi_pacijente_entry.get()), key=lambda pacijent: pacijent.prezime)[
            indeks]
        self.__podaci.obrisi_pacijenta(pacijent_za_brisanje)
        self.__pretrazi_pacijente.set('')
        self.config(cursor='wait')
        Podaci.sacuvaj(self.__podaci)
        self.config(cursor='')
        self.popuni_listbox_pacijentima('')

        self.__pacijenti_listbox.delete(indeks)
        self.popuni_listbox_pacijentima('')
        self.__pacijenti_listbox.selection_set(indeks-1)
        self.promena_selekcije_u_listboxu()

    def komanda_dodaj(self):

        self.__pretrazi_pacijente.set('')

        dodavanje_pacijenta_prozor = DodajPacijentaProzor(self, self.__podaci)
        self.wait_window(dodavanje_pacijenta_prozor)
        if dodavanje_pacijenta_prozor.otkazan:
            return

        pacijent = self.__podaci.pacijenti[-1]
        indeks = sorted(self.__podaci.pacijenti, key=lambda pacijent: pacijent.prezime).index(pacijent)
        self.__pacijenti_listbox.insert(indeks, pacijent.prezime + ' ' + pacijent.ime)
        self.__pacijenti_listbox.selection_set(indeks)
        self.promena_selekcije_u_listboxu()

    def komanda_prikaz_snimanja(self):
        indeks1  = self.__pacijenti_listbox.curselection()[0]
        pacijent = sorted(self.pretrazi_pacijente(self.__pretrazi_pacijente_entry.get()), key=lambda pacijent:pacijent.prezime)[indeks1]

        indeks2 = sorted(self.__podaci.pacijenti, key=lambda pacijent:pacijent.prezime).index(pacijent)

        prozor_prikaz_snimanja = ProzorSnimanje(self, self.__podaci, indeks2 + 1)
        self.wait_window(prozor_prikaz_snimanja)

    def komanda_povratak(self):
        self.destroy()

    def komanda_izmeni(self):

        if self.__pretrazi_pacijente.get() == '':
            indeks = self.__pacijenti_listbox.curselection()[0]
            pacijent = sorted(self.__podaci.pacijenti, key=lambda pacijent: pacijent.prezime)[indeks]

            izmena_pacijenta_prozor = IzmeniPacijentaProzor(self, self.__podaci, pacijent)
            self.wait_window(izmena_pacijenta_prozor)

            if izmena_pacijenta_prozor.otkazan:
                return

            self.__pacijenti_listbox.delete(indeks)
            self.__pacijenti_listbox.insert(indeks, pacijent.prezime + ' ' + pacijent.ime)
            self.__pretrazi_pacijente.set('')
            self.__pacijenti_listbox.selection_set(indeks)
            self.promena_selekcije_u_listboxu()
        else:
            indeks = self.__pacijenti_listbox.curselection()[0]
            pacijent = \
                sorted(self.pretrazi_pacijente(self.__pretrazi_pacijente.get()), key=lambda pacijent: pacijent.prezime)[
                    indeks]

            izmena_pacijenta_prozor = IzmeniPacijentaProzor(self, self.__podaci, pacijent)
            self.wait_window(izmena_pacijenta_prozor)

            if izmena_pacijenta_prozor.otkazan:
                return

            self.__pacijenti_listbox.delete(indeks)
            self.__pacijenti_listbox.insert(indeks, pacijent.prezime + ' ' + pacijent.ime)
            self.__pretrazi_pacijente.set('')
            self.__pacijenti_listbox.selection_set(indeks)
            self.promena_selekcije_u_listboxu()

    def __init__(self, master, podaci):

        super().__init__(master)

        self.__podaci = podaci

        self.__pacijenti_listbox = Listbox(self, activestyle='none')
        self.__pacijenti_listbox.pack(side=LEFT, fill=BOTH, expand=1)
        self.__pacijenti_listbox.bind('<<ListboxSelect>>', self.promena_selekcije_u_listboxu)

        self.__pacijenti_frame = Frame(self, borderwidth=2, relief='ridge', padx=10, pady=10)
        self.__pacijenti_frame.pack(side=RIGHT, fill=BOTH, expand=1)

        self.__lbo_labela = Label(self.__pacijenti_frame)
        self.__ime_labela = Label(self.__pacijenti_frame)
        self.__prezime_labela = Label(self.__pacijenti_frame)
        self.__datum_rodjenja_labela = Label(self.__pacijenti_frame)

        self.__pretrazi_pacijente = StringVar(master)
        self.__pretrazi_pacijente_entry = Entry(self.__pacijenti_frame, width=20,
                                                textvariable=self.__pretrazi_pacijente)


        self.__button_ocisti = Button(self.__pacijenti_frame, text='Očisti', width=10, command=self.komanda_ocisti, state=DISABLED)
        self.__button_obrisi = Button(self.__pacijenti_frame, text='Obriši', width=10, command=self.komanda_obrisi, state=DISABLED)
        self.__button_dodaj = Button(self.__pacijenti_frame, text='Dodaj', width=10, command=self.komanda_dodaj)
        self.__button_prikaz_snimanja = Button(self.__pacijenti_frame, text='Prikaz snimanja', width=15, command=self.komanda_prikaz_snimanja, state=DISABLED)
        self.__button_izmeni = Button(self.__pacijenti_frame, text='Izmeni', width=10, command=self.komanda_izmeni, state=DISABLED)
        self.__button_povratak = Button(self.__pacijenti_frame, text='Povratak', width=10, command=self.komanda_povratak)

        red = 0
        kolona = 0
        Label(self.__pacijenti_frame, text='Pretraži pacijente:').grid(row=red, sticky=E)
        red += 1
        Label(self.__pacijenti_frame, text='LBO:').grid(row=red, sticky=E)
        red += 1
        Label(self.__pacijenti_frame, text='Ime:').grid(row=red, sticky=E)
        red += 1
        Label(self.__pacijenti_frame, text='Prezime:').grid(row=red, sticky=E)
        red += 1
        Label(self.__pacijenti_frame, text='Datum rođenja:').grid(row=red, sticky=E)
        red += 1
        kolona += 1
        self.__button_prikaz_snimanja.grid(row=red, column=kolona, sticky=E)
        kolona += 1
        self.__button_dodaj.grid(row=red, column=kolona, sticky=W)
        kolona += 1
        self.__button_izmeni.grid(row=red, column=kolona, sticky=W)

        red = 0
        kolona = 1
        self.__pretrazi_pacijente_entry.grid(row=red, column=kolona, sticky=W)
        self.__pretrazi_pacijente_entry.bind("<KeyRelease>", self.popuni_listbox_pacijentima)

        red += 1
        self.__lbo_labela.grid(row=red, column=kolona, sticky=W)
        red += 1
        self.__ime_labela.grid(row=red, column=kolona, sticky=W)
        red += 1
        self.__prezime_labela.grid(row=red, column=kolona, sticky=W)
        red += 1
        self.__datum_rodjenja_labela.grid(row=red, column=kolona, sticky=W)
        red += 2
        kolona = 1
        self.__button_ocisti.grid(row=red, column=kolona, sticky=E)
        kolona += 1
        self.__button_obrisi.grid(row=red, column=kolona, sticky=W)
        kolona += 1
        self.__button_povratak.grid(row=red, column=kolona, sticky=W)

        self.protocol('WM_DELETE_WINDOW', self.komanda_povratak)
        self.popuni_listbox_pacijentima('')

        self.title('Lista pacijenata')
        self.iconbitmap('radiology.ico')

        self.update_idletasks()
        sirina = self.winfo_width()

        visina = self.winfo_height()
        self.minsize(sirina, visina)

        self.transient(master)
        self.focus_force()
        self.grab_set()


class ProzorDodaj(Toplevel):

    def ime_validacija(self):
        ime = self.__ime.get()
        if len(ime) <= 2:
            messagebox.showerror('Greška', 'Ime mora sadržati više od dva karaktera!')
            return None
        return ime

    def prezime_validacija(self):

        prezime = self.__prezime.get()
        if len(prezime) <= 2:
            messagebox.showerror('Greška', 'Prezime mora sadržati više od dva karaktera!')
            return None
        return prezime

    def datum_rodjenja_validacija(self):
        try:
            datum_rodjenja = datetime.date(self.__datum_rodjenja_godina.get(), self.__datum_rodjenja_mesec.get(),
                                           self.__datum_rodjenja_dan.get())
            if not datum_rodjenja < datetime.date.today():
                messagebox.showerror('Greška', 'Datum nije validan!')
                return None
            return datum_rodjenja
        except TclError:
            messagebox.showerror('Greška', 'Datum nije validan!')

    def komanda_potvrdi(self):

        self.config(cursor='wait')
        Podaci.sacuvaj(self.__podaci)
        self.config(cursor='')

        self.__otkazan = False

        self.destroy()

    def komanda_povratak(self):
        self.destroy()

    def __init__(self, master, podaci):
        super().__init__(master)

        self.__podaci = podaci

        self.__otkazan = True

        self.__pacijenti_frame = Frame(self, borderwidth=2, relief='ridge', padx=10, pady=10)
        self.__pacijenti_frame.pack(fill=BOTH, expand=1)

        self.__ime = StringVar(master)
        self.__prezime = StringVar(master)
        self.__datum_rodjenja_dan = IntVar(master)
        self.__datum_rodjenja_mesec = IntVar(master)
        self.__datum_rodjenja_godina = IntVar(master)
        self.__lbo = StringVar(master)

        self.__ime_entry = Entry(self.__pacijenti_frame, width=20, textvariable=self.__ime)
        self.__prezime_entry = Entry(self.__pacijenti_frame, width=20, textvariable=self.__prezime)
        self.__datum_rodjenja_dan_spinbox = Spinbox(self.__pacijenti_frame, width=5, from_=1, increment=1, to=31,
                                                    textvariable=self.__datum_rodjenja_dan)
        self.__datum_rodjenja_mesec_spinbox = Spinbox(self.__pacijenti_frame, width=5, from_=1, increment=1, to=12,
                                                      textvariable=self.__datum_rodjenja_mesec)
        self.__datum_rodjenja_godina_spinbox = Spinbox(self.__pacijenti_frame, width=5, from_=1900, increment=1,
                                                       to=datetime.date.today().year,
                                                       textvariable=self.__datum_rodjenja_godina)
        self.__lbo_entry = Entry(self.__pacijenti_frame, width=20, textvariable=self.__lbo, state=DISABLED)

        self.__button_potvrdi = Button(self.__pacijenti_frame, text='', width=10, command=self.komanda_potvrdi)
        self.__button_povratak = Button(self.__pacijenti_frame, text='Повратак', width=10,
                                        command=self.komanda_povratak)

        red = 0
        Label(self.__pacijenti_frame, text='LBO').grid(row=red, sticky=E)
        red += 1
        Label(self.__pacijenti_frame, text='Ime:').grid(row=red, sticky=E)
        red += 1
        Label(self.__pacijenti_frame, text='Prezime:').grid(row=red, sticky=E)
        red += 1
        Label(self.__pacijenti_frame, text='Datum rođenja(dan/mesec/godina):').grid(row=red, sticky=E)

        red = 0
        kolona = 1
        self.__lbo_entry.grid(row=red, column=kolona, sticky=W)
        red += 1
        self.__ime_entry.grid(row=red, column=kolona, sticky=W)
        red += 1
        self.__prezime_entry.grid(row=red, column=kolona, sticky=W)
        red += 1
        self.__datum_rodjenja_dan_spinbox.grid(row=red, column=kolona, sticky=E)
        kolona += 1
        self.__datum_rodjenja_mesec_spinbox.grid(row=red, column=kolona, sticky=W + E + S + N)
        kolona += 1
        self.__datum_rodjenja_godina_spinbox.grid(row=red, column=kolona, sticky=W)
        red += 1
        kolona = 1
        self.__button_potvrdi.grid(row=red, column=kolona, sticky=E)
        kolona += 1
        self.__button_povratak.grid(row=red, column=kolona, sticky=W)

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
    def podaci(self):
        return self.__podaci

    @property
    def lbo(self):
        return self.__lbo

    @property
    def ime(self):
        return self.__ime

    @property
    def prezime(self):
        return self.__prezime

    @property
    def datum_rodjenja_dan(self):
        return self.__datum_rodjenja_dan

    @property
    def datum_rodjenja_mesec(self):
        return self.__datum_rodjenja_mesec

    @property
    def datum_rodjenja_godina(self):
        return self.__datum_rodjenja_godina

    @property
    def button_potvrdi(self):
        return self.__button_potvrdi


class DodajPacijentaProzor(ProzorDodaj):

    def komanda_potvrdi(self):

        ime = self.ime_validacija()
        if not ime:
            return
        prezime = self.prezime_validacija()
        if not prezime:
            return
        datum_rodjenja = self.datum_rodjenja_validacija()
        if not datum_rodjenja:
            return

        pacijent = Pacijent(ime, prezime, datum_rodjenja)
        self.__podaci.dodaj_pacijenta(pacijent)

        super().komanda_potvrdi()

    def __init__(self, master, podaci):

        super().__init__(master, podaci)

        self.__podaci = podaci

        self.button_potvrdi['text'] = 'Dodaj'
        self.title('Dodaj pacijenta')
        self.iconbitmap('radiology.ico')


class IzmeniPacijentaProzor(ProzorDodaj):

    def komanda_potvrdi(self):

        ime = self.ime_validacija()
        if not ime:
            return
        prezime = self.prezime_validacija()
        if not prezime:
            return
        datum_rodjenja = self.datum_rodjenja_validacija()
        if not datum_rodjenja:
            return

        self.__pacijent.ime = ime
        self.__pacijent.prezime = prezime
        self.__pacijent.datum_rodjenja = datum_rodjenja

        super().komanda_potvrdi()

    def __init__(self, master, podaci, pacijent):

        super().__init__(master, podaci)

        self.__pacijent = pacijent

        self.lbo.set(pacijent.lbo)
        self.ime.set(pacijent.ime)
        self.prezime.set(pacijent.prezime)
        self.datum_rodjenja_dan.set(pacijent.datum_rodjenja.day)
        self.datum_rodjenja_mesec.set(pacijent.datum_rodjenja.month)
        self.datum_rodjenja_godina.set(pacijent.datum_rodjenja.year)

        self.button_potvrdi['text'] = 'Izmeni'
        self.title('Izmeni pacijenta')
        self.iconbitmap('radiology.ico')


def main():
    podaci = Podaci.ucitaj()

    radiologija_prozor = RadiologijaProzor(podaci)
    radiologija_prozor.mainloop()


main()

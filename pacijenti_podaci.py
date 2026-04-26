from uuid import uuid4
import datetime
import pickle

class Pacijent():

    @property
    def lbo(self):
        return self.__lbo

    @property
    def ime(self):
        return self.__ime
    @ime.setter
    def ime(self, ime):
        self.__ime = ime

    @property
    def prezime(self):
        return self.__prezime
    @prezime.setter
    def prezime(self, prezime):
        self.__prezime = prezime

    @property
    def datum_rodjenja(self):
        return self.__datum_rodjenja

    @property
    def snimanja(self):
        return self.__snimanja

    @datum_rodjenja.setter
    def datum_rodjenja(self, datum_rodjenja):
        self.__datum_rodjenja = datum_rodjenja

    def dodaj_snimanje(self, snimanje):
        self.__snimanja.append(snimanje)

    __tekuci_datum = datetime.date.today()

    def __init__(self, ime, prezime, datum_rodjenja):

        if len(ime) >= 2 and len(prezime) >= 2 and datum_rodjenja <= self.__tekuci_datum:

            self.__lbo = uuid4().hex[:11]
            self.__ime = ime
            self.__prezime = prezime
            self.__datum_rodjenja = datum_rodjenja
            self.__snimanja = []

        else:
            return

    def __str__(self):
        try:
            format_linije = '{:>13}: {}'

            return '\n'.join([
                '',
                format_linije.format('LBO', self.__lbo),
                format_linije.format('Ime', self.__ime),
                format_linije.format('Prezime', self.__prezime),
                format_linije.format('Datum rođenja', self.__datum_rodjenja.strftime('%d.%m.%Y.')),
                Snimanje.tabela(self.__snimanja)
            ])
        except:
            return 'Uneti podaci nisu validni!'

class Snimanje():

    @property
    def pacijent(self):
        return self.__pacijent
    @pacijent.setter
    def pacijent(self, pacijent):
        self.__pacijent = pacijent

    @property
    def datum_i_vreme(self):
        return self.__datum_i_vreme
    @datum_i_vreme.setter
    def datum_i_vreme(self, datum_i_vreme):
        self.__datum_i_vreme = datum_i_vreme

    @property
    def tip(self):
        return self.__tip
    @tip.setter
    def tip(self, tip):
        self.__tip = tip

    @property
    def izvestaj(self):
        return self.__izvestaj
    @izvestaj.setter
    def izvestaj(self, izvestaj):
        self.__izvestaj = izvestaj

    @property
    def lekar(self):
        return self.__lekar
    @lekar.setter
    def lekar(self, lekar):
        self.__lekar = lekar

    @property
    def snimak(self):
        return self.__snimak
    @snimak.setter
    def snimak(self, snimak):
        self.__snimak = snimak

    @classmethod
    def tabela(self, snimanja):

        format_linije = '{:20} {:40} {:20} {:20}'

        prikaz = [
            '',
            format_linije.format('Datum i vreme', 'Tip', 'Lekar', 'Izveštaj'),
            format_linije.format('-'*20, '-'*40, '-'*20, '-'*20)
        ]
        for snimanje in snimanja:
            prikaz.append(format_linije.format(
                snimanje.__datum_i_vreme.strftime('%d.%m.%Y %H:%M:%S'),
                snimanje.__tip,
                snimanje.__lekar,
                snimanje.__izvestaj
            ))

        return '\n'.join(prikaz)

    def __init__(self, pacijent, datum_i_vreme, tip, izvestaj, lekar, snimak):

        if pacijent.datum_rodjenja <= datetime.date(datum_i_vreme.year, datum_i_vreme.month, datum_i_vreme.day) <= datetime.date.today():
            self.__pacijent = pacijent
            self.__datum_i_vreme = datum_i_vreme
            self.__tip = tip
            self.__izvestaj = izvestaj
            self.__lekar = lekar
            self.__snimak = snimak
        else:
            None

    def __str__(self):
        try:
            format_linije = '{:>13}: {}'

            return '\n'.join([
                '',
                format_linije.format('Pacijent', self.__pacijent.ime + ' ' + self.__pacijent.prezime),
                format_linije.format('Datum i vreme', self.__datum_i_vreme.strftime('%d.%m.%Y. %H:%M:%S')),
                format_linije.format('Tip', self.__tip),
                format_linije.format('Izveštaj', self.__izvestaj),
                format_linije.format('Lekar', self.__lekar),
                format_linije.format('Snimak', self.__snimak)
            ])
        except:
            return 'Uneti podaci nisu validni!'

class Podaci():

    @classmethod
    def pocetni_podaci(cls):
        podaci = Podaci()

        pacijenti = podaci.pacijenti
        pacijent1 = Pacijent('Ivan', 'Petrović', datetime.date(2010, 3, 29))
        pacijent2 = Pacijent('Milena', 'Stajić', datetime.date(1984, 8, 1))
        pacijent3 = Pacijent('Jovan', 'Kovačević', datetime.date(2000, 7, 21))

        snimanja = podaci.snimanja
        snimanje1 = Snimanje(pacijent1, datetime.datetime(2018, 3, 15, 14, 30, 0), 'Magnetna rezonanca (MR)', 'Izveštaj1', 'Nemanja Perić', r'E:\Kasandra\UMI\Projekat UMI\Projekat\CT-MONO2-16-ort.dcm')
        snimanje2 = Snimanje(pacijent2, datetime.datetime(1999, 12, 7, 9, 45, 0), 'Mamografija', 'Izveštaj4', 'Sanja Miletić', r'E:\Kasandra\UMI\Projekat UMI\Projekat\MR-MONO2-16-head.dcm')
        snimanje3 = Snimanje(pacijent3, datetime.datetime(2005, 1, 10, 12, 15, 0), 'Magnetna rezonanca (MR)', 'Izveštaj6', 'Bojana Đukić', r'E:\Kasandra\UMI\Projekat UMI\Projekat\MRBRAIN.DCM')

        pacijenti.append(pacijent1)
        pacijenti.append(pacijent2)
        pacijenti.append(pacijent3)

        snimanja.append(snimanje1)
        snimanja.append(snimanje2)
        snimanja.append(snimanje3)

        pacijent1.dodaj_snimanje(snimanje1)
        pacijent2.dodaj_snimanje(snimanje2)
        pacijent2.dodaj_snimanje(snimanje3)


        return podaci

    @property
    def pacijenti(self):
        return self.__pacijenti

    @property
    def snimanja(self):
        return self.__snimanja

    def __init__(self):
        self.__pacijenti = []
        self.__snimanja = []
        self.__snimci= []

    __naziv_datoteke = 'podaci_pacijenti'

    @classmethod
    def sacuvaj(cls, podaci):
        datoteka = open(cls.__naziv_datoteke, "wb")
        pickle.dump(podaci, datoteka)
        datoteka.close()

    def sacuvaj_se(self):
        self.sacuvaj(self)

    @classmethod
    def ucitaj(cls):
        try:
            datoteka = open(cls.__naziv_datoteke, "rb")
            podaci = pickle.load(datoteka)
            datoteka.close()
        except FileNotFoundError:
            return Podaci.pocetni_podaci()

        return podaci

    def obrisi_pacijenta(self, pacijent):
        self.__pacijenti.remove(pacijent)

        snimanja_za_brisanje = []

        for snimanje in self.__snimanja:
            if pacijent == snimanje.pacijent:
                snimanja_za_brisanje.append(snimanje)

        for snimanje in snimanja_za_brisanje:
            self.__snimanja.remove(snimanje)

    def dodaj_pacijenta(self, pacijent):
        self.__pacijenti.append(pacijent)

    def obrisi_snimanje(self, snimanje):
        self.__snimanja.remove(snimanje)

        for pacijent in self.__pacijenti:
            if snimanje in pacijent.snimanja:
                pacijent.snimanja.remove(snimanje)

    def dodaj_snimanje(self, snimanje):
        self.__snimanja.append(snimanje)

    def dodaj_snimak(self, snimak):
        self.__snimci.append(snimak)


def test():
    podaci = Podaci.pocetni_podaci()

    print()
    print("Čuvanje...")
    Podaci.sacuvaj(podaci)

    print("Učitavanje...")
    podaci = Podaci.ucitaj()
    pacijenti = podaci.pacijenti
    snimanja = podaci.snimanja

    for pacijent in pacijenti:
        print(pacijent)

    for snimanje in snimanja:
        print(snimanje)

#test()
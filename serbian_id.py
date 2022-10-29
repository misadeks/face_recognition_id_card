from freesteel.common import get_reader_list, get_default_reader
from freesteel.eid_card import EidCard, PersonalField, DocumentField, ResidenceField
from freesteel.exceptions import *
from smartcard.Exceptions import *
from datetime import date, datetime
import json

class Personal:
    def __init__(self, data):
        self.jmbg = data[PersonalField.PIN]
        self.first_name = data[PersonalField.FIRST_NAME]
        self.last_name = data[PersonalField.LAST_NAME]
        self.middle_name = data[PersonalField.MIDDLE_NAME]
        self.sex = data[PersonalField.SEX]
        self.birth_place = data[PersonalField.BIRTH_PLACE]
        self.birth_municipality = data[PersonalField.BIRTH_MUNICIPAL]
        self.birth_country = data[PersonalField.BIRTH_COUNTRY]
        self.birth_country_code = data[PersonalField.BIRTH_COUNTRY_CODE]

        raw_date = self.jmbg[:7]
        raw_day = raw_date[:2]
        raw_month = raw_date[2:4]
        raw_year = raw_date[4:]
        raw_year = "2" + raw_year if raw_year[0] == '0' else '1' + raw_year  # fixes the leading digit
        self.date_of_birth = date(int(raw_year), int(raw_month), int(raw_day))

        try:
            self.father_jmbg = data[40]
        except KeyError:
            self.father_jmbg = None

        try:
            self.mother_jmbg = data[41]
        except KeyError:
            self.mother_jmbg = None

        today = date.today()
        self.age = today.year - self.date_of_birth.year - \
                   ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))


class Document:
    def __init__(self, data):
        self.id_number = data[DocumentField.ID]
        self.issue_date = datetime.strptime(data[DocumentField.RELEASE_DATE], '%d%m%Y').date()
        self.expiry_date = datetime.strptime(data[DocumentField.VALID_UNTIL], '%d%m%Y').date()
        self.issuer = data[DocumentField.ISSUER]
        self.issuer_country = data[DocumentField.ISSUER_COUNTRY]
        self.valid = self.expiry_date > date.today()


class Residence:
    def __init__(self, data):
        self.country_code = data[ResidenceField.COUNTRY_CODE]
        self.place = data[ResidenceField.PLACE]
        self.municipality = data[ResidenceField.MUNICIPAL]
        self.street_name = data[ResidenceField.STREET]
        self.street_number = data[ResidenceField.NUMBER]

        try:
            self.floor = data[39]
        except KeyError:
            self.floor = None

        try:
            self.apartment_number = data[42]
        except KeyError:
            self.apartment_number = None


class SerbianId:
    """
    Helper and wrapper class for freesteel
    """

    def __init__(self):
        self.__reader = None
        self.readers = get_reader_list()
        self.__card = None

    def set_default_reader(self, reader=None):
        if reader is not None:
            self.__reader = reader
        else:
            self.__reader = get_default_reader()

    def wait_for_card(self):
        card = self.__reader.wait_for_card()
        self.__card = EidCard(card)

    def get_data(self):
        self.personal = Personal(self.__card.get_personal())
        self.document = Document(self.__card.get_document())
        self.residence = Residence(self.__card.get_residence())
        self.photo = self.__card.get_photo()
        pass

    def __repr__(self):
        return json.dumps({
            'personal': {
                'first_name': self.personal.first_name,
                'middle_name': self.personal.middle_name,
                'last_name': self.personal.last_name,
                'sex': self.personal.sex,
                'jmbg': self.personal.jmbg,
                'date_of_birth': self.personal.date_of_birth.strftime('%d.%m.%Y.'),
                'birth_country': self.personal.birth_country,
                'birth_country_code': self.personal.birth_country_code,
                'birth_place': self.personal.birth_place,
                'birth_municipality': self.personal.birth_municipality,
                'father_jmbg': self.personal.father_jmbg,
                'mother_jmbg': self.personal.mother_jmbg
            },
            'document': {},
            'residence': {}
        }, ensure_ascii=False)
def get_id_data():
    try:
        reader = get_default_reader()
        card = reader.wait_for_card()
        eid_card = EidCard(card)
        personal = eid_card.get_personal()
        personal_num = personal[PersonalField.PIN]
        photo = eid_card.get_photo()
        card.disconnect()
        return {"status": "success",
                "of_age": of_age(personal_num)
                }
    except EmptyReaderListError:  # no readers
        return {"status": "error",
                "error_desc": "EmptyReaderListError"}
    except GetReaderListError:  # no readers
        return {"status": "error",
                "error_desc": "GetReaderListError"}
    except CardConnectionException:  # unpowered card (flipped)
        return {"status": "error",
                "error_desc": "CardConnectionException"}
    except ConnectCardError:  # unknown card
        return {"status": "error",
                "error_desc": "ConnectCardError"}
    except NoCardException:  # card disconnected while reading
        return {"status": "error",
                "error_desc": "NoCardException"}


def of_age(personal_num):
    raw_date = personal_num[:7]
    raw_day = raw_date[:2]
    raw_month = raw_date[2:4]
    raw_year = raw_date[4:]

    raw_year = "2" + raw_year if raw_year[0] == "0" else "1" + raw_year  # fixes the leading digit
    date = datetime.date(int(raw_year), int(raw_month), int(raw_day))
    today = datetime.date.today()

    if today.month < date.month or \
            (today.month == date.month and today.day < date.day):
        age = today.year - date.year - 1
    else:
        age = today.year - date.year

    return age >= 18


def valid(expiration_date):
    pass

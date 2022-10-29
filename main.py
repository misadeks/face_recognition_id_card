from freesteel.common import get_default_reader, get_reader_list
from freesteel.eid_card import EidCard, PersonalField
from freesteel.exceptions import *
from smartcard.Exceptions import *
from rich.console import Console
from face import recognize_face
import datetime
import srtools
from serbian_id import SerbianId

console = Console(color_system='standard')
try:
    console.print('ID card facial recognition')
    id_card = SerbianId()
    id_card.set_default_reader()
    console.print('Insert a card!')
    id_card.wait_for_card()
    console.print('Card inserted! Reading...')
    id_card.get_data()
    if id_card.document.valid:
        console.print('ID card is valid!', style='green')
    else:
        console.print('ID card is invalid!', style='red')
        exit(0)
    if id_card.personal.age >= 18:
        console.print('Person is of age!', style='green')
    else:
        console.print('Person is underage!', style='red')
        exit(0)
    console.print('Starting facial verification...')
    result = recognize_face(id_card.photo, srtools.cyrillic_to_latin(id_card.personal.first_name))
    if result:
        console.print('Facial verification successful!', style='green')
    else:
        console.print('Facial verification failed!', style='red')

except (EmptyReaderListError, GetReaderListError):  # no readers
    console.print('No readers found.', style='red')
except CardConnectionException:  # unpowered card (flipped)
    console.print('Inserted card is flipped or non-functional.', style='red')
except ConnectCardError:  # unknown card
    console.print('Inserted card is unrecognized.', style='red')
except (NoCardException, GetDataError):  # card disconnected while reading
    console.print('Card was removed while reading it.', style='red')


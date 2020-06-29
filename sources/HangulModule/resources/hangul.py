import unicodedata
import os

class Jamos:

    initial = "ᄀᄁᄂᄃᄄᄅᄆᄇᄈᄉᄊᄋᄌᄍᄎᄏᄐᄑᄒ"
    medial = "ᅡᅢᅣᅤᅥᅦᅧᅨᅩᅪᅫᅬᅭᅮᅯᅰᅱᅲᅳᅴᅵ"
    final = "ᆨᆩᆪᆫᆬᆭᆮᆯᆰᆱᆲᆳᆴᆵᆶᆷᆸᆹᆺᆻᆼᆽᆾᆿᇀᇁᇂ"

    consonants = initial + final
    vowels = medial

    @classmethod
    def all(cls):
        return cls.initial + cls.medial + cls.final

    @classmethod
    def get(cls, position):
        if position == 'initial':
            return cls.initial
        if position == 'medial':
            return cls.medial
        if position == 'final':
            return cls.final

class CharacterInfos:

    def __init__(self, composition: str = ""):
        self.composition = composition

    def __str__(self):
        return self.composition

    def __repr__(self):
        return str(self)

    def __iter__(self):
        for c in self.composition:
            yield c

    @property
    def initial(self):
        for c in self.composition:
            if c in Jamos.initial:
                return c

    @property
    def medial(self):
        for c in self.composition:
            if c in Jamos.medial:
                return c

    @property
    def final(self):
        for c in self.composition:
            if c in Jamos.final:
                return c    
        return ""

class Composition:

    def __init__(self, composition = {}):
        if not composition:
            cwd = os.getcwd()
            path = os.path.join(cwd, 'resources', 'HangulUnicode.txt')
            with open(path, "r", encoding = "utf-8") as file:
                encoding = file.read()

            for char in encoding:
                comp = "".join(list(set(unicodedata.normalize('NFD', char))))
                setattr(self, char, CharacterInfos(comp))

    def __getitem__(self, item):
        if not hasattr(self, item):
            return ""
        return getattr(self, item)

    def __iter__(self):
        for x in vars(self):
            yield x


if __name__ == '__main__':
    composition = Composition()
    medial = set()
    for x in composition:
        for c in composition[x]:
            if c != composition[x].initial and c != composition[x].final:
                medial.add(c)

    print("".join(list(medial)))
    print(len("".join(list(medial))))

    print(len("ㅏㅑㅓㅕㅗㅛㅜㅠㅡㅣㅐㅒㅔㅖㅘㅙㅚㅝㅞㅟㅢ"))


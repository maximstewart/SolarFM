# Python imports

# Lib imports

# Application imports


class SingletonError(Exception):
    pass



class Singleton:
    ccount = 0

    def __new__(cls, *args, **kwargs):
        obj        = super(Singleton, cls).__new__(cls)
        cls.ccount += 1

        if cls.ccount == 2:
            raise SingletonError(f"Exceeded {cls.__name__} instantiation limit...")

        return obj

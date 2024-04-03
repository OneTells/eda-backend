from time import time


class TimeCounter:

    def __init__(self, *, hours: int = 0, minutes: int = 0, seconds: int = 0, milliseconds: int = 0) -> None:
        self.__period = int(hours * 3600 + minutes * 60 + seconds + milliseconds / 1000)

        self.__first_element: int | None = None
        self.__last_element: int | None = None

        self.__deltas: list[int] = []

    def __check(self) -> None:
        current_time = time() - self.__period
        element = self.__first_element

        for index, delta in enumerate(self.__deltas):
            element += delta

            if element > current_time:
                del self.__deltas[:index]

                self.__first_element = element
                self.__deltas[0] = 0
                return

        self.__deltas.clear()
        self.__first_element = None
        self.__last_element = None

    def add(self) -> int:
        element = int(time())

        if self.__last_element is not None:
            self.__deltas.append(element - self.__last_element)
            self.__last_element = element
        else:
            self.__deltas.append(0)
            self.__first_element = element
            self.__last_element = element

        self.__check()
        return len(self.__deltas)

    @property
    def time_until_element_is_deleted(self) -> int:
        return self.__period - (int(time()) - self.__first_element)

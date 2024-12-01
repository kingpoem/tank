

from abc import ABC, abstractmethod


class Shootable(ABC):
    @abstractmethod
    def shoot(self):
        pass
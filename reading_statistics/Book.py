from typing import Optional
from dataclasses import dataclass


@dataclass
class Book:
    author_name: Optional[str]
    series_name: Optional[str]
    isbn: int
    title: Optional[str]
    series_index: Optional[float]
    chapters: Optional[int]
    pages: Optional[int]
    released: Optional[str]
    finished: Optional[str]
    speed: Optional[int]
    time: Optional[float]

    def print(self):  # pragma: no cover
        print(f"ISBN:\t\t{self.isbn}\nAuthor:\t\t{self.author_name}\nSeries:\t\t{self.series_name}\nTitle:\t\t{self.title}\nSeries index:\t{self.series_index}\nChapters:\t{self.chapters}\nPages:\t\t{self.pages}\nReleased:\t{self.released}\nFinished:\t{self.finished}\nSpeed:\t\t{self.speed}\nTime:\t\t{self.time}\n")

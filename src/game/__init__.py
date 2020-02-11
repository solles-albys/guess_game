from .category import Category
from .song import Song
from random import randint

from typing import Optional, List


class Game:
    def __init__(self, categories: List[Category]):
        self.categories: List[Category] = categories
        self.current_category: Optional[Category] = None

        self.is_finished = False

    @property
    def is_category_finished(self):
        return ((self.current_category and self.current_category.is_finished) or
                not self.current_category or
                self.is_finished)

    @property
    def is_song_picked(self):
        return self.current_category.current_song is not None

    @property
    def is_song_playing(self):
        return (self.current_category.current_song is not None and
                self.current_category.is_playing)

    async def next_category(self):
        if not self.categories:
            self.is_finished = True
            self.current_category = None
            return

        category = self.categories.pop(0)
        self.current_category = category

    async def pick_song(self, score: int) -> Song:
        if not self.current_category:
            raise RuntimeError('не выбрана категория')

        return await self.current_category.pick_song(score)

    async def unpick_song(self) -> str:
        if not self.current_category:
            raise RuntimeError('не выбрана категория')

        if not self.current_category.current_song:
            raise RuntimeError('не выбрана песня')

        return await self.current_category.unpick_song()

    async def play_song(self):
        if not self.current_category:
            raise RuntimeError('не выбрана категория')

        if not self.current_category.current_song:
            raise RuntimeError('не выбрана песня')

        await self.current_category.play_song(forever=False)

    async def play_full_song(self):
        if not self.current_category:
            raise RuntimeError('не выбрана категория')

        if not self.current_category.current_song:
            raise RuntimeError('не выбрана песня')

        await self.current_category.play_song(forever=True)

    async def stop_play_song(self):
        if not self.current_category:
            raise RuntimeError('не выбрана категория')

        if not self.current_category.current_song:
            raise RuntimeError('не выбрана песня')

        await self.current_category.stop_song()

    @classmethod
    def from_cfg(cls, data: dict) -> 'Game':
        categories = data['categories']
        categories = [Category.from_cfg(c) for c in categories]

        return cls(categories)


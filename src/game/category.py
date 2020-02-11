from .song import Song
from typing import List, Optional
from random import randint


class Category:
    def __init__(self, name: str, songs: List[Song]):
        self.name = name
        self.songs: List[Song] = songs

        by_score = {}
        for s in songs:
            if s.score not in by_score:
                by_score[s.score] = []

            by_score[s.score].append(s)
        self.by_score = by_score

        self.current_song: Optional[Song] = None

    @property
    def is_finished(self):
        return not self.by_score

    @property
    def is_playing(self):
        if not self.current_song:
            return False

        return self.current_song.is_playing

    async def pick_song(self, score: int):
        if score not in self.by_score:
            raise ValueError('Нет таких значений очков.')

        if self.current_song is not None:
            raise RuntimeError('Песня уже выбрана.')

        _songs = self.by_score[score]
        if len(_songs) == 1:
            song = _songs.pop()
            del self.by_score[score]
            self.current_song = song
            return

        index = randint(0, len(_songs) - 1)
        song = _songs.pop(index)
        self.current_song = song
        return song

    async def play_song(self, forever=False):
        if not self.current_song:
            raise RuntimeError('Не выбрана песня.')

        func = self.current_song.play if forever else self.current_song.play_limited
        await func()

    async def stop_song(self):
        if not self.is_playing:
            return

        if not self.current_song:
            return

        await self.current_song.stop()

    async def unpick_song(self) -> str:
        if not self.current_song:
            raise RuntimeError('Песня не выбрана.')

        song = self.current_song
        self.current_song = None
        return song.answer

    def to_json(self):
        return {
            score: [s.to_json() for s in songs]
            for score, songs in self.by_score.items()
        }

    @classmethod
    def from_cfg(cls, data: dict) -> 'Category':
        name = data['name']

        songs = [
            Song(**s) for s in data['songs']
        ]
        return cls(name, songs)

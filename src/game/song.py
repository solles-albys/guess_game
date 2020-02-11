import vlc
from asyncio import sleep


class Song:
    def __init__(self, name: str, answer: str, score: int, duration=5):
        self.answer = answer
        self.score = score

        self._player: vlc.MediaPlayer = vlc.MediaPlayer(
            f'file:///Users/gvdozd/Projects/guess_song/files/{name}.mp3'
        )

        self._duration = duration

        self.is_done = False

    @property
    def is_playing(self) -> bool:
        return self._player.is_playing()

    async def play_limited(self):
        self._player.play()
        self._player.set_position(0.0)

        await sleep(self._duration)
        self._player.stop()

    async def play(self):
        self._player.play()
        self._player.set_position(0.0)

    async def stop(self):
        self._player.stop()

    @classmethod
    def from_cfg(cls, data: dict) -> 'Song':
        return cls(**data)

    def to_json(self) -> dict:
        return {
            'score': self.score,
            'answer': self.answer,
            'duration': self._duration,
        }

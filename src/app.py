import json
from asyncio import iscoroutinefunction
from typing import List

from aiohttp.web import Request, Response, json_response

from src.game import Game
from src.players import (
    Community,
    player_json
)


def on_error(func):
    def sync_wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            if not isinstance(result, Response):
                return Response()
        except Exception as e:
            return json_response({'error': str(e)})

    async def async_wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            if not isinstance(result, Response):
                return Response()
        except Exception as e:
            return json_response({'error': str(e)})

    return async_wrapper if iscoroutinefunction(func) else sync_wrapper


class Service:
    def __init__(self):
        with open('config.json', 'r') as file:
            content = file.read()

        config = json.loads(content)
        server_cfg = config.get('server', {})

        self.port = server_cfg.get('port', 80)
        self.host = server_cfg.get('host', '0.0.0.0')

        self.community = Community()
        self.game = Game.from_cfg(config['game'])

    #   BOARD METHODS

    @on_error
    async def is_allowed_to_push_button(self, r):
        return json_response({
            'result': self._is_allowed_to_push_button()
        })

    @on_error
    async def is_game_finished(self, r):
        return json_response({
            'result': self.game.is_finished
        })

    @on_error
    async def is_category_finished(self, r):
        return json_response({
            'result': self.game.is_category_finished
        })

    @on_error
    async def get_current_category(self, r):
        if not self.game.current_category:
            data = {
                "result": None
            }
        else:
            data = {
                "result": self.game.current_category.to_json()
            }

        return json_response(data)

    @on_error
    async def list_teams(self, r):
        return {
            "result": self.teams_json()
        }

    @on_error
    async def get_current_move_team(self, r):
        return {
            "result": self.community.move_on
        }

    #   PLAYER METHODS
    #   songs and game
    @on_error
    async def pick_song(self, r: Request):
        c = self.community
        team = c.move_on
        if not team:
            raise RuntimeError('Сейчас не ваш ход')

        ip = _get_ip(r)
        if not c.is_participant(team, ip):
            raise RuntimeError('Сейчас не ваш ход')

        data = await r.json()
        score = data['score']

        song = await self.game.pick_song(score)
        return json_response({
            'result': song.to_json()
        })

    @on_error
    async def push_button(self, r: Request):
        if not self._is_allowed_to_push_button():
            return

        await self.community.push_button(_get_ip(r))
        return json_response({
            "result": self.community.button_pushed
        })

    # logins

    @on_error
    async def login(self, r: Request):
        data = await r.json()
        await self.community.login(_get_ip(r), data['name'])

    @on_error
    async def logout(self, r: Request):
        await self.community.logout(_get_ip(r))

    @on_error
    async def create_team(self, r: Request):
        ip = _get_ip(r)

        data = await r.json()
        newname = data['name']

        await self.community.create_team(newname, ip)

        return json_response({
            'result': self.teams_json()
        })

    @on_error
    async def join_team(self, r: Request):
        data = await r.json()
        await self.community.join_team(data['name'], _get_ip(r))

    @on_error
    async def remove_team(self, r: Request):
        await self.community.remove_team(_get_ip(r))
        return json_response({
            'result': self.teams_json()
        })

    #   ADMIN METHODS

    @on_error
    async def change_max_group_size(self, r):
        data = await r.json()
        size = data['size']
        await self.community.change_max_team_size(size)

    #   game

    @on_error
    async def pass_move_to(self, r: Request):
        data = await r.json()
        await self.community.pass_move_to(data['name'])

    @on_error
    async def release_button(self, _):
        await self.community.release_button()

    #   music

    @on_error
    async def get_current_song(self, _):
        category = self.game.current_category
        if category:
            song = category.current_song
            if song:
                return {
                    "result": song.to_json()
                }

        return {
            "result": None
        }

    @on_error
    async def unpick_song(self, _):
        answer = await self.game.unpick_song()

        return json_response({
            "result": answer
        })

    @on_error
    async def next_category(self, _):
        if self.game.is_finished:
            return

        if self.game.is_category_finished:
            await self.game.next_category()

    @on_error
    async def play_music(self, _):
        await self.game.play_song()

    @on_error
    async def play_full_music(self, _):
        await self.game.play_full_song()

    @on_error
    async def stop_music(self, _):
        await self.game.stop_play_song()

    #   SOME USEFUL

    def teams_json(self) -> List[dict]:
        return [
            t.to_json() for t in self.community.teams.values()
        ]

    def _is_allowed_to_push_button(self):
        return (not self.game.is_song_playing and
                self.community.allow_push)


def _get_ip(r: Request) -> str:
    peername = r.transport.get_extra_info('peername')
    if peername is not None:
        return peername[1]

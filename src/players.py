from typing import Dict, Tuple, List, Optional

PlayerIP = str
PlayerName = str
Player = Tuple[PlayerIP, PlayerName]

def player_json(p: Player):
    return p[1]


class Players(list):
    def get(self, ip=None, name=None) -> (PlayerIP, PlayerName):
        if not ip and not name:
            return None, None

        for i, n in self:
            if i == ip or name == n:
                return i, n

        return None, None

    def change_name(self, ip: PlayerIP, newname: PlayerName) -> (PlayerIP, PlayerName):
        for index, p in enumerate(self):
            i = p[0]
            if i == ip:
                self[index] = (ip, newname)
                return ip, newname

        return None, None


class Team:
    def __init__(self, name: str, owner: Player):
        self.score = 0
        self.name = name
        self.owner: Player = owner
        self.players = Players()

    async def add_score(self, amount: int) -> int:
        self.score += amount
        return self.score

    async def remove_score(self, amount: int) -> int:
        self.score -= amount
        return self.score

    async def add_player(self, p: Player):
        self.players.append(p)

    async def remove_player(self, p: Player = None):
        if not p:
            self.players.pop(-1)
        self.players.remove(p)

    def is_participant(self, p: Player):
        if p[0] == self.owner[0]:
            return True

        i, n = self.players.get(p[0], p[1])
        return i is not None

    @property
    def size(self):
        return len(self.players) + 1

    def to_json(self) -> dict:
        return {
            'name': self.name,
            'score': self.score,
            'owner': player_json(self.owner),
            'participants': [
                player_json(p) for p in self.players
            ]
        }


class Community:
    def __init__(self):
        self.players: Players = Players()
        self.teams: Dict[str, Team] = {}

        self.max_team_size = 3

        self.button_pushed: Optional[str] = None
        self.allow_push = False
        self.move_on: Optional[Team] = None

    async def pass_move_to(self, name: str):
        if name not in self.teams:
            raise ValueError('Нет такой команды.')

        self.move_on = self.teams[name]

    async def push_button(self, ip: PlayerIP) -> Optional[Team]:
        if self.button_pushed is not None:
            return

        if not self.allow_push:
            return

        team = self.get_team(ip)
        self.button_pushed = team.name
        return team

    async def release_button(self):
        self.move_on = None
        self.button_pushed = None
        self.allow_push = False

    async def add_scores(self, name: str, amount: int) -> int:
        if name not in self.teams:
            raise ValueError('Неизвестная команда')

        return await self.teams[name].add_score(amount)

    async def remove_scores(self, name: str, amount: int ) -> int:
        if name not in self.teams:
            raise ValueError('Неизвестная команда')

        return await self.teams[name].remove_score(amount)

    async def login(self, ip: PlayerIP, name: PlayerName):
        i, n = self.players.get(ip, name)
        if i is not None:
            self.players.change_name(ip, name)
            return

        p = (ip, name)
        self.players.append(p)

    async def logout(self, ip: PlayerIP):
        p = self.players.get(ip)
        if p[0] is None:
            return

        self.players.remove(p)

        for t in self.teams.values():
            if t.is_participant(p):
                await t.remove_player(p)

    async def create_team(self, name: str, ip: PlayerIP):
        name = name.lower().strip()
        if name in self.teams:
            raise RuntimeError('Команда уже существует')

        if self.is_owner(ip):
            raise RuntimeError('Уже есть своя команда.')

        p = self.players.get(ip)
        t = self.get_team(ip)
        if t is not None:
            await t.remove_player(p)

        newteam = Team(name, p)
        self.teams[name] = newteam

    async def remove_team(self, ip: PlayerIP):
        team = self.get_team(ip)

        if team.owner != ip:
            raise RuntimeError('Удалить группу может только ее владелец')

        else:
            self.teams.pop(team.name)

    def is_owner(self, ip: PlayerIP):
        for t in self.teams.values():
            if ip == t.owner[0]:
                return True

        return False

    def is_participant(self, team: Team, ip: PlayerIP) -> bool:
        p = self.players.get(ip)
        return team.is_participant(p)

    def get_team(self, ip: PlayerIP) -> Optional[Team]:
        p = self.players.get(ip)

        for t in self.teams.values():
            if t.is_participant(p):
                return t

        return None

    async def join_team(self, name: str, ip: PlayerIP):
        name = name.lower().strip()
        if name not in self.teams:
            raise RuntimeError('Команды не существует')

        if self.is_owner(ip):
            raise RuntimeError('Нельзя вступать в группы, если пользователь владеет своей группой.')

        p = self.players.get(ip)
        group_already = self.get_team(ip)

        if group_already is not None:
            await group_already.remove_player(p)

        t = self.teams[name]

        if t.size >= self.max_team_size:
            raise RuntimeError('В команде нет мест.')

        if t.is_participant(p):
            raise RuntimeError('Пользователь уже состоит в этой группе.')

        await t.add_player(p)

    async def change_max_team_size(self, newsize: int):
        if newsize <= 2:
            newsize = 3

        self.max_team_size = newsize
        for g in self.teams.values():
            while g.size > newsize:
                await g.remove_player()

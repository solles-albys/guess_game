from aiohttp import web
from random import seed
from time import time
from src.app import Service

seed(time())


def main():
    app = web.Application()
    service = Service()

    app.add_routes([
        # board methods
        web.get('/board/is_allowed_to_push_button', service.is_allowed_to_push_button),
        web.get('/board/is_game_finished', service.is_game_finished),
        web.get('/board/is_category_finished', service.is_category_finished),
        web.get('/board/get_current_category', service.get_current_category),
        web.get('/board/list_teams', service.list_teams),
        web.get('/board/get_current_move_team', service.get_current_move_team),

        # admin methods
        web.post('/admin/change_max_group_size', service.change_max_group_size),
        # admin moves
        web.post('/admin/pass_move_to', service.pass_move_to),
        web.post('/admin/release_button', service.release_button),
        # admin music
        web.get('/admin/get_current_song', service.get_current_song),
        web.post('/admin/unpick_song', service.unpick_song),
        web.post('/admin/next_category', service.next_category),
        web.post('/admin/play_music', service.play_music),
        web.post('/admin/play_full_music', service.play_full_music),
        web.post('/admin/stop_music', service.stop_music),

        # player methods
        web.post('/player/pick_song', service.pick_song),
        web.post('/player/push_button', service.push_button),
        # player login methods
        web.post('/player/login', service.login),
        web.post('/player/logout', service.logout),
        web.post('/player/create_team', service.create_team),
        web.post('/player/join_team', service.join_team),
        web.post('/player/remove_team', service.join_team),
    ])

    port = service.port
    host = service.host

    web.run_app(app, port=port, host=host)


if __name__ == '__main__':
    main()

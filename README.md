# Guess Song Game

The game for friends to play at home.
This is actually backend server that provides handlers for the host, for the game board and for players.

The idea is to let players use their phones to choose categories and answers.

---
###Before start
Install VLC before.

Collect several songs whenever you want inside `./files`. Personally, i prefer to put them in subdirs by category.

Then create file `config.json` and describe songs and server params there:

```json
{
    "server": {
        "host": "0.0.0.0",
        "port": "80"
    },
    "game": {
        "categories": [
            {
                "name": "Songs of 80's",
                "songs": [
                    {
                        "name": "path/to/song_file",
                        "score": 100,
                        "answer": "42",
                        "duration": 10.0
                    }
                ]
            }
        ]
    }
}
```

A little bit about `path/to/song_file`:

Actually, this is path to file from files dir without file extension

Example: I have file `./files/mysongs/song.mp3`, so i put there `mysong/song`


## TODO

- [x] basic setup
    - [ ] global settings for rooms etc
        - but i have nothing to set so far (i guess)
- [x] reputation
    - [x] parsing to message " +rep @user "reason plus or minus rep" "
    - [x] no self rep
    - [x] spam protection
    - [x] saving and loading current (currently to json, mby into database)
        - [x] saving once per time
- [x] basic song player
    - [x] play
    - [x] pause
    - [x] loading lists
        - downloading source url takes long time and it must be remade to async or something
    - [x] insert into position
    - [ ] fix bugs with playing songs and suddenly skipping
- [ ] reminder
    - [ ] just remind me into dms and into channel where i wrote this command

## instalation

- ffmpeg is required
    - in the executable folder
- rename `example-config.ini` to `config.ini` and write there your discord token
- new enviroment and source it
- install `requirements.txt`
- run `python main.py`

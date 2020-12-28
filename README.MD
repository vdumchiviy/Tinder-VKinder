# **Tinder-VKinder project (pre alpha)**

## The project presents a way to find person in social network VK by bot. User has to connect to community (for example, VKinder that created by me). The conversation will starts when user sends one of the commands below:

## - **search**: search pair
## - **new**: begin new search settings
## - **set age from**: set minimal age for ## searching
## - **set age to**: set maximum age for searching
## - **set age**: set exact age for searching
## - **set sex**: set exact sex for searching
## - **set relation**: set relation for searching
## - **list**: list all pairs
## - **del**: delete pair
## - **blacklist**: list all blacklist pairs
----------------------

### How to install:
#### Before run you have to save community token in file 'resources\vkinder_key.ini' and administrator (like a user) token in file 'resources\vkuser_key.ini'. See https://vk.com/dev how you can take tokens.

----------------------
### How to run:
#### The main file locates in folder 'vkbot\vk_bot.py'. Just run it. Make sure that you set test_mode to False and do comment line *vk_bot._repository_hard_reset()* in that file if you run it NOT in the first time.

----------------------
### For developers:
#### This project supports to save data in various repositories. You can add your repository in your own folder and then change 'def __init__' recorded your own import using your own 'mode':
        elif mode == 'your own mode indentificator':
            from your folder import Repository
            .... some code if you need ...
            self.repository = Repository()

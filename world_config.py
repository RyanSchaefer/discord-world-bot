
items = {
    'wood': {
        'limit': 500,
        'time_to_produce': 1,
        'substrates': {},
        'toolbonus': {},
        'product_range': (1, 10)
    },
    'woodaxe': {
        'limit':1,
        'time_to_produce': 30,
        'substrates': {
            'wood': -10
        },
        'toolbonus': {
            'wood': 0.5
        },
        'product_range': (1, 1)
    }
}
vehicles = {
    'woodencart': {
        'storage_limits':{
            'wood': 100
        },
        'attachments':{
            'limit':0
        },
        'speed_bonus': 0
    },
    'train': {

    }
}
era = 'Phase I'
tips = [
    'Keep up with the development of World Bot at: https://trello.com/b/HzqmpLDf/world-bot'
]
admins = [
    '142735811454959616'
]
admin_failed = [
    'You have no power here!',
    'You shall not pass!',
    'User does not have a high enough squid content to acess this command!',
    'Segmentation fault',
    'I built my self up to admin with a very small loan of one million dollars',
    'Stop trying please',
    ';DROP ALL DATABASES;--',
    'You are not an admin'
]
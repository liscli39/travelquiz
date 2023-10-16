class Enum:
    GROUP_STATUS_DEFAULT = 0
    GROUP_STATUS_WAITING = 1
    GROUP_STATUS_PLAYING = 2
    GROUP_STATUS_FINISHED = 3
    GroupStatus = (
        (GROUP_STATUS_DEFAULT, 'default'),
        (GROUP_STATUS_WAITING, 'waiting'),
        (GROUP_STATUS_PLAYING, 'playing'),
        (GROUP_STATUS_FINISHED, 'finished'),
    )

    USER_GROUP_STATUS_DEFAULT = 0
    USER_GROUP_STATUS_WAITING = 1
    USER_GROUP_STATUS_READY = 2
    USER_GROUP_STATUS_INGAME = 3
    USER_GROUP_STATUS_FINISHED = 4
    GroupUserStatus = (
        (USER_GROUP_STATUS_DEFAULT, 'default'),
        (USER_GROUP_STATUS_WAITING, 'waiting'),
        (USER_GROUP_STATUS_READY, 'ready'),
        (USER_GROUP_STATUS_INGAME, 'ingame'),
        (USER_GROUP_STATUS_FINISHED, 'finished'),
    )

    MIN_JOIN_MEMBER = 1

    GENDER_MALE = 1
    GENDER_FEMALE = 0
    Genders = (
        (GENDER_MALE, 'male'),
        (GENDER_FEMALE, 'female'),
    )

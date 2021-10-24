LEAD_PAGE_NAME = 'Brain Team'
SIGN_IN_PAGE_NAME = 'Вход'
SIGN_UP_PAGE_NAME = 'Регистрация'
EVENT_INFO = "Инфо."
EVENT_ERROR = "Ошибка"
NON_CORRECT_DATA = "Введены некорректные данные"

PROFILE_PAGE_NAME = "Профиль"
COMPANY_PAGE_NAME = "Организация"
TEAMS_PAGE_NAME = "Команды"
SCHEDULE_PAGE_NAME = "Расписание"
SIGN_OUT_PAGE = "Выйти"
EVENTS_PAGE_NAME = "Мероприятия"

PROFILE_STATUS = {0: '-', 1: 'на подтверждение', -1: 'запрос отклонен'}
PAGES = [[PROFILE_PAGE_NAME, 'profile'], [COMPANY_PAGE_NAME, 'company'], [TEAMS_PAGE_NAME, 'teams'],
         [SCHEDULE_PAGE_NAME, 'schedule'], [EVENTS_PAGE_NAME, 'events'], [SIGN_OUT_PAGE, 'sign_out']]

PAGES_DICT = {key: value for key, value in PAGES}

SUBPAGES = {COMPANY_PAGE_NAME: [['Описание', 'description'], ['Запросы', 'requests']],
            TEAMS_PAGE_NAME: [['Список', 'teams'], ['Создать команду', 'create_team'],
                              ['Запросы', 'requests_teams_list'], ['Отправить запрос', 'request_to_team']],

            EVENTS_PAGE_NAME: [['Создать мероприятие', 'create_event'], ['Тестирование', 'test_event']],
            SCHEDULE_PAGE_NAME: [['Квизы', 'quiz_list']]}

from aiogram import Router


def setup_routers() -> Router:

    from handlers import (start_command, help_command, cancel_all_fire_subs,
                          echo_handler, handle_munic_name, last_fires_news, my_fire_subs,
                          subscribe_all_fires, subscribe_one_fire, support, daily_fire_report, statistics)

    from callbacks import main_menu, cb_subscribe_all_fires, wait_for_munic_name
    
    from support import adminmode, usermode

    router = Router()
    router.include_router(adminmode.router)
    router.include_router(usermode.router)
    router.include_router(start_command.router)
    router.include_router(help_command.router)
    router.include_router(cancel_all_fire_subs.router)
    router.include_router(daily_fire_report.router)
    router.include_router(statistics.router)
    # router.include_router(echo_handler.router)
    router.include_router(handle_munic_name.router)
    router.include_router(last_fires_news.router)
    router.include_router(my_fire_subs.router)
    router.include_router(subscribe_all_fires.router)
    router.include_router(subscribe_one_fire.router)
    router.include_router(support.router)
    router.include_router(main_menu.router)
    router.include_router(cb_subscribe_all_fires.router)
    router.include_router(wait_for_munic_name.router)
    
    

    return router

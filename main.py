import argparse
import traceback

import helpers


def main(mode: str, channel: str = 'stable') -> int:
    if mode not in ('cli', 'gui', 'gui-no-interrupt'):
        raise ValueError('Invalid mode')
    if channel not in helpers.CHANNELS:
        raise ValueError('Invalid channel')
    if mode == 'cli':
        info = lambda title, message: print(message)
        error = info
    else:
        import gui
        gui.SHOW_INFO = mode != 'gui-no-interrupt'
        info, error = gui.show_info, gui.show_error
    elevation = 'sudo' if mode == 'cli' else 'auto'
    try:
        package = helpers.fetch_file(channel=channel)
        if package:
            info('Info', 'An update has been downloaded. Installation will begin.')
            if not helpers.install_file(package, elevate_command=elevation):
                error('Error', 'Installation failed.')
                return 1
            helpers.mark_installed(package, channel)
            info('Success', 'Installation completed successfully.')
        else:
            info('Info', 'No updates available.')
        helpers.replace_discord_desktop(elevate_command=elevation)
        helpers.clear_downloads()
        return 0
    except Exception:
        error('Error', traceback.format_exc())
        return 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['cli', 'gui', 'gui-no-interrupt'])
    parser.add_argument('channel', nargs='?', default='stable', choices=helpers.CHANNELS)
    arguments = parser.parse_args()
    raise SystemExit(main(arguments.mode, arguments.channel))

import helpers
from sys import argv as args
from sys import exit
import traceback

def main(mode: str, channel: str = 'stable') -> int:
    modes = ['gui', 'cli', "gui-no-interrupt"]
    return_code = 0

    if mode not in modes:   
        raise ValueError(f"Invalid mode. Choose from {modes}.")
    error = ""
    error_class = None
    try:
        file = helpers.fetch_file(pkg='deb')
    except Exception as e:
        return_code = 1
        error = traceback.format_exc()
        error_class = e.__class__.__name__
    
    if mode == 'cli':   
        if return_code != 0:
            print(f"Error fetching file due to {error_class}.\n\n{error}\n\nFull traceback:\n{error}")
        elif file:
            success = helpers.install_file(file, elevate_command='sudo')
            if success:
                print("Installation completed successfully.")
            else:
                print("Installation failed.")
                return_code = 1
    elif mode.startswith('gui'):
        import gui

        if mode == 'gui-no-interrupt':
            gui.SHOW_INFO = False

        if return_code != 0:
            gui.show_error("Error", f"Error fetching file due to {error_class}.")
        elif file:
            gui.show_info("Info", "An update has been downloaded. Installation will begin. Press OK to continue.")
            success = helpers.install_file(file, elevate_command='auto')
            if success:
                gui.show_info("Success", "Installation completed successfully.")
            else:
                gui.show_error("Error", "Update failed.")
        else:
            gui.show_info("Info", "No updates available.")

    helpers.clear_downloads()
    return return_code


if __name__ == '__main__':
    if len(args) > 1:
        modes = ['gui', 'cli', "gui-no-interrupt"]
        channels = ['stable', 'ptb', 'canary']
        mode_arg = ""
        channel_arg = "stable"

        for channel in channels:
            if channel in args:
                channel_arg = channel
                break

        for mode in modes:
            if mode in args:
                mode_arg = mode
                break
        try:
            return_code = main(mode=mode_arg, channel=channel_arg)
        except ValueError:
            print("Invalid argument. Use 'gui', 'gui-no-interrupt' or 'cli'.")
            exit(1)
        
        exit(return_code)
    else:
        print("Please provide a mode argument: 'gui' or 'cli'.")
        exit(1)
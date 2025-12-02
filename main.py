import helpers
from sys import argv as args
from sys import exit

def main(mode: str):
    modes = ['gui', 'cli']
    return_code = 0

    if mode not in modes:   
        raise ValueError(f"Invalid mode. Choose from {modes}.")
    file = helpers.fetch_file(pkg='deb')
    if mode == 'cli':   
        

        if file:
            success = helpers.install_file(file, elevate_cmd='sudo')
            if success:
                print("Installation completed successfully.")
            else:
                print("Installation failed.")
                return_code = 1
    elif mode == 'gui':
        import gui
        if file:
            gui.show_info("Info", "An update has been downloaded. Installation will begin. Press OK to continue.")
            success = helpers.install_file(file, elevate_cmd='auto')
            if success:
                gui.show_info("Success", "Installation completed successfully.")
            else:
                gui.show_error("Error", "Installation failed.")
        else:
            gui.show_info("Info", "No updates available.")

    helpers.clear_downloads()
    return return_code


if __name__ == '__main__':
    if len(args) > 1:
        mode_arg = args[1].lower()
        try:
            return_code = main(mode=mode_arg)
        except ValueError:
            print("Invalid argument. Use 'gui' or 'cli'.")
            exit(1)
        
        exit(return_code)
    else:
        print("Please provide a mode argument: 'gui' or 'cli'.")
        exit(1)
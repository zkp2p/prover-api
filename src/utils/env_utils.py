import os
from dotenv import load_dotenv

def read_env_credentials(env_example_path, env_path):
    env_credentials = {}
    if os.path.isfile(env_example_path):
        def get_variable_names_from_env_file(file_path=env_example_path):
            variable_names = []
            with open(file_path) as file:
                for line in file:
                    # Ignore comments and empty lines
                    if line.startswith('#') or line.strip() == '':
                        continue
                    # Extract variable name (part before the '=' character)
                    variable_name = line.split('=')[0].strip()
                    variable_names.append(variable_name)
            return variable_names

        # Load additional environment variables from the .env file
        additional_vars = get_variable_names_from_env_file()
        load_dotenv(env_path)  # Load environment variables from .env file
        for var_name in additional_vars:
            # If it doesnt start with local
            if not var_name.startswith("LOCAL_"):
                var_value = os.getenv(var_name)
                if var_value is not None:
                    # TODO: Make this cleaner; remove all uses of a non local/modal path env var
                    env_credentials[var_name] = var_value
                    var_name = var_name.replace("MODAL_", "")
                    env_credentials[var_name] = var_value
    return env_credentials
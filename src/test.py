import unittest
from dotenv import load_dotenv
SERVICE_STATE = "dev"
load_dotenv(f"./token_{SERVICE_STATE}.env") # load all the variables from the env file

from mod.league import retrieve_test


if __name__ == "__main__":
    unittest.main()
    
from pathlib import Path

from processing.core.ProcessingConfig import ProcessingConfig
from qgis.PyQt.QtCore import QCoreApplication, QSettings

from processing_r.processing.provider import RAlgorithmProvider
from processing_r.processing.utils import RUtils


def test_r_is_installed():
    """
    Test checking that R is installed
    """
    assert RUtils.check_r_is_installed() is None

    ProcessingConfig.setSettingValue(RUtils.R_FOLDER, "/home")

    assert isinstance(RUtils.check_r_is_installed(), str)
    assert "R is not installed" in RUtils.check_r_is_installed()

    ProcessingConfig.setSettingValue(RUtils.R_FOLDER, None)
    assert RUtils.check_r_is_installed() is None


def test_guess_r_binary_folder():
    """
    Test guessing the R binary folder -- not much to do here, all the logic is Windows specific
    """
    assert RUtils.guess_r_binary_folder() == ""


def test_r_binary_folder():
    """
    Test retrieving R binary folder
    """
    assert RUtils.r_binary_folder() == ""

    ProcessingConfig.setSettingValue(RUtils.R_FOLDER, "/usr/local/bin")
    assert RUtils.r_binary_folder() == "/usr/local/bin"

    ProcessingConfig.setSettingValue(RUtils.R_FOLDER, None)
    assert RUtils.r_binary_folder() == ""


def test_r_executable():
    """
    Test retrieving R executable
    """
    assert RUtils.path_to_r_executable() == "R"
    assert RUtils.path_to_r_executable(script_executable=True) == "Rscript"

    ProcessingConfig.setSettingValue(RUtils.R_FOLDER, "/usr/local/bin")
    assert RUtils.path_to_r_executable() == "/usr/local/bin/R"
    assert RUtils.path_to_r_executable(script_executable=True) == "/usr/local/bin/Rscript"

    ProcessingConfig.setSettingValue(RUtils.R_FOLDER, None)
    assert RUtils.path_to_r_executable() == "R"
    assert RUtils.path_to_r_executable(script_executable=True) == "Rscript"


def test_package_repo():
    """
    Test retrieving/setting the package repo
    """
    assert RUtils.package_repo() == "http://cran.at.r-project.org/"

    ProcessingConfig.setSettingValue(RUtils.R_REPO, "http://mirror.at.r-project.org/")
    assert RUtils.package_repo() == "http://mirror.at.r-project.org/"

    ProcessingConfig.setSettingValue(RUtils.R_REPO, "http://cran.at.r-project.org/")
    assert RUtils.package_repo() == "http://cran.at.r-project.org/"


def test_use_user_library():
    """
    Test retrieving/setting the user library setting
    """
    assert RUtils.use_user_library() is True

    ProcessingConfig.setSettingValue(RUtils.R_USE_USER_LIB, False)
    assert RUtils.use_user_library() is False

    ProcessingConfig.setSettingValue(RUtils.R_USE_USER_LIB, True)
    assert RUtils.use_user_library() is True


def test_library_folder():
    """
    Test retrieving/setting the library folder
    """
    assert "/profiles/default/processing/rlibs" in RUtils.r_library_folder()

    ProcessingConfig.setSettingValue(RUtils.R_LIBS_USER, "/usr/local")
    assert RUtils.r_library_folder() == "/usr/local"

    ProcessingConfig.setSettingValue(RUtils.R_LIBS_USER, None)
    assert "/profiles/default/processing/rlibs" in RUtils.r_library_folder()


def test_is_error_line():
    """
    Test is_error_line
    """
    assert RUtils.is_error_line("xxx yyy") is False
    assert RUtils.is_error_line("Error something went wrong") is True
    assert RUtils.is_error_line("Execution halted") is True


def test_is_valid_r_variable():
    """
    Test for strings to check if they are valid R variables.
    """
    assert RUtils.is_valid_r_variable("var_name%") is False
    assert RUtils.is_valid_r_variable("2var_name") is False
    assert RUtils.is_valid_r_variable(".2var_name") is False
    assert RUtils.is_valid_r_variable("_var_name") is False

    assert RUtils.is_valid_r_variable("var_name2.") is True
    assert RUtils.is_valid_r_variable(".var_name") is True
    assert RUtils.is_valid_r_variable("var.name") is True


def test_scripts_folders():
    """
    Test script folders
    """
    assert RUtils.script_folders()
    assert RUtils.default_scripts_folder() in RUtils.script_folders()
    assert RUtils.builtin_scripts_folder() in RUtils.script_folders()


def test_descriptive_name():
    """
    Tests creating descriptive name
    """
    assert RUtils.create_descriptive_name("a B_4324_asd") == "a B 4324 asd"


def test_strip_special_characters():
    """
    Tests stripping special characters from a name
    """
    assert RUtils.strip_special_characters("aB 43 24a:sd") == "aB4324asd"


def test_is_windows():
    """
    Test is_windows
    """
    assert RUtils.is_windows() is False  # suck it, Windows users!


def test_is_macos():
    """
    Test is_macos
    """
    assert RUtils.is_macos() is False  # suck it even more, MacOS users!


def test_built_in_path():
    """
    Tests built in scripts path
    """
    assert RUtils.builtin_scripts_folder()
    assert "builtin_scripts" in RUtils.builtin_scripts_folder()
    assert Path(RUtils.builtin_scripts_folder()).exists()


def test_default_scripts_folder():
    """
    Tests default user scripts folder
    """
    assert RUtils.default_scripts_folder()
    assert "rscripts" in RUtils.default_scripts_folder()
    assert Path(RUtils.default_scripts_folder()).exists()

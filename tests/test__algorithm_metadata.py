from qgis.core import QgsProcessingContext, QgsProcessingFeedback

from processing_r.processing.algorithm import RAlgorithm
from tests.utils import IS_API_ABOVE_31604, script_path


def test_dont_load_any_packages():
    """
    Test dont_load_any_packages keyword
    """
    alg = RAlgorithm(description_file=script_path("test_dont_load_any_packages.rsx"))
    alg.initAlgorithm()

    context = QgsProcessingContext()
    feedback = QgsProcessingFeedback()

    script = alg.build_r_script({}, context, feedback)

    assert not any([x == 'library("sf")' for x in script])
    assert not any([x == 'library("raster")' for x in script])
    assert not any(["library(" in x for x in script])


def test_library_with_options():
    """
    Test library with options
    """

    alg = RAlgorithm(description_file=script_path("test_library_with_option.rsx"))
    alg.initAlgorithm()

    script = alg.r_templates.build_script_header_commands(alg.script)

    assert 'tryCatch(find.package("MASS"), error = function(e) install.packages("MASS", dependencies=TRUE))' in script

    assert (
        'tryCatch(find.package("Matrix"), error = function(e) install.packages("Matrix", dependencies=TRUE))' in script
    )

    assert 'library("MASS", quietly=True)' in script
    assert 'library("Matrix")' in script


def test_help():  # pylint: disable=too-many-locals,too-many-statements
    """
    Test algorithm help
    """
    alg = RAlgorithm(description_file=script_path("test_algorithm_1.rsx"))
    alg.initAlgorithm()

    assert "A polygon layer" in alg.shortHelpString()
    assert "Me2" in alg.shortHelpString()
    assert "Test help." in alg.shortHelpString()

    # param help
    if IS_API_ABOVE_31604:
        polyg_param = alg.parameterDefinition("polyg")
        assert polyg_param.help() == "A polygon layer"

    # no help file
    alg = RAlgorithm(description_file=script_path("test_algorithm_2.rsx"))
    alg.initAlgorithm()

    assert alg.shortHelpString() == ""

    alg = RAlgorithm(description_file=script_path("test_algorithm_inline_help.rsx"))
    alg.initAlgorithm()

    assert "A polygon layer" in alg.shortHelpString()
    assert "Me2" in alg.shortHelpString()
    assert "Test help." in alg.shortHelpString()

    # param help
    if IS_API_ABOVE_31604:
        polyg_param = alg.parameterDefinition("polyg")
        assert polyg_param.help() == "A polygon layer description from multi-lines"


def test_ussuported_lines():
    alg = RAlgorithm(None, script="##load_raster_using_rgdal")
    alg.initAlgorithm()
    assert "This command is no longer supported" in alg.error

    alg = RAlgorithm(None, script="##load_vector_using_rgdal")
    alg.initAlgorithm()
    assert "This command is no longer supported" in alg.error

    alg = RAlgorithm(None, script="##dontuserasterpackage")
    alg.initAlgorithm()
    assert "This command is no longer supported" in alg.error

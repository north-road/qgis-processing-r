from processing_r.processing.r_templates import RTemplates


def test_github_install():
    """
    Test github install code generation.
    """
    templates = RTemplates()
    templates.install_github = True
    templates.github_dependencies = "user_1/repo_1, user_2/repo_2"
    assert (
        templates.install_package_github(templates.github_dependencies[0]) == 'remotes::install_github("user_1/repo_1")'
    )

    assert (
        templates.install_package_github(templates.github_dependencies[1]) == 'remotes::install_github("user_2/repo_2")'
    )


def test_string():  # pylint: disable=too-many-locals,too-many-statements
    """
    Test string variable
    """
    templates = RTemplates()
    assert templates.set_variable_string("var", "val") == 'var <- "val"'
    assert templates.set_variable_string("var", 'va"l') == 'var <- "va\\"l"'


def test_string_list_variable():  # pylint: disable=too-many-locals,too-many-statements
    """
    Test string list variable
    """
    templates = RTemplates()
    assert templates.set_variable_string_list("var", []) == "var <- c()"
    assert templates.set_variable_string_list("var", ["aaaa"]) == 'var <- c("aaaa")'
    assert templates.set_variable_string_list("var", ["aaaa", 'va"l']) == 'var <- c("aaaa","va\\"l")'

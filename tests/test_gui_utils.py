from processing_r.gui.gui_utils import GuiUtils


def test_get_icon():
    """
    Tests get_icon
    """
    assert GuiUtils.get_icon("providerR.svg").isNull() is False
    assert GuiUtils.get_icon("not_an_icon.svg").isNull() is True


def test_get_icon_svg():
    """
    Tests get_icon svg path
    """
    assert GuiUtils.get_icon_svg("providerR.svg")
    assert "providerR.svg" in GuiUtils.get_icon_svg("providerR.svg")
    assert GuiUtils.get_icon_svg("not_an_icon.svg") == ""

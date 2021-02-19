from pytest_mock import MockFixture
from server.lib import ReportCardGenerator


def test_report_card_generator_init(mocker: MockFixture) -> None:
    def __mock_init(*args):
        assert len(args) == 3

    mocker.patch('server.lib.report_card_generator.ReportCardGenerator.__init__', __mock_init)
    ReportCardGenerator("templates", "report_card_template.html", "output")

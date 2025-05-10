from typing import Final

from jinja2 import Environment, FileSystemLoader, Template

REPORTS_TEMPLATE_DIR: Final[str] = "src/reports/infrastructure/pdf_reports/templates"


class TemplatesLoader:
    def __init__(self) -> None:
        self._loader = FileSystemLoader(REPORTS_TEMPLATE_DIR)
        self._env = Environment(loader=self._loader, autoescape=True)

    def get_report_template(self) -> Template:
        return self._env.get_template("report_template.html")

"""Static files for the server."""

import fastapi.templating
import pathlib

_BUILD_DIR = pathlib.Path(__file__).parent.parent.parent.parent.parent / "client" / "build"
_TEMPLATES_DIR = _BUILD_DIR
_STATIC_DIR = _BUILD_DIR / "static"
_MAIN_PAGE_FILENAME = "index.html"
_TEMPLATES = fastapi.templating.Jinja2Templates(directory=_TEMPLATES_DIR)


def create_main_page_html_response(request: fastapi.Request) -> fastapi.responses.HTMLResponse:
	"""Create a main page HTML response."""
	return _TEMPLATES.TemplateResponse(_MAIN_PAGE_FILENAME, {"request": request})


def mount_static_files(app: fastapi.FastAPI) -> None:
	"""Mount the static files."""
	app.mount("/static", fastapi.staticfiles.StaticFiles(directory=_STATIC_DIR), name="static")

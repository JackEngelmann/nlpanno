"""Logging configuration."""

import logging.config

LOGGING = {
	"version": 1,
	"disable_existing_loggers": False,
	"filters": {
		"correlation_id": {
			"()": "asgi_correlation_id.CorrelationIdFilter",
			"uuid_length": 32,
			"default_value": "-",
		},
	},
	"formatters": {
		"web": {
			"class": "colorlog.ColoredFormatter",
			"format": (
				"%(log_color)s%(levelname)s %(asctime)s "
				"[%(correlation_id)s]%(reset)s %(name)s - %(message)s"
			),
		},
	},
	"handlers": {
		"web": {
			"class": "logging.StreamHandler",
			"filters": ["correlation_id"],
			"formatter": "web",
		},
	},
	"loggers": {
		"": {
			"handlers": ["web"],
			"level": "DEBUG",
			"propagate": True,
		},
		"nlpanno": {
			"handlers": ["web"],
			"level": "DEBUG",
			"propagate": True,
		},
		"nlpanno.embedding": {
			"handlers": ["web"],
			"level": "DEBUG",
			"propagate": False,
		},
		"nlpanno.estimation": {
			"handlers": ["web"],
			"level": "DEBUG",
			"propagate": False,
		},
		"uvicorn": {
			"handlers": ["web"],
			"level": "INFO",
			"propagate": True,
		},
		"uvicorn.access": {
			"handlers": ["web"],
			"level": "ERROR",
			"propagate": True,
		},
	},
}


def configure_logging() -> None:
	"""Configure the logging."""
	logging.config.dictConfig(LOGGING)

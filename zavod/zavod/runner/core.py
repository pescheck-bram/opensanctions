# from typing import Callable
# from sqlalchemy.exc import OperationalError
# from requests.exceptions import RequestException
# from datapatch import LookupException

from zavod.meta import Dataset
from zavod.context import Context
from zavod.runtime.stats import ContextStats
from zavod.runtime.loader import load_entry_point
from zavod.runner.enrich import dataset_enricher

# HACK: Importing the enrich module in the test avoids a segfault otherwise happening
# on OS X, probably related to the nested use of import_module.
assert dataset_enricher is not None


def run_dataset(dataset: Dataset, dry_run: bool = False) -> ContextStats:
    """Load the dataset entry point, configure a context, and then execute the entry
    point; finally disband the context."""
    context = Context(dataset, dry_run=dry_run)
    try:
        context.begin(clear=True)
        entry_point = load_entry_point(dataset)
        entry_point(context)
    finally:
        context.close()
    return context.stats


# def execute_runner(dataset: Dataset, method: Callable):
#     """Run the crawler."""
#     context = Context(dataset)
#     if dataset.disabled:
#         context.log.info("Source is disabled", dataset=dataset.name)
#         return True

#     context.bind()
#     if context.source.disabled:
#         context.log.info("Source is disabled")
#         return True
#     context.issues.clear()
#     # with engine_tx() as conn:
#     #     clear_resources(conn, context.dataset, category=context.SOURCE_CATEGORY)
#     # context.log.info("Begin crawl", run_time=settings.RUN_TIME_ISO)
#     context._entity_count = 0
#     context._statement_count = 0
#     try:
#         # Run the dataset:
#         context.source.method(context)
#         context.flush()
#         if context._entity_count == 0:
#             context.log.warn(
#                 "Crawler did not emit entities",
#                 statements=context._statement_count,
#             )
#         else:
#             if not context.dry_run:
#                 # with engine_tx() as conn:
#                 #     cleanup_dataset(conn, context.dataset)
#                 pass
#         context.log.info("Crawl completed", entities=context._entity_count)
#         return True
#     except KeyboardInterrupt:
#         context.log.warning("Aborted by user (SIGINT)")
#         return False
#     except LookupException as lexc:
#         context.log.error(lexc.message, lookup=lexc.lookup.name, value=lexc.value)
#         return False
#     except OperationalError as oexc:
#         context.log.error("Database error: %r" % oexc)
#         return False
#     except RequestException as rexc:
#         resp = repr(rexc.response)
#         context.log.error(str(rexc), url=rexc.request.url, response=resp)
#         return False
#     except Exception as exc:
#         context.log.exception("Crawl failed", error=str(exc))
#         raise
#     finally:
#         context.close()
from functools import lru_cache
from html.parser import HTMLParser
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import parse_qs, quote_plus, unquote, urlparse

import requests

from utils.skill_formatter import format_skill


class OrganicResultParser(HTMLParser):
    def __init__(
        self
    ):
        super().__init__()
        self.links = []
        self._inside_result_link = False

    def handle_starttag(
        self,
        tag,
        attrs
    ):
        attrs = dict(
            attrs
        )

        if tag != "a":
            return

        classes = attrs.get(
            "class",
            ""
        )

        if "result__a" not in classes:
            return

        href = attrs.get(
            "href",
            ""
        )

        if href:
            self.links.append(
                href
            )


def _search_url(
    query
):
    return f"https://duckduckgo.com/?q={quote_plus(f'!ducky {query}')}"


def _extract_direct_url(
    href
):
    parsed = urlparse(
        href
    )

    if parsed.query:
        query = parse_qs(
            parsed.query
        )

        if "uddg" in query:
            return unquote(
                query["uddg"][0]
            )

    if href.startswith(
        "//"
    ):
        return f"https:{href}"

    return href


@lru_cache(
    maxsize=256
)
def _first_organic_result(
    query
):
    search_page = f"https://duckduckgo.com/html/?q={quote_plus(query)}"

    try:
        response = requests.get(
            search_page,
            timeout=4,
            headers={
                "User-Agent": "Mozilla/5.0 CareerAuditAI/1.0"
            }
        )
        response.raise_for_status()
        parser = OrganicResultParser()
        parser.feed(
            response.text
        )

        for href in parser.links:
            direct_url = _extract_direct_url(
                href
            )

            if direct_url.startswith(
                "http"
            ):
                return direct_url

    except requests.RequestException:
        pass

    return _search_url(
        query
    )


def recommend_resources(
    missing_skills
):
    recommendations = {}
    jobs = []

    for skill in missing_skills:
        skill_name = format_skill(
            skill
        )

        if not skill_name:
            continue

        queries = {
            "course": f"{skill_name} practical course job ready",
            "docs": f"{skill_name} official documentation",
            "projects": f"{skill_name} portfolio project GitHub",
            "interview": f"{skill_name} interview questions"
        }

        recommendations[skill_name] = {}

        for resource_type, query in queries.items():
            jobs.append(
                (
                    skill_name,
                    resource_type,
                    query
                )
            )

    with ThreadPoolExecutor(
        max_workers=8
    ) as executor:
        future_map = {
            executor.submit(
                _first_organic_result,
                query
            ): (
                skill_name,
                resource_type
            )
            for skill_name, resource_type, query in jobs
        }

        for future, (
            skill_name,
            resource_type
        ) in future_map.items():
            recommendations[skill_name][resource_type] = future.result()

    for skill_name, links in recommendations.items():
        if links:
            continue

        recommendations[skill_name] = {
            "course": _search_url(
                f"{skill_name} practical course job ready"
            ),
            "docs": _search_url(
                f"{skill_name} official documentation"
            ),
            "projects": _search_url(
                f"{skill_name} portfolio project GitHub"
            ),
            "interview": _search_url(
                f"{skill_name} interview questions"
            )
        }

    return recommendations

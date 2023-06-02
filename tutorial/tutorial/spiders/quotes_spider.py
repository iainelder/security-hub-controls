from pathlib import Path
import urllib.parse
from itertools import dropwhile

from more_itertools import split_before
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import SelectorList


class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def start_requests(self):
        yield scrapy.Request(
            url="https://docs.aws.amazon.com/securityhub/latest/userguide/securityhub-controls-reference.html",
            callback=self.parse_links_to_control_pages
        )
    
    def parse_links_to_control_pages(self, response):
        links = LinkExtractor(restrict_text=".* controls$").extract_links(response)
        for request in response.follow_all(links, callback=self.parse_controls):
            yield request
    
    def parse_controls(self, response):
        body_elements = response.css('[id="main-col-body"] > *')
        drop_till_control_header = dropwhile(
            lambda s: s.root.tag != "h2", body_elements
        )
        drop_non_control_elements = (
            s for s in drop_till_control_header if not s.root.tag.startswith("aws")
        )
        group_by_control = split_before(
            drop_non_control_elements, lambda s: s.root.tag == "h2"
        )
        selector_lists = (SelectorList(group) for group in group_by_control)

        for sl in selector_lists:
            control = self.extract_control(response, sl)
            yield control

    def extract_control(self, response, control_selectors):
        id_and_title = control_selectors[0].xpath("normalize-space(text())").get()
        dirty_id, title = id_and_title.split(" ", maxsplit=1)
        control_id = dirty_id.strip("[]")

        requirements = self.extract_requirements(response, control_selectors)

        severity = self.extract_severity(response, control_selectors)

        schedule_type = self.extract_schedule_type(response, control_selectors)

        # Key order for now is same as table-driven v1 scraper to make comparisons easier.
        return {
            "Id": control_id,
            "RelatedRequirements": requirements,
            "Title": title,
            "Severity": severity,
            "SecheduleType": schedule_type,
        }

    def extract_requirements(self, response, control_selectors):
        dirty_requirements = first_whose_text_contains(
            "Related requirements", control_selectors
        )
        if dirty_requirements is None:
            return None

        dirty_split = (
            dirty_requirements.root.text_content()
            .split("Related requirements: ")[1]
            .split(",")
        )

        requirements = [d.strip() for d in dirty_split]

        return requirements

    def extract_severity(self, repsonse, control_selectors):
        dirty_severity = first_whose_text_contains("Severity", control_selectors)
        if dirty_severity is None:
            return None
        
        severity = dirty_severity.root.text_content().split("Severity: ")[1]

        return severity

    def extract_schedule_type(self, repsonse, control_selectors):
        dirty_schedule = first_whose_text_contains("Schedule type", control_selectors)
        if dirty_schedule is None:
            return None

        schedule_type = dirty_schedule.root.text_content().split("Schedule type: ")[1]

        return schedule_type


def first_whose_text_contains(text, selectors):
    for s in selectors:
        if text in s.root.text_content():
            return s
    return None

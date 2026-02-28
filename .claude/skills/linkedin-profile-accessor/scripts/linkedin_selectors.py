"""
LinkedIn Profile Accessor - CSS Selectors

Defines all CSS selectors used for LinkedIn profile data extraction.
Multiple fallback selectors are provided for robustness.
"""

from typing import List, Dict


# Profile section selectors with fallbacks
PROFILE_SELECTORS: Dict[str, List[str]] = {
    'name': [
        'h1.text-heading-xlarge',
        'h1',
        '[data-anonymize="person-name"]',
        '.pv-text-details__left-panel h1',
        '.pv-top-card--list-bullet li:first-child'
    ],
    'headline': [
        'div.text-body-medium.break-words',
        '.text-body-medium',
        '.headline',
        '.pv-text-details__left-panel .text-body-medium',
        '.pv-top-card--list-bullet li:nth-child(2)'
    ],
    'location': [
        'span.text-body-small.inline.t-black--light',
        '.pv-text-details__left-panel .text-body-small',
        '.mt2.relative .text-body-small',
        '.pv-top-card--list-bullet li:nth-child(3) span'
    ],
    'about': [
        'div.display-flex.ph5.pv-about__summary-text',
        '.pv-about__summary-text',
        '.pv-about-section',
        '#about ~ div div',
        '.pv-about-section__summary-text'
    ],
    'connections': [
        'span.t-black--light',
        '.pv-top-card--list-bullet li span',
        '.pv-top-card--list-bullet li',
        '.pv-top-card--list-bullet'
    ],
    'profile_photo': [
        'img.pv-top-card-profile-picture__image',
        '.pv-top-card-profile-picture img',
        'img.profile-photo-edit__preview',
        '.pv-top-card__photo img'
    ]
}


# Section container selectors
SECTION_SELECTORS: Dict[str, List[str]] = {
    'experience': [
        '#experience',
        '.pv-profile-section__card-item-v2',
        '[data-section="experience"]',
        'section[aria-labelledby="experience"]',
        '.pvs-list__outer-container:has(span:has-text("Experience"))'
    ],
    'education': [
        '#education',
        '.pv-profile-section__card-item-v2',
        '[data-section="education"]',
        'section[aria-labelledby="education"]',
        '.pvs-list__outer-container:has(span:has-text("Education"))'
    ],
    'skills': [
        '#skills',
        '.pv-skill-category-entity__name',
        '[data-section="skills"]',
        'section[aria-labelledby="skills"]',
        '.pvs-list__outer-container:has(span:has-text("Skills"))'
    ],
    'recommendations': [
        '#recommendations',
        '.pv-recommendation-entity',
        '[data-section="recommendations"]',
        '.pv-recommendations-section'
    ],
    'activity': [
        '#activity',
        '.occludable-update',
        '[data-section="activity"]',
        '.pv-recent-activity-section',
        '.pv-profile-section__activity-section'
    ]
}


# Experience item selectors
EXPERIENCE_SELECTORS: Dict[str, List[str]] = {
    'container': [
        '.pvs-list__item--line-separated',
        '.pv-profile-section__card-item-v2',
        '.experience-item',
        '[data-urn*="experience"]'
    ],
    'title': [
        '.t-semibold',
        'span[aria-hidden="true"]',
        '.pv-entity__summary-info h3',
        '.t-16'
    ],
    'company': [
        '.t-14.t-black--light',
        '.pv-entity__secondary-title',
        '.inline-show-more-text'
    ],
    'date_range': [
        '.t-14.t-black--light',
        '.pv-entity__date-range span:nth-child(2)',
        'span.t-black--light'
    ],
    'description': [
        '.pv-entity__description',
        '.inline-show-more-text--is-collapsed',
        '.t-14.t-normal'
    ]
}


# Education item selectors
EDUCATION_SELECTORS: Dict[str, List[str]] = {
    'container': [
        '.pvs-list__item--line-separated',
        '.pv-profile-section__card-item-v2',
        '.education-item',
        '[data-urn*="education"]'
    ],
    'school': [
        '.t-semibold',
        'span[aria-hidden="true"]',
        '.pv-entity__school-name'
    ],
    'degree': [
        '.pv-entity__degree-name',
        '.t-14',
        'span:has-text("Degree")'
    ],
    'field_of_study': [
        '.pv-entity__fos',
        '.t-14.t-black--light'
    ],
    'years': [
        '.pv-entity__dates',
        '.t-14.t-black--light'
    ]
}


# Skills selectors
SKILLS_SELECTORS: Dict[str, List[str]] = {
    'container': [
        '.pvs-list__item--line-separated',
        '.pv-skill-category-entity__name',
        '.pv-skill-entity',
        '[data-urn*="skill"]'
    ],
    'name': [
        '.t-semibold',
        'span[aria-hidden="true"]',
        '.pv-skill-entity__name'
    ],
    'endorsements': [
        '.pv-skill-entity__endorpment-count',
        '.t-black--light.t-12',
        'span:has-text("endorsement")'
    ]
}


# Post selectors
POST_SELECTORS: Dict[str, List[str]] = {
    'container': [
        '.occludable-update',
        '.pv-recent-activity-section__update-item',
        '[data-urn*="activity"]',
        '.feed-shared-update'
    ],
    'text': [
        '.feed-shared-update-v2__description',
        '.feed-shared-text',
        '.update-card__content',
        '[data-urn*="feedUpdate"] span'
    ],
    'reactions': [
        '.social-details-reactors__count',
        'span:has-text("reaction")',
        '.t-black--light'
    ],
    'comments': [
        '.social-details-social-counts__comments',
        'span:has-text("comment")'
    ],
    'date': [
        '.feed-shared-update-v2__time-ago',
        'span:has-text("ago")',
        '.t-12'
    ]
}


# Navigation selectors
NAVIGATION_SELECTORS: Dict[str, List[str]] = {
    'profile_tab': [
        '//nav//a[contains(text(), "Profile")]',
        '//a[@data-link-to="profile"]',
        '.global-nav__nav-item a[href*="/in/"]',
        'a[ href*="/in/"][aria-label]'
    ],
    'network_tab': [
        '//nav//a[contains(text(), "My Network")]',
        '//a[@data-link-to="network"]',
        '.global-nav__nav-item a[href*="/mynetwork/"]'
    ]
}


# Connection selectors
CONNECTION_SELECTORS: Dict[str, List[str]] = {
    'container': [
        '.mn-connection-card',
        '.pv-entity__summary-info',
        '.artdeco-entity-lockup',
        '[data-urn*="connection"]'
    ],
    'name': [
        '.mn-connection-card__name',
        '.pv-entity__summary-title-text',
        '.artdeco-entity-lockup__title',
        'a[href*="/in/"]'
    ],
    'headline': [
        '.mn-connection-card__occupation',
        '.pv-entity__summary-subtitle',
        '.artdeco-entity-lockup__subtitle',
        '.t-14'
    ],
    'company': [
        '.t-14.t-black--light',
        '.pv-entity__secondary-title'
    ],
    'mutual_connections': [
        '.mn-connection-card__mutual-connections',
        'span:has-text("mutual")'
    ]
}


# Login status detection
LOGIN_INDICATORS: List[str] = [
    '.global-nav__me',
    '[data-control-name="identity_watcher_profile_photo"]',
    '.profile-rail-card__actor-link',
    'div.profile-rail-card',
    '.nav-item__icon--profile'
]


# Utility functions for selectors
def get_primary_selector(selector_dict: Dict[str, List[str]], key: str) -> str:
    """Get the primary (first) selector for a key."""
    return selector_dict.get(key, [""])[0]


def get_all_selectors(selector_dict: Dict[str, List[str]], key: str) -> List[str]:
    """Get all selectors for a key (including fallbacks)."""
    return selector_dict.get(key, [])


# XPath selectors (as strings for use with page.locator() or page.evaluate())
XPATH_SELECTORS = {
    'name': '//h1[contains(@class, "text-heading-xlarge")]',
    'headline': '//div[contains(@class, "text-body-medium")]',
    'about': '//div[contains(@class, "pv-about__summary-text")]',
}

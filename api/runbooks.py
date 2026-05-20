"""
Runbook query suggestions mapped from issue category.
Based on Marvis Runbooks 01 (Wireless), 02 (Switching), 03 (End-to-End).

Each suggestion has a `troubleshoot_type` that maps to the Mist troubleshoot API:
  "client"   → GET /orgs/{org_id}/troubleshoot?mac={mac}
  "wireless" → GET /orgs/{org_id}/troubleshoot?site_id={site_id}
  "wired"    → GET /orgs/{org_id}/troubleshoot?site_id={site_id}&type=wired
  "wan"      → GET /orgs/{org_id}/troubleshoot?site_id={site_id}&type=wan
"""


ISSUE_CATEGORIES = [
    {"id": "cant_connect",     "label": "Can't connect to Wi-Fi",          "hint": "No connection, authentication failure, keeps disconnecting", "type": "wireless"},
    {"id": "wifi_slow",        "label": "Wi-Fi is slow or calls dropping",  "hint": "Performance issues, coverage problems, roaming drops",       "type": "wireless"},
    {"id": "auth_failed",      "label": "Device won't authenticate",         "hint": "802.1X, RADIUS, WPA-Enterprise, wrong password",             "type": "wireless"},
    {"id": "connected_no_net", "label": "Connected but nothing works",       "hint": "Has an IP address, but no traffic flows",                    "type": "wireless"},
    {"id": "port_dead",        "label": "Desk port / cable is dead",         "hint": "No link light, no DHCP on wired connection",                 "type": "wired"},
    {"id": "poe_issue",        "label": "Phone / AP / camera not powering",  "hint": "PoE device won't boot, AP not coming up",                   "type": "wired"},
    {"id": "switch_down",      "label": "Whole floor or closet is down",     "hint": "Multiple wired ports affected, switch unreachable",          "type": "wired"},
    {"id": "site_wide",        "label": "Whole site is affected",            "hint": "Everyone at a location has issues, not one user",            "type": "both"},
    {"id": "auth_backend",     "label": "SSO / RADIUS / cert auth broken",   "hint": "Identity system issue affecting many users",                 "type": "both"},
    {"id": "slow_both",        "label": "Slow on Wi-Fi AND when plugged in", "hint": "Performance bad regardless of connection type",              "type": "both"},
    {"id": "other",            "label": "Something else",                    "hint": "Not covered by the options above",                           "type": "both"},
]

# Maps issue category to ordered list of troubleshoot checks.
# "client" requires a MAC; "wireless"/"wired"/"wan" require a site_id.
_QUERIES = {
    "cant_connect": [
        {"label": "Troubleshoot this client (start here)", "troubleshoot_type": "client"},
        {"label": "Site wireless health check",            "troubleshoot_type": "wireless"},
    ],
    "wifi_slow": [
        {"label": "Troubleshoot this client",              "troubleshoot_type": "client"},
        {"label": "Site wireless health check",            "troubleshoot_type": "wireless"},
    ],
    "auth_failed": [
        {"label": "Troubleshoot this client",              "troubleshoot_type": "client"},
        {"label": "Site wireless health check",            "troubleshoot_type": "wireless"},
    ],
    "connected_no_net": [
        {"label": "Troubleshoot this client",              "troubleshoot_type": "client"},
        {"label": "Site wireless health check",            "troubleshoot_type": "wireless"},
        {"label": "Site wired health check",               "troubleshoot_type": "wired"},
    ],
    "port_dead": [
        {"label": "Troubleshoot this client",              "troubleshoot_type": "client"},
        {"label": "Site wired health check",               "troubleshoot_type": "wired"},
    ],
    "poe_issue": [
        {"label": "Site wired health check",               "troubleshoot_type": "wired"},
    ],
    "switch_down": [
        {"label": "Site wired health check",               "troubleshoot_type": "wired"},
    ],
    "site_wide": [
        {"label": "Site wireless health check",            "troubleshoot_type": "wireless"},
        {"label": "Site wired health check",               "troubleshoot_type": "wired"},
        {"label": "WAN / gateway health check",            "troubleshoot_type": "wan"},
    ],
    "auth_backend": [
        {"label": "Site wireless health check",            "troubleshoot_type": "wireless"},
    ],
    "slow_both": [
        {"label": "Site wireless health check",            "troubleshoot_type": "wireless"},
        {"label": "Site wired health check",               "troubleshoot_type": "wired"},
        {"label": "WAN / gateway health check",            "troubleshoot_type": "wan"},
    ],
    "other": [
        {"label": "Troubleshoot this client",              "troubleshoot_type": "client"},
        {"label": "Site wireless health check",            "troubleshoot_type": "wireless"},
    ],
}


def get_suggested_queries(category_id: str) -> list[dict]:
    return _QUERIES.get(category_id, _QUERIES["other"])


ESCALATION_GUIDANCE = {
    "cant_connect":     "If Marvis reports 'RADIUS server is inactive' or 'NAC IdP is unreachable,' escalate to Tier 3 / Identity team.",
    "auth_failed":      "If Marvis identifies a RADIUS or 802.1X backend issue, loop in the Identity/NAC team before going deeper.",
    "auth_backend":     "If RADIUS is inactive or the IdP is unreachable, the problem is upstream of Mist. Loop in IAM before going deeper.",
    "poe_issue":        "Confirm total PoE budget on the switch isn't exceeded before escalating to hardware replacement.",
    "switch_down":      "If spanning-tree issues detected, do not make changes without consulting the network team.",
    "connected_no_net": "If rogue DHCP is detected, disable the offending port and involve the network team.",
}

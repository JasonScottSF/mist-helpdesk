"""
Runbook query suggestions mapped from issue category + context.
Based on Marvis Runbooks 01 (Wireless), 02 (Switching), 03 (End-to-End).
"""

from typing import Optional


ISSUE_CATEGORIES = [
    {"id": "cant_connect",        "label": "Can't connect to Wi-Fi",          "hint": "No connection, authentication failure, keeps disconnecting", "type": "wireless"},
    {"id": "wifi_slow",           "label": "Wi-Fi is slow or calls dropping",  "hint": "Performance issues, coverage problems, roaming drops",       "type": "wireless"},
    {"id": "auth_failed",         "label": "Device won't authenticate",         "hint": "802.1X, RADIUS, WPA-Enterprise, wrong password",             "type": "wireless"},
    {"id": "connected_no_net",    "label": "Connected but nothing works",       "hint": "Has an IP address, but no traffic flows",                    "type": "wireless"},
    {"id": "port_dead",           "label": "Desk port / cable is dead",         "hint": "No link light, no DHCP on wired connection",                 "type": "wired"},
    {"id": "poe_issue",           "label": "Phone / AP / camera not powering",  "hint": "PoE device won't boot, AP not coming up",                   "type": "wired"},
    {"id": "switch_down",         "label": "Whole floor or closet is down",     "hint": "Multiple wired ports affected, switch unreachable",          "type": "wired"},
    {"id": "site_wide",           "label": "Whole site is affected",            "hint": "Everyone at a location has issues, not one user",            "type": "both"},
    {"id": "auth_backend",        "label": "SSO / RADIUS / cert auth broken",   "hint": "Identity system issue affecting many users",                 "type": "both"},
    {"id": "slow_both",           "label": "Slow on Wi-Fi AND when plugged in", "hint": "Performance bad regardless of connection type",              "type": "both"},
    {"id": "other",               "label": "Something else",                    "hint": "Not covered by the options above",                           "type": "both"},
]


def get_suggested_queries(
    category_id: str,
    client: Optional[str] = None,
    site: Optional[str] = None,
    timeframe: str = "today",
) -> list[dict]:
    """
    Return a list of { label, query } dicts pre-filled with client/site names.
    """
    c = client or "<client>"
    s = site or "<site>"
    tf = timeframe

    queries = {
        "cant_connect": [
            {"label": "Troubleshoot this client (start here)",     "query": f"troubleshoot client {c}"},
            {"label": "Ask why they can't connect",                "query": f"why can't {c} connect to the Wi-Fi?"},
            {"label": "Scope to reported timeframe",               "query": f"troubleshoot {c} {tf}"},
            {"label": "Show event timeline",                       "query": f"show me the events for {c} in the last 2 hours"},
            {"label": "Show authentication failures",              "query": f"show me {c}'s authentication failures today"},
            {"label": "Check scope — unhappy clients at site",     "query": f"show me unhappy clients at {s}"},
        ],

        "wifi_slow": [
            {"label": "Troubleshoot client",                       "query": f"troubleshoot {c}"},
            {"label": "Check client roaming history",              "query": f"show me {c}'s roaming today"},
            {"label": "Show coverage problems at site",            "query": f"show me clients with coverage problems at {s}"},
            {"label": "Show capacity issues at site",              "query": f"show me clients with capacity issues at {s}"},
            {"label": "Show throughput problems at site",          "query": f"show me clients with throughput problems at {s}"},
            {"label": "Identify problem APs",                      "query": f"which APs are generating the most client issues at {s}?"},
            {"label": "Show roaming failures at site",             "query": f"show me roaming failures at {s}"},
            {"label": "APs at 100 Mbps (hidden Wi-Fi degradation)","query": "show me APs running at 100 megs"},
        ],

        "auth_failed": [
            {"label": "Why can't client authenticate?",            "query": f"why can't {c} authenticate?"},
            {"label": "Troubleshoot client",                       "query": f"troubleshoot client {c}"},
            {"label": "Auth failures at site today",               "query": f"show me authentication failures at {s} today"},
            {"label": "Rank clients by auth failures (scope check)","query": "rank clients by authentication failures"},
            {"label": "Check RADIUS server health",                "query": "is the RADIUS server up?"},
            {"label": "Wrong-password events (PSK rotation issue)","query": "show me wrong-password events today"},
        ],

        "connected_no_net": [
            {"label": "Check DHCP servers at site",                "query": f"show me all the DHCP servers at {s}"},
            {"label": "Check DNS servers at site",                 "query": f"show me all the DNS servers in use at {s}"},
            {"label": "Check gateways at site",                    "query": f"show me all the gateways at {s}"},
            {"label": "DHCP failures this week",                   "query": "show me DHCP failures this week"},
            {"label": "DNS failures at site",                      "query": f"show me DNS failures at {s} today"},
            {"label": "Any rogue DHCP servers?",                   "query": "are there any rogue DHCP servers?"},
        ],

        "port_dead": [
            {"label": "Troubleshoot wired switch",                 "query": f"troubleshoot switch"},
            {"label": "Show wired clients at site",                "query": f"show me wired clients at {s}"},
            {"label": "Show port flaps",                           "query": "show me port flaps"},
            {"label": "Show port-down events today",               "query": "show me port-down events today"},
            {"label": "List switches at site",                     "query": f"list switches at {s}"},
            {"label": "Search for client by name or MAC",          "query": f"search for client {c}"},
        ],

        "poe_issue": [
            {"label": "Show PoE failures at site",                 "query": f"show me PoE failures at {s}"},
            {"label": "Show PoE-denied events",                    "query": f"show me PoE-denied events at {s}"},
            {"label": "APs at 100 Mbps (degraded PoE)",           "query": "show me APs running at 100 megs"},
            {"label": "APs not getting full PoE power",            "query": "which APs aren't getting full PoE power?"},
            {"label": "Is switch over PoE budget?",                "query": "is the switch over its PoE budget?"},
        ],

        "switch_down": [
            {"label": "Site health check",                         "query": f"troubleshoot {s}"},
            {"label": "List switches at site",                     "query": f"list switches at {s}"},
            {"label": "Which switches are offline?",               "query": "which switches are offline?"},
            {"label": "Switch restarts in last 24h",               "query": "show me switch restarts in the last 24 hours"},
            {"label": "Spanning-tree topology changes",            "query": f"show me spanning-tree topology changes at {s}"},
            {"label": "BPDU guard events (loop / rogue switch)",   "query": "show me BPDU block events"},
        ],

        "site_wide": [
            {"label": "Site health check (quick verdict)",         "query": f"how is {s}?"},
            {"label": "Site full troubleshoot",                    "query": f"troubleshoot {s}"},
            {"label": "Show unhappy clients at site",              "query": f"show me unhappy clients at {s}"},
            {"label": "Identify problem APs",                      "query": f"which APs are generating the most issues at {s}?"},
            {"label": "Switches reporting issues",                 "query": f"which switches are reporting issues at {s}?"},
            {"label": "Any active anomalies org-wide?",            "query": "are there any active anomalies?"},
        ],

        "auth_backend": [
            {"label": "Is RADIUS server up?",                      "query": "is the RADIUS server up?"},
            {"label": "Auth failures in last hour",                "query": "show me authentication failures in the last hour"},
            {"label": "Rank clients by auth failures",             "query": "rank clients by authentication failures"},
            {"label": "Is identity provider reachable?",           "query": "is the identity provider reachable?"},
            {"label": "Why can't users authenticate at site?",     "query": f"why can't users authenticate at {s}?"},
        ],

        "slow_both": [
            {"label": "Site full troubleshoot",                    "query": f"troubleshoot {s}"},
            {"label": "Show uplink issues at site",                "query": f"show me uplink issues at {s}"},
            {"label": "Show interfaces with high utilization",     "query": f"show me interfaces with high utilization at {s}"},
            {"label": "APs at 100 Mbps (uplink not gig)",         "query": f"show me APs running at 100 megs at {s}"},
            {"label": "Show throughput problems at site",          "query": f"show me clients with throughput problems at {s}"},
            {"label": "WAN / gateway health check",                "query": f"is there a WAN issue at {s}?"},
        ],

        "other": [
            {"label": "Troubleshoot client",                       "query": f"troubleshoot client {c}"},
            {"label": "Site health check",                         "query": f"how is {s}?"},
            {"label": "Show unhappy clients",                      "query": f"show me unhappy clients at {s}"},
        ],
    }

    return queries.get(category_id, queries["other"])


ESCALATION_GUIDANCE = {
    "cant_connect":     "If Marvis reports 'RADIUS server is inactive' or 'NAC IdP is unreachable,' escalate to Tier 3 / Identity team.",
    "auth_failed":      "If Marvis identifies a RADIUS or 802.1X backend issue, loop in the Identity/NAC team before going deeper.",
    "auth_backend":     "If RADIUS is inactive or the IdP is unreachable, the problem is upstream of Mist. Loop in IAM before going deeper.",
    "poe_issue":        "Confirm total PoE budget on the switch isn't exceeded before escalating to hardware replacement.",
    "switch_down":      "If spanning-tree issues detected, do not make changes without consulting the network team.",
    "connected_no_net": "If rogue DHCP is detected, disable the offending port and involve the network team.",
}

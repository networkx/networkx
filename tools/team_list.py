import os
import sys
import requests


project = "networkx"
core = "core-developers"
emeritus = "emeritus-developers"
core_url = f"https://api.github.com/orgs/{project}/teams/{core}/members"
emeritus_url = f"https://api.github.com/orgs/{project}/teams/{emeritus}/members"


token = os.environ.get("GH_TOKEN", None)
if token is None:
    print(
        "No token found.  Please export a GH_TOKEN with permissions "
        "to read team members."
    )
    sys.exit(-1)


def api(url):
    return requests.get(url=url, headers={"Authorization": f"token {token}"}).json()


resp = api(core_url)
core = sorted(resp, key=lambda user: user["login"].lower())

resp = api(emeritus_url)
emeritus = sorted(resp, key=lambda user: user["login"].lower())


def render_team(team):
    for member in team:
        profile = api(member["url"])

        print(
            f"""
.. raw:: html

   <div class="team-member">
     <div class="team-member-photo">
       <img src="{member['avatar_url']}&s=40"/>
     </div>
     <a href="https://github.com/{member['login']}" class="team-member-name">{profile['name']}</a>
     <div class="team-member-handle">@{member['login']}</div>
   </div>
"""
        )


print(
    """
Our Team
--------

Along with a large community of contributors, NetworkX development
is guided by the following core team:

"""
)

render_team(core)

print(
    """

Emeritus Developers
-------------------

We thank these previously-active core developers for their contributions to NetworkX.

"""
)

render_team(emeritus)

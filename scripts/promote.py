"""Open an immutable dev promotion using a narrowly scoped GitHub App token."""
import base64
import json
import os
import urllib.request

REPO = "expertnafees-hub/gitops-platform-config"

def api(method, path, data=None):
    request = urllib.request.Request(
        "https://api.github.com" + path,
        data=json.dumps(data).encode() if data is not None else None,
        method=method,
        headers={"Authorization": "Bearer " + os.environ["GH_TOKEN"],
                 "Accept": "application/vnd.github+json",
                 "Content-Type": "application/json",
                 "X-GitHub-Api-Version": "2022-11-28"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)

def main():
    base = f"/repos/{REPO}"
    branch = "promote/dev-" + os.environ["GITHUB_RUN_ID"] + "-" + os.environ["GITHUB_RUN_ATTEMPT"]
    head = api("GET", base + "/git/ref/heads/main")["object"]["sha"]
    api("POST", base + "/git/refs", {"ref": "refs/heads/" + branch, "sha": head})
    path = "/contents/environments/dev/values.yaml"
    previous = api("GET", base + path + "?ref=" + head)
    # JSON is valid YAML; preserve every existing environment setting.
    values = json.loads(base64.b64decode(previous["content"]))
    values["image"] = {"repository": os.environ["IMAGE_REPOSITORY"], "digest": os.environ["IMAGE_DIGEST"]}
    values["appVersion"] = os.environ["GITHUB_SHA"]
    api("PUT", base + path, {
        "message": "Promote core-api to development",
        "branch": branch, "sha": previous["sha"],
        "content": base64.b64encode((json.dumps(values, indent=2) + "\n").encode()).decode(),
    })
    pull = api("POST", base + "/pulls", {
        "title": "Deploy core-api " + os.environ["GITHUB_SHA"][:12] + " to development",
        "head": branch, "base": "main",
        "body": "Selects the scanned image `" + os.environ["IMAGE_REPOSITORY"] + "@" + os.environ["IMAGE_DIGEST"] + "`. Review required before Argo CD reconciliation.",
    })
    print(pull["html_url"])

if __name__ == "__main__":
    main()
